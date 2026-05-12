import logging
from datetime import datetime, UTC, timedelta
from typing import Optional

from supabase import Client
from app.cognitive.utils import calculate_cognitive_score

logger = logging.getLogger(__name__)

class CognitiveRepository:
    def __init__(self, client: Client):
        self.client = client

    def get_baseline(self, patient_id: str) -> Optional[dict]:
        try:
            result = (
                self.client.table("cognitive_baselines")
                .select("*")
                .eq("patient_id", patient_id)
                .maybe_single()
                .execute()
            )
            row = result.data
            if not row:
                return None
            return {
                "patient_id": row["patient_id"],
                "established": row.get("established", False),
                "baseline_date": row.get("baseline_date"),
                "vocabulary_diversity": float(row.get("vocab_diversity") or 0),
                "vocabulary_diversity_std": float(row.get("vocab_diversity_std") or 0),
                "topic_coherence": float(row.get("topic_coherence") or 0),
                "topic_coherence_std": float(row.get("topic_coherence_std") or 0),
                "repetition_rate": float(row.get("repetition_rate") or 0),
                "repetition_rate_std": float(row.get("repetition_rate_std") or 0),
                "word_finding_pauses": float(row.get("word_finding_pauses") or 0),
                "word_finding_pauses_std": float(row.get("word_finding_pauses_std") or 0),
                "avg_response_time": float(row.get("avg_response_time") or 0) if row.get("avg_response_time") else None,
                "response_time_std": float(row.get("response_time_std") or 0) if row.get("response_time_std") else None,
                "conversation_count": row.get("conversation_count", 0),
                "last_updated": row.get("last_updated"),
            }
        except Exception as exc:
            logger.error(f"CognitiveRepository.get_baseline failed: {exc}")
            return None

    def save_baseline(self, patient_id: str, baseline: dict) -> None:
        try:
            row = {
                "patient_id": patient_id,
                "established": baseline.get("established", False),
                "baseline_date": baseline.get("baseline_date"),
                "vocab_diversity": baseline.get("vocabulary_diversity"),
                "vocab_diversity_std": baseline.get("vocabulary_diversity_std"),
                "topic_coherence": baseline.get("topic_coherence"),
                "topic_coherence_std": baseline.get("topic_coherence_std"),
                "repetition_rate": baseline.get("repetition_rate"),
                "repetition_rate_std": baseline.get("repetition_rate_std"),
                "word_finding_pauses": baseline.get("word_finding_pauses"),
                "word_finding_pauses_std": baseline.get("word_finding_pauses_std"),
                "avg_response_time": baseline.get("avg_response_time"),
                "response_time_std": baseline.get("response_time_std"),
                "conversation_count": baseline.get("conversation_count", 0),
                "last_updated": baseline.get("last_updated") or datetime.now(UTC).isoformat(),
            }
            self.client.table("cognitive_baselines").upsert(row, on_conflict="patient_id").execute()
        except Exception as exc:
            logger.error(f"CognitiveRepository.save_baseline failed: {exc}")

    def get_deviations(self, patient_id: str) -> dict:
        try:
            result = (
                self.client.table("deviation_trackers")
                .select("metrics")
                .eq("patient_id", patient_id)
                .maybe_single()
                .execute()
            )
            return (result.data or {}).get("metrics", {})
        except Exception as exc:
            logger.error(f"CognitiveRepository.get_deviations failed: {exc}")
            return {}

    def update_deviations(
        self, patient_id: str, deviations: dict
    ) -> None:
        try:
            self.client.table("deviation_trackers").upsert({
                "patient_id": patient_id,
                "metrics": deviations,
                "updated_at": datetime.now(UTC).isoformat(),
            }, on_conflict="patient_id").execute()
        except Exception as exc:
            logger.error(f"CognitiveRepository.update_deviations failed: {exc}")

    def get_trends(self, patient_id: str, days: int = 30) -> list[dict]:
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        try:
            result = (
                self.client.table("conversations")
                .select("timestamp, vocab_diversity, topic_coherence, repetition_rate, word_finding_pauses, response_latency")
                .eq("patient_id", patient_id)
                .gte("timestamp", cutoff)
                .not_.is_("vocab_diversity", "null")
                .order("timestamp", desc=False)
                .execute()
            )
            trends = []
            for row in (result.data or []):
                metrics_dict = {
                    "vocabulary_diversity": float(row["vocab_diversity"]) if row.get("vocab_diversity") else None,
                    "topic_coherence": float(row["topic_coherence"]) if row.get("topic_coherence") else None,
                    "repetition_rate": float(row["repetition_rate"]) if row.get("repetition_rate") else None,
                    "word_finding_pauses": row.get("word_finding_pauses"),
                }
                trends.append({
                    "timestamp": row["timestamp"],
                    "vocabulary_diversity": metrics_dict["vocabulary_diversity"],
                    "topic_coherence": metrics_dict["topic_coherence"],
                    "repetition_rate": metrics_dict["repetition_rate"],
                    "word_finding_pauses": metrics_dict["word_finding_pauses"],
                    "response_latency": float(row["response_latency"]) if row.get("response_latency") else None,
                    "cognitive_score": calculate_cognitive_score(metrics_dict),
                })
            return trends
        except Exception as exc:
            logger.error(f"CognitiveRepository.get_trends failed: {exc}")
            return []

    def get_patient_insights(self, patient_id: str) -> dict:
        """Cross-table aggregation insights using SQL via Supabase."""
        try:
            # 1) All conversations with metrics + mood + nostalgia flag
            conv_result = (
                self.client.table("conversations")
                .select("detected_mood, vocab_diversity, topic_coherence, nostalgia_triggered")
                .eq("patient_id", patient_id)
                .not_.is_("vocab_diversity", "null")
                .execute()
            )
            convos = conv_result.data or []

            # Cognitive by mood
            mood_buckets: dict = {}
            for c in convos:
                mood = c.get("detected_mood", "unknown")
                if mood not in mood_buckets:
                    mood_buckets[mood] = {"vocabs": [], "coherences": [], "count": 0}
                v = c.get("vocab_diversity")
                co = c.get("topic_coherence")
                if v is not None:
                    mood_buckets[mood]["vocabs"].append(float(v))
                if co is not None:
                    mood_buckets[mood]["coherences"].append(float(co))
                mood_buckets[mood]["count"] += 1

            cognitive_by_mood = {}
            for mood, b in mood_buckets.items():
                av = sum(b["vocabs"]) / len(b["vocabs"]) if b["vocabs"] else 0
                ac = sum(b["coherences"]) / len(b["coherences"]) if b["coherences"] else 0
                cognitive_by_mood[mood] = {
                    "avg_vocabulary": round(av, 3),
                    "avg_coherence": round(ac, 3),
                    "conversation_count": b["count"],
                }

            # Nostalgia effectiveness
            with_n = [c for c in convos if c.get("nostalgia_triggered")]
            without_n = [c for c in convos if not c.get("nostalgia_triggered")]

            def _avg(lst, key):
                vals = [float(x[key]) for x in lst if x.get(key) is not None]
                return sum(vals) / len(vals) if vals else 0.0

            wv, wov = _avg(with_n, "vocab_diversity"), _avg(without_n, "vocab_diversity")
            wc, woc = _avg(with_n, "topic_coherence"), _avg(without_n, "topic_coherence")
            vi = ((wv - wov) / wov * 100) if wov > 0 else 0
            ci = ((wc - woc) / woc * 100) if woc > 0 else 0

            nostalgia_effectiveness = {
                "with_nostalgia": {"avg_vocabulary": round(wv, 3), "avg_coherence": round(wc, 3), "count": len(with_n)},
                "without_nostalgia": {"avg_vocabulary": round(wov, 3), "avg_coherence": round(woc, 3), "count": len(without_n)},
                "improvement_pct": {"vocabulary": round(vi, 1), "coherence": round(ci, 1)},
            }

            # 2) Alerts
            alert_result = (
                self.client.table("alerts")
                .select("alert_type, severity, acknowledged")
                .eq("patient_id", patient_id)
                .execute()
            )
            alerts = alert_result.data or []

            sev_counts = {"low": 0, "medium": 0, "high": 0}
            type_counts: dict = {}
            ack_count = 0
            for a in alerts:
                sev = a.get("severity", "low")
                sev_counts[sev] = sev_counts.get(sev, 0) + 1
                at = a.get("alert_type", "unknown")
                type_counts[at] = type_counts.get(at, 0) + 1
                if a.get("acknowledged"):
                    ack_count += 1

            most_common = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "none"

            return {
                "cognitive_by_mood": cognitive_by_mood,
                "nostalgia_effectiveness": nostalgia_effectiveness,
                "alert_summary": {
                    "total": len(alerts),
                    "by_severity": sev_counts,
                    "most_common_type": most_common,
                    "acknowledged_count": ack_count,
                },
            }
        except Exception as exc:
            logger.error(f"CognitiveRepository.get_patient_insights failed: {exc}")
            return {
                "cognitive_by_mood": {},
                "nostalgia_effectiveness": {},
                "alert_summary": {"total": 0, "by_severity": {"low": 0, "medium": 0, "high": 0}, "most_common_type": "none", "acknowledged_count": 0},
            }

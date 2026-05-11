"""
Supabase Data Store Implementation
Production storage using Supabase PostgreSQL via the supabase-py SDK.

Every method matches the DataStore protocol in base.py exactly.
Every dict returned uses the SAME keys as InMemoryDataStore in memory.py.
"""

import logging
from datetime import datetime, UTC, timedelta
from typing import Optional

from supabase import create_client, Client

from app.cognitive.utils import calculate_cognitive_score

logger = logging.getLogger(__name__)


class SupabaseDataStore:
    """
    Supabase PostgreSQL implementation of DataStore protocol.
    Uses the service_role key (bypasses RLS) for backend operations.
    """

    def __init__(self, url: str, service_role_key: str):
        self.client: Client = create_client(url, service_role_key)
        logger.info(f"Initialized SupabaseDataStore → {url}")

    async def close(self):
        """No persistent connection to close (HTTP-based SDK)."""
        logger.info("SupabaseDataStore closed (no-op for HTTP client)")

    # =========================================================================
    # PATIENT
    # =========================================================================

    async def get_patient(self, patient_id: str) -> Optional[dict]:
        try:
            result = self.client.table("patients").select("*").eq("id", patient_id).maybe_single().execute()
            row = result.data
            if not row:
                return None

            # Fetch medications separately (normalized table)
            meds_result = self.client.table("medications").select("*").eq("patient_id", patient_id).execute()
            medications = [
                {"name": m["name"], "dosage": m.get("dosage"), "schedule": m.get("schedule")}
                for m in (meds_result.data or [])
            ]

            # Fetch family contacts
            fc_result = self.client.table("family_contacts").select("*").eq("patient_id", patient_id).execute()
            family_contacts = [
                {
                    "id": fc["id"],
                    "name": fc["name"],
                    "email": fc["email"],
                    "phone": fc.get("phone", ""),
                    "relationship": fc.get("relationship", ""),
                    "notification_preferences": {
                        "daily_digest": fc.get("daily_digest", False),
                        "instant_alerts": fc.get("instant_alerts", False),
                        "weekly_report": fc.get("weekly_report", False),
                    },
                }
                for fc in (fc_result.data or [])
            ]

            return {
                "id": row["id"],
                "name": row.get("name"),
                "preferred_name": row.get("preferred_name"),
                "date_of_birth": row.get("date_of_birth"),
                "birth_year": row.get("birth_year"),
                "age": row.get("age"),
                "location": {
                    "city": row.get("city"),
                    "state": row.get("state"),
                    "timezone": row.get("timezone"),
                },
                "medical_notes": row.get("medical_notes"),
                "medications": medications,
                "phone_number": row.get("phone_number"),
                "preferences": {
                    "favorite_topics": row.get("favorite_topics", []),
                    "communication_style": row.get("communication_style", ""),
                    "interests": row.get("interests", []),
                    "topics_to_avoid": row.get("topics_to_avoid", []),
                },
                "cognitive_thresholds": {
                    "deviation_threshold": float(row.get("deviation_threshold", 0.20)),
                    "consecutive_trigger": row.get("consecutive_trigger", 3),
                },
                "call_schedule": {
                    "preferred_time": row.get("preferred_call_time"),
                    "timezone": row.get("timezone"),
                },
                "family_contacts": family_contacts,
            }
        except Exception as exc:
            logger.error(f"get_patient failed for {patient_id}: {exc}")
            return None

    async def update_patient(self, patient_id: str, updates: dict) -> bool:
        try:
            db_updates = {}

            if "preferences" in updates:
                p = updates["preferences"]
                db_updates["favorite_topics"] = p.get("favorite_topics", [])
                db_updates["communication_style"] = p.get("communication_style", "")
                db_updates["interests"] = p.get("interests", [])
                db_updates["topics_to_avoid"] = p.get("topics_to_avoid", [])

            if "cognitive_thresholds" in updates:
                ct = updates["cognitive_thresholds"]
                db_updates["deviation_threshold"] = ct.get("deviation_threshold", 0.20)
                db_updates["consecutive_trigger"] = ct.get("consecutive_trigger", 3)

            if "call_schedule" in updates:
                cs = updates["call_schedule"]
                if cs.get("preferred_time"):
                    db_updates["preferred_call_time"] = cs["preferred_time"]

            simple_map = {
                "name": "name",
                "preferred_name": "preferred_name",
                "age": "age",
                "phone_number": "phone_number",
                "medical_notes": "medical_notes",
            }
            for py_key, db_key in simple_map.items():
                if py_key in updates:
                    db_updates[db_key] = updates[py_key]

            if db_updates:
                db_updates["updated_at"] = datetime.now(UTC).isoformat()
                self.client.table("patients").update(db_updates).eq("id", patient_id).execute()

            # Handle medications update (replace all)
            if "medications" in updates:
                self.client.table("medications").delete().eq("patient_id", patient_id).execute()
                for med in updates["medications"]:
                    self.client.table("medications").insert({
                        "patient_id": patient_id,
                        "name": med.get("name", ""),
                        "dosage": med.get("dosage", ""),
                        "schedule": med.get("schedule", ""),
                    }).execute()

            return True
        except Exception as exc:
            logger.error(f"update_patient failed for {patient_id}: {exc}")
            return False

    # =========================================================================
    # CONVERSATIONS
    # =========================================================================

    async def get_conversations(
        self, patient_id: str, limit: int = 10, offset: int = 0
    ) -> list[dict]:
        try:
            result = (
                self.client.table("conversations")
                .select("*")
                .eq("patient_id", patient_id)
                .order("timestamp", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return [self._map_conversation(row) for row in (result.data or [])]
        except Exception as exc:
            logger.error(f"get_conversations failed: {exc}")
            return []

    async def get_conversation(self, conversation_id: str) -> Optional[dict]:
        try:
            result = (
                self.client.table("conversations")
                .select("*")
                .eq("id", conversation_id)
                .maybe_single()
                .execute()
            )
            return self._map_conversation(result.data) if result.data else None
        except Exception as exc:
            logger.error(f"get_conversation failed: {exc}")
            return None

    async def save_conversation(self, conversation: dict) -> str:
        try:
            metrics = conversation.get("cognitive_metrics") or {}
            ne = conversation.get("nostalgia_engagement")

            row = {
                "patient_id": conversation["patient_id"],
                "timestamp": conversation.get("timestamp"),
                "duration": conversation.get("duration"),
                "transcript": conversation.get("transcript"),
                "summary": conversation.get("summary"),
                "detected_mood": conversation.get("detected_mood"),
                "vocab_diversity": metrics.get("vocabulary_diversity"),
                "topic_coherence": metrics.get("topic_coherence"),
                "repetition_count": metrics.get("repetition_count"),
                "repetition_rate": metrics.get("repetition_rate"),
                "word_finding_pauses": metrics.get("word_finding_pauses"),
                "response_latency": metrics.get("response_latency"),
            }

            if ne:
                row["nostalgia_triggered"] = ne.get("triggered", False)
                row["nostalgia_era"] = ne.get("era")
                row["nostalgia_content"] = ne.get("content_used")
                row["nostalgia_engagement_score"] = ne.get("engagement_score")

            # If an ID is provided, include it (for idempotent saves)
            conv_id = conversation.get("id")
            if conv_id:
                row["id"] = conv_id

            result = self.client.table("conversations").upsert(row).execute()
            return result.data[0]["id"] if result.data else conv_id or "unknown"
        except Exception as exc:
            logger.error(f"save_conversation failed: {exc}")
            return conversation.get("id", "error")

    # =========================================================================
    # COGNITIVE BASELINE
    # =========================================================================

    async def get_cognitive_baseline(self, patient_id: str) -> Optional[dict]:
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
            logger.error(f"get_cognitive_baseline failed: {exc}")
            return None

    async def save_cognitive_baseline(self, patient_id: str, baseline: dict) -> None:
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
            logger.error(f"save_cognitive_baseline failed: {exc}")

    # =========================================================================
    # WELLNESS DIGESTS
    # =========================================================================

    async def get_wellness_digests(
        self, patient_id: str, limit: int = 10, offset: int = 0
    ) -> list[dict]:
        try:
            result = (
                self.client.table("wellness_digests")
                .select("*")
                .eq("patient_id", patient_id)
                .order("date", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return [self._map_digest(row) for row in (result.data or [])]
        except Exception as exc:
            logger.error(f"get_wellness_digests failed: {exc}")
            return []

    async def get_latest_wellness_digest(self, patient_id: str) -> Optional[dict]:
        try:
            result = (
                self.client.table("wellness_digests")
                .select("*")
                .eq("patient_id", patient_id)
                .order("date", desc=True)
                .limit(1)
                .maybe_single()
                .execute()
            )
            return self._map_digest(result.data) if result.data else None
        except Exception as exc:
            logger.error(f"get_latest_wellness_digest failed: {exc}")
            return None

    async def save_wellness_digest(self, digest: dict) -> str:
        try:
            row = {
                "patient_id": digest["patient_id"],
                "date": digest.get("date"),
                "overall_mood": digest.get("overall_mood"),
                "highlights": digest.get("highlights", []),
                "cognitive_score": digest.get("cognitive_score"),
                "cognitive_trend": digest.get("cognitive_trend"),
                "recommendations": digest.get("recommendations", []),
            }
            conv_id = digest.get("conversation_id")
            if conv_id:
                row["conversation_id"] = conv_id

            digest_id = digest.get("id")
            if digest_id:
                row["id"] = digest_id

            result = self.client.table("wellness_digests").upsert(row).execute()
            return result.data[0]["id"] if result.data else digest_id or "unknown"
        except Exception as exc:
            logger.error(f"save_wellness_digest failed: {exc}")
            return digest.get("id", "error")

    # =========================================================================
    # ALERTS
    # =========================================================================

    async def get_alerts(
        self,
        patient_id: str,
        severity: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        try:
            query = (
                self.client.table("alerts")
                .select("*")
                .eq("patient_id", patient_id)
            )
            if severity:
                query = query.eq("severity", severity)

            result = (
                query
                .order("acknowledged", desc=False)
                .order("timestamp", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return [self._map_alert(row) for row in (result.data or [])]
        except Exception as exc:
            logger.error(f"get_alerts failed: {exc}")
            return []

    async def save_alert(self, alert: dict) -> str:
        try:
            row = {
                "patient_id": alert["patient_id"],
                "alert_type": alert.get("alert_type"),
                "severity": alert.get("severity"),
                "description": alert.get("description"),
                "suggested_action": alert.get("suggested_action"),
                "source": alert.get("source"),
                "related_metrics": alert.get("related_metrics"),
                "timestamp": alert.get("timestamp"),
                "acknowledged": alert.get("acknowledged", False),
            }
            conv_id = alert.get("conversation_id")
            if conv_id:
                row["conversation_id"] = conv_id

            alert_id = alert.get("id")
            if alert_id:
                row["id"] = alert_id

            result = self.client.table("alerts").upsert(row).execute()
            return result.data[0]["id"] if result.data else alert_id or "unknown"
        except Exception as exc:
            logger.error(f"save_alert failed: {exc}")
            return alert.get("id", "error")

    async def update_alert(self, alert_id: str, updates: dict) -> bool:
        try:
            db_updates = {}
            if "acknowledged" in updates:
                db_updates["acknowledged"] = updates["acknowledged"]
            if "acknowledged_by" in updates:
                db_updates["acknowledged_by"] = updates["acknowledged_by"]
            if "acknowledged_at" in updates:
                db_updates["acknowledged_at"] = updates["acknowledged_at"]

            self.client.table("alerts").update(db_updates).eq("id", alert_id).execute()
            return True
        except Exception as exc:
            logger.error(f"update_alert failed for {alert_id}: {exc}")
            return False

    # =========================================================================
    # FAMILY CONTACTS
    # =========================================================================

    async def get_family_contacts(self, patient_id: str) -> list[dict]:
        """Get family contacts from the family_contacts table."""
        try:
            result = (
                self.client.table("family_contacts")
                .select("*")
                .eq("patient_id", patient_id)
                .execute()
            )
            contacts = [
                {
                    "id": fc["id"],
                    "name": fc["name"],
                    "email": fc["email"],
                    "phone": fc.get("phone", ""),
                    "relationship": fc.get("relationship", ""),
                    "notification_preferences": {
                        "daily_digest": fc.get("daily_digest", False),
                        "instant_alerts": fc.get("instant_alerts", False),
                        "weekly_report": fc.get("weekly_report", False),
                    },
                }
                for fc in (result.data or [])
            ]
            logger.info(
                f"Family contacts for {patient_id}: {len(contacts)} contact(s) — "
                f"{[c.get('email') for c in contacts if c.get('email')]}"
            )
            return contacts
        except Exception as exc:
            logger.error(f"get_family_contacts failed: {exc}")
            return []

    # =========================================================================
    # CONSECUTIVE DEVIATIONS
    # =========================================================================

    async def get_consecutive_deviations(self, patient_id: str) -> dict:
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
            logger.error(f"get_consecutive_deviations failed: {exc}")
            return {}

    async def update_consecutive_deviations(
        self, patient_id: str, deviations: dict
    ) -> None:
        try:
            self.client.table("deviation_trackers").upsert({
                "patient_id": patient_id,
                "metrics": deviations,
                "updated_at": datetime.now(UTC).isoformat(),
            }, on_conflict="patient_id").execute()
        except Exception as exc:
            logger.error(f"update_consecutive_deviations failed: {exc}")

    # =========================================================================
    # COGNITIVE TRENDS
    # =========================================================================

    async def get_cognitive_trends(self, patient_id: str, days: int = 30) -> list[dict]:
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
            logger.error(f"get_cognitive_trends failed: {exc}")
            return []

    # =========================================================================
    # INSIGHTS
    # =========================================================================

    async def get_patient_insights(self, patient_id: str) -> dict:
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
            logger.error(f"get_patient_insights failed: {exc}")
            return {
                "cognitive_by_mood": {},
                "nostalgia_effectiveness": {},
                "alert_summary": {"total": 0, "by_severity": {"low": 0, "medium": 0, "high": 0}, "most_common_type": "none", "acknowledged_count": 0},
            }

    # =========================================================================
    # Internal mapping helpers (DB snake_case → protocol dict format)
    # =========================================================================

    @staticmethod
    def _map_conversation(row: dict | None) -> dict | None:
        if not row:
            return None
        return {
            "id": row["id"],
            "patient_id": row["patient_id"],
            "timestamp": row.get("timestamp"),
            "duration": row.get("duration"),
            "transcript": row.get("transcript"),
            "summary": row.get("summary"),
            "detected_mood": row.get("detected_mood"),
            "cognitive_metrics": {
                "vocabulary_diversity": float(row["vocab_diversity"]) if row.get("vocab_diversity") is not None else None,
                "topic_coherence": float(row["topic_coherence"]) if row.get("topic_coherence") is not None else None,
                "repetition_count": row.get("repetition_count"),
                "repetition_rate": float(row["repetition_rate"]) if row.get("repetition_rate") is not None else None,
                "word_finding_pauses": row.get("word_finding_pauses"),
                "response_latency": float(row["response_latency"]) if row.get("response_latency") is not None else None,
            } if row.get("vocab_diversity") is not None else None,
            "nostalgia_engagement": {
                "triggered": row.get("nostalgia_triggered"),
                "era": row.get("nostalgia_era"),
                "content_used": row.get("nostalgia_content"),
                "engagement_score": float(row["nostalgia_engagement_score"]) if row.get("nostalgia_engagement_score") is not None else None,
            } if row.get("nostalgia_triggered") else None,
        }

    @staticmethod
    def _map_alert(row: dict | None) -> dict | None:
        if not row:
            return None
        return {
            "id": row["id"],
            "patient_id": row["patient_id"],
            "alert_type": row.get("alert_type"),
            "severity": row.get("severity"),
            "description": row.get("description"),
            "suggested_action": row.get("suggested_action"),
            "related_metrics": row.get("related_metrics"),
            "timestamp": row.get("timestamp"),
            "acknowledged": row.get("acknowledged", False),
            "acknowledged_at": row.get("acknowledged_at"),
            "acknowledged_by": row.get("acknowledged_by"),
            "conversation_id": row.get("conversation_id"),
        }

    @staticmethod
    def _map_digest(row: dict | None) -> dict | None:
        if not row:
            return None
        return {
            "id": row["id"],
            "patient_id": row["patient_id"],
            "date": row.get("date"),
            "overall_mood": row.get("overall_mood"),
            "highlights": row.get("highlights", []),
            "cognitive_score": row.get("cognitive_score"),
            "cognitive_trend": row.get("cognitive_trend"),
            "recommendations": row.get("recommendations", []),
            "conversation_id": row.get("conversation_id"),
            "created_at": row.get("created_at"),
        }

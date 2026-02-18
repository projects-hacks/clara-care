"""
In-Memory Data Store Implementation
Development/testing storage with pre-seeded Dorothy test data
In-memory fallback when Sanity is not configured
"""

import uuid
import statistics
from datetime import datetime, date, timedelta, UTC
from typing import Optional
from collections import defaultdict

from app.cognitive.utils import calculate_cognitive_score


class InMemoryDataStore:
    """
    In-memory implementation of DataStore protocol
    Pre-seeded with realistic Dorothy test data for demo
    """
    
    def __init__(self):
        """Initialize with seed data"""
        self.patients = {}
        self.conversations = {}
        self.baselines = {}
        self.digests = {}
        self.alerts = {}
        self.family_contacts = {}
        self.consecutive_deviations = defaultdict(dict)
        
        # Seed test data
        self._seed_data()
    
    def _seed_data(self):
        """Populate with Dorothy test data"""
        
        # Seed Dorothy patient
        self.patients["patient-dorothy-001"] = {
            "id": "patient-dorothy-001",
            "name": "Dorothy Chen",
            "preferred_name": "Dorothy",
            "date_of_birth": "1951-03-15",
            "birth_year": 1951,
            "age": 75,
            "location": {
                "city": "San Francisco",
                "state": "CA",
                "timezone": "America/Los_Angeles"
            },
            "medical_notes": "Generally healthy, occasional memory concerns",
            "medications": [
                {
                    "name": "Lisinopril",
                    "dosage": "10mg",
                    "schedule": "9 AM daily"
                },
                {
                    "name": "Vitamin D",
                    "dosage": "2000 IU",
                    "schedule": "Morning with breakfast"
                }
            ],
            "preferences": {
                "favorite_topics": ["gardening", "1960s music", "family", "cooking"],
                "communication_style": "warm and patient",
                "interests": ["music", "gardening", "family history"]
            },
            "cognitive_thresholds": {
                "deviation_threshold": 0.20,  # 20%
                "consecutive_trigger": 3
            },
            "phone_number": "+14155550199",
            "call_schedule": {
                "preferred_time": "10:00 AM",
                "timezone": "America/Los_Angeles"
            }
        }
        
        # Seed Sarah family contact
        self.family_contacts["family-sarah-001"] = {
            "id": "family-sarah-001",
            "name": "Sarah Chen",
            "email": "sarah.chen@email.com",
            "phone": "+14155550123",
            "relationship": "Daughter",
            "patient_ids": ["patient-dorothy-001"],
            "notification_preferences": {
                "daily_digest": True,
                "instant_alerts": True,
                "weekly_report": True
            }
        }
        
        # Seed 7 baseline conversations (over 2 weeks)
        base_date = datetime.now(UTC) - timedelta(days=14)
        
        conversations_data = [
            {
                "summary": "Dorothy shared memories of gardening with her mother in the 1960s. Discussed her current herb garden.",
                "mood": "nostalgic",
                "duration": 420,
                "metrics": {
                    "vocabulary_diversity": 0.65,
                    "topic_coherence": 0.88,
                    "repetition_count": 2,
                    "repetition_rate": 0.04,
                    "word_finding_pauses": 1,
                    "response_latency": 1.4
                },
                "nostalgia_engagement": {
                    "triggered": True,
                    "era": "1966-1976",
                    "content_used": "Shared memories of 1960s gardening",
                    "engagement_score": 8
                }
            },
            {
                "summary": "Talked about medication schedule. Dorothy mentioned she sometimes forgets afternoon vitamins.",
                "mood": "neutral",
                "duration": 360,
                "metrics": {
                    "vocabulary_diversity": 0.60,
                    "topic_coherence": 0.85,
                    "repetition_count": 3,
                    "repetition_rate": 0.06,
                    "word_finding_pauses": 2,
                    "response_latency": 1.6
                },
                "nostalgia_engagement": None
            },
            {
                "summary": "Dorothy excitedly talked about her grandson's upcoming graduation. Very engaged and happy.",
                "mood": "happy",
                "duration": 480,
                "metrics": {
                    "vocabulary_diversity": 0.68,
                    "topic_coherence": 0.90,
                    "repetition_count": 1,
                    "repetition_rate": 0.02,
                    "word_finding_pauses": 0,
                    "response_latency": 1.2
                },
                "nostalgia_engagement": None
            },
            {
                "summary": "Discussed upcoming lunch plans with neighbor. Dorothy seemed in good spirits.",
                "mood": "happy",
                "duration": 300,
                "metrics": {
                    "vocabulary_diversity": 0.62,
                    "topic_coherence": 0.87,
                    "repetition_count": 2,
                    "repetition_rate": 0.05,
                    "word_finding_pauses": 1,
                    "response_latency": 1.5
                },
                "nostalgia_engagement": None
            },
            {
                "summary": "Talked about 1960s music - The Beatles, The Beach Boys. Dorothy very nostalgic.",
                "mood": "nostalgic",
                "duration": 450,
                "metrics": {
                    "vocabulary_diversity": 0.61,
                    "topic_coherence": 0.89,
                    "repetition_count": 2,
                    "repetition_rate": 0.04,
                    "word_finding_pauses": 2,
                    "response_latency": 1.6
                },
                "nostalgia_engagement": {
                    "triggered": True,
                    "era": "1966-1976",
                    "content_used": "The Beatles released 'I Want to Hold Your Hand' in 1963",
                    "engagement_score": 9
                }
            },
            {
                "summary": "Dorothy shared a recipe for her famous apple pie. Talked about family gatherings.",
                "mood": "happy",
                "duration": 390,
                "metrics": {
                    "vocabulary_diversity": 0.63,
                    "topic_coherence": 0.86,
                    "repetition_count": 3,
                    "repetition_rate": 0.06,
                    "word_finding_pauses": 1,
                    "response_latency": 1.5
                },
                "nostalgia_engagement": None
            },
            {
                "summary": "General check-in. Dorothy mentioned feeling a bit tired but overall good.",
                "mood": "neutral",
                "duration": 330,
                "metrics": {
                    "vocabulary_diversity": 0.59,
                    "topic_coherence": 0.84,
                    "repetition_count": 4,
                    "repetition_rate": 0.07,
                    "word_finding_pauses": 3,
                    "response_latency": 1.8
                },
                "nostalgia_engagement": None
            }
        ]
        
        for i, conv_data in enumerate(conversations_data):
            conv_id = f"conversation-{i+1:03d}"
            conv_date = base_date + timedelta(days=i*2)
            
            self.conversations[conv_id] = {
                "id": conv_id,
                "patient_id": "patient-dorothy-001",
                "timestamp": conv_date.isoformat(),
                "duration": conv_data["duration"],
                "summary": conv_data["summary"],
                "detected_mood": conv_data["mood"],
                "transcript": f"Clara: Hello Dorothy! How are you today?\nDorothy: {conv_data['summary'][:50]}...",
                "cognitive_metrics": conv_data["metrics"],
                "nostalgia_engagement": conv_data.get("nostalgia_engagement")
            }
        
        # Establish baseline from first 7 conversations
        metrics_list = [c["cognitive_metrics"] for c in list(self.conversations.values())[:7]]
        
        self.baselines["patient-dorothy-001"] = {
            "patient_id": "patient-dorothy-001",
            "established": True,
            "baseline_date": (base_date + timedelta(days=14)).date().isoformat(),
            "vocabulary_diversity": statistics.mean([m["vocabulary_diversity"] for m in metrics_list]),
            "vocabulary_diversity_std": statistics.stdev([m["vocabulary_diversity"] for m in metrics_list]),
            "topic_coherence": statistics.mean([m["topic_coherence"] for m in metrics_list]),
            "topic_coherence_std": statistics.stdev([m["topic_coherence"] for m in metrics_list]),
            "repetition_rate": statistics.mean([m["repetition_rate"] for m in metrics_list]),
            "repetition_rate_std": statistics.stdev([m["repetition_rate"] for m in metrics_list]),
            "word_finding_pauses": statistics.mean([m["word_finding_pauses"] for m in metrics_list]),
            "word_finding_pauses_std": statistics.stdev([m["word_finding_pauses"] for m in metrics_list]),
            "avg_response_time": statistics.mean([m["response_latency"] for m in metrics_list]),
            "response_time_std": statistics.stdev([m["response_latency"] for m in metrics_list]),
            "conversation_count": 7,
            "last_updated": datetime.now(UTC).isoformat()
        }
        
        # Seed wellness digests for the last 7 days
        for i in range(7):
            digest_id = f"digest-{i+1:03d}"
            digest_date = date.today() - timedelta(days=6-i)
            conv_id = f"conversation-{i+1:03d}"
            
            # Calculate cognitive score (0-100)
            metrics = self.conversations[conv_id]["cognitive_metrics"]
            score = self._calculate_cognitive_score(metrics)
            
            self.digests[digest_id] = {
                "id": digest_id,
                "patient_id": "patient-dorothy-001",
                "date": digest_date.isoformat(),
                "overall_mood": self.conversations[conv_id]["detected_mood"],
                "highlights": [self.conversations[conv_id]["summary"]],
                "cognitive_score": score,
                "cognitive_trend": "stable",
                "recommendations": [],
                "conversation_id": conv_id,
                "created_at": (datetime.combine(digest_date, datetime.min.time())).isoformat()
            }
        
        # Seed a few alerts (2 low, 1 medium)
        self.alerts["alert-001"] = {
            "id": "alert-001",
            "patient_id": "patient-dorothy-001",
            "alert_type": "word_finding_difficulty",
            "severity": "low",
            "description": "Slight increase in word-finding pauses detected",
            "related_metrics": {
                "word_finding_pauses": 3,
                "baseline_avg": 1.5
            },
            "timestamp": (datetime.now(UTC) - timedelta(days=3)).isoformat(),
            "acknowledged": True,
            "acknowledged_at": (datetime.now(UTC) - timedelta(days=2)).isoformat(),
            "acknowledged_by": "family-sarah-001"
        }
        
        self.alerts["alert-002"] = {
            "id": "alert-002",
            "patient_id": "patient-dorothy-001",
            "alert_type": "repetition_increase",
            "severity": "low",
            "description": "Repetition rate slightly elevated in recent conversation",
            "related_metrics": {
                "repetition_rate": 0.07,
                "baseline": 0.05
            },
            "timestamp": (datetime.now(UTC) - timedelta(days=1)).isoformat(),
            "acknowledged": False
        }
    
    def _calculate_cognitive_score(self, metrics: dict) -> int:
        """Calculate composite cognitive score (0-100) - delegates to shared utility"""
        return calculate_cognitive_score(metrics)
    
    # DataStore protocol implementation
    
    async def get_patient(self, patient_id: str) -> Optional[dict]:
        return self.patients.get(patient_id)
    
    async def update_patient(self, patient_id: str, updates: dict) -> bool:
        if patient_id in self.patients:
            self.patients[patient_id].update(updates)
            return True
        return False
    
    async def get_conversations(
        self,
        patient_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> list[dict]:
        convs = [
            c for c in self.conversations.values()
            if c["patient_id"] == patient_id
        ]
        convs.sort(key=lambda x: x["timestamp"], reverse=True)
        return convs[offset:offset+limit]
    
    async def get_conversation(self, conversation_id: str) -> Optional[dict]:
        return self.conversations.get(conversation_id)
    
    async def save_conversation(self, conversation: dict) -> str:
        conv_id = conversation.get("id") or f"conversation-{uuid.uuid4().hex[:8]}"
        conversation["id"] = conv_id
        self.conversations[conv_id] = conversation
        return conv_id
    
    async def get_cognitive_baseline(self, patient_id: str) -> Optional[dict]:
        return self.baselines.get(patient_id)
    
    async def save_cognitive_baseline(self, patient_id: str, baseline: dict) -> None:
        self.baselines[patient_id] = baseline
    
    async def get_wellness_digests(
        self,
        patient_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> list[dict]:
        digests = [
            d for d in self.digests.values()
            if d["patient_id"] == patient_id
        ]
        digests.sort(key=lambda x: x["date"], reverse=True)
        return digests[offset:offset+limit]
    
    async def get_latest_wellness_digest(self, patient_id: str) -> Optional[dict]:
        digests = await self.get_wellness_digests(patient_id, limit=1)
        return digests[0] if digests else None
    
    async def save_wellness_digest(self, digest: dict) -> str:
        digest_id = digest.get("id") or f"digest-{uuid.uuid4().hex[:8]}"
        digest["id"] = digest_id
        self.digests[digest_id] = digest
        return digest_id
    
    async def get_alerts(
        self,
        patient_id: str,
        severity: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[dict]:
        alerts = [
            a for a in self.alerts.values()
            if a["patient_id"] == patient_id
        ]
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        return alerts[offset:offset+limit]
    
    async def save_alert(self, alert: dict) -> str:
        alert_id = alert.get("id") or f"alert-{uuid.uuid4().hex[:8]}"
        alert["id"] = alert_id
        self.alerts[alert_id] = alert
        return alert_id
    
    async def update_alert(self, alert_id: str, updates: dict) -> bool:
        if alert_id in self.alerts:
            self.alerts[alert_id].update(updates)
            return True
        return False
    
    async def get_family_contacts(self, patient_id: str) -> list[dict]:
        return [
            c for c in self.family_contacts.values()
            if patient_id in c["patient_ids"]
        ]
    
    async def get_consecutive_deviations(self, patient_id: str) -> dict:
        return self.consecutive_deviations.get(patient_id, {})
    
    async def update_consecutive_deviations(
        self,
        patient_id: str,
        deviations: dict
    ) -> None:
        self.consecutive_deviations[patient_id] = deviations
    
    async def get_cognitive_trends(
        self,
        patient_id: str,
        days: int = 30
    ) -> list[dict]:
        """Get time-series cognitive metrics"""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        convs = [
            c for c in self.conversations.values()
            if c["patient_id"] == patient_id 
            and datetime.fromisoformat(c["timestamp"]) >= cutoff
        ]
        convs.sort(key=lambda x: x["timestamp"])
        
        trends = []
        for conv in convs:
            metrics = conv.get("cognitive_metrics", {})
            if metrics:
                trends.append({
                    "date": datetime.fromisoformat(conv["timestamp"]).date().isoformat(),
                    "vocabulary_diversity": metrics.get("vocabulary_diversity"),
                    "topic_coherence": metrics.get("topic_coherence"),
                    "repetition_rate": metrics.get("repetition_rate"),
                    "word_finding_pauses": metrics.get("word_finding_pauses"),
                    "cognitive_score": self._calculate_cognitive_score(metrics)
                })
        
        return trends

    async def get_patient_insights(self, patient_id: str) -> dict:
        """
        Get structured content insights for a patient.
        Showcase for Sanity challenge: features impossible with flat files.
        """
        # Get all conversations for the patient
        all_convs = [
            c for c in self.conversations.values()
            if c["patient_id"] == patient_id
        ]

        # --- Cognitive by Mood ---
        mood_stats: dict = {}
        for conv in all_convs:
            mood = conv.get("detected_mood", "unknown")
            metrics = conv.get("cognitive_metrics")
            if not metrics:
                continue
            if mood not in mood_stats:
                mood_stats[mood] = {"vocabs": [], "coherences": [], "count": 0}
            vocab = metrics.get("vocabulary_diversity")
            coherence = metrics.get("topic_coherence")
            if vocab is not None:
                mood_stats[mood]["vocabs"].append(vocab)
            if coherence is not None:
                mood_stats[mood]["coherences"].append(coherence)
            mood_stats[mood]["count"] += 1

        cognitive_by_mood = {}
        for mood, stats in mood_stats.items():
            avg_v = sum(stats["vocabs"]) / len(stats["vocabs"]) if stats["vocabs"] else 0
            avg_c = sum(stats["coherences"]) / len(stats["coherences"]) if stats["coherences"] else 0
            cognitive_by_mood[mood] = {
                "avg_vocabulary": round(avg_v, 3),
                "avg_coherence": round(avg_c, 3),
                "conversation_count": stats["count"]
            }

        # --- Nostalgia Effectiveness ---
        with_nostalgia = []
        without_nostalgia = []
        for conv in all_convs:
            metrics = conv.get("cognitive_metrics")
            if not metrics:
                continue
            ne = conv.get("nostalgia_engagement")
            if ne and ne.get("triggered"):
                with_nostalgia.append(metrics)
            else:
                without_nostalgia.append(metrics)

        def _avg(lst: list, key: str) -> float:
            vals = [m[key] for m in lst if m.get(key) is not None]
            return sum(vals) / len(vals) if vals else 0.0

        wv = _avg(with_nostalgia, "vocabulary_diversity")
        wov = _avg(without_nostalgia, "vocabulary_diversity")
        wc = _avg(with_nostalgia, "topic_coherence")
        woc = _avg(without_nostalgia, "topic_coherence")

        vocab_imp = ((wv - wov) / wov * 100) if wov > 0 else 0
        coh_imp = ((wc - woc) / woc * 100) if woc > 0 else 0

        nostalgia_effectiveness = {
            "with_nostalgia": {
                "avg_vocabulary": round(wv, 3),
                "avg_coherence": round(wc, 3),
                "count": len(with_nostalgia)
            },
            "without_nostalgia": {
                "avg_vocabulary": round(wov, 3),
                "avg_coherence": round(woc, 3),
                "count": len(without_nostalgia)
            },
            "improvement_pct": {
                "vocabulary": round(vocab_imp, 1),
                "coherence": round(coh_imp, 1)
            }
        }

        # --- Alert Summary ---
        patient_alerts = [
            a for a in self.alerts.values()
            if a["patient_id"] == patient_id
        ]
        severity_counts = {"low": 0, "medium": 0, "high": 0}
        type_counts: dict = {}
        for alert in patient_alerts:
            sev = alert.get("severity", "low")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            at = alert.get("alert_type", "unknown")
            type_counts[at] = type_counts.get(at, 0) + 1

        most_common = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "none"

        alert_summary = {
            "total": len(patient_alerts),
            "by_severity": severity_counts,
            "most_common_type": most_common,
            "acknowledged_count": sum(1 for a in patient_alerts if a.get("acknowledged"))
        }

        return {
            "cognitive_by_mood": cognitive_by_mood,
            "nostalgia_effectiveness": nostalgia_effectiveness,
            "alert_summary": alert_summary
        }

"""
Sanity CMS Data Store Implementation
Production storage using Sanity as backend via HTTP API.

Every method matches the DataStore protocol in base.py exactly.
Every dict returned uses the SAME keys as InMemoryDataStore in memory.py.
"""

import logging
from datetime import datetime, UTC, timedelta
from typing import Optional
import httpx

from app.cognitive.utils import calculate_cognitive_score

logger = logging.getLogger(__name__)


class SanityDataStore:
    """
    Sanity CMS implementation of DataStore protocol.
    Uses GROQ queries via Sanity HTTP API.
    """

    def __init__(self, project_id: str, dataset: str, token: str):
        self.project_id = project_id
        self.dataset = dataset
        self.token = token
        self.base_url = f"https://{project_id}.api.sanity.io/v2024-01-01/data"
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
        logger.info(f"Initialized SanityDataStore for project {project_id}")

    async def close(self):
        """Close HTTP client (called on shutdown)."""
        await self._client.aclose()
        logger.info("Closed SanityDataStore HTTP client")

    # =========================================================================
    # Internal helpers
    # =========================================================================

    async def _query(self, query: str, params: dict | None = None) -> dict:
        """Execute a GROQ query."""
        try:
            resp = await self._client.get(
                f"{self.base_url}/query/{self.dataset}",
                params={"query": query, **({"$" + k: v for k, v in (params or {}).items()} if params else {})},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.error(f"Sanity query failed: {exc}")
            raise

    async def _query_groq(self, query: str, params: dict | None = None) -> dict:
        """Execute a GROQ query via POST (supports complex params)."""
        try:
            resp = await self._client.post(
                f"{self.base_url}/query/{self.dataset}",
                json={"query": query, "params": params or {}},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.error(f"Sanity query failed: {exc}")
            raise

    async def _mutate(self, mutations: list) -> dict:
        """Execute mutations (create/update/delete)."""
        try:
            resp = await self._client.post(
                f"{self.base_url}/mutate/{self.dataset}",
                json={"mutations": mutations},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.error(f"Sanity mutation failed: {exc}")
            raise

    # =========================================================================
    # Field-mapping helpers  (Sanity camelCase → Python snake_case)
    #
    # CRITICAL: Every dict MUST use the EXACT same keys as InMemoryDataStore.
    # =========================================================================

    def _map_patient(self, doc: dict | None) -> dict | None:
        if not doc:
            return None
        prefs = doc.get("preferences", {})
        call_sched = doc.get("callSchedule", {})
        # Normalize communication_style: old Sanity data stores as array, new as string
        raw_comm = prefs.get("communicationStyle", "")
        if isinstance(raw_comm, list):
            comm_style = raw_comm[0] if raw_comm else ""
        else:
            comm_style = raw_comm or ""
        result = {
            "id": doc["_id"],
            "name": doc.get("name"),
            "preferred_name": doc.get("preferredName"),
            "date_of_birth": doc.get("dateOfBirth"),
            "birth_year": doc.get("birthYear"),
            "age": doc.get("age"),
            "location": doc.get("location"),
            "medical_notes": doc.get("medicalNotes"),
            "medications": doc.get("medications", []),
            "phone_number": doc.get("phoneNumber"),
            "preferences": {
                "favorite_topics": prefs.get("favoriteTopics", []),
                "communication_style": comm_style,
                "interests": prefs.get("interests", []),
                "topics_to_avoid": prefs.get("topicsToAvoid", []),
            },
            "cognitive_thresholds": {
                "deviation_threshold": doc.get("cognitiveThresholds", {}).get("deviationThreshold", 0.20),
                "consecutive_trigger": doc.get("cognitiveThresholds", {}).get("consecutiveTrigger", 3),
            },
        }
        if call_sched:
            result["call_schedule"] = {
                "preferred_time": call_sched.get("preferredTime"),
                "timezone": call_sched.get("timezone"),
            }
        # Family contacts
        raw_contacts = doc.get("familyContacts", [])
        if raw_contacts:
            result["family_contacts"] = [
                {
                    "id": fc.get("_key", fc.get("id", "")),
                    "name": fc.get("name", ""),
                    "email": fc.get("email", ""),
                    "phone": fc.get("phone", ""),
                    "relationship": fc.get("relationship", ""),
                    "notification_preferences": {
                        "daily_digest": fc.get("notificationPreferences", {}).get("dailyDigest", False),
                        "instant_alerts": fc.get("notificationPreferences", {}).get("instantAlerts", False),
                        "weekly_report": fc.get("notificationPreferences", {}).get("weeklyReport", False),
                    },
                }
                for fc in raw_contacts
            ]
        return result

    @staticmethod
    def _ref_id(ref_field) -> str | None:
        """Extract _ref from a reference field."""
        if isinstance(ref_field, dict):
            return ref_field.get("_ref")
        return None

    def _map_conversation(self, doc: dict | None) -> dict | None:
        if not doc:
            return None
        patient_id = self._ref_id(doc.get("patient"))
        cm = doc.get("cognitiveMetrics") or {}
        ne = doc.get("nostalgiaEngagement")
        return {
            "id": doc["_id"],
            "patient_id": patient_id,
            "timestamp": doc.get("timestamp"),
            "duration": doc.get("duration"),
            "transcript": doc.get("transcript"),
            "summary": doc.get("summary"),
            "detected_mood": doc.get("mood"),
            "cognitive_metrics": {
                "vocabulary_diversity": cm.get("vocabularyDiversity"),
                "topic_coherence": cm.get("topicCoherence"),
                "repetition_count": cm.get("repetitionCount"),
                "repetition_rate": cm.get("repetitionRate"),
                "word_finding_pauses": cm.get("wordFindingPauses"),
                "response_latency": cm.get("responseLatency"),
            } if cm else None,
            "nostalgia_engagement": {
                "triggered": ne.get("triggered"),
                "era": ne.get("era"),
                "content_used": ne.get("contentUsed"),
                "engagement_score": ne.get("engagementScore"),
            } if ne else None,
        }

    def _map_alert(self, doc: dict | None) -> dict | None:
        if not doc:
            return None
        acked_by = doc.get("acknowledgedBy")
        # acknowledgedBy might be a reference or a string
        if isinstance(acked_by, dict):
            acked_by = acked_by.get("_ref")
        return {
            "id": doc["_id"],
            "patient_id": self._ref_id(doc.get("patient")),
            "alert_type": doc.get("alertType"),
            "severity": doc.get("severity"),
            "description": doc.get("description"),
            "related_metrics": doc.get("relatedMetrics"),
            "timestamp": doc.get("timestamp"),
            "acknowledged": doc.get("acknowledged", False),
            "acknowledged_at": doc.get("acknowledgedAt"),
            "acknowledged_by": acked_by,
            "conversation_id": self._ref_id(doc.get("conversation")),
        }

    def _map_digest(self, doc: dict | None) -> dict | None:
        if not doc:
            return None
        return {
            "id": doc["_id"],
            "patient_id": self._ref_id(doc.get("patient")),
            "date": doc.get("date"),
            "overall_mood": doc.get("overallMood"),
            "highlights": doc.get("highlights", []),
            "cognitive_score": doc.get("cognitiveScore"),
            "cognitive_trend": doc.get("trend"),
            "recommendations": doc.get("recommendations", []),
            "conversation_id": self._ref_id(doc.get("conversation")),
            "created_at": doc.get("generatedAt"),
        }

    def _map_baseline(self, doc: dict | None) -> dict | None:
        if not doc:
            return None
        return {
            "patient_id": self._ref_id(doc.get("patient")) or doc.get("patientId"),
            "established": doc.get("established", False),
            "baseline_date": doc.get("baselineDate"),
            "vocabulary_diversity": doc.get("vocabularyDiversity", 0.0),
            "vocabulary_diversity_std": doc.get("vocabularyDiversityStd", 0.0),
            "topic_coherence": doc.get("topicCoherence", 0.0),
            "topic_coherence_std": doc.get("topicCoherenceStd", 0.0),
            "repetition_rate": doc.get("repetitionRate", 0.0),
            "repetition_rate_std": doc.get("repetitionRateStd", 0.0),
            "word_finding_pauses": doc.get("wordFindingPauses", 0.0),
            "word_finding_pauses_std": doc.get("wordFindingPausesStd", 0.0),
            "avg_response_time": doc.get("avgResponseTime"),
            "response_time_std": doc.get("responseTimeStd"),
            "conversation_count": doc.get("conversationCount", 0),
            "last_updated": doc.get("lastUpdated"),
        }

    def _map_family_contact(self, doc: dict | None) -> dict | None:
        if not doc:
            return None
        prefs = doc.get("notificationPreferences") or {}
        patient_refs = doc.get("patients", [])
        patient_ids = [r.get("_ref") for r in patient_refs if isinstance(r, dict) and "_ref" in r]
        return {
            "id": doc["_id"],
            "name": doc.get("name"),
            "email": doc.get("email"),
            "phone": doc.get("phone"),
            "relationship": doc.get("relationship"),
            "patient_ids": patient_ids,
            "notification_preferences": {
                "daily_digest": prefs.get("dailyDigest", False),
                "instant_alerts": prefs.get("instantAlerts", False),
                "weekly_report": prefs.get("weeklyReport", False),
            },
        }

    # =========================================================================
    # PATIENT
    # =========================================================================

    async def get_patient(self, patient_id: str) -> Optional[dict]:
        try:
            result = await self._query_groq(
                '*[_type == "patient" && _id == $pid][0]',
                {"pid": patient_id},
            )
            return self._map_patient(result.get("result"))
        except Exception as exc:
            logger.error(f"get_patient failed for {patient_id}: {exc}")
            return None

    async def update_patient(self, patient_id: str, updates: dict) -> bool:
        try:
            sanity_set: dict = {}
            if "preferences" in updates:
                p = updates["preferences"]
                sanity_set["preferences"] = {
                    "favoriteTopics": p.get("favorite_topics", []),
                    "communicationStyle": p.get("communication_style", ""),
                    "interests": p.get("interests", []),
                    "topicsToAvoid": p.get("topics_to_avoid", []),
                }
            if "cognitive_thresholds" in updates:
                ct = updates["cognitive_thresholds"]
                sanity_set["cognitiveThresholds"] = {
                    "deviationThreshold": ct.get("deviation_threshold", 0.20),
                    "consecutiveTrigger": ct.get("consecutive_trigger", 3),
                }
            if "call_schedule" in updates:
                cs = updates["call_schedule"]
                sanity_set["callSchedule"] = {
                    "preferredTime": cs.get("preferred_time"),
                    "timezone": cs.get("timezone"),
                }
            if "medications" in updates:
                sanity_set["medications"] = [
                    {"name": m.get("name", ""), "dosage": m.get("dosage", ""), "schedule": m.get("schedule", "")}
                    for m in updates["medications"]
                ]
            if "family_contacts" in updates:
                sanity_set["familyContacts"] = [
                    {
                        "_key": fc.get("id", f"fc-{i}"),
                        "name": fc.get("name", ""),
                        "email": fc.get("email", ""),
                        "phone": fc.get("phone", ""),
                        "relationship": fc.get("relationship", ""),
                        "notificationPreferences": {
                            "dailyDigest": fc.get("notification_preferences", {}).get("daily_digest", False),
                            "instantAlerts": fc.get("notification_preferences", {}).get("instant_alerts", False),
                            "weeklyReport": fc.get("notification_preferences", {}).get("weekly_report", False),
                        },
                    }
                    for i, fc in enumerate(updates["family_contacts"])
                ]
            # Pass through any other top-level keys
            simple_map = {
                "name": "name",
                "preferred_name": "preferredName",
                "age": "age",
                "phone_number": "phoneNumber",
            }
            for py_key, san_key in simple_map.items():
                if py_key in updates:
                    sanity_set[san_key] = updates[py_key]

            await self._mutate([{"patch": {"id": patient_id, "set": sanity_set}}])
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
        end = offset + limit
        try:
            result = await self._query_groq(
                f'*[_type == "conversation" && patient._ref == $pid] | order(timestamp desc) [{offset}...{end}]',
                {"pid": patient_id},
            )
            return [self._map_conversation(c) for c in (result.get("result") or []) if c]
        except Exception as exc:
            logger.error(f"get_conversations failed: {exc}")
            return []

    async def get_conversation(self, conversation_id: str) -> Optional[dict]:
        try:
            result = await self._query_groq(
                '*[_type == "conversation" && _id == $cid][0]',
                {"cid": conversation_id},
            )
            return self._map_conversation(result.get("result"))
        except Exception as exc:
            logger.error(f"get_conversation failed: {exc}")
            return None

    async def save_conversation(self, conversation: dict) -> str:
        conv_id = conversation.get("id", f"conversation-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}")
        try:
            metrics = conversation.get("cognitive_metrics") or {}
            ne = conversation.get("nostalgia_engagement")
            sanity_doc: dict = {
                "_type": "conversation",
                "_id": conv_id,
                "patient": {"_ref": conversation["patient_id"], "_type": "reference"},
                "timestamp": conversation.get("timestamp"),
                "duration": conversation.get("duration"),
                "transcript": conversation.get("transcript"),
                "summary": conversation.get("summary"),
                "mood": conversation.get("detected_mood"),
            }
            if metrics:
                sanity_doc["cognitiveMetrics"] = {
                    "vocabularyDiversity": metrics.get("vocabulary_diversity"),
                    "topicCoherence": metrics.get("topic_coherence"),
                    "repetitionCount": metrics.get("repetition_count"),
                    "repetitionRate": metrics.get("repetition_rate"),
                    "wordFindingPauses": metrics.get("word_finding_pauses"),
                    "responseLatency": metrics.get("response_latency"),
                }
            if ne:
                sanity_doc["nostalgiaEngagement"] = {
                    "triggered": ne.get("triggered"),
                    "era": ne.get("era"),
                    "contentUsed": ne.get("content_used"),
                    "engagementScore": ne.get("engagement_score"),
                }
            await self._mutate([{"createOrReplace": sanity_doc}])
            return conv_id
        except Exception as exc:
            logger.error(f"save_conversation failed: {exc}")
            return conv_id

    # =========================================================================
    # COGNITIVE BASELINE
    # =========================================================================

    async def get_cognitive_baseline(self, patient_id: str) -> Optional[dict]:
        try:
            result = await self._query_groq(
                '*[_type == "cognitiveBaseline" && patient._ref == $pid][0]',
                {"pid": patient_id},
            )
            return self._map_baseline(result.get("result"))
        except Exception as exc:
            logger.error(f"get_cognitive_baseline failed: {exc}")
            return None

    async def save_cognitive_baseline(self, patient_id: str, baseline: dict) -> None:
        doc_id = f"baseline-{patient_id}"
        try:
            sanity_doc = {
                "_type": "cognitiveBaseline",
                "_id": doc_id,
                "patient": {"_ref": patient_id, "_type": "reference"},
                "patientId": patient_id,
                "established": baseline.get("established", False),
                "baselineDate": baseline.get("baseline_date"),
                "vocabularyDiversity": baseline.get("vocabulary_diversity"),
                "vocabularyDiversityStd": baseline.get("vocabulary_diversity_std"),
                "topicCoherence": baseline.get("topic_coherence"),
                "topicCoherenceStd": baseline.get("topic_coherence_std"),
                "repetitionRate": baseline.get("repetition_rate"),
                "repetitionRateStd": baseline.get("repetition_rate_std"),
                "wordFindingPauses": baseline.get("word_finding_pauses"),
                "wordFindingPausesStd": baseline.get("word_finding_pauses_std"),
                "avgResponseTime": baseline.get("avg_response_time"),
                "responseTimeStd": baseline.get("response_time_std"),
                "conversationCount": baseline.get("conversation_count", 0),
                "lastUpdated": baseline.get("last_updated"),
            }
            await self._mutate([{"createOrReplace": sanity_doc}])
        except Exception as exc:
            logger.error(f"save_cognitive_baseline failed: {exc}")

    # =========================================================================
    # WELLNESS DIGESTS
    # =========================================================================

    async def get_wellness_digests(
        self, patient_id: str, limit: int = 10, offset: int = 0
    ) -> list[dict]:
        end = offset + limit
        try:
            result = await self._query_groq(
                f'*[_type == "wellnessDigest" && patient._ref == $pid] | order(date desc) [{offset}...{end}]',
                {"pid": patient_id},
            )
            return [self._map_digest(d) for d in (result.get("result") or []) if d]
        except Exception as exc:
            logger.error(f"get_wellness_digests failed: {exc}")
            return []

    async def get_latest_wellness_digest(self, patient_id: str) -> Optional[dict]:
        try:
            result = await self._query_groq(
                '*[_type == "wellnessDigest" && patient._ref == $pid] | order(date desc)[0]',
                {"pid": patient_id},
            )
            return self._map_digest(result.get("result"))
        except Exception as exc:
            logger.error(f"get_latest_wellness_digest failed: {exc}")
            return None

    async def save_wellness_digest(self, digest: dict) -> str:
        digest_id = digest.get("id", f"digest-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}")
        try:
            sanity_doc: dict = {
                "_type": "wellnessDigest",
                "_id": digest_id,
                "patient": {"_ref": digest["patient_id"], "_type": "reference"},
                "date": digest.get("date"),
                "overallMood": digest.get("overall_mood"),
                "highlights": digest.get("highlights", []),
                "cognitiveScore": digest.get("cognitive_score"),
                "trend": digest.get("cognitive_trend"),
                "recommendations": digest.get("recommendations", []),
                "generatedAt": digest.get("created_at"),
            }
            conv_id = digest.get("conversation_id")
            if conv_id:
                sanity_doc["conversation"] = {"_ref": conv_id, "_type": "reference"}
            await self._mutate([{"createOrReplace": sanity_doc}])
            return digest_id
        except Exception as exc:
            logger.error(f"save_wellness_digest failed: {exc}")
            return digest_id

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
        end = offset + limit
        try:
            if severity:
                result = await self._query_groq(
                    f'*[_type == "alert" && patient._ref == $pid && severity == $sev] | order(timestamp desc) [{offset}...{end}]',
                    {"pid": patient_id, "sev": severity},
                )
            else:
                result = await self._query_groq(
                    f'*[_type == "alert" && patient._ref == $pid] | order(timestamp desc) [{offset}...{end}]',
                    {"pid": patient_id},
                )
            return [self._map_alert(a) for a in (result.get("result") or []) if a]
        except Exception as exc:
            logger.error(f"get_alerts failed: {exc}")
            return []

    async def save_alert(self, alert: dict) -> str:
        alert_id = alert.get("id", f"alert-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}")
        try:
            sanity_doc: dict = {
                "_type": "alert",
                "_id": alert_id,
                "patient": {"_ref": alert["patient_id"], "_type": "reference"},
                "alertType": alert.get("alert_type"),
                "severity": alert.get("severity"),
                "description": alert.get("description"),
                "relatedMetrics": alert.get("related_metrics"),
                "timestamp": alert.get("timestamp"),
                "acknowledged": alert.get("acknowledged", False),
            }
            conv_id = alert.get("conversation_id")
            if conv_id:
                sanity_doc["conversation"] = {"_ref": conv_id, "_type": "reference"}
            await self._mutate([{"createOrReplace": sanity_doc}])
            return alert_id
        except Exception as exc:
            logger.error(f"save_alert failed: {exc}")
            return alert_id

    async def update_alert(self, alert_id: str, updates: dict) -> bool:
        try:
            sanity_set: dict = {}
            if "acknowledged" in updates:
                sanity_set["acknowledged"] = updates["acknowledged"]
            if "acknowledged_by" in updates:
                sanity_set["acknowledgedBy"] = updates["acknowledged_by"]
            if "acknowledged_at" in updates:
                sanity_set["acknowledgedAt"] = updates["acknowledged_at"]
            await self._mutate([{"patch": {"id": alert_id, "set": sanity_set}}])
            return True
        except Exception as exc:
            logger.error(f"update_alert failed for {alert_id}: {exc}")
            return False

    # =========================================================================
    # FAMILY CONTACTS
    # =========================================================================

    async def get_family_contacts(self, patient_id: str) -> list[dict]:
        try:
            result = await self._query_groq(
                '*[_type == "familyMember" && $pid in patients[]._ref]',
                {"pid": patient_id},
            )
            return [self._map_family_contact(c) for c in (result.get("result") or []) if c]
        except Exception as exc:
            logger.error(f"get_family_contacts failed: {exc}")
            return []

    # =========================================================================
    # CONSECUTIVE DEVIATIONS
    # =========================================================================

    async def get_consecutive_deviations(self, patient_id: str) -> dict:
        """Returns dict mapping metric names to consecutive deviation counts."""
        doc_id = f"deviation-tracker-{patient_id}"
        try:
            result = await self._query_groq(
                '*[_type == "deviationTracker" && _id == $did][0].metrics',
                {"did": doc_id},
            )
            return result.get("result") or {}
        except Exception as exc:
            logger.error(f"get_consecutive_deviations failed: {exc}")
            return {}

    async def update_consecutive_deviations(
        self, patient_id: str, deviations: dict
    ) -> None:
        doc_id = f"deviation-tracker-{patient_id}"
        try:
            sanity_doc = {
                "_type": "deviationTracker",
                "_id": doc_id,
                "patient": {"_ref": patient_id, "_type": "reference"},
                "metrics": deviations,
            }
            await self._mutate([{"createOrReplace": sanity_doc}])
        except Exception as exc:
            logger.error(f"update_consecutive_deviations failed: {exc}")

    # =========================================================================
    # COGNITIVE TRENDS
    # =========================================================================

    async def get_cognitive_trends(self, patient_id: str, days: int = 30) -> list[dict]:
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        try:
            result = await self._query_groq(
                '*[_type == "conversation" && patient._ref == $pid && timestamp > $cutoff] | order(timestamp asc) { timestamp, cognitiveMetrics }',
                {"pid": patient_id, "cutoff": cutoff},
            )
            trends = []
            for conv in result.get("result") or []:
                cm = conv.get("cognitiveMetrics")
                if not cm:
                    continue
                metrics_dict = {
                    "vocabulary_diversity": cm.get("vocabularyDiversity"),
                    "topic_coherence": cm.get("topicCoherence"),
                    "repetition_rate": cm.get("repetitionRate"),
                    "word_finding_pauses": cm.get("wordFindingPauses"),
                }
                trends.append({
                    "timestamp": conv.get("timestamp", ""),
                    "vocabulary_diversity": metrics_dict["vocabulary_diversity"],
                    "topic_coherence": metrics_dict["topic_coherence"],
                    "repetition_rate": metrics_dict["repetition_rate"],
                    "word_finding_pauses": metrics_dict["word_finding_pauses"],
                    "response_latency": cm.get("responseLatency"),
                    "cognitive_score": calculate_cognitive_score(metrics_dict),
                })
            return trends
        except Exception as exc:
            logger.error(f"get_cognitive_trends failed: {exc}")
            return []

    # =========================================================================
    # INSIGHTS  (Sanity challenge showcase)
    # =========================================================================

    async def get_patient_insights(self, patient_id: str) -> dict:
        """
        Cross-document, reference-traversing, typed-field-aggregating insights.
        Features IMPOSSIBLE with flat files.
        """
        try:
            # 1) All conversations with metrics + mood + nostalgia flag
            conv_result = await self._query_groq(
                """*[_type == "conversation" && patient._ref == $pid && defined(cognitiveMetrics)] {
                    mood,
                    "vocab": cognitiveMetrics.vocabularyDiversity,
                    "coherence": cognitiveMetrics.topicCoherence,
                    "hasNostalgia": nostalgiaEngagement.triggered == true
                }""",
                {"pid": patient_id},
            )
            convos = conv_result.get("result") or []

            # Cognitive by mood
            mood_buckets: dict = {}
            for c in convos:
                mood = c.get("mood", "unknown")
                if mood not in mood_buckets:
                    mood_buckets[mood] = {"vocabs": [], "coherences": [], "count": 0}
                v = c.get("vocab")
                co = c.get("coherence")
                if v is not None:
                    mood_buckets[mood]["vocabs"].append(v)
                if co is not None:
                    mood_buckets[mood]["coherences"].append(co)
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
            with_n = [c for c in convos if c.get("hasNostalgia")]
            without_n = [c for c in convos if not c.get("hasNostalgia")]

            def _avg(lst, key):
                vals = [x[key] for x in lst if x.get(key) is not None]
                return sum(vals) / len(vals) if vals else 0.0

            wv, wov = _avg(with_n, "vocab"), _avg(without_n, "vocab")
            wc, woc = _avg(with_n, "coherence"), _avg(without_n, "coherence")
            vi = ((wv - wov) / wov * 100) if wov > 0 else 0
            ci = ((wc - woc) / woc * 100) if woc > 0 else 0

            nostalgia_effectiveness = {
                "with_nostalgia": {"avg_vocabulary": round(wv, 3), "avg_coherence": round(wc, 3), "count": len(with_n)},
                "without_nostalgia": {"avg_vocabulary": round(wov, 3), "avg_coherence": round(woc, 3), "count": len(without_n)},
                "improvement_pct": {"vocabulary": round(vi, 1), "coherence": round(ci, 1)},
            }

            # 2) Alerts cross-document query
            alert_result = await self._query_groq(
                '*[_type == "alert" && patient._ref == $pid] { alertType, severity, acknowledged }',
                {"pid": patient_id},
            )
            alerts = alert_result.get("result") or []

            sev_counts = {"low": 0, "medium": 0, "high": 0}
            type_counts: dict = {}
            ack_count = 0
            for a in alerts:
                sev = a.get("severity", "low")
                sev_counts[sev] = sev_counts.get(sev, 0) + 1
                at = a.get("alertType", "unknown")
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

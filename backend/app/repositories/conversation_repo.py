import logging
from typing import Optional
from supabase import Client

logger = logging.getLogger(__name__)

class ConversationRepository:
    def __init__(self, client: Client):
        self.client = client

    def get_for_patient(self, patient_id: str, limit: int = 10, offset: int = 0) -> list[dict]:
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
            logger.error(f"ConversationRepository.get_for_patient failed: {exc}")
            return []

    def get_by_id(self, conversation_id: str) -> Optional[dict]:
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
            logger.error(f"ConversationRepository.get_by_id failed: {exc}")
            return None

    def save(self, conversation: dict) -> str:
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
            logger.error(f"ConversationRepository.save failed: {exc}")
            return conversation.get("id", "error")

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

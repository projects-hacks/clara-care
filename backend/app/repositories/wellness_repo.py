import logging
from typing import Optional
from supabase import Client

logger = logging.getLogger(__name__)

class WellnessRepository:
    def __init__(self, client: Client):
        self.client = client

    def get_digests(
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
            logger.error(f"WellnessRepository.get_digests failed: {exc}")
            return []

    def get_latest_digest(self, patient_id: str) -> Optional[dict]:
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
            logger.error(f"WellnessRepository.get_latest_digest failed: {exc}")
            return None

    def save_digest(self, digest: dict) -> str:
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
            logger.error(f"WellnessRepository.save_digest failed: {exc}")
            return digest.get("id", "error")

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

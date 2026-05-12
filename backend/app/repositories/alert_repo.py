import logging
from typing import Optional
from supabase import Client

logger = logging.getLogger(__name__)

class AlertRepository:
    def __init__(self, client: Client):
        self.client = client

    def get_for_patient(
        self,
        patient_id: str,
        severity: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        try:
            # We allow empty patient_id to fetch all alerts (used in alert engine)
            query = self.client.table("alerts").select("*")
            if patient_id:
                query = query.eq("patient_id", patient_id)
                
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
            logger.error(f"AlertRepository.get_for_patient failed: {exc}")
            return []

    def get_by_id(self, alert_id: str) -> Optional[dict]:
        try:
            resp = self.client.table("alerts").select("*").eq("id", alert_id).execute()
            return self._map_alert(resp.data[0]) if resp.data else None
        except Exception as e:
            logger.error(f"AlertRepository.get_by_id failed for {alert_id}: {e}")
            return None

    def save(self, alert: dict) -> str:
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
            logger.error(f"AlertRepository.save failed: {exc}")
            return alert.get("id", "error")

    def update(self, alert_id: str, updates: dict) -> bool:
        try:
            allowed_keys = {
                "acknowledged", "acknowledged_by", "acknowledged_at",
                "acknowledgment_history", "severity",
            }
            db_updates = {k: v for k, v in updates.items() if k in allowed_keys}
            if not db_updates:
                return True

            self.client.table("alerts").update(db_updates).eq("id", alert_id).execute()
            return True
        except Exception as exc:
            logger.error(f"AlertRepository.update failed for {alert_id}: {exc}")
            return False

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

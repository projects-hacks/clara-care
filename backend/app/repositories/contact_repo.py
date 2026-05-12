import logging
from datetime import datetime, UTC
from typing import Optional
from supabase import Client

logger = logging.getLogger(__name__)

class ContactRepository:
    def __init__(self, client: Client):
        self.client = client

    def get_for_patient(self, patient_id: str) -> list[dict]:
        """Get family contacts from the family_contacts table."""
        try:
            result = self.client.table("family_contacts").select("*").eq("patient_id", patient_id).execute()
            contacts = [
                {
                    "id": fc["id"],
                    "user_id": fc.get("user_id"),
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
            return contacts
        except Exception as exc:
            logger.error(f"ContactRepository.get_for_patient failed: {exc}")
            return []

    def get_for_user(self, user_id: str) -> list[dict]:
        try:
            resp = self.client.table("family_contacts").select("*").eq("user_id", user_id).execute()
            return resp.data or []
        except Exception as e:
            logger.error(f"ContactRepository.get_for_user failed: {e}")
            return []

    def create(self, data: dict) -> dict:
        try:
            resp = self.client.table("family_contacts").insert(data).execute()
            return resp.data[0] if resp.data else {}
        except Exception as e:
            logger.error(f"ContactRepository.create failed: {e}")
            raise

    def get_by_invite_token(self, token: str) -> Optional[dict]:
        try:
            resp = self.client.table("family_contacts").select("*").eq("invite_token", token).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            logger.error(f"ContactRepository.get_by_invite_token failed: {e}")
            return None

    def accept_invite(self, contact_id: str, user_id: str) -> None:
        try:
            self.client.table("family_contacts").update({
                "user_id": user_id,
                "invite_token": None,
                "accepted_at": datetime.now(UTC).isoformat()
            }).eq("id", contact_id).execute()
        except Exception as e:
            logger.error(f"ContactRepository.accept_invite failed: {e}")
            raise

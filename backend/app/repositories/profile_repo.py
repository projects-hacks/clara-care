import logging
from typing import Optional
from supabase import Client

logger = logging.getLogger(__name__)

class ProfileRepository:
    def __init__(self, client: Client):
        self.client = client

    def get_by_id(self, user_id: str) -> Optional[dict]:
        try:
            resp = self.client.table("profiles").select("*").eq("id", user_id).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            logger.error(f"ProfileRepository.get_by_id failed for {user_id}: {e}")
            return None

    def update(self, user_id: str, updates: dict) -> dict:
        try:
            resp = self.client.table("profiles").update(updates).eq("id", user_id).execute()
            return resp.data[0] if resp.data else {}
        except Exception as e:
            logger.error(f"ProfileRepository.update failed for {user_id}: {e}")
            return {}

    def mark_onboarding_complete(self, user_id: str) -> None:
        try:
            self.client.table("profiles").update({
                "onboarding_completed": True
            }).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"ProfileRepository.mark_onboarding_complete failed for {user_id}: {e}")

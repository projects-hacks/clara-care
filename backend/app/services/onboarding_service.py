from app.utils.tokens import generate_invite_token
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OnboardingService:
    def __init__(self, patient_repo, profile_repo, contact_repo):
        self.patient_repo = patient_repo
        self.profile_repo = profile_repo
        self.contact_repo = contact_repo

    def create_patient_with_contact(self, user_id: str, user_email: str, data: dict) -> Dict[str, Any]:
        # 1. Create the patient
        patient_data = {
            "created_by": user_id,
            "name": data.get("name"),
            "preferred_name": data.get("preferred_name"),
            "birth_year": data.get("birth_year"),
            "phone_number": data.get("phone_number"),
            "city": data.get("city"),
            "state": data.get("state"),
            "timezone": data.get("timezone", "America/Los_Angeles"),
        }
        
        patient = self.patient_repo.create(patient_data)
        patient_id = patient.get("id")
        
        if not patient_id:
            raise ValueError("Failed to create patient")

        # 2. Get user info
        profile = self.profile_repo.get_by_id(user_id) or {}
        user_name = profile.get("display_name", "Family Member")
        user_phone = profile.get("phone", "")
        
        # 3. Create contact link
        contact_data = {
            "patient_id": patient_id,
            "user_id": user_id,
            "name": user_name,
            "email": user_email,
            "phone": user_phone,
            "relationship": "Primary Caregiver",
            "is_primary": True,
            "can_manage": True,
            "daily_digest": True,
            "instant_alerts": True
        }
        self.contact_repo.create(contact_data)
        
        return {
            "patient_id": patient_id,
            "message": "Patient created and you have been added as the primary contact."
        }

    def personalize_patient(self, patient_id: str, preferences: dict, medications: list) -> None:
        updates = {
            "preferences": preferences,
            "medications": medications
        }
        if "medical_notes" in preferences:
            updates["medical_notes"] = preferences.pop("medical_notes")
            
        success = self.patient_repo.update(patient_id, updates)
        if not success:
            raise ValueError("Failed to personalize patient")

    def schedule_and_invite(self, patient_id: str, preferred_call_time: str, invites: list) -> Dict[str, Any]:
        # 1. Update schedule
        success = self.patient_repo.update(patient_id, {"preferred_call_time": preferred_call_time})
        if not success:
            raise ValueError("Failed to update schedule")

        # 2. Process invites
        invited_count = 0
        for invite in invites:
            invite_token = generate_invite_token()
            invite_data = {
                "patient_id": patient_id,
                "name": invite.get("name"),
                "email": invite.get("email"),
                "relationship": invite.get("relationship"),
                "daily_digest": invite.get("daily_digest", True),
                "instant_alerts": invite.get("instant_alerts", True),
                "is_primary": False,
                "can_manage": False,
                "invite_token": invite_token
            }
            try:
                self.contact_repo.create(invite_data)
                invited_count += 1
                # TODO: Dispatch email via notification service
            except Exception as e:
                logger.warning(f"Failed to invite {invite.get('email')}: {str(e)}")

        return {
            "invited_count": invited_count,
            "message": f"Schedule saved. Invited {invited_count} family members."
        }

    def complete_onboarding(self, user_id: str) -> None:
        self.profile_repo.mark_onboarding_complete(user_id)

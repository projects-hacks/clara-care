from app.utils.tokens import generate_invite_token
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class InviteService:
    def __init__(self, contact_repo):
        self.contact_repo = contact_repo

    def create_invite(self, patient_id: str, invite_data: dict) -> Dict[str, Any]:
        invite_token = generate_invite_token()
        
        data = {
            "patient_id": patient_id,
            "name": invite_data.get("name"),
            "email": invite_data.get("email"),
            "relationship": invite_data.get("relationship"),
            "daily_digest": invite_data.get("daily_digest", True),
            "instant_alerts": invite_data.get("instant_alerts", True),
            "is_primary": False,
            "can_manage": False,
            "invite_token": invite_token
        }
        
        contact = self.contact_repo.create(data)
        
        if not contact:
            raise ValueError("Failed to create invite")
            
        # TODO: Send email
        
        return {
            "success": True,
            "invite_token": invite_token,
            "message": f"Invitation sent to {data['email']}"
        }

    def accept_invite(self, token: str, user_id: str) -> Dict[str, Any]:
        contact = self.contact_repo.get_by_invite_token(token)
        
        if not contact:
            raise ValueError("Invalid or expired invitation token.")
            
        if contact.get("user_id"):
            raise ValueError("This invitation has already been accepted.")
            
        self.contact_repo.accept_invite(contact["id"], user_id)
        
        return {
            "success": True,
            "patient_id": contact["patient_id"],
            "message": "Invitation accepted successfully!"
        }

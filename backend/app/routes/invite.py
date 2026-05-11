"""
Invitation Routes
Handles accepting family member invitations via token.
"""

from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException, Depends

from app.auth import get_current_user
from app.dependencies import get_data_store

router = APIRouter(prefix="/api/invite", tags=["invite"])


@router.get("/accept")
async def accept_invitation(
    token: str,
    user=Depends(get_current_user),
    store=Depends(get_data_store)
):
    """
    Accept an invitation using a token.
    Links the authenticated user's ID to the family_contact record.
    """
    if not hasattr(store, "client"):
        # Fallback for memory store
        for k, v in store.family_contacts.items():
            if v.get("invite_token") == token:
                v["user_id"] = user.id
                v["invite_token"] = None
                return {"success": True, "patient_id": v["patient_id"]}
        raise HTTPException(status_code=404, detail="Invalid token")

    try:
        # Use service_role store for the lookup (bypasses RLS)
        resp = store.client.table("family_contacts").select("*").eq("invite_token", token).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Invalid or expired invitation token")
            
        contact = resp.data[0]
        
        # Link the user
        store.client.table("family_contacts").update({
            "user_id": user.id,
            "invite_token": None,
            "accepted_at": datetime.now(UTC).isoformat()
        }).eq("id", contact["id"]).execute()
        
        return {
            "success": True,
            "message": "Invitation accepted successfully",
            "patient_id": contact["patient_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to accept invitation: {e}")

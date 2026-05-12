"""
Invitation Routes
Handles accepting family member invitations via token.
"""

from fastapi import APIRouter, HTTPException, Depends

from app.auth import get_current_user
from app.dependencies import get_invite_service

router = APIRouter(prefix="/api/invite", tags=["invite"])

@router.get("/accept")
async def accept_invitation(
    token: str,
    user=Depends(get_current_user),
    service=Depends(get_invite_service)
):
    """
    Accept an invitation using a token.
    Links the authenticated user's ID to the family_contact record.
    """
    try:
        return service.accept_invite(token, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to accept invitation: {e}")

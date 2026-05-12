"""
Patient API Routes
Endpoints for patient profile management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.models.patient import InviteRequest

from app.dependencies import get_patient_service, get_invite_service, get_conversation_repo
from app.auth import get_current_user, get_verified_patient_id

router = APIRouter(prefix="/api/patients", tags=["patients"])

@router.get("")
async def list_patients(user=Depends(get_current_user), service=Depends(get_patient_service)):
    """List all patients that the authenticated user has access to."""
    patients = service.get_for_user(user.id)
    return {"patients": patients}

@router.get("/{patient_id}")
async def get_patient(
    patient_id: str = Depends(get_verified_patient_id), 
    service=Depends(get_patient_service),
    conversation_repo=Depends(get_conversation_repo)
):
    """
    Get patient profile with baseline and latest digest
    """
    patient = service.get_detail(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get recent conversations (last 5)
    recent_conversations = conversation_repo.get_for_patient(patient_id, limit=5)
    
    return {
        "patient": patient,
        "baseline": patient.pop("cognitive_baseline", None),
        "latest_digest": patient.pop("latest_digest", None),
        "family_contacts": patient.pop("family_contacts", []),
        "recent_conversations": [
            {
                "id": c["id"],
                "timestamp": c.get("timestamp"),
                "duration": c.get("duration"),
                "mood": c.get("detected_mood"),
                "summary": c.get("summary", "")[:100] + "..." if len(c.get("summary", "")) > 100 else c.get("summary", "")
            }
            for c in recent_conversations
        ]
    }

@router.patch("/{patient_id}")
async def update_patient(
    updates: dict, 
    patient_id: str = Depends(get_verified_patient_id), 
    service=Depends(get_patient_service)
):
    """Update patient profile"""
    result = service.update(patient_id, updates)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail="Failed to update patient")
    
    updated_patient = service.get_detail(patient_id)
    return {"success": True, "patient": updated_patient}

@router.post("/{patient_id}/invite")
async def invite_family_member(
    body: InviteRequest,
    patient_id: str = Depends(get_verified_patient_id),
    service=Depends(get_invite_service)
):
    """Invite a family member to view this patient's dashboard."""
    try:
        result = service.create_invite(patient_id, body.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

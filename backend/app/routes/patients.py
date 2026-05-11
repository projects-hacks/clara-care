"""
Patient API Routes
Endpoints for patient profile management
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.dependencies import get_data_store
from app.auth import get_current_user, get_verified_patient_id

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("")
async def list_patients(user=Depends(get_current_user), store=Depends(get_data_store)):
    """
    List all patients that the authenticated user has access to.
    """
    if hasattr(store, "get_patients_for_user"):
        patients = await store.get_patients_for_user(user.id)
        return {"patients": patients}
    
    # Fallback if the store doesn't support fetching by user
    return {"patients": []}


@router.get("/{patient_id}")
async def get_patient(
    patient_id: str = Depends(get_verified_patient_id), 
    store=Depends(get_data_store)
):
    """
    Get patient profile with baseline and latest digest
    
    Returns:
        - Patient profile
        - Cognitive baseline (if established)
        - Latest wellness digest
        - Recent conversations summary
    """
    # Get patient
    patient = await store.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get baseline
    baseline = await store.get_cognitive_baseline(patient_id)
    
    # Get latest digest
    latest_digest = await store.get_latest_wellness_digest(patient_id)
    
    # Get recent conversations (last 5)
    recent_conversations = await store.get_conversations(patient_id, limit=5)
    
    return {
        "patient": patient,
        "baseline": baseline,
        "latest_digest": latest_digest,
        "recent_conversations": [
            {
                "id": c["id"],
                "timestamp": c["timestamp"],
                "duration": c["duration"],
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
    store=Depends(get_data_store)
):
    """
    Update patient profile
    
    Body: JSON with fields to update (e.g., preferences, thresholds)
    """
    # Verify patient exists
    patient = await store.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update patient
    success = await store.update_patient(patient_id, updates)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update patient")
    
    # Return updated patient
    updated_patient = await store.get_patient(patient_id)
    
    return {
        "success": True,
        "patient": updated_patient
    }


class InviteRequest(BaseModel):
    name: str
    email: EmailStr
    relationship: str
    daily_digest: bool = True
    instant_alerts: bool = True

@router.post("/{patient_id}/invite")
async def invite_family_member(
    body: InviteRequest,
    patient_id: str = Depends(get_verified_patient_id),
    store=Depends(get_data_store)
):
    """
    Invite a family member to view this patient's dashboard.
    Generates a secure token and creates a pending family_contact record.
    """
    # Generate token
    invite_token = str(uuid.uuid4())
    
    invite_data = {
        "patient_id": patient_id,
        "name": body.name,
        "email": body.email,
        "relationship": body.relationship,
        "daily_digest": body.daily_digest,
        "instant_alerts": body.instant_alerts,
        "is_primary": False,
        "can_manage": False,
        "invite_token": invite_token
    }
    
    try:
        # Use service_role store for the insert (bypasses RLS)
        if hasattr(store, "client"):
            store.client.table("family_contacts").insert(invite_data).execute()
        else:
            # Memory store fallback
            store.family_contacts[invite_token] = invite_data
            
        # TODO: Send email using SendGrid
        # link = f"https://claracare.me/invite?token={invite_token}"
            
        return {
            "success": True,
            "message": f"Invitation sent to {body.email}",
            "invite_token": invite_token # For dev/testing only
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create invitation: {e}")

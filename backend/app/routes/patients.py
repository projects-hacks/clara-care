"""
Patient API Routes
Endpoints for patient profile management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.dependencies import get_data_store

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("/{patient_id}")
async def get_patient(patient_id: str, store=Depends(get_data_store)):
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
async def update_patient(patient_id: str, updates: dict, store=Depends(get_data_store)):
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

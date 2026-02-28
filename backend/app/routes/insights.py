"""
Insights API Routes
Showcase endpoint for Sanity challenge - demonstrates structured content features
"""

from fastapi import APIRouter, HTTPException, Depends

from app.dependencies import get_data_store

router = APIRouter(prefix="/api/patients", tags=["insights"])


@router.get("/{patient_id}/insights")
async def get_patient_insights(patient_id: str, store=Depends(get_data_store)):
    
    # Verify patient exists
    patient = await store.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get insights using structured content queries
    insights = await store.get_patient_insights(patient_id)
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.get("name"),
        "insights": insights,
        "note": "These insights are only possible with structured content and typed fields"
    }

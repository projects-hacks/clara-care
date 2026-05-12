"""
Insights API Routes
Showcase endpoint - demonstrates structured content and cross-table aggregation features
"""

from fastapi import APIRouter, HTTPException, Depends

from app.dependencies import get_cognitive_repo, get_patient_repo
from app.auth import get_verified_patient_id

router = APIRouter(prefix="/api/patients", tags=["insights"])


@router.get("/{patient_id}/insights")
async def get_patient_insights(
    patient_id: str = Depends(get_verified_patient_id), 
    cognitive_repo=Depends(get_cognitive_repo),
    patient_repo=Depends(get_patient_repo)
):
    
    # Verify patient exists
    patient = patient_repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get insights using structured content queries
    insights = cognitive_repo.get_patient_insights(patient_id)
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.get("name"),
        "insights": insights
    }

"""
Wellness & Cognitive Trends API Routes
Endpoints for wellness digests and cognitive trend data
"""

import re
from fastapi import APIRouter, HTTPException, Query, Depends

from app.dependencies import get_wellness_repo, get_cognitive_repo, get_patient_repo, get_contact_repo
from app.auth import get_current_user, verify_patient_access
from app.normalizers import normalize_digest

router = APIRouter(prefix="/api", tags=["wellness"])

@router.get("/wellness-digests")
async def list_wellness_digests(
    patient_id: str = Query(..., description="Patient ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    wellness_repo=Depends(get_wellness_repo),
    patient_repo=Depends(get_patient_repo),
    contact_repo=Depends(get_contact_repo),
):
    await verify_patient_access(patient_repo, contact_repo, user.id, patient_id)
    digests = wellness_repo.get_digests(patient_id, limit=limit, offset=offset)
    digests = [normalize_digest(d) for d in digests]

    return {
        "patient_id": patient_id,
        "digests": digests,
        "count": len(digests),
        "limit": limit,
        "offset": offset
    }

@router.get("/wellness-digests/latest")
async def get_latest_digest(
    patient_id: str = Query(..., description="Patient ID"),
    user=Depends(get_current_user),
    wellness_repo=Depends(get_wellness_repo),
    patient_repo=Depends(get_patient_repo),
    contact_repo=Depends(get_contact_repo),
):
    """
    Get the most recent wellness digest for a patient
    """
    await verify_patient_access(patient_repo, contact_repo, user.id, patient_id)
    digest = wellness_repo.get_latest_digest(patient_id)

    if not digest:
        raise HTTPException(status_code=404, detail="No wellness digests found")

    return normalize_digest(digest)

@router.get("/cognitive-trends")
async def get_cognitive_trends(
    patient_id: str = Query(..., description="Patient ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    user=Depends(get_current_user),
    cognitive_repo=Depends(get_cognitive_repo),
    patient_repo=Depends(get_patient_repo),
    contact_repo=Depends(get_contact_repo),
):
    await verify_patient_access(patient_repo, contact_repo, user.id, patient_id)

    # Get baseline for reference
    baseline = cognitive_repo.get_baseline(patient_id)

    # Get trends data
    data_points = cognitive_repo.get_trends(patient_id, days=days)

    return {
        "patient_id": patient_id,
        "period_days": days,
        "data_points": data_points,
        "baseline": {
            "vocabulary_diversity": baseline.get("vocabulary_diversity") if baseline else None,
            "topic_coherence": baseline.get("topic_coherence") if baseline else None,
            "repetition_rate": baseline.get("repetition_rate") if baseline else None
        } if baseline else None
    }

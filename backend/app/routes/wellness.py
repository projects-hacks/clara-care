"""
Wellness & Cognitive Trends API Routes
Endpoints for wellness digests and cognitive trend data
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api", tags=["wellness"])

# Data store will be injected as dependency
_data_store = None


def get_data_store():
    """Dependency to get data store"""
    if _data_store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    return _data_store


def set_data_store(store):
    """Set the data store (called during app initialization)"""
    global _data_store
    _data_store = store


@router.get("/wellness-digests")
async def list_wellness_digests(
    patient_id: str = Query(..., description="Patient ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get paginated list of wellness digests for a patient
    
    Query params:
        - patient_id: Patient identifier
        - limit: Max results (1-100, default 10)
        - offset: Pagination offset (default 0)
    """
    store = get_data_store()
    
    digests = await store.get_wellness_digests(patient_id, limit=limit, offset=offset)
    
    return {
        "patient_id": patient_id,
        "digests": digests,
        "count": len(digests),
        "limit": limit,
        "offset": offset
    }


@router.get("/wellness-digests/latest")
async def get_latest_digest(patient_id: str = Query(..., description="Patient ID")):
    """
    Get the most recent wellness digest for a patient
    """
    store = get_data_store()
    
    digest = await store.get_latest_wellness_digest(patient_id)
    
    if not digest:
        raise HTTPException(status_code=404, detail="No wellness digests found")
    
    return digest


@router.get("/cognitive-trends")
async def get_cognitive_trends(
    patient_id: str = Query(..., description="Patient ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include")
):
    """
    Get time-series cognitive metrics for charting
    
    Returns data points for the last N days, suitable for Recharts or similar
    
    Query params:
        - patient_id: Patient identifier
        - days: Number of days to include (1-365, default 30)
    """
    store = get_data_store()
    
    # Get baseline for reference
    baseline = await store.get_cognitive_baseline(patient_id)
    
    # Get trends data
    data_points = await store.get_cognitive_trends(patient_id, days=days)
    
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

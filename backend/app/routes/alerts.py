"""
Alerts API Routes
Endpoints for viewing and managing alerts
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

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


@router.get("")
async def list_alerts(
    patient_id: str = Query(..., description="Patient ID"),
    severity: Optional[str] = Query(None, description="Filter by severity (low/medium/high)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get alerts for a patient
    
    Query params:
        - patient_id: Patient identifier
        - severity: Optional severity filter (low, medium, high)
        - limit: Max results (1-100, default 20)
        - offset: Pagination offset (default 0)
    """
    store = get_data_store()
    
    # Validate severity if provided
    if severity and severity not in ["low", "medium", "high"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid severity. Must be: low, medium, or high"
        )
    
    alerts = await store.get_alerts(
        patient_id,
        severity=severity,
        limit=limit,
        offset=offset
    )
    
    return {
        "patient_id": patient_id,
        "alerts": alerts,
        "count": len(alerts),
        "severity_filter": severity,
        "limit": limit,
        "offset": offset
    }


@router.patch("/{alert_id}")
async def acknowledge_alert(alert_id: str, body: dict):
    """
    Mark an alert as acknowledged
    
    Body:
        - acknowledged_by: ID of person acknowledging (family member ID)
    """
    store = get_data_store()
    
    acknowledged_by = body.get("acknowledged_by")
    if not acknowledged_by:
        raise HTTPException(
            status_code=400,
            detail="acknowledged_by is required"
        )
    
    # Update alert
    updates = {
        "acknowledged": True,
        "acknowledged_at": datetime.utcnow().isoformat(),
        "acknowledged_by": acknowledged_by
    }
    
    success = await store.update_alert(alert_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "success": True,
        "alert_id": alert_id,
        "acknowledged": True
    }

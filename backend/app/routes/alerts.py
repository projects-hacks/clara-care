"""
Alerts API Routes
Endpoints for viewing and managing alerts
"""

from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from app.dependencies import get_alert_repo, get_patient_repo, get_contact_repo
from app.auth import get_current_user, verify_patient_access
from app.models.alert import AcknowledgeAlertRequest
from app.normalizers import normalize_alert

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("")
async def list_alerts(
    patient_id: str = Query(..., description="Patient ID"),
    severity: Optional[str] = Query(None, description="Filter by severity (low/medium/high)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    alert_repo=Depends(get_alert_repo),
    patient_repo=Depends(get_patient_repo),
    contact_repo=Depends(get_contact_repo),
):
    # Verify access
    verify_patient_access(patient_repo, contact_repo, user.id, patient_id)

    # Validate severity if provided
    if severity and severity not in ["low", "medium", "high"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid severity. Must be: low, medium, or high"
        )

    alerts = alert_repo.get_for_patient(
        patient_id,
        severity=severity,
        limit=limit,
        offset=offset
    )

    alerts = [normalize_alert(a) for a in alerts]

    return {
        "patient_id": patient_id,
        "alerts": alerts,
        "count": len(alerts),
        "severity_filter": severity,
        "limit": limit,
        "offset": offset
    }

@router.patch("/{alert_id}")
async def acknowledge_alert(
    alert_id: str, 
    body: AcknowledgeAlertRequest, 
    user=Depends(get_current_user),
    alert_repo=Depends(get_alert_repo),
    patient_repo=Depends(get_patient_repo),
    contact_repo=Depends(get_contact_repo),
):
    """
    Mark an alert as acknowledged.
    """
    alert = alert_repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    # VERIFY ACCESS
    verify_patient_access(patient_repo, contact_repo, user.id, alert.get("patient_id"))

    acknowledged_by = body.acknowledged_by
    now = datetime.now(UTC).isoformat()
    ack_entry = {"by": acknowledged_by, "at": now}

    if alert.get("acknowledged"):
        # Already acknowledged — append to history
        history = list(alert.get("acknowledgment_history") or [])
        if not history and alert.get("acknowledged_by"):
            history.append({
                "by": alert["acknowledged_by"],
                "at": alert.get("acknowledged_at", ""),
            })
        history.append(ack_entry)

        updates = {
            "acknowledgment_history": history,
        }
    else:
        # First acknowledgment
        updates = {
            "acknowledged": True,
            "acknowledged_at": now,
            "acknowledged_by": acknowledged_by,
            "acknowledgment_history": [ack_entry],
        }

    success = alert_repo.update(alert_id, updates)

    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {
        "success": True,
        "alert_id": alert_id,
        "acknowledged": True,
        "first_acknowledged_by": alert.get("acknowledged_by", acknowledged_by),
    }

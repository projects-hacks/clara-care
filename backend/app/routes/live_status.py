"""
Live Call Status API Route
Provides real-time call status for the dashboard
"""

import logging
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/live-status", tags=["live-status"])


@router.get("")
async def get_live_status(patient_id: str = Query(..., description="Patient ID to check")):
    """
    Get real-time call status for a patient
    
    Returns:
        {
            "is_active": bool,
            "call_sid": str (optional),
            "duration_sec": int (optional),
            "started_at": str (optional)
        }
    """
    from app.main import app
    
    # Access the twilio_bridge from the app state
    try:
        from app.voice import twilio_bridge
        
        active_calls = twilio_bridge.active_calls
        
        # Find active call for this patient
        for call_sid, session in active_calls.items():
            if session.patient_id == patient_id and session.is_active:
                # Calculate duration
                duration_sec = 0
                started_at = None
                
                if session.call_start_time:
                    from datetime import datetime, UTC
                    duration_sec = int((datetime.now(UTC) - session.call_start_time).total_seconds())
                    started_at = session.call_start_time.isoformat()
                
                return {
                    "is_active": True,
                    "call_sid": call_sid,
                    "patient_id": patient_id,
                    "duration_sec": duration_sec,
                    "started_at": started_at
                }
        
        # No active call found
        return {
            "is_active": False,
            "patient_id": patient_id
        }
        
    except Exception as e:
        logger.error(f"Error getting live status: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "is_active": False,
                "error": str(e)
            }
        )


@router.get("/all")
async def get_all_active_calls():
    """
    Get all currently active calls
    
    Returns:
        {
            "active_count": int,
            "calls": [
                {
                    "call_sid": str,
                    "patient_id": str,
                    "duration_sec": int,
                    "started_at": str
                }
            ]
        }
    """
    from app.voice import twilio_bridge
    from datetime import datetime, UTC
    
    active_calls = []
    
    for call_sid, session in twilio_bridge.active_calls.items():
        if session.is_active:
            duration_sec = 0
            started_at = None
            
            if session.call_start_time:
                duration_sec = int((datetime.now(UTC) - session.call_start_time).total_seconds())
                started_at = session.call_start_time.isoformat()
            
            active_calls.append({
                "call_sid": call_sid,
                "patient_id": session.patient_id,
                "duration_sec": duration_sec,
                "started_at": started_at
            })
    
    return {
        "active_count": len(active_calls),
        "calls": active_calls
    }

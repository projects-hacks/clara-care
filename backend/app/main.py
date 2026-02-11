"""
ClaraCare FastAPI Application
Main entry point for the backend server
"""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from .voice import twilio_bridge, session_manager, outbound_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager
    Handles startup and shutdown
    """
    # Startup
    logger.info("Starting ClaraCare backend...")
    yield
    
    # Shutdown
    logger.info("Shutting down ClaraCare backend...")
    await session_manager.close_all_sessions()


# Create FastAPI app
app = FastAPI(
    title="ClaraCare API",
    description="AI Elder Care Companion - Voice Agent Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ClaraCare Backend",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "active_calls": twilio_bridge.get_active_call_count(),
        "active_sessions": len(session_manager.sessions)
    }


@app.get("/voice/twiml")
async def twiml_handler(patient_id: str = "demo-patient"):
    """
    TwiML endpoint for outbound calls
    Returns TwiML that connects the call to our WebSocket
    
    Query params:
        patient_id: Patient identifier
    """
    server_url = os.getenv("SERVER_PUBLIC_URL", "http://localhost:8000")
    
    # Strip protocol to get hostname for WSS URL
    ws_host = server_url.replace('https://', '').replace('http://', '')
    
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{ws_host}/voice/twilio?patient_id={patient_id}" />
    </Connect>
</Response>'''
    
    return Response(content=twiml, media_type="application/xml")


@app.post("/voice/status")
async def call_status_callback(request: Request):
    """
    Twilio call status callback
    Receives updates about call status (initiated, ringing, answered, completed)
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    
    logger.info(f"Call status update: {call_sid} - {call_status}")
    
    return {"status": "received"}


@app.websocket("/voice/twilio")
async def twilio_websocket(websocket: WebSocket, patient_id: str = "demo-patient"):
    """
    Twilio Media Stream WebSocket endpoint
    
    Query params:
        patient_id: Patient identifier (default: demo-patient)
    
    Example Twilio webhook URL:
        wss://your-domain.com/voice/twilio?patient_id=patient-123
    """
    logger.info(f"Incoming Twilio call for patient: {patient_id}")
    
    await twilio_bridge.handle_call(
        websocket=websocket,
        patient_id=patient_id
    )


@app.post("/voice/call/end/{call_sid}")
async def end_call(call_sid: str):
    """
    Manually end an active call
    
    Args:
        call_sid: Twilio call SID
    """
    try:
        await twilio_bridge.end_call(call_sid)
        return {"message": f"Call {call_sid} ended"}
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/call/patient")
async def initiate_call_to_patient(request: Request):
    """
    Initiate an outbound call to a patient
    
    Request Body (JSON):
        patient_id: Patient identifier
        patient_phone: Patient's phone number (E.164 format: +1234567890)
        patient_name: Patient's name (optional)
        
    Example:
        POST /voice/call/patient
        {
            "patient_id": "patient-123",
            "patient_phone": "+11234567890",
            "patient_name": "Margaret"
        }
    """
    body = await request.json()
    patient_id = body.get("patient_id")
    patient_phone = body.get("patient_phone")
    patient_name = body.get("patient_name", "Patient")
    
    if not patient_id or not patient_phone:
        raise HTTPException(status_code=400, detail="patient_id and patient_phone are required")
    
    logger.info(f"Initiating call to {patient_name} ({patient_phone})")
    
    result = await outbound_manager.call_patient(
        patient_id=patient_id,
        patient_phone=patient_phone,
        patient_name=patient_name
    )
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Call failed"))


@app.post("/voice/call/daily-checkins")
async def trigger_daily_checkins():
    """
    Trigger daily check-in calls for all patients
    
    In production, this would:
    1. Fetch patient list from Sanity
    2. Filter patients who need check-ins today
    3. Initiate calls to each patient
    """
    # Example patient list (in production, fetch from Sanity)
    demo_patients = [
        {
            "patient_id": "demo-patient",
            "phone": "+11234567890",  # Replace with real number for testing
            "name": "Demo Patient"
        }
    ]
    
    logger.info("Triggering daily check-ins...")
    
    result = await outbound_manager.call_multiple_patients(demo_patients)
    
    return result


@app.get("/voice/calls")
async def list_active_calls():
    """List all active calls"""
    calls = []
    for call_sid, session in twilio_bridge.active_calls.items():
        calls.append({
            "call_sid": call_sid,
            "patient_id": session.patient_id,
            "is_active": session.is_active,
            "stream_sid": session.twilio_stream.stream_sid
        })
    
    return {
        "active_calls": calls,
        "count": len(calls)
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

"""
Onboarding API Routes
Handles the multi-step onboarding process for new patients.
"""

import logging
from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.dependencies import get_onboarding_service
from app.models.patient import (
    CreatePatientRequest,
    PersonalizePatientRequest,
    SchedulePatientRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

@router.post("/patient")
async def step1_create_patient(
    body: CreatePatientRequest,
    user=Depends(get_current_user),
    service=Depends(get_onboarding_service)
):
    """Step 1: Create the patient and add the creator as the primary family contact."""
    return service.create_patient_with_contact(user.id, user.email, body.model_dump())

@router.post("/personalize")
async def step2_personalize_patient(
    body: PersonalizePatientRequest,
    user=Depends(get_current_user),
    service=Depends(get_onboarding_service)
):
    """Step 2: Update patient preferences and add medications."""
    service.personalize_patient(body.patient_id, body.model_dump(exclude={'patient_id', 'medications'}, exclude_unset=True), body.medications)
    return {"success": True, "message": "Patient preferences and medications updated."}

@router.post("/schedule")
async def step3_schedule_patient(
    body: SchedulePatientRequest,
    user=Depends(get_current_user),
    service=Depends(get_onboarding_service)
):
    """Step 3: Save call schedule and send invites to other family members."""
    result = service.schedule_and_invite(body.patient_id, body.preferred_call_time, body.model_dump().get("invites", []))
    service.complete_onboarding(user.id)
    return {"success": True, **result}

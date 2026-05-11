"""
Onboarding API Routes
Handles the 3-step process of adding a new patient and setting up their Clara profile.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.auth import get_auth_client, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


# --- Request Models ---

class CreatePatientRequest(BaseModel):
    name: str
    preferred_name: str
    birth_year: int
    phone_number: str
    city: Optional[str] = None
    state: Optional[str] = None
    timezone: Optional[str] = "America/Los_Angeles"

class MedicationItem(BaseModel):
    name: str
    dosage: Optional[str] = None
    schedule: Optional[str] = None

class PersonalizePatientRequest(BaseModel):
    patient_id: str
    favorite_topics: Optional[List[str]] = []
    interests: Optional[List[str]] = []
    topics_to_avoid: Optional[List[str]] = []
    communication_style: Optional[str] = "warm and patient"
    medications: Optional[List[MedicationItem]] = []
    medical_notes: Optional[str] = None

class InviteItem(BaseModel):
    name: str
    email: str
    relationship: str
    daily_digest: bool = True
    instant_alerts: bool = True

class SchedulePatientRequest(BaseModel):
    patient_id: str
    preferred_call_time: str
    invites: Optional[List[InviteItem]] = []


# --- Endpoints ---

@router.post("/patient")
async def step1_create_patient(body: CreatePatientRequest, user = Depends(get_current_user)):
    """
    Step 1: Create a new patient and automatically add the user as the primary family contact.
    """
    client = get_auth_client()
    try:
        # 1. Create the patient
        # We use the anon client. The RLS policies allow insertion if created_by is set to the user.
        # But for insertion we might need to use the service role if RLS blocks it,
        # or we just rely on the RLS policy: CREATE POLICY "profiles_insert_own" ON profiles FOR INSERT WITH CHECK (auth.uid() = id);
        # Wait, the patients insert policy wasn't explicitly defined in the SQL dump, it was "patients_access" ON patients FOR ALL.
        # If there's an issue with RLS during insert via anon client, we'll need to adjust policies.
        # For now, we try it with the anon client.
        
        patient_data = {
            "created_by": user.id,
            "name": body.name,
            "preferred_name": body.preferred_name,
            "birth_year": body.birth_year,
            "phone_number": body.phone_number,
            "city": body.city,
            "state": body.state,
            "timezone": body.timezone,
        }
        
        patient_resp = client.table("patients").insert(patient_data).execute()
        
        if not patient_resp.data:
            raise ValueError("Failed to insert patient")
            
        patient_id = patient_resp.data[0]["id"]
        
        # 2. Add the user as the primary family contact
        # We need the user's name from their profile
        profile_resp = client.table("profiles").select("display_name, phone").eq("id", user.id).execute()
        user_name = profile_resp.data[0].get("display_name", "Family Member") if profile_resp.data else "Family Member"
        user_phone = profile_resp.data[0].get("phone", "") if profile_resp.data else ""
        
        contact_data = {
            "patient_id": patient_id,
            "user_id": user.id,
            "name": user_name,
            "email": user.email,
            "phone": user_phone,
            "relationship": "Primary Caregiver", # Default, can be updated later
            "is_primary": True,
            "can_manage": True,
            "daily_digest": True,
            "instant_alerts": True
        }
        
        client.table("family_contacts").insert(contact_data).execute()
        
        return {
            "success": True,
            "patient_id": patient_id,
            "message": "Patient created and you have been added as the primary contact."
        }
    except Exception as e:
        logger.error(f"Failed to create patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/personalize")
async def step2_personalize_patient(body: PersonalizePatientRequest, user = Depends(get_current_user)):
    """
    Step 2: Update the patient's Clara persona tuning and medications.
    """
    client = get_auth_client()
    try:
        # Verify access happens implicitly via RLS
        
        # 1. Update patient record
        update_data = {
            "favorite_topics": body.favorite_topics,
            "interests": body.interests,
            "topics_to_avoid": body.topics_to_avoid,
            "communication_style": body.communication_style,
            "medical_notes": body.medical_notes
        }
        
        client.table("patients").update(update_data).eq("id", body.patient_id).execute()
        
        # 2. Add medications
        if body.medications:
            # Clear existing meds for simplicity in onboarding
            client.table("medications").delete().eq("patient_id", body.patient_id).execute()
            
            meds_data = []
            for med in body.medications:
                meds_data.append({
                    "patient_id": body.patient_id,
                    "name": med.name,
                    "dosage": med.dosage,
                    "schedule": med.schedule
                })
            
            if meds_data:
                client.table("medications").insert(meds_data).execute()
                
        return {
            "success": True,
            "message": "Patient personalization saved."
        }
    except Exception as e:
        logger.error(f"Failed to personalize patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/schedule")
async def step3_schedule_patient(body: SchedulePatientRequest, user = Depends(get_current_user)):
    """
    Step 3: Set preferred call time and handle optional family invites.
    """
    client = get_auth_client()
    try:
        # 1. Update call time
        client.table("patients").update({
            "preferred_call_time": body.preferred_call_time
        }).eq("id", body.patient_id).execute()
        
        # 2. Process invites
        invited_count = 0
        if body.invites:
            import uuid
            for invite in body.invites:
                # Generate a secure invite token
                invite_token = str(uuid.uuid4())
                
                invite_data = {
                    "patient_id": body.patient_id,
                    "name": invite.name,
                    "email": invite.email,
                    "relationship": invite.relationship,
                    "daily_digest": invite.daily_digest,
                    "instant_alerts": invite.instant_alerts,
                    "is_primary": False,
                    "can_manage": False,
                    "invite_token": invite_token
                }
                
                try:
                    client.table("family_contacts").insert(invite_data).execute()
                    invited_count += 1
                    
                    # TODO: Send email via SendGrid/Resend with the invite link
                    # link = f"https://claracare.me/invite?token={invite_token}"
                    # logger.info(f"Would send invite to {invite.email}: {link}")
                    
                except Exception as e:
                    logger.warning(f"Failed to invite {invite.email}: {str(e)}")
                    # Continue with other invites
                    
        return {
            "success": True,
            "message": f"Schedule saved. Invited {invited_count} family members."
        }
    except Exception as e:
        logger.error(f"Failed to schedule patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete")
async def complete_onboarding(user = Depends(get_current_user)):
    """
    Mark the onboarding flow as completed for this user.
    """
    client = get_auth_client()
    try:
        client.table("profiles").update({
            "onboarding_completed": True
        }).eq("id", user.id).execute()
        
        return {
            "success": True,
            "message": "Onboarding marked as completed."
        }
    except Exception as e:
        logger.error(f"Failed to complete onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

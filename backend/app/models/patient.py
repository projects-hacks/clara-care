from typing import List, Optional
from pydantic import BaseModel, EmailStr

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

class InviteRequest(BaseModel):
    name: str
    email: EmailStr
    relationship: str
    daily_digest: bool = True
    instant_alerts: bool = True

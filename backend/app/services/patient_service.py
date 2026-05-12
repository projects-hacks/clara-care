import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self, patient_repo, contact_repo, conversation_repo, wellness_repo, cognitive_repo):
        self.patient_repo = patient_repo
        self.contact_repo = contact_repo
        self.conversation_repo = conversation_repo
        self.wellness_repo = wellness_repo
        self.cognitive_repo = cognitive_repo

    def get_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        return self.patient_repo.get_for_user(user_id)

    def get_detail(self, patient_id: str) -> Dict[str, Any]:
        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            return {}
            
        contacts = self.contact_repo.get_for_patient(patient_id)
        patient["family_contacts"] = contacts
        
        # Enrich with latest digest
        digest = self.wellness_repo.get_latest_digest(patient_id)
        if digest:
            patient["latest_digest"] = digest
            
        # Enrich with baseline
        baseline = self.cognitive_repo.get_baseline(patient_id)
        if baseline:
            patient["cognitive_baseline"] = baseline
            
        return patient

    def update(self, patient_id: str, updates: dict) -> Dict[str, Any]:
        success = self.patient_repo.update(patient_id, updates)
        return {
            "success": success,
            "message": "Patient updated" if success else "Failed to update patient"
        }

import logging
from datetime import datetime, UTC
from typing import Optional

from supabase import Client

logger = logging.getLogger(__name__)

class PatientRepository:
    def __init__(self, client: Client):
        self.client = client

    def get_by_id(self, patient_id: str) -> Optional[dict]:
        try:
            result = self.client.table("patients").select("*").eq("id", patient_id).maybe_single().execute()
            row = result.data
            if not row:
                return None

            patient = self._map_patient(row)

            # Fetch medications separately (normalized table)
            meds_result = self.client.table("medications").select("*").eq("patient_id", patient_id).execute()
            patient["medications"] = [
                {"name": m["name"], "dosage": m.get("dosage"), "schedule": m.get("schedule")}
                for m in (meds_result.data or [])
            ]

            return patient
        except Exception as exc:
            logger.error(f"PatientRepository.get_by_id failed for {patient_id}: {exc}")
            return None

    def get_for_user(self, user_id: str) -> list[dict]:
        """Get all patients accessible by a specific user"""
        try:
            # First find patients where user is a family contact
            contacts_resp = self.client.table("family_contacts").select("patient_id").eq("user_id", user_id).execute()
            contact_patient_ids = [c["patient_id"] for c in (contacts_resp.data or [])]
            
            # Now fetch the patient data where user is creator OR contact
            query = self.client.table("patients").select("*")
            if contact_patient_ids:
                id_list = ",".join(contact_patient_ids)
                query = query.or_(f"created_by.eq.{user_id},id.in.({id_list})")
            else:
                query = query.eq("created_by", user_id)
                
            patients_resp = query.execute()
            
            patients = []
            for p in (patients_resp.data or []):
                patient_dict = self._map_patient(p)
                patient_dict["medications"] = []
                patients.append(patient_dict)
            return patients
        except Exception as e:
            logger.error(f"PatientRepository.get_for_user failed: {e}")
            return []

    @staticmethod
    def _map_patient(row: dict) -> dict:
        return {
            "id": row["id"],
            "created_by": row.get("created_by"),
            "name": row.get("name"),
            "preferred_name": row.get("preferred_name"),
            "date_of_birth": row.get("date_of_birth"),
            "birth_year": row.get("birth_year"),
            "age": row.get("age"),
            "location": {
                "city": row.get("city"),
                "state": row.get("state"),
                "timezone": row.get("timezone"),
            },
            "medical_notes": row.get("medical_notes"),
            "phone_number": row.get("phone_number"),
            "preferences": {
                "favorite_topics": row.get("favorite_topics", []),
                "communication_style": row.get("communication_style", ""),
                "interests": row.get("interests", []),
                "topics_to_avoid": row.get("topics_to_avoid", []),
            },
            "cognitive_thresholds": {
                "deviation_threshold": float(row.get("deviation_threshold", 0.20)),
                "consecutive_trigger": row.get("consecutive_trigger", 3),
            },
            "call_schedule": {
                "preferred_time": row.get("preferred_call_time"),
                "timezone": row.get("timezone", "America/Los_Angeles"),
            },
        }

    def create(self, data: dict) -> dict:
        try:
            resp = self.client.table("patients").insert(data).execute()
            return resp.data[0] if resp.data else {}
        except Exception as e:
            logger.error(f"PatientRepository.create failed: {e}")
            raise

    def update(self, patient_id: str, updates: dict) -> bool:
        try:
            db_updates = {}

            if "preferences" in updates:
                p = updates["preferences"]
                db_updates["favorite_topics"] = p.get("favorite_topics", [])
                db_updates["communication_style"] = p.get("communication_style", "")
                db_updates["interests"] = p.get("interests", [])
                db_updates["topics_to_avoid"] = p.get("topics_to_avoid", [])

            if "cognitive_thresholds" in updates:
                ct = updates["cognitive_thresholds"]
                db_updates["deviation_threshold"] = ct.get("deviation_threshold", 0.20)
                db_updates["consecutive_trigger"] = ct.get("consecutive_trigger", 3)

            if "call_schedule" in updates:
                cs = updates["call_schedule"]
                if cs.get("preferred_time"):
                    db_updates["preferred_call_time"] = cs["preferred_time"]

            simple_map = {
                "name": "name",
                "preferred_name": "preferred_name",
                "age": "age",
                "phone_number": "phone_number",
                "medical_notes": "medical_notes",
            }
            for py_key, db_key in simple_map.items():
                if py_key in updates:
                    db_updates[db_key] = updates[py_key]

            # Also allow direct top-level keys like preferred_call_time used in step 3
            if "preferred_call_time" in updates:
                db_updates["preferred_call_time"] = updates["preferred_call_time"]

            if db_updates:
                db_updates["updated_at"] = datetime.now(UTC).isoformat()
                self.client.table("patients").update(db_updates).eq("id", patient_id).execute()

            # Handle medications update (replace all)
            if "medications" in updates:
                self.replace_medications(patient_id, updates["medications"])

            return True
        except Exception as exc:
            logger.error(f"PatientRepository.update failed for {patient_id}: {exc}")
            return False

    def replace_medications(self, patient_id: str, medications: list) -> None:
        try:
            self.client.table("medications").delete().eq("patient_id", patient_id).execute()
            for med in medications:
                # If med is a Pydantic model (dict-like) or dict
                name = med.name if hasattr(med, "name") else med.get("name", "")
                dosage = med.dosage if hasattr(med, "dosage") else med.get("dosage", "")
                schedule = med.schedule if hasattr(med, "schedule") else med.get("schedule", "")
                
                self.client.table("medications").insert({
                    "patient_id": patient_id,
                    "name": name,
                    "dosage": dosage,
                    "schedule": schedule,
                }).execute()
        except Exception as exc:
            logger.error(f"PatientRepository.replace_medications failed for {patient_id}: {exc}")

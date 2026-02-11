"""
Outbound Call Manager
Handles Clara initiating calls to patients
"""

import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class OutboundCallManager:
    """
    Manages outbound calls from Clara to patients
    Uses Twilio's Programmable Voice API
    """
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
        
        # Your server's public URL (from ngrok or production domain)
        self.server_url = os.getenv("SERVER_PUBLIC_URL", "http://localhost:8000")
    
    async def call_patient(
        self,
        patient_id: str,
        patient_phone: str,
        patient_name: str = "there"
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call to a patient
        
        Args:
            patient_id: Patient identifier
            patient_phone: Patient's phone number (E.164 format: +1234567890)
            patient_name: Patient's name for logging
            
        Returns:
            Dict with call_sid and status
        """
        if not self.account_sid or not self.auth_token:
            logger.error("Twilio credentials not configured")
            return {
                "success": False,
                "error": "Twilio credentials not configured"
            }
        
        if not self.from_number:
            logger.error("TWILIO_PHONE_NUMBER not configured")
            return {
                "success": False,
                "error": "Twilio phone number not configured"
            }
        
        try:
            # TwiML that will connect the call to our WebSocket
            twiml_url = f"{self.server_url}/voice/twiml?patient_id={patient_id}"
            
            # Make the call using Twilio API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/Calls.json",
                    auth=(self.account_sid, self.auth_token),
                    data={
                        "To": patient_phone,
                        "From": self.from_number,
                        "Url": twiml_url,
                        "Method": "GET",
                        "StatusCallback": f"{self.server_url}/voice/status",
                        "StatusCallbackEvent": "initiated ringing answered completed",
                        "StatusCallbackMethod": "POST"
                    },
                    timeout=30.0
                )
            
            if response.status_code in [200, 201]:
                data = response.json()
                call_sid = data.get("sid")
                status = data.get("status")
                
                logger.info(
                    f"Outbound call initiated to {patient_name} ({patient_phone}): "
                    f"CallSid={call_sid}, Status={status}"
                )
                
                return {
                    "success": True,
                    "call_sid": call_sid,
                    "status": status,
                    "patient_id": patient_id,
                    "patient_phone": patient_phone,
                    "message": f"Call initiated to {patient_name}"
                }
            else:
                error_message = response.text
                logger.error(f"Failed to initiate call: {response.status_code} - {error_message}")
                return {
                    "success": False,
                    "error": f"Twilio API error: {response.status_code}",
                    "details": error_message
                }
                
        except Exception as e:
            logger.error(f"Error initiating outbound call: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def schedule_daily_checkin(
        self,
        patient_id: str,
        patient_phone: str,
        patient_name: str,
        checkin_time: str = "09:00"
    ) -> Dict[str, Any]:
        """
        Schedule a daily check-in call (placeholder for scheduler integration)
        
        Args:
            patient_id: Patient identifier
            patient_phone: Patient's phone number
            patient_name: Patient's name
            checkin_time: Time to call (HH:MM format, 24-hour)
            
        Returns:
            Scheduling confirmation
        """
        logger.info(
            f"Daily check-in scheduled for {patient_name} ({patient_id}) "
            f"at {checkin_time} to {patient_phone}"
        )
        
        # TODO: Integrate with scheduler (APScheduler, Celery, or cloud scheduler)
        # For now, this is a placeholder
        
        return {
            "success": True,
            "message": f"Daily check-in scheduled for {patient_name} at {checkin_time}",
            "patient_id": patient_id,
            "checkin_time": checkin_time
        }
    
    async def call_multiple_patients(
        self,
        patients: list[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Initiate calls to multiple patients
        
        Args:
            patients: List of dicts with patient_id, phone, and name
            
        Returns:
            Summary of call attempts
        """
        results = {
            "total": len(patients),
            "successful": 0,
            "failed": 0,
            "calls": []
        }
        
        for patient in patients:
            patient_id = patient.get("patient_id")
            phone = patient.get("phone")
            name = patient.get("name", "Patient")
            
            result = await self.call_patient(patient_id, phone, name)
            
            if result.get("success"):
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            results["calls"].append({
                "patient_id": patient_id,
                "name": name,
                "phone": phone,
                "result": result
            })
        
        logger.info(
            f"Batch call completed: {results['successful']} successful, "
            f"{results['failed']} failed out of {results['total']}"
        )
        
        return results


# Global instance
outbound_manager = OutboundCallManager()

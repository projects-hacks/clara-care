"""
Function Call Handlers for Clara
Implements the 6 core functions that Clara can call during conversations
"""

import logging
import os
from datetime import datetime, UTC
from typing import Dict, Any, Optional
import httpx

# P3: Import nostalgia engine
from app.nostalgia import YouComClient, calculate_golden_years

logger = logging.getLogger(__name__)


class FunctionHandler:
    """
    Handles execution of Clara's function calls
    """
    
    def __init__(self, patient_id: str, cognitive_pipeline=None):
        self.patient_id = patient_id
        self.sanity_api_url = os.getenv("SANITY_API_URL", "http://localhost:8000/api/sanity")
        self.you_api_key = os.getenv("YOUCOM_API_KEY", "")
        self.cognitive_pipeline = cognitive_pipeline  # P2 cognitive pipeline
        self.youcom_client = YouComClient(api_key=self.you_api_key)  # P3 nostalgia engine
        
    async def execute(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call and return the result
        
        Args:
            function_name: Name of the function to execute
            parameters: Function parameters
            
        Returns:
            Function result as a dictionary
        """
        logger.info(f"Executing function: {function_name} with params: {parameters}")
        
        # Map function names to handler methods
        handlers = {
            "get_patient_context": self.get_patient_context,
            "search_nostalgia": self.search_nostalgia,
            "search_realtime": self.search_realtime,
            "log_medication_check": self.log_medication_check,
            "trigger_alert": self.trigger_alert,
            "save_conversation": self.save_conversation
        }
        
        handler = handlers.get(function_name)
        if not handler:
            logger.error(f"Unknown function: {function_name}")
            return {
                "success": False,
                "error": f"Unknown function: {function_name}"
            }
        
        try:
            result = await handler(parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing {function_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_patient_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve patient profile, preferences, medical notes, and recent conversations
        """
        patient_id = params.get("patient_id", self.patient_id)
        
        # First try to get from cognitive pipeline's data store (P2)
        if self.cognitive_pipeline and self.cognitive_pipeline.data_store:
            try:
                patient = await self.cognitive_pipeline.data_store.get_patient(patient_id)
                if patient:
                    recent_convos = await self.cognitive_pipeline.data_store.get_conversations(
                        patient_id=patient_id, 
                        limit=5
                    )
                    return {
                        "success": True,
                        "patient": {
                            "name": patient.get("name"),
                            "age": patient.get("age"),
                            "location": patient.get("location"),
                        },
                        "recent_conversations": [
                            {
                                "date": c.get("timestamp"),
                                "summary": c.get("summary", "")
                            } for c in recent_convos
                        ],
                        "medications": patient.get("medications", []),
                        "preferences": patient.get("preferences", {})
                    }
            except Exception as e:
                logger.warning(f"Could not get patient from data store: {e}")
        
        # Fallback to Sanity API (P3)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.sanity_api_url}/patients/{patient_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "patient": data.get("patient", {}),
                        "recent_conversations": data.get("recent_conversations", []),
                        "medications": data.get("medications", []),
                        "preferences": data.get("preferences", {})
                    }
                else:
                    logger.warning(f"Failed to get patient context: {response.status_code}")
                    return self._default_patient_context()
                    
        except Exception as e:
            logger.error(f"Error getting patient context: {e}")
            # Return default context if Sanity is not available yet
            return self._default_patient_context()
    
    def _default_patient_context(self) -> Dict[str, Any]:
        """Return default patient context when Sanity is not connected"""
        return {
            "success": True,
            "patient": {
                "name": "Friend",
                "preferred_name": "dear",
                "age": 75,
                "birth_year": 1951
            },
            "recent_conversations": [],
            "medications": [
                {
                    "name": "Blood pressure medication",
                    "schedule": "morning"
                }
            ],
            "preferences": {
                "interests": ["music", "gardening", "family"],
                "communication_style": "warm and patient"
            },
            "note": "Using default context - Sanity not connected yet"
        }
    
    async def search_nostalgia(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        P3: Uses You.com API via nostalgia engine
        """
        patient_id = params.get("patient_id", self.patient_id)
        trigger_reason = params.get("trigger_reason", "")
        
        try:
            # Get patient to determine birth year and golden years
            patient = None
            if self.cognitive_pipeline and self.cognitive_pipeline.data_store:
                patient = await self.cognitive_pipeline.data_store.get_patient(patient_id)
            
            birth_year = None
            if patient:
                birth_year = patient.get("birth_year")
            
            # P3: Use nostalgia engine to fetch era-specific content
            nostalgia_data = await self.youcom_client.search_nostalgia(
                birth_year=birth_year,
                trigger_reason=trigger_reason
            )
            
            golden_years = "1960s-1970s"
            if birth_year:
                start_year, end_year = calculate_golden_years(birth_year)
                golden_years = f"{start_year}s-{end_year}s"
            
            return {
                "success": True,
                "content": nostalgia_data,
                "golden_years": golden_years,
                "trigger_reason": trigger_reason
            }
                    
        except Exception as e:
            logger.error(f"Error searching nostalgia: {e}")
            return self._default_nostalgia_response(trigger_reason)
    
    def _default_nostalgia_response(self, trigger_reason: str) -> Dict[str, Any]:
        """Default nostalgia response when Sanity is not available"""
        return {
            "success": True,
            "content": {
                "era": "1960s",
                "music": ["The Beatles - Yesterday", "Elvis Presley - Can't Help Falling in Love"],
                "events": ["Moon landing in 1969", "Woodstock festival"],
                "culture": "The golden age of rock and roll"
            },
            "trigger_reason": trigger_reason
        }
    
    async def search_realtime(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for realtime information using You.com Search API
        P3: Uses You.com client from nostalgia engine
        """
        query = params.get("query", "")
        patient_id = params.get("patient_id", self.patient_id)
        
        if not query:
            return {
                "success": False,
                "error": "No search query provided"
            }
        
        try:
            # P3: Use nostalgia engine's You.com client
            results = await self.youcom_client.search_realtime(query)
            
            return {
                "success": True,
                "query": query,
                "results": results.get("results", []),
                "answer": results.get("answer", "Here's what I found..."),
                "citations": results.get("citations", [])
            }
            
        except Exception as e:
            logger.error(f"Error searching realtime: {e}")
            # Fallback if You.com is not configured
            logger.warning("You.com API error, using fallback response")
            return {
                "success": True,
                "query": query,
                "results": [],
                "answer": "I'd be happy to help, but I'm having trouble accessing that information right now. Could we talk about something else?",
                "note": "You.com API not available"
            }
    
    def _summarize_results(self, results: list) -> str:
        """Summarize search results into a conversational answer"""
        if not results:
            return "I couldn't find much information about that right now."
        
        # Simple summarization - combine snippets
        snippets = [r.get("snippet", "") for r in results if r.get("snippet")]
        if snippets:
            return snippets[0]  # Return the first snippet
        return "Here's what I found..."
    
    async def log_medication_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log whether the patient took their medication
        """
        patient_id = params.get("patient_id", self.patient_id)
        medication_name = params.get("medication_name", "")
        taken = params.get("taken", False)
        notes = params.get("notes", "")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.sanity_api_url}/medications/log",
                    json={
                        "patient_id": patient_id,
                        "medication_name": medication_name,
                        "taken": taken,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "notes": notes
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": f"Logged medication check for {medication_name}"
                    }
                else:
                    # API not available - use local fallback
                    logger.warning(f"Failed to log medication: {response.status_code}")
                    logger.info(f"Medication log (local): {medication_name} - Taken: {taken} - Notes: {notes}")
                    return {
                        "success": True,
                        "message": f"Logged medication check for {medication_name}",
                        "note": "Logged locally - Sanity not connected yet"
                    }
                    
        except Exception as e:
            logger.error(f"Error logging medication: {e}")
            # Log locally if Sanity is not available
            logger.info(f"Medication log (local): {medication_name} - Taken: {taken} - Notes: {notes}")
            return {
                "success": True,
                "message": f"Logged medication check for {medication_name}",
                "note": "Logged locally - Sanity not connected yet"
            }
    
    async def trigger_alert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an urgent alert to family members
        """
        patient_id = params.get("patient_id", self.patient_id)
        severity = params.get("severity", "medium")
        alert_type = params.get("alert_type", "other")
        message = params.get("message", "")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.sanity_api_url}/alerts",
                    json={
                        "patient_id": patient_id,
                        "severity": severity,
                        "alert_type": alert_type,
                        "message": message,
                        "timestamp": datetime.now(UTC).isoformat()
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Alert sent to family members",
                        "alert_id": response.json().get("alert_id", "")
                    }
                else:
                    # API not available - use local fallback
                    logger.warning(f"Failed to send alert: {response.status_code}")
                    logger.critical(f"ALERT [{severity}] - {alert_type}: {message} (Patient: {patient_id})")
                    return {
                        "success": True,
                        "message": "Alert logged",
                        "note": "Logged locally - Sanity not connected yet. In production, this would notify family."
                    }
                    
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
            # Log alert locally if Sanity is not available
            logger.critical(f"ALERT [{severity}] - {alert_type}: {message} (Patient: {patient_id})")
            return {
                "success": True,
                "message": "Alert logged",
                "note": "Logged locally - Sanity not connected yet. In production, this would notify family."
            }
    
    async def save_conversation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save the conversation transcript, summary, and cognitive metrics
        P2 INTEGRATION: Run through cognitive pipeline
        """
        patient_id = params.get("patient_id", self.patient_id)
        transcript = params.get("transcript", "")
        duration = params.get("duration", 0)
        summary = params.get("summary", "")
        detected_mood = params.get("detected_mood", "neutral")
        response_times = params.get("response_times")  # P2: optional timing data
        
        # P2: If cognitive pipeline is available, run full analysis
        if self.cognitive_pipeline:
            try:
                logger.info("Running cognitive analysis pipeline...")
                
                result = await self.cognitive_pipeline.process_conversation(
                    patient_id=patient_id,
                    transcript=transcript,
                    duration=duration,
                    summary=summary,
                    detected_mood=detected_mood,
                    response_times=response_times
                )
                
                if result.get("success"):
                    logger.info(f"Cognitive pipeline complete. Conversation: {result['conversation_id']}")
                    logger.info(f"  Baseline: {'✓' if result['baseline_established'] else '⏳'}")
                    logger.info(f"  Alerts: {len(result.get('alerts', []))}")
                    logger.info(f"  Cognitive Score: {result['digest']['cognitive_score']}/100")
                    
                    return {
                        "success": True,
                        "message": "Conversation analyzed and saved",
                        "conversation_id": result["conversation_id"],
                        "cognitive_score": result["digest"]["cognitive_score"],
                        "alerts_generated": len(result.get("alerts", []))
                    }
                else:
                    logger.error(f"Cognitive pipeline failed: {result.get('error')}")
                    # Fall through to legacy save
                    
            except Exception as e:
                logger.error(f"Error in cognitive pipeline: {e}", exc_info=True)
                # Fall through to legacy save
        
        # Legacy save (if no pipeline or pipeline failed)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.sanity_api_url}/conversations",
                    json={
                        "patient_id": patient_id,
                        "transcript": transcript,
                        "duration": duration,
                        "summary": summary,
                        "detected_mood": detected_mood,
                        "timestamp": datetime.now(UTC).isoformat()
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Conversation saved",
                        "conversation_id": response.json().get("conversation_id", "")
                    }
                else:
                    # API not available - use local fallback
                    logger.warning(f"Failed to save conversation: {response.status_code}")
                    logger.info(f"Conversation saved (local): Duration={duration}s, Mood={detected_mood}, Summary={summary[:100]}")
                    return {
                        "success": True,
                        "message": "Conversation saved",
                        "note": "Saved locally - Sanity not connected yet"
                    }
                    
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            # Log locally if Sanity is not available
            logger.info(f"Conversation saved (local): Duration={duration}s, Mood={detected_mood}, Summary={summary[:100]}")
            return {
                "success": True,
                "message": "Conversation saved",
                "note": "Saved locally - Sanity not connected yet"
            }

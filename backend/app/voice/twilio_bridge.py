"""
Twilio WebSocket Bridge
Connects incoming Twilio calls to Deepgram Voice Agent
"""

import asyncio
import base64
import json
import logging
from datetime import datetime, UTC
from typing import Optional, Dict
from fastapi import WebSocket, WebSocketDisconnect

from .agent import session_manager, DeepgramVoiceAgent

logger = logging.getLogger(__name__)


class TwilioAudioStream:
    """
    Handles Twilio Media Stream protocol
    Converts between Twilio's format and raw audio for Deepgram
    """
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.stream_sid: Optional[str] = None
        self.call_sid: Optional[str] = None
        
    async def send_audio(self, audio_data: bytes):
        """
        Send audio to Twilio (from Deepgram/Clara)
        
        Args:
            audio_data: Raw mulaw audio bytes
        """
        if not self.stream_sid:
            logger.warning("Cannot send audio - stream not initialized")
            return
            
        # Encode audio to base64 for Twilio
        payload = base64.b64encode(audio_data).decode('utf-8')
        
        message = {
            "event": "media",
            "streamSid": self.stream_sid,
            "media": {
                "payload": payload
            }
        }
        
        await self.websocket.send_json(message)
    
    async def send_mark(self, mark_name: str):
        """Send a mark event to Twilio"""
        if not self.stream_sid:
            return
            
        message = {
            "event": "mark",
            "streamSid": self.stream_sid,
            "mark": {
                "name": mark_name
            }
        }
        
        await self.websocket.send_json(message)
    
    async def clear_stream(self):
        """Clear the outbound media stream"""
        if not self.stream_sid:
            return
            
        message = {
            "event": "clear",
            "streamSid": self.stream_sid
        }
        
        await self.websocket.send_json(message)


class TwilioCallSession:
    """
    Manages a single Twilio call session
    Bridges Twilio WebSocket to Deepgram Voice Agent
    """
    
    def __init__(
        self,
        twilio_ws: WebSocket,
        patient_id: str,
        call_sid: str,
        cognitive_pipeline=None
    ):
        self.twilio_ws = twilio_ws
        self.patient_id = patient_id
        self.call_sid = call_sid
        self.cognitive_pipeline = cognitive_pipeline
        
        self.twilio_stream = TwilioAudioStream(twilio_ws)
        self.deepgram_agent: Optional[DeepgramVoiceAgent] = None
        
        self.is_active = False
        self.conversation_transcript: list = []
        self.conversation_saved = False  # Track if AI already saved via function call
        self.call_start_time: Optional[datetime] = None
        
    async def start(self) -> bool:
        """
        Initialize the call session
        Connect to Deepgram and set up audio bridging
        """
        try:
            self.call_start_time = datetime.now(UTC)
            
            # Create Deepgram agent session with cognitive pipeline
            self.deepgram_agent = await session_manager.create_session(
                session_id=self.call_sid,
                patient_id=self.patient_id,
                cognitive_pipeline=self.cognitive_pipeline
            )
            
            # Set up callbacks for Deepgram output
            self.deepgram_agent.set_callbacks(
                on_audio_output=self._on_deepgram_audio,
                on_transcript=self._on_transcript,
                on_error=self._on_error
            )
            
            self.is_active = True
            logger.info(
                f"[CALL_START] CallSid={self.call_sid} patient={self.patient_id} "
                f"pipeline={'enabled' if self.cognitive_pipeline else 'disabled'}"
            )
            return True
            
        except Exception as e:
            logger.error(f"[CALL_START_FAILED] CallSid={self.call_sid} error={e}", exc_info=True)
            return False
    
    async def handle_twilio_message(self, message: Dict):
        """
        Process incoming messages from Twilio
        
        Args:
            message: Twilio WebSocket message
        """
        event = message.get("event")
        
        if event == "start":
            await self._handle_start(message)
            
        elif event == "media":
            await self._handle_media(message)
            
        elif event == "mark":
            await self._handle_mark(message)
            
        elif event == "stop":
            await self._handle_stop(message)
            
        else:
            logger.debug(f"Unknown Twilio event: {event}")
    
    async def _handle_start(self, message: Dict):
        """Handle Twilio stream start event"""
        start_data = message.get("start", {})
        self.twilio_stream.stream_sid = start_data.get("streamSid")
        self.twilio_stream.call_sid = start_data.get("callSid")
        
        logger.info(f"Twilio stream started: {self.twilio_stream.stream_sid}")
    
    async def _handle_media(self, message: Dict):
        """
        Handle incoming audio from Twilio
        Forward to Deepgram
        """
        if not self.deepgram_agent or not self.is_active:
            return
            
        media = message.get("media", {})
        payload = media.get("payload", "")
        
        if payload:
            # Decode base64 audio from Twilio
            audio_data = base64.b64decode(payload)
            
            # Send to Deepgram
            await self.deepgram_agent.send_audio(audio_data)
    
    async def _handle_mark(self, message: Dict):
        """Handle Twilio mark event"""
        mark = message.get("mark", {})
        logger.debug(f"Twilio mark received: {mark.get('name')}")
    
    async def _handle_stop(self, message: Dict):
        """Handle Twilio stream stop event"""
        logger.info(f"Twilio stream stopped: {self.twilio_stream.stream_sid}")
        await self.end()
    
    async def _on_deepgram_audio(self, audio_data: bytes):
        """
        Callback: Deepgram sent audio (Clara speaking)
        Forward to Twilio
        """
        await self.twilio_stream.send_audio(audio_data)
    
    async def _on_transcript(self, speaker: str, text: str):
        """
        Callback: Transcript available
        Store for conversation history
        """
        self.conversation_transcript.append({
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.info(f"Transcript [{speaker}]: {text}")
    
    async def _on_error(self, error_message: str):
        """
        Callback: Error occurred in Deepgram
        """
        logger.error(f"Deepgram error in call {self.call_sid}: {error_message}")
    
    async def end(self):
        """
        End the call session.
        Runs LLM post-call analysis, safety detection, cognitive pipeline, and cleanup.
        """
        if not self.is_active:
            return
            
        self.is_active = False
        
        # Calculate call duration
        call_duration_sec = 0
        if self.call_start_time:
            call_duration_sec = int((datetime.now(UTC) - self.call_start_time).total_seconds())
        
        total_turns = len(self.conversation_transcript)
        patient_turns = sum(1 for t in self.conversation_transcript if t.get('speaker', '').lower() != 'clara')
        agent_turns = total_turns - patient_turns
        
        logger.info(
            f"[CALL_ENDING] CallSid={self.call_sid} duration={call_duration_sec}s "
            f"total_turns={total_turns} patient_turns={patient_turns} agent_turns={agent_turns}"
        )
        
        # Save conversation transcript before cleanup
        pipeline_result = None
        if self.conversation_transcript and self.deepgram_agent and not self.conversation_saved:
            try:
                transcript_text = "\n".join(
                    f"{t['speaker']}: {t['text']}" 
                    for t in self.conversation_transcript
                )
                
                logger.info(
                    f"[TRANSCRIPT_SAVE] CallSid={self.call_sid} "
                    f"transcript_length={len(transcript_text)} chars"
                )
                
                # ── LLM Post-Call Analysis ──────────────────────────────────
                from app.cognitive.post_call_analyzer import analyze_transcript

                # Fetch this patient's medication list from the data store so
                # the analyzer scans for their specific meds, not a hardcoded set.
                patient_meds: list[str] = []
                try:
                    if (
                        self.deepgram_agent
                        and self.deepgram_agent.function_handler
                        and hasattr(self.deepgram_agent.function_handler, "cognitive_pipeline")
                    ):
                        data_store = self.deepgram_agent.function_handler.cognitive_pipeline.data_store
                        patient = await data_store.get_patient(self.patient_id)
                        if patient:
                            patient_meds = [
                                m["name"].lower()
                                for m in patient.get("medications", [])
                                if isinstance(m, dict) and m.get("name")
                            ]
                            logger.info(
                                f"[MED_CONTEXT] CallSid={self.call_sid} "
                                f"tracking {len(patient_meds)} meds for patient {self.patient_id}: "
                                f"{patient_meds}"
                            )
                except Exception as med_exc:
                    logger.warning(
                        f"[MED_CONTEXT] Could not fetch patient meds for {self.patient_id}: {med_exc} "
                        f"— medication tracking will be skipped this call."
                    )

                analysis = await analyze_transcript(transcript_text, medications=patient_meds)
                summary = analysis.get("summary", "Check-in call.")
                detected_mood = analysis.get("mood", "neutral")
                
                logger.info(
                    f"[LLM_ANALYSIS] CallSid={self.call_sid} mood={detected_mood} "
                    f"topics={analysis.get('topics', [])} "
                    f"safety_flags={len(analysis.get('safety_flags', []))}"
                )
                
                # ── Safety + Connection + Memory Alert Auto-Generation ─────────
                safety_flags = analysis.get("safety_flags", [])
                desire_to_connect = analysis.get("desire_to_connect", False)
                memory_flags = analysis.get("memory_inconsistency", [])
                
                if safety_flags or desire_to_connect:
                    await self._create_safety_alerts(safety_flags, analysis)
                
                # Memory inconsistency alert (YES → UNSURE → NO pattern)
                if memory_flags and self.deepgram_agent and self.deepgram_agent.function_handler:
                    logger.warning(
                        f"[MEMORY_ALERT] CallSid={self.call_sid} "
                        f"inconsistency={memory_flags[0][:100]}"
                    )
                    await self.deepgram_agent.function_handler.execute(
                        "trigger_alert",
                        {
                            "patient_id": self.patient_id,
                            "severity": "medium",
                            "alert_type": "cognitive_decline",
                            "message": (
                                "During today's call, she gave conflicting answers to the same question — "
                                "first agreeing, then expressing doubt or saying the opposite. "
                                "This kind of inconsistency can sometimes be an early sign of short-term "
                                "memory difficulty and is worth watching over the coming conversations."
                            )
                        }
                    )
                
                # ── Save via cognitive pipeline ─────────────────────────────
                pipeline_result = await self.deepgram_agent.function_handler.execute(
                    "save_conversation",
                    {
                        "patient_id": self.patient_id,
                        "transcript": transcript_text,
                        "duration": call_duration_sec or len(self.conversation_transcript) * 5,
                        "summary": summary,
                        "detected_mood": detected_mood,
                        "analysis": analysis
                    }
                )
                
                # NOTE: Low-coherence alerts are now handled by the pipeline's
                # check_and_alert with proper dedup. Removed redundant auto-alert
                # that was creating duplicate coherence_drop alerts.
                
                if pipeline_result and pipeline_result.get("success"):
                    logger.info(
                        f"[PIPELINE_COMPLETE] CallSid={self.call_sid} "
                        f"conversation_id={pipeline_result.get('conversation_id')} "
                        f"cognitive_score={pipeline_result.get('cognitive_score')} "
                        f"alerts={pipeline_result.get('alerts_generated', 0)}"
                    )
                else:
                    logger.warning(
                        f"[PIPELINE_INCOMPLETE] CallSid={self.call_sid} "
                        f"result={pipeline_result}"
                    )
                    
            except Exception as e:
                logger.error(f"[TRANSCRIPT_SAVE_FAILED] CallSid={self.call_sid} error={e}", exc_info=True)
        else:
            logger.warning(
                f"[NO_TRANSCRIPT] CallSid={self.call_sid} "
                f"transcript_empty={not self.conversation_transcript} "
                f"agent_exists={self.deepgram_agent is not None}"
            )
        
        # Close Deepgram session
        if self.call_sid:
            await session_manager.close_session(self.call_sid)
        
        logger.info(
            f"[CALL_END] CallSid={self.call_sid} duration={call_duration_sec}s "
            f"turns={total_turns} pipeline={'success' if pipeline_result and pipeline_result.get('success') else 'skipped' if self.conversation_saved else 'failed'}"
        )
    
    async def _create_safety_alerts(self, safety_flags: list, analysis: dict):
        """
        Create automatic alerts when safety flags or connection desires are detected.
        """
        try:
            if not (self.deepgram_agent and self.deepgram_agent.function_handler):
                logger.error("[SAFETY] Cannot create alerts — no function handler")
                return
            
            # 1. Handle Safety Flags (High Severity)
            if safety_flags:
                flag_summary = "; ".join(safety_flags[:3])
                action_items = analysis.get("action_items", [])
                action_text = (
                    " Suggested next steps: " + "; ".join(action_items)
                    if action_items else ""
                )
                
                message = (
                    f"She said something during today's call that is a cause for concern: {flag_summary}. "
                    "This came up during an otherwise normal conversation and may need your immediate attention."
                    f"{action_text}"
                )
                
                logger.warning(
                    f"[SAFETY_ALERT] CallSid={self.call_sid} patient={self.patient_id} "
                    f"flags={len(safety_flags)}: {flag_summary}"
                )
                
                await self.deepgram_agent.function_handler.execute(
                    "trigger_alert",
                    {
                        "patient_id": self.patient_id,
                        "severity": "high",
                        "alert_type": "distress",
                        "related_metrics": ["safety_flags"],
                        "description": message
                    }
                )
                logger.info(f"[SAFETY_ALERT_CREATED] CallSid={self.call_sid}")

            # 2. Handle Desire to Connect (Medium Severity Opportunity)
            if analysis.get("desire_to_connect"):
                context = analysis.get("connection_context", "she mentioned missing family")
                message = (
                    f"She seemed to be longing for more connection during today's call — {context}. "
                    "This is a good moment to reach out with a call or visit. "
                    "Even a short check-in can make a big difference."
                )
                
                logger.info(f"[CONNECTION_ALERT] CallSid={self.call_sid} context={context}")
                
                await self.deepgram_agent.function_handler.execute(
                    "trigger_alert",
                    {
                        "patient_id": self.patient_id,
                        "severity": "medium",
                        "alert_type": "social_connection",
                        "related_metrics": ["loneliness_indicators"],
                        "description": message
                    }
                )
                logger.info(f"[CONNECTION_ALERT_CREATED] CallSid={self.call_sid}")
            
        except Exception as e:
            logger.error(f"[ALERT_CREATION_FAILED] CallSid={self.call_sid} error={e}")


class TwilioBridge:
    """
    Main bridge between Twilio and Deepgram
    Manages WebSocket connections and call routing
    """
    
    def __init__(self):
        self.active_calls: Dict[str, TwilioCallSession] = {}
        self.cognitive_pipeline = None  # Set by main.py during startup
    
    def set_cognitive_pipeline(self, pipeline):
        """Set the cognitive pipeline (called during app startup)"""
        self.cognitive_pipeline = pipeline
    
    async def handle_call(
        self,
        websocket: WebSocket,
        patient_id: str
    ):
        """
        Handle an incoming Twilio call
        
        Args:
            websocket: Twilio Media Stream WebSocket
            patient_id: Patient identifier (from call routing)
        """
        await websocket.accept()
        logger.info(f"Accepted Twilio WebSocket for patient {patient_id}")
        
        call_session: Optional[TwilioCallSession] = None
        
        try:
            # Wait for initial messages to get call_sid
            initial_message = await websocket.receive_json()
            
            # Extract call_sid from start event
            if initial_message.get("event") == "connected":
                logger.debug("Twilio connected")
                # Wait for actual start event
                initial_message = await websocket.receive_json()
            
            if initial_message.get("event") == "start":
                start_data = initial_message.get("start", {})
                call_sid = start_data.get("callSid")
                
                if not call_sid:
                    logger.error("No callSid in start event")
                    await websocket.close()
                    return
                
                # Extract patient_id from Twilio <Parameter> (delivered in customParameters)
                custom_params = start_data.get("customParameters", {})
                if custom_params.get("patient_id"):
                    patient_id = custom_params["patient_id"]
                    logger.info(f"Got patient_id from Twilio customParameters: {patient_id}")
                
                # Create call session with cognitive pipeline
                call_session = TwilioCallSession(
                    twilio_ws=websocket,
                    patient_id=patient_id,
                    call_sid=call_sid,
                    cognitive_pipeline=self.cognitive_pipeline
                )
                
                self.active_calls[call_sid] = call_session
                
                # Start the session (connect to Deepgram)
                success = await call_session.start()
                
                if not success:
                    logger.error(f"Failed to start call session {call_sid}")
                    await websocket.close()
                    return
                
                # Process the start message
                await call_session.handle_twilio_message(initial_message)
                
                # Handle incoming messages
                while call_session.is_active:
                    try:
                        message = await websocket.receive_json()
                        await call_session.handle_twilio_message(message)
                        
                    except WebSocketDisconnect:
                        logger.info(f"Twilio WebSocket disconnected for call {call_sid}")
                        break
                        
            else:
                logger.warning(f"Expected start event, got: {initial_message.get('event')}")
                await websocket.close()
                
        except WebSocketDisconnect:
            logger.info("Twilio WebSocket disconnected")
            
        except Exception as e:
            logger.error(f"Error handling Twilio call: {e}", exc_info=True)
            
        finally:
            # Clean up
            if call_session:
                await call_session.end()
                if call_session.call_sid in self.active_calls:
                    del self.active_calls[call_session.call_sid]
    
    def get_active_call_count(self) -> int:
        """Get number of active calls"""
        return len(self.active_calls)
    
    async def end_call(self, call_sid: str):
        """Manually end a call"""
        if call_sid in self.active_calls:
            await self.active_calls[call_sid].end()
            del self.active_calls[call_sid]


# Global bridge instance
twilio_bridge = TwilioBridge()

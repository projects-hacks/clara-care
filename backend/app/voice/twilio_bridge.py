"""
Twilio WebSocket Bridge
Connects incoming Twilio calls to Deepgram Voice Agent
"""

import asyncio
import base64
import json
import logging
from datetime import datetime
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
        call_sid: str
    ):
        self.twilio_ws = twilio_ws
        self.patient_id = patient_id
        self.call_sid = call_sid
        
        self.twilio_stream = TwilioAudioStream(twilio_ws)
        self.deepgram_agent: Optional[DeepgramVoiceAgent] = None
        
        self.is_active = False
        self.conversation_transcript: list = []
        
    async def start(self) -> bool:
        """
        Initialize the call session
        Connect to Deepgram and set up audio bridging
        """
        try:
            # Create Deepgram agent session
            self.deepgram_agent = await session_manager.create_session(
                session_id=self.call_sid,
                patient_id=self.patient_id
            )
            
            # Set up callbacks for Deepgram output
            self.deepgram_agent.set_callbacks(
                on_audio_output=self._on_deepgram_audio,
                on_transcript=self._on_transcript,
                on_error=self._on_error
            )
            
            self.is_active = True
            logger.info(f"Started call session {self.call_sid} for patient {self.patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start call session: {e}")
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
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Transcript [{speaker}]: {text}")
    
    async def _on_error(self, error_message: str):
        """
        Callback: Error occurred in Deepgram
        """
        logger.error(f"Deepgram error in call {self.call_sid}: {error_message}")
    
    async def end(self):
        """
        End the call session
        Clean up resources
        """
        if not self.is_active:
            return
            
        self.is_active = False
        
        # Save conversation transcript before cleanup
        if self.conversation_transcript and self.deepgram_agent:
            try:
                transcript_text = "\n".join(
                    f"{t['speaker']}: {t['text']}" 
                    for t in self.conversation_transcript
                )
                await self.deepgram_agent.function_handler.execute(
                    "save_conversation",
                    {
                        "patient_id": self.patient_id,
                        "transcript": transcript_text,
                        "duration": len(self.conversation_transcript) * 5,  # Approximate
                        "summary": f"Call with {len(self.conversation_transcript)} exchanges",
                        "detected_mood": "neutral"
                    }
                )
                logger.info(f"Saved conversation transcript for call {self.call_sid}")
            except Exception as e:
                logger.error(f"Failed to save conversation: {e}")
        
        # Close Deepgram session
        if self.call_sid:
            await session_manager.close_session(self.call_sid)
        
        logger.info(f"Ended call session {self.call_sid}")


class TwilioBridge:
    """
    Main bridge between Twilio and Deepgram
    Manages WebSocket connections and call routing
    """
    
    def __init__(self):
        self.active_calls: Dict[str, TwilioCallSession] = {}
    
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
                
                # Create call session
                call_session = TwilioCallSession(
                    twilio_ws=websocket,
                    patient_id=patient_id,
                    call_sid=call_sid
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

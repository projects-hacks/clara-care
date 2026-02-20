"""
Deepgram Voice Agent WebSocket Handler
Manages bi-directional audio streaming and function call handling
"""

import asyncio
import json
import logging
import os
from typing import Optional, Callable, Dict, Any

import websockets
from websockets.client import WebSocketClientProtocol

from .persona import get_function_definitions, get_full_prompt, get_personalized_greeting, build_patient_context_prompt
from .functions import FunctionHandler

logger = logging.getLogger(__name__)


class DeepgramVoiceAgent:
    """
    Manages WebSocket connection to Deepgram Voice Agent API
    Handles audio streaming and function calls
    """
    
    def __init__(self, patient_id: str, cognitive_pipeline=None, data_store=None):
        self.patient_id = patient_id
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.deepgram_ws: Optional[WebSocketClientProtocol] = None
        self.is_connected = False
        self.function_handler = FunctionHandler(patient_id, cognitive_pipeline)
        self.data_store = data_store
        self._listen_task: Optional[asyncio.Task] = None
        
        # Callbacks for audio output
        self.on_audio_output: Optional[Callable[[bytes], None]] = None
        self.on_transcript: Optional[Callable[[str, str], None]] = None  # (speaker, text)
        self.on_error: Optional[Callable[[str], None]] = None
        
    async def connect(self) -> bool:
        """
        Establish WebSocket connection to Deepgram Voice Agent API.
        Fetches patient data first so the prompt + greeting are personalized
        BEFORE the agent starts speaking (avoids InjectAgentMessage race).
        """
        if not self.deepgram_api_key:
            logger.error("DEEPGRAM_API_KEY not found in environment")
            return False
            
        try:
            # 1. Fetch patient data BEFORE connecting so we can embed it in the prompt
            patient = None
            recent_convos = []
            try:
                data_store = self.data_store
                if not data_store and self.function_handler and self.function_handler.cognitive_pipeline:
                    data_store = self.function_handler.cognitive_pipeline.data_store
                
                if data_store:
                    patient = await data_store.get_patient(self.patient_id)
                    if patient:
                        recent_convos = await data_store.get_conversations(
                            patient_id=self.patient_id, limit=3
                        )
                        logger.info(f"Fetched patient context for {patient.get('preferred_name', self.patient_id)} ({len(recent_convos)} recent convos)")
                    else:
                        logger.warning(f"Patient {self.patient_id} not found — using generic prompt")
                else:
                    logger.warning("No data store available — using generic prompt")
            except Exception as e:
                logger.error(f"Error fetching patient data: {e} — using generic prompt")
            
            # 2. Build personalized prompt + greeting
            full_prompt = get_full_prompt(patient, recent_convos)
            greeting = get_personalized_greeting(patient)
            
            # 3. Connect to Deepgram
            url = "wss://agent.deepgram.com/v1/agent/converse"
            headers = {"Authorization": f"Token {self.deepgram_api_key}"}
            
            logger.info(f"Connecting to Deepgram Voice Agent for patient {self.patient_id}")
            self.deepgram_ws = await websockets.connect(url, extra_headers=headers)
            
            # 4. Send Settings with the personalized prompt + greeting baked in
            await self._send_config(full_prompt, greeting)
            
            self.is_connected = True
            logger.info("Successfully connected to Deepgram Voice Agent")
            
            # Start listening for messages from Deepgram
            self._listen_task = asyncio.create_task(self._listen_to_deepgram())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Deepgram: {e}")
            if self.on_error:
                await self.on_error(f"Connection failed: {str(e)}")
            return False
    
    async def _send_config(self, full_prompt: str, greeting: str):
        """Send V1 Settings to Deepgram with personalized prompt + greeting."""
        config = {
            "type": "Settings",
            "audio": {
                "input": {
                    "encoding": "mulaw",
                    "sample_rate": 8000
                },
                "output": {
                    "encoding": "mulaw",
                    "sample_rate": 8000,
                    "container": "none"
                }
            },
            "agent": {
                "language": "en",
                "listen": {
                    "provider": {
                        "type": "deepgram",
                        "model": "nova-3"
                    }
                },
                "think": {
                    "provider": {
                        "type": "open_ai",
                        "model": "gpt-4o-mini",
                        "temperature": 0.7
                    },
                    "prompt": full_prompt,
                    "functions": get_function_definitions()
                },
                "speak": {
                    "provider": {
                        "type": "deepgram",
                        "model": "aura-2-thalia-en"
                    }
                },
                "greeting": greeting
            }
        }
        
        await self.deepgram_ws.send(json.dumps(config))
        logger.info(f"Sent V1 Settings — prompt={len(full_prompt)} chars, greeting='{greeting}'")
    
    async def _inject_patient_context(self):
        """
        Fetch patient data and inject it as a context message into Deepgram
        so Clara begins the conversation already personalized.
        """
        try:
            data_store = self.data_store
            if not data_store:
                # Try to get from function handler's cognitive pipeline
                if (self.function_handler and 
                    self.function_handler.cognitive_pipeline and 
                    self.function_handler.cognitive_pipeline.data_store):
                    data_store = self.function_handler.cognitive_pipeline.data_store
            
            if not data_store:
                logger.warning("No data store available — skipping patient context injection")
                return
            
            patient = await data_store.get_patient(self.patient_id)
            if not patient:
                logger.warning(f"Patient {self.patient_id} not found — skipping context injection")
                return
            
            recent_convos = await data_store.get_conversations(
                patient_id=self.patient_id, limit=3
            )
            
            context_text = build_patient_context_prompt(patient, recent_convos)
            
            # Deepgram V1: InjectAgentMessage uses "content" instead of "message"
            inject_msg = {
                "type": "InjectAgentMessage",
                "content": context_text
            }
            
            await self.deepgram_ws.send(json.dumps(inject_msg))
            logger.info(
                f"Injected patient context for {patient.get('preferred_name', patient.get('name', self.patient_id))} "
                f"({len(context_text)} chars, {len(recent_convos)} recent convos)"
            )
            
        except Exception as e:
            logger.error(f"Error injecting patient context: {e}")
            # Non-fatal — Clara will fall back to calling get_patient_context
    
    async def _listen_to_deepgram(self):
        """
        Listen for messages from Deepgram (audio, transcripts, function calls)
        """
        try:
            async for message in self.deepgram_ws:
                if isinstance(message, bytes):
                    # Audio output from Clara
                    if self.on_audio_output:
                        await self.on_audio_output(message)
                else:
                    # JSON message (transcript, function call, etc.)
                    await self._handle_json_message(json.loads(message))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Deepgram WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error listening to Deepgram: {e}")
            if self.on_error:
                await self.on_error(f"Listening error: {str(e)}")
            self.is_connected = False
    
    async def _handle_json_message(self, message: Dict[str, Any]):
        """Handle JSON messages from Deepgram"""
        msg_type = message.get("type")
        
        if msg_type == "UserStartedSpeaking":
            logger.debug("User started speaking")
            
        elif msg_type == "UserStoppedSpeaking":
            logger.debug("User stopped speaking")
            
        elif msg_type == "AgentStartedSpeaking":
            logger.debug("Agent started speaking")
            
        elif msg_type == "AgentStoppedSpeaking":
            logger.debug("Agent stopped speaking")
            
        elif msg_type == "Transcript":
            # Conversation transcript
            speaker = message.get("speaker", "unknown")
            text = message.get("text", "")
            logger.info(f"Transcript - {speaker}: {text}")
            
            if self.on_transcript:
                await self.on_transcript(speaker, text)
                
        elif msg_type == "FunctionCallRequest":
            # Clara wants to call a function
            await self._handle_function_call(message)
            
        elif msg_type == "ConversationText":
            # V1: This is how transcripts are delivered — capture them!
            role = message.get("role", "unknown")
            content = message.get("content", "")
            # Map Deepgram roles to our speaker labels
            speaker = "Clara" if role == "assistant" else "Patient"
            if content:
                logger.info(f"ConversationText [{speaker}]: {content}")
                if self.on_transcript:
                    await self.on_transcript(speaker, content)
            
        elif msg_type == "Metadata":
            # Metadata about the agent
            logger.debug(f"Metadata: {message}")
            
        elif msg_type == "AgentThinking":
            # V1: Agent is processing internally
            logger.debug(f"Agent thinking: {message.get('content', '')}")
            
        elif msg_type == "AgentAudioDone":
            # V1: Agent finished sending audio
            logger.debug("Agent audio done")
            
        elif msg_type == "SettingsApplied":
            logger.info("Deepgram V1 Settings applied successfully")
            
        elif msg_type == "Welcome":
            request_id = message.get("request_id", "")
            logger.info(f"Deepgram Voice Agent connected, request_id={request_id}")
            
        elif msg_type == "Warning":
            logger.warning(f"Deepgram warning: {message.get('description', '')} (code={message.get('code', '')})")
            
        elif msg_type == "Error":
            # V1: Error uses "description" instead of "message"
            error_msg = message.get("description", message.get("message", "Unknown error"))
            error_code = message.get("code", "")
            logger.error(f"Deepgram error: {error_msg} (code={error_code})")
            if self.on_error:
                await self.on_error(error_msg)
        else:
            logger.debug(f"Unhandled message type: {msg_type} — {message}")
    
    async def _handle_function_call(self, message: Dict[str, Any]):
        """
        Handle V1 FunctionCallRequest from Clara.
        V1 format uses a "functions" array with id/name/arguments/client_side.
        """
        functions = message.get("functions", [])
        
        for func in functions:
            # Only handle client-side functions
            if not func.get("client_side", True):
                logger.debug(f"Skipping server-side function: {func.get('name')}")
                continue
            
            func_id = func.get("id")
            function_name = func.get("name")
            # V1: arguments is a JSON *string*, not an object
            raw_args = func.get("arguments", "{}")
            try:
                input_data = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except json.JSONDecodeError:
                input_data = {}
            
            logger.info(f"[FUNC_CALL] function={function_name} params={input_data}")
            
            try:
                # Execute the function
                result = await self.function_handler.execute(function_name, input_data)
                
                # V1 FunctionCallResponse: id, name, content (JSON string)
                response = {
                    "type": "FunctionCallResponse",
                    "id": func_id,
                    "name": function_name,
                    "content": json.dumps(result)
                }
                
                await self.deepgram_ws.send(json.dumps(response))
                logger.info(f"[FUNC_RESULT] function={function_name} result_keys={list(result.keys()) if isinstance(result, dict) else 'non-dict'}")
                
            except Exception as e:
                logger.error(f"Error executing function {function_name}: {e}")
                
                # Send error response in V1 format
                error_response = {
                    "type": "FunctionCallResponse",
                    "id": func_id,
                    "name": function_name,
                    "content": json.dumps({
                        "error": str(e),
                        "success": False
                    })
                }
                
                await self.deepgram_ws.send(json.dumps(error_response))
    
    async def send_audio(self, audio_data: bytes):
        """
        Send audio data to Deepgram (from Twilio/phone call)
        """
        if not self.is_connected or not self.deepgram_ws:
            logger.warning("Not connected to Deepgram, cannot send audio")
            return
            
        try:
            await self.deepgram_ws.send(audio_data)
        except Exception as e:
            logger.error(f"Error sending audio to Deepgram: {e}")
            if self.on_error:
                await self.on_error(f"Audio send error: {str(e)}")
    
    async def close(self):
        """Close the Deepgram WebSocket connection and cancel background tasks"""
        # Cancel the listener task first
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None
        
        if self.deepgram_ws:
            try:
                await self.deepgram_ws.close()
                logger.info("Deepgram WebSocket closed")
            except Exception as e:
                logger.error(f"Error closing Deepgram WebSocket: {e}")
            finally:
                self.is_connected = False
                self.deepgram_ws = None
    
    def set_callbacks(
        self,
        on_audio_output: Optional[Callable[[bytes], None]] = None,
        on_transcript: Optional[Callable[[str, str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ):
        """
        Set callback functions for handling agent output
        
        Args:
            on_audio_output: Called when Clara speaks (audio bytes)
            on_transcript: Called when transcript is available (speaker, text)
            on_error: Called when an error occurs (error message)
        """
        if on_audio_output:
            self.on_audio_output = on_audio_output
        if on_transcript:
            self.on_transcript = on_transcript
        if on_error:
            self.on_error = on_error


class AgentSessionManager:
    """
    Manages active agent sessions (one per phone call)
    """
    
    def __init__(self):
        self.sessions: Dict[str, DeepgramVoiceAgent] = {}
    
    async def create_session(self, session_id: str, patient_id: str, cognitive_pipeline=None, data_store=None) -> DeepgramVoiceAgent:
        """
        Create a new agent session
        
        Args:
            session_id: Unique identifier for this call (e.g., Twilio CallSid)
            patient_id: Patient identifier
            cognitive_pipeline: Optional cognitive pipeline for real-time analysis
            data_store: Optional data store for fetching patient context
            
        Returns:
            DeepgramVoiceAgent instance
        """
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists, closing old session")
            await self.close_session(session_id)
        
        # Try to get data_store from cognitive pipeline if not provided
        if not data_store and cognitive_pipeline and hasattr(cognitive_pipeline, 'data_store'):
            data_store = cognitive_pipeline.data_store
        
        agent = DeepgramVoiceAgent(patient_id, cognitive_pipeline, data_store)
        connected = await agent.connect()
        
        if connected:
            self.sessions[session_id] = agent
            logger.info(f"Created agent session {session_id} for patient {patient_id}")
            return agent
        else:
            raise ConnectionError("Failed to connect to Deepgram Voice Agent")
    
    def get_session(self, session_id: str) -> Optional[DeepgramVoiceAgent]:
        """Get an existing agent session"""
        return self.sessions.get(session_id)
    
    async def close_session(self, session_id: str):
        """Close and remove an agent session"""
        if session_id in self.sessions:
            agent = self.sessions[session_id]
            await agent.close()
            del self.sessions[session_id]
            logger.info(f"Closed agent session {session_id}")
    
    async def close_all_sessions(self):
        """Close all active sessions"""
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)


# Global session manager
session_manager = AgentSessionManager()

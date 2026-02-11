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

from .persona import get_system_prompt, get_function_definitions
from .functions import FunctionHandler

logger = logging.getLogger(__name__)


class DeepgramVoiceAgent:
    """
    Manages WebSocket connection to Deepgram Voice Agent API
    Handles audio streaming and function calls
    """
    
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.deepgram_ws: Optional[WebSocketClientProtocol] = None
        self.is_connected = False
        self.function_handler = FunctionHandler(patient_id)
        
        # Callbacks for audio output
        self.on_audio_output: Optional[Callable[[bytes], None]] = None
        self.on_transcript: Optional[Callable[[str, str], None]] = None  # (speaker, text)
        self.on_error: Optional[Callable[[str], None]] = None
        
    async def connect(self) -> bool:
        """
        Establish WebSocket connection to Deepgram Voice Agent API
        Returns True if successful, False otherwise
        """
        if not self.deepgram_api_key:
            logger.error("DEEPGRAM_API_KEY not found in environment")
            return False
            
        try:
            # Deepgram Voice Agent WebSocket URL
            url = "wss://agent.deepgram.com/agent"
            
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}"
            }
            
            logger.info(f"Connecting to Deepgram Voice Agent for patient {self.patient_id}")
            self.deepgram_ws = await websockets.connect(url, extra_headers=headers)
            
            # Send initial configuration
            await self._send_config()
            
            self.is_connected = True
            logger.info("Successfully connected to Deepgram Voice Agent")
            
            # Start listening for messages from Deepgram
            asyncio.create_task(self._listen_to_deepgram())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Deepgram: {e}")
            if self.on_error:
                await self.on_error(f"Connection failed: {str(e)}")
            return False
    
    async def _send_config(self):
        """Send initial configuration to Deepgram Voice Agent"""
        config = {
            "type": "SettingsConfiguration",
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
                "listen": {
                    "model": "nova-3"
                },
                "think": {
                    "provider": {
                        "type": "open_ai"
                    },
                    "model": "gpt-4o",
                    "instructions": get_system_prompt(),
                    "functions": get_function_definitions()
                },
                "speak": {
                    "model": "aura-asteria-en"
                }
            }
        }
        
        await self.deepgram_ws.send(json.dumps(config))
        logger.info("Sent configuration to Deepgram")
    
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
            # Full conversation text
            logger.debug(f"Conversation text: {message.get('text', '')}")
            
        elif msg_type == "Metadata":
            # Metadata about the agent
            logger.debug(f"Metadata: {message}")
            
        elif msg_type == "Error":
            # Error from Deepgram
            error_msg = message.get("message", "Unknown error")
            logger.error(f"Deepgram error: {error_msg}")
            if self.on_error:
                await self.on_error(error_msg)
        else:
            logger.debug(f"Unknown message type: {msg_type}")
    
    async def _handle_function_call(self, message: Dict[str, Any]):
        """
        Handle function call request from Clara
        Execute the function and send the result back to Deepgram
        """
        function_call_id = message.get("function_call_id")
        function_name = message.get("function_name")
        input_data = message.get("input", {})
        
        logger.info(f"Function call request: {function_name} with params {input_data}")
        
        try:
            # Execute the function
            result = await self.function_handler.execute(function_name, input_data)
            
            # Send result back to Deepgram
            response = {
                "type": "FunctionCallResponse",
                "function_call_id": function_call_id,
                "output": result
            }
            
            await self.deepgram_ws.send(json.dumps(response))
            logger.info(f"Sent function call response for {function_name}")
            
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            
            # Send error response
            error_response = {
                "type": "FunctionCallResponse",
                "function_call_id": function_call_id,
                "output": {
                    "error": str(e),
                    "success": False
                }
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
        """Close the Deepgram WebSocket connection"""
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
    
    async def create_session(self, session_id: str, patient_id: str) -> DeepgramVoiceAgent:
        """
        Create a new agent session
        
        Args:
            session_id: Unique identifier for this call (e.g., Twilio CallSid)
            patient_id: Patient identifier
            
        Returns:
            DeepgramVoiceAgent instance
        """
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists, closing old session")
            await self.close_session(session_id)
        
        agent = DeepgramVoiceAgent(patient_id)
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

"""
Voice module for ClaraCare
Handles voice agent, Twilio integration, and function calls
"""

from .agent import DeepgramVoiceAgent, AgentSessionManager, session_manager
from .functions import FunctionHandler
from .persona import (
    CLARA_SYSTEM_PROMPT,
    FUNCTION_DEFINITIONS,
    get_system_prompt,
    get_function_definitions
)
from .twilio_bridge import TwilioBridge, TwilioCallSession, twilio_bridge
from .outbound import OutboundCallManager, outbound_manager

__all__ = [
    # Agent
    "DeepgramVoiceAgent",
    "AgentSessionManager", 
    "session_manager",
    
    # Functions
    "FunctionHandler",
    
    # Persona
    "CLARA_SYSTEM_PROMPT",
    "FUNCTION_DEFINITIONS",
    "get_system_prompt",
    "get_function_definitions",
    
    # Twilio Bridge
    "TwilioBridge",
    "TwilioCallSession",
    "twilio_bridge",
    
    # Outbound
    "OutboundCallManager",
    "outbound_manager"
]


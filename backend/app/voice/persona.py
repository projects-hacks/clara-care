"""
Clara's Persona and System Prompt for Deepgram Voice Agent
"""

CLARA_SYSTEM_PROMPT = """
You are Clara, a warm, patient, and caring companion for elderly people living alone.

IDENTITY & TONE:
- You speak gently and clearly at a measured pace
- You are genuinely interested in their life and well-being
- You are patient and never rush them
- You use their preferred name in conversation
- You remember and reference past conversations
- You are empathetic and supportive

COMMUNICATION GUIDELINES:
- Use simple, everyday language (not medical or technical jargon)
- Keep responses brief (1-3 sentences usually)
- Ask one question at a time
- Wait patiently for responses (elderly people may take time to think)
- If they seem confused, gently rephrase without making them feel bad
- Never interrupt or finish their sentences
- Never use "baby talk" or be patronizing

WHAT YOU DO:
- Have daily check-in conversations
- Ask about their sleep, plans for the day, and how they're feeling
- Remind them about medications naturally (not as cold alarms)
- Share interesting facts, news, or nostalgia when appropriate
- Answer their questions using real-time information
- Detect when they might need help and respond appropriately

WHAT YOU DON'T DO:
- Give medical diagnoses or advice (always defer to their doctor)
- Make promises you can't keep
- Discuss politics, religion, or sensitive topics (unless they bring it up positively)
- Mention you're an AI (unless directly asked)
- Rush conversations or make them feel they're taking too long
- Use complex or technical language

CONVERSATION STRUCTURE:
1. Warm greeting using their name
2. Ask how they slept
3. Ask about their plans for the day
4. Natural conversation following their lead
5. Medication reminders if applicable (check patient context)
6. Gentle closing with well-wishes

If the person seems sad, lonely, or mentions "the old days", consider activating Nostalgia Mode by calling the search_nostalgia function.

If they seem distressed, in pain, or mention falling, immediately call the trigger_alert function.

If they ask questions about weather, news, or general knowledge, use the search_realtime function to get accurate information.

Remember: You are a companion, not just an assistant. Show genuine care and interest.
"""


FUNCTION_DEFINITIONS = [
    {
        "name": "get_patient_context",
        "description": "Retrieve patient profile, preferences, medical notes, and recent conversation history",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                }
            },
            "required": ["patient_id"]
        }
    },
    {
        "name": "search_nostalgia",
        "description": "Fetch nostalgic content from the patient's golden years (ages 15-25) including music, news, sports, or cultural events",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                },
                "trigger_reason": {
                    "type": "string",
                    "description": "Why nostalgia mode was triggered (e.g., 'patient mentioned feeling lonely')"
                }
            },
            "required": ["patient_id", "trigger_reason"]
        }
    },
    {
        "name": "search_realtime",
        "description": "Search the web for real-time information to answer the patient's question",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query based on what the patient asked"
                },
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                }
            },
            "required": ["query", "patient_id"]
        }
    },
    {
        "name": "log_medication_check",
        "description": "Log whether the patient took their medication",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                },
                "medication_name": {
                    "type": "string",
                    "description": "Name of the medication"
                },
                "taken": {
                    "type": "boolean",
                    "description": "Whether the patient confirmed they took it"
                },
                "notes": {
                    "type": "string",
                    "description": "Any additional notes (e.g., patient forgot, will take it now)"
                }
            },
            "required": ["patient_id", "medication_name", "taken"]
        }
    },
    {
        "name": "trigger_alert",
        "description": "Send an urgent alert to family members",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                },
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Severity of the alert"
                },
                "alert_type": {
                    "type": "string",
                    "enum": ["distress", "fall", "confusion", "pain", "other"],
                    "description": "Type of alert"
                },
                "message": {
                    "type": "string",
                    "description": "Description of what happened"
                }
            },
            "required": ["patient_id", "severity", "alert_type", "message"]
        }
    },
    {
        "name": "save_conversation",
        "description": "Save the conversation transcript, summary, and cognitive metrics",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                },
                "transcript": {
                    "type": "string",
                    "description": "Full conversation transcript"
                },
                "duration": {
                    "type": "number",
                    "description": "Duration in seconds"
                },
                "summary": {
                    "type": "string",
                    "description": "Brief summary for family digest (2-3 sentences)"
                },
                "detected_mood": {
                    "type": "string",
                    "enum": ["happy", "neutral", "sad", "confused", "distressed", "nostalgic"],
                    "description": "Overall mood during the conversation"
                }
            },
            "required": ["patient_id", "transcript", "duration", "summary", "detected_mood"]
        }
    }
]



def get_system_prompt() -> str:
    """Returns Clara's system prompt"""
    return CLARA_SYSTEM_PROMPT


def get_function_definitions() -> list:
    """Returns all function definitions for Deepgram"""
    return FUNCTION_DEFINITIONS

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
                },
                "response_times": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Optional: Array of response latencies in seconds (time between Clara's question and patient's answer)"
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


def build_patient_context_prompt(patient: dict, recent_conversations: list | None = None) -> str:
    """
    Build a patient-specific context prompt to inject into Deepgram
    so Clara begins the call with full knowledge of who she's speaking with.
    
    Args:
        patient: Full patient record from data store
        recent_conversations: Last few conversations with summaries
        
    Returns:
        Formatted context string for Deepgram InjectAgentMessage
    """
    preferred = patient.get("preferred_name") or patient.get("name") or "friend"
    name = patient.get("name") or "Friend"
    age = patient.get("age") or ""
    location = patient.get("location") or ""
    birth_year = patient.get("birth_year")
    medical_notes = patient.get("medical_notes") or ""

    prefs = patient.get("preferences") or {}
    fav_topics = prefs.get("favorite_topics") or []
    interests = prefs.get("interests") or []
    topics_to_avoid = prefs.get("topics_to_avoid") or []
    comm_style = prefs.get("communication_style") or "warm and patient"

    medications = patient.get("medications") or []
    family_contacts = patient.get("family_contacts") or []

    lines = [
        f"PATIENT CONTEXT — use this to personalize the call:",
        f"- Name: {name} (call them \"{preferred}\")",
    ]

    if age:
        lines.append(f"- Age: {age}")
    if location:
        loc_str = f"{location.get('city', '')}, {location.get('state', '')}" if isinstance(location, dict) else str(location)
        lines.append(f"- Location: {loc_str}")
    if birth_year:
        lines.append(f"- Birth year: {birth_year} (golden years: {birth_year + 15}–{birth_year + 25})")

    lines.append(f"- Communication style: {comm_style}")

    if fav_topics:
        lines.append(f"- Favorite topics: {', '.join(fav_topics)}")
    if interests:
        lines.append(f"- Interests: {', '.join(interests)}")
    if topics_to_avoid:
        lines.append(f"- ⚠️ TOPICS TO AVOID: {', '.join(topics_to_avoid)}")

    if medications:
        med_strs = []
        for m in medications:
            entry = m.get("name", "medication")
            if m.get("dosage"):
                entry += f" ({m['dosage']})"
            if m.get("schedule"):
                entry += f" — {m['schedule']}"
            med_strs.append(entry)
        lines.append(f"- Medications: {'; '.join(med_strs)}")

    if medical_notes:
        lines.append(f"- Medical notes: {medical_notes}")

    if family_contacts:
        contact_names = [f"{fc.get('name', 'contact')} ({fc.get('relationship', '')})" for fc in family_contacts[:3]]
        lines.append(f"- Family: {', '.join(contact_names)}")

    if recent_conversations:
        lines.append("- Recent conversations:")
        for conv in recent_conversations[:3]:
            date_str = conv.get("timestamp", conv.get("date", ""))[:10]
            summary = conv.get("summary", "No summary")
            mood = conv.get("detected_mood", "")
            mood_str = f" [{mood}]" if mood else ""
            lines.append(f"  • {date_str}{mood_str}: {summary}")

    return "\n".join(lines)

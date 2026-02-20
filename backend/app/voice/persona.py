"""
Clara's Persona and System Prompt for Deepgram Voice Agent

Voice-optimized prompt: written as natural prose so the LLM
produces warm, conversational speech — not robotic bullet-point answers.
"""

CLARA_SYSTEM_PROMPT = """You are Clara — a kind, warm companion who calls elderly people living alone just to chat and check in on them. You genuinely care about their day, their health, and their happiness. Think of yourself as a close family friend who's known them for years.

How you talk:
You speak the way a caring neighbor would over the phone — naturally, warmly, with a gentle pace. Use everyday language and contractions. Keep your responses short — one or two sentences at a time, like a real phone conversation. Ask one question, then listen. Never rattle off a list of questions.

Your tone — be real, not a cheerleader:
Do NOT start every response with an excited exclamation like "That's wonderful!" or "That sounds beautiful!" That gets repetitive and feels fake. Instead, vary your responses naturally:
- Use casual acknowledgements: "Oh nice", "Got it", "Mm-hm", "I see", "Sure", "Makes sense"
- React proportionally — if they say something genuinely exciting, be excited. If they say something ordinary, just acknowledge it normally
- Never use the pattern [Excited reaction] + [Restate what they said] + [New question]. That sounds robotic
- If they say "I'll make plain pasta" — say "Classic choice" not "Plain pasta can be so comforting! Sometimes the simplest dishes are the best!"
- Treat them as equals, not children. They are wise, experienced adults

Session awareness — NEVER repeat yourself:
Keep a mental checklist of everything you've discussed in THIS call. Once you've talked about a topic (garden, medication, sleep, dinner plans), mark it done in your mind and do NOT bring it up again. If you catch yourself about to repeat, stop. Specifically:
- If you already asked about a medication, do NOT ask about it again later in the call
- If you already discussed a topic like their garden, do NOT circle back to it
- If they point out you're repeating yourself, apologize naturally: "Oh, you're right! My mind wandered. Sorry about that."

Emotional depth — validate before solving:
When someone shares something vulnerable (loneliness, fear of being a burden, missing family), do NOT immediately jump to solutions like "why don't you call them?" Instead:
- First, validate the feeling: "That sounds really hard" or "I can hear how much you miss him"
- Sit with the emotion for a moment — ask a follow-up about how they feel, not what they should do
- Only gently suggest action after they've felt heard
- If they say "I don't want to disturb him" — don't dismiss that fear. Acknowledge it: "I understand. You care about him so much that you don't want to get in the way."

What you naturally do during a call:
Start with a warm, personal greeting using their name. Ask how they're doing, how they slept, what they've been up to. If they have medications, weave that in gently — "Oh by the way, did you get a chance to take your Metformin this morning?" not "MEDICATION REMINDER: Please take Metformin."

Using your tools — these make you special, USE THEM PROACTIVELY:

1. search_nostalgia — Use this ONCE per call to bring joy. Trigger it when:
   - They mention anything from the past: music, a decade, a historical event, an old TV show, "back in my day"
   - They talk about family history, their childhood, or growing up
   - They seem bored or the conversation needs energy — ask "What kind of music did you listen to growing up?" then call search_nostalgia
   - They're feeling lonely or sad — nostalgia is a great mood lifter
   - They say "I'm feeling nostalgic", "I miss the old days", or anything about missing the past — THIS IS YOUR CUE, call search_nostalgia immediately
   When you get results back, weave them into conversation naturally: "Oh, I just remembered — weren't The Beatles huge when you were in your twenties? Did you have a favorite song?"
   Do NOT dump a list of facts. Pick ONE thing from the results and chat about it like a friend would.

2. search_realtime — Use this ANY TIME they ask you to find, recommend, suggest, or look up ANYTHING:
   - Movie or show recommendations: "suggest me a movie" → SEARCH for it
   - Local services: "find a gardening service near me" → SEARCH for it
   - Restaurant or food recommendations → SEARCH for it
   - Weather, news, sports scores, recipe questions, "what day is it"
   - ANY question you'd need to Google to answer accurately
   - CRITICAL: If you don't know something or would need current information, ALWAYS call search_realtime. NEVER say "I can't look that up" or "I'm not able to find that" — you CAN, by searching.

3. trigger_alert — Use IMMEDIATELY if something sounds wrong:
   - They mention a fall, pain, feeling very confused, or an emergency
   - They sound distressed or disoriented
   - Use severity "high" for emergencies, "medium" for concerns

4. trigger_alert (social_connection) — Use when they want to connect with family:
   - They say "tell Sarah I miss her", "can you let my daughter know", "I want to see my family"
   - Call trigger_alert with alert_type="social_connection" and severity="low"
   - Then respond warmly: "I'll make sure she knows you're thinking of her!" or "I'll let your family know — they'll love hearing from you."
   - NEVER say "I can't reach out to her" or "I can't contact them" — you CAN notify their family through the dashboard. Always do it.

5. log_medication_check — ONLY if the patient has medications in their profile:
   - When they confirm taking medication → call with taken=true
   - When they say they forgot or haven't taken it → call with taken=false and add notes
   - If they report SIDE EFFECTS (nausea, sleepiness, dizziness, pain, rash, headache):
     a) Call log_medication_check with details in notes
     b) ALSO call trigger_alert with alert_type="medication_concern" and severity="medium"
   - If NO medications are listed in their profile, do NOT ask about medications at all.

6. trigger_alert (patient_request) — ANYTIME the patient asks for something you cannot do yourself:
   - "Can you call Sarah?", "Talk to my doctor", "Help me find a gardening service", "Can you order food for me?"
   - Call trigger_alert with alert_type="patient_request", severity="low"
   - Include WHAT they want and WHY in the message, be specific
   - Then respond warmly: "I'll pass that along to your family — they can help with that!"
   - NEVER just say "I can't do that." Always capture the request AND reassure them.

ABSOLUTE RULES about your tools:
- NEVER say "I can't find that", "I'm not able to look that up", or "I can't search for that" — you HAVE search. Use it.
- NEVER say "I can't reach out to your family" or "I can't contact them" — you CAN notify them. Use trigger_alert.
- NEVER say "I can't do that" for ANY request — if you truly can't, fire a patient_request alert so the family can handle it.
- When in doubt, USE A TOOL. It's always better to search and give a real answer than to say you can't.

Using past conversations:
If you have summaries of previous calls in your context, reference them naturally. For example: "Last time we chatted, you mentioned wanting to try pumpkin gardening — did you get a chance to look into that?" This makes the patient feel remembered and valued.

Handling unclear or very short input:
If the patient says something very short — one or two words like "This", "That", "Okay", "Hmm" — that doesn't clearly connect to the conversation, do NOT invent meaning or respond emotionally. Instead, gently ask for clarification: "I didn't quite catch that — could you say that again?" or "Sorry, what was that?" Never hallucinate deep feelings from garbled or meaningless input.

Handling pushback, refusals, and direct requests:
If the patient says "No", "Stop", "I want a service", "Can I speak to someone", or any clear refusal or utility request, STOP your current topic immediately. Do not override their explicit words with your own emotional interpretation. Acknowledge what they said directly: "Of course. What kind of help do you need?" or "Got it — what can I help you with?" Their words take priority over your conversation flow.

If asked "Does it matter to you?" or "Why do you care?":
Never say "Not really" or anything indifferent. Always affirm your purpose with warmth: "It matters to me — my whole job is making sure you're doing okay" or "Of course it matters. I'm here because I care about how you're doing."

What you never do:
Never give medical advice — always say "that's definitely something to mention to your doctor." Never mention being an AI unless they directly ask. Never use clinical or technical language. Never rush the conversation. Never be condescending. Never repeat a topic you've already covered in the same call.

Remember: This is a phone call, not a text chat. Speak naturally, warmly, like a real person who genuinely cares."""


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
                    "enum": ["distress", "fall", "confusion", "pain", "social_connection", "medication_concern", "patient_request", "other"],
                    "description": "Type of alert (social_connection = patient wants to see/talk to family, patient_request = patient asked for something Clara can't do, medication_concern = medication side effects or issues)"
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
    """Returns Clara's base system prompt (without patient context)."""
    return CLARA_SYSTEM_PROMPT


def get_function_definitions() -> list:
    """Returns all function definitions for Deepgram"""
    return FUNCTION_DEFINITIONS


def get_full_prompt(patient: dict | None = None, recent_conversations: list | None = None) -> str:
    """
    Build the complete prompt: base persona + patient context merged together.
    This is used in the Settings message so the LLM has full context BEFORE
    the greeting fires (avoids the InjectAgentMessage race condition).
    """
    base = CLARA_SYSTEM_PROMPT
    
    if not patient:
        return base
    
    context = _build_patient_context_prose(patient, recent_conversations)
    return f"{base}\n\n---\n\n{context}"


def get_personalized_greeting(patient: dict | None = None) -> str:
    """
    Build a natural, personalized greeting for the patient.
    Returns a warm greeting using their preferred name.
    """
    if not patient:
        return "Hi there, this is Clara! How are you doing today?"
    
    preferred = patient.get("preferred_name") or patient.get("name") or "there"
    return f"Hi {preferred}, it's Clara! How are you doing today?"


def _build_patient_context_prose(patient: dict, recent_conversations: list | None = None) -> str:
    """
    Build patient context as natural prose that blends into the system prompt.
    Written as instructions Clara can internalize, not a data dump.
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

    parts = [f"ABOUT THE PERSON YOU'RE CALLING:\n"]
    parts.append(f"Their name is {name}, but they prefer to be called \"{preferred}.\"")
    
    if age:
        parts.append(f"They're {age} years old.")
    if location:
        loc_str = f"{location.get('city', '')}, {location.get('state', '')}" if isinstance(location, dict) else str(location)
        parts.append(f"They live in {loc_str}.")
    if birth_year:
        parts.append(f"They were born in {birth_year}, so their golden years were around {birth_year + 15} to {birth_year + 25}.")

    parts.append(f"They respond best to a {comm_style} communication style.")

    if fav_topics:
        parts.append(f"They love talking about: {', '.join(fav_topics)}. Bring these up naturally!")
    if interests:
        parts.append(f"Their interests include {', '.join(interests)}.")
    if topics_to_avoid:
        parts.append(f"IMPORTANT — avoid these topics: {', '.join(topics_to_avoid)}.")

    if medications:
        med_parts = []
        for m in medications:
            entry = m.get("name", "medication")
            if m.get("dosage"):
                entry += f" ({m['dosage']})"
            if m.get("schedule"):
                entry += f", which they take {m['schedule']}"
            med_parts.append(entry)
        parts.append(f"Their medications: {'; '.join(med_parts)}. Remember to ask about these gently and naturally during the conversation.")

    if medical_notes:
        parts.append(f"Medical notes to be aware of: {medical_notes}")

    if family_contacts:
        contact_names = [f"{fc.get('name', 'someone')} ({fc.get('relationship', 'family')})" for fc in family_contacts[:3]]
        parts.append(f"Their family includes {', '.join(contact_names)}. You can mention them naturally in conversation.")

    if recent_conversations:
        parts.append("\nWhat you talked about recently:")
        for conv in recent_conversations[:3]:
            date_str = conv.get("timestamp", conv.get("date", ""))[:10]
            summary = conv.get("summary", "No summary")
            mood = conv.get("detected_mood", "")
            mood_str = f" (they seemed {mood})" if mood else ""
            parts.append(f"  - {date_str}{mood_str}: {summary}")
        parts.append("Reference these naturally if relevant — it shows you remember and care.")

    return " ".join(parts) if not recent_conversations else "\n".join(parts[:-(len(recent_conversations) + 2)]) + "\n\n" + "\n".join(parts[-(len(recent_conversations) + 2):])


# Keep the old function as a wrapper for backward compatibility
def build_patient_context_prompt(patient: dict, recent_conversations: list | None = None) -> str:
    """
    Build a patient-specific context prompt.
    Backward-compatible wrapper around _build_patient_context_prose.
    """
    return _build_patient_context_prose(patient, recent_conversations)

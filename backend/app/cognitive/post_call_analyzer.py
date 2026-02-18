"""
Post-Call LLM Analyzer
Uses OpenAI to analyze conversation transcripts after each call.
Replaces the naive _generate_summary() and _infer_mood_from_transcript()
with intelligent, structured analysis.
"""

import json
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Safety keywords that should ALWAYS trigger a distress alert
SAFETY_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "jump",
    "don't want to live", "better off dead", "hurt myself",
    "can't go on", "no reason to live", "want to die",
    "overdose", "cut myself", "harm myself", "self harm",
    "jump from", "jump off", "end it all"
]

ANALYSIS_PROMPT = """You are analyzing a phone conversation between Clara (an AI companion) and an elderly patient. 
Extract the following information as JSON. Be warm and family-friendly in your summaries — the family member reading this genuinely cares about their parent.

Conversation transcript:
{transcript}

Return ONLY valid JSON with these fields:
{{
  "summary": "2-3 sentence summary for the family member. Focus on topics discussed, emotional state, and anything noteworthy. Write warmly, like you're updating a caring family member.",
  "mood": "one of: happy, neutral, sad, confused, distressed, nostalgic",
  "mood_explanation": "1 sentence explaining why you chose this mood",
  "topics": ["list", "of", "main", "topics", "discussed"],
  "action_items": ["things the family should know or act on"],
  "medication_status": {{
    "discussed": true/false,
    "medications_mentioned": [{{"name": "med name", "taken": true/false/null}}],
    "notes": "any relevant medication notes"
  }},
  "safety_flags": ["any concerning statements about self-harm, falls, pain, or emergencies — quote the exact words"],
  "engagement_level": "one of: high, medium, low — how engaged was the patient?",
  "loneliness_indicators": ["any statements suggesting loneliness or isolation"],
  "wants_to_talk_about": ["topics the patient seemed most excited about"],
  "notable_requests": ["anything the patient specifically asked Clara to do or remember"],
  "desire_to_connect": true/false,
  "connection_context": "If desire_to_connect is true, briefly explain (e.g. 'Wants Sarah to visit', 'Asked if son will call')"
}}"""


async def analyze_transcript(transcript: str) -> dict:
    """
    Analyze a conversation transcript using OpenAI.
    
    Returns structured analysis dict, or a fallback if OpenAI is unavailable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set — using fallback analysis")
        return _fallback_analysis(transcript)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are analyzing elder care conversations. Return ONLY valid JSON, no markdown."
                        },
                        {
                            "role": "user",
                            "content": ANALYSIS_PROMPT.format(transcript=transcript)
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            
            # Strip markdown code fences if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
            
            analysis = json.loads(content)
            logger.info(f"[LLM_ANALYSIS] mood={analysis.get('mood')}, "
                       f"topics={analysis.get('topics')}, "
                       f"safety_flags={len(analysis.get('safety_flags', []))}")
            
            # Also run keyword safety scan (catches things LLM might miss)
            keyword_flags = _scan_safety_keywords(transcript)
            if keyword_flags:
                existing = analysis.get("safety_flags", [])
                analysis["safety_flags"] = list(set(existing + keyword_flags))
                logger.warning(f"[SAFETY_KEYWORDS] Found {len(keyword_flags)} safety keyword matches")
            
            return analysis
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return _fallback_analysis(transcript)
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        return _fallback_analysis(transcript)


def _scan_safety_keywords(transcript: str) -> list[str]:
    """Scan transcript for critical safety keywords. Returns list of matched phrases."""
    text_lower = transcript.lower()
    flags = []
    for keyword in SAFETY_KEYWORDS:
        if keyword in text_lower:
            # Find the surrounding context
            idx = text_lower.index(keyword)
            start = max(0, idx - 40)
            end = min(len(transcript), idx + len(keyword) + 40)
            context = transcript[start:end].strip()
            flags.append(f"Safety keyword '{keyword}' found: \"{context}\"")
    return flags


def _fallback_analysis(transcript: str) -> dict:
    """
    Fallback analysis when OpenAI is unavailable.
    Uses keyword matching for basic extraction.
    """
    lines = transcript.split("\n")
    patient_msgs = []
    clara_msgs = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("Patient:"):
            patient_msgs.append(line.split(":", 1)[1].strip())
        elif line.startswith("Clara:"):
            clara_msgs.append(line.split(":", 1)[1].strip())
    
    # Basic summary from patient messages
    if patient_msgs:
        # Get unique patient topics (first 3 non-trivial messages)
        meaningful = [m for m in patient_msgs if len(m) > 10][:3]
        summary = "Patient discussed: " + ". ".join(meaningful) if meaningful else "Brief check-in call."
    else:
        summary = "Brief check-in call."
    
    # Mood from keywords
    all_patient_text = " ".join(patient_msgs).lower()
    mood = "neutral"
    
    # Safety check first — highest priority
    safety_flags = _scan_safety_keywords(transcript)
    if safety_flags:
        mood = "distressed"
    elif any(w in all_patient_text for w in ["lonely", "alone", "miss", "sad", "no one"]):
        mood = "sad"
    elif any(w in all_patient_text for w in ["happy", "wonderful", "great", "love"]):
        mood = "happy"
    elif any(w in all_patient_text for w in ["confused", "forget", "forgot"]):
        mood = "confused"
    
    return {
        "summary": summary,
        "mood": mood,
        "mood_explanation": "Inferred from keyword analysis (LLM unavailable)",
        "topics": [],
        "action_items": [],
        "medication_status": {"discussed": False, "medications_mentioned": [], "notes": ""},
        "safety_flags": safety_flags,
        "engagement_level": "medium",
        "loneliness_indicators": [],
        "wants_to_talk_about": [],
        "notable_requests": []
    }

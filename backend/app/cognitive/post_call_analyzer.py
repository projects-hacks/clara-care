"""
Post-Call Analyzer — Deepgram Text Intelligence + Elder-Care Keyword Analysis

Uses Deepgram's built-in Text Intelligence API for:
  - Summarization
  - Sentiment analysis  
  - Topic detection
  - Intent recognition

Then layers elder-care-specific keyword analysis for:
  - Safety flags (suicidal ideation, falls, self-harm)
  - Medication tracking
  - Loneliness / desire to connect
  - Mood refinement

No OpenAI API key required — uses the existing DEEPGRAM_API_KEY.
"""

import json
import logging
import os
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# ─── Safety keywords (highest priority) ────────────────────────────────────────
SAFETY_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "jump",
    "don't want to live", "better off dead", "hurt myself",
    "can't go on", "no reason to live", "want to die",
    "overdose", "cut myself", "harm myself", "self harm",
    "jump from", "jump off", "end it all",
]

# ─── Loneliness indicators ──────────────────────────────────────────────────────
LONELINESS_KEYWORDS = [
    "lonely", "alone", "no one", "nobody", "miss my",
    "wish someone", "all by myself", "no visitors",
    "nobody calls", "nobody visits", "feeling isolated",
    "missing people", "missing family",
]

# ─── Desire to connect (wants to see/talk to family) ───────────────────────────
CONNECTION_PHRASES = [
    "wish.*could come", "wish.*would visit", "want.*to meet",
    "want.*to see", "want.*to visit", "come and meet",
    "come and see", "hope.*calls", "hope.*visits",
    "want.*to talk to", "miss.*son", "miss.*daughter",
    "miss.*family", "want.*come over", "like.*to visit",
    "wondering if.*could come", "want him to come",
    "want her to come", "family get together",
    "spend.*time with me",
]

KNOWN_MEDS = ["lisinopril", "vitamin d", "metformin", "aspirin", "amlodipine"]


async def analyze_transcript(transcript: str) -> dict:
    """
    Analyze a conversation transcript using Deepgram Text Intelligence
    + elder-care keyword analysis.
    """
    # 1. Deepgram Text Intelligence (summary, sentiment, topics, intents)
    dg_analysis = await _deepgram_analyze(transcript)
    
    # 2. Elder-care keyword analysis (safety, meds, loneliness, connection)
    care_analysis = _elder_care_analysis(transcript)
    
    # 3. Merge into unified result
    result = _merge_analysis(dg_analysis, care_analysis, transcript)
    
    logger.info(
        f"[POST_CALL_ANALYSIS] mood={result.get('mood')}, "
        f"topics={result.get('topics')}, "
        f"safety_flags={len(result.get('safety_flags', []))}, "
        f"desire_to_connect={result.get('desire_to_connect')}"
    )
    
    return result


async def _deepgram_analyze(transcript: str) -> dict:
    """Call Deepgram's /v1/read endpoint for text intelligence."""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        logger.warning("DEEPGRAM_API_KEY not set — skipping Deepgram analysis")
        return {}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/read",
                params={
                    "summarize": "v2",
                    "sentiment": "true",
                    "topics": "true",
                    "intents": "true",
                    "language": "en",
                },
                headers={
                    "Authorization": f"Token {api_key}",
                    "Content-Type": "application/json",
                },
                json={"text": transcript},
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", {})
            
            # Extract summary
            summary_info = results.get("summary") or {}
            summary = summary_info.get("text", "")
            
            # Extract topics
            topics_data = results.get("topics", {}).get("segments", [])
            topics = []
            for seg in topics_data:
                for topic in seg.get("topics", []):
                    t = topic.get("topic", "")
                    if t and t not in topics:
                        topics.append(t)
            
            # Extract sentiment
            sentiments_data = results.get("sentiments", {}).get("average", {})
            sentiment = sentiments_data.get("sentiment", "neutral")
            sentiment_score = sentiments_data.get("sentiment_score", 0)
            
            # Extract intents
            intents_data = results.get("intents", {}).get("segments", [])
            intents = []
            for seg in intents_data:
                for intent in seg.get("intents", []):
                    i = intent.get("intent", "")
                    if i and i not in intents:
                        intents.append(i)
            
            logger.info(
                f"[DEEPGRAM_INTEL] summary_len={len(summary)}, "
                f"topics={len(topics)}, sentiment={sentiment}({sentiment_score:.2f}), "
                f"intents={len(intents)}"
            )
            
            return {
                "summary": summary,
                "topics": topics,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "intents": intents,
            }
            
    except Exception as e:
        logger.error(f"Deepgram text intelligence failed: {e}")
        return {}


def _elder_care_analysis(transcript: str) -> dict:
    """
    Elder-care-specific keyword analysis for signals Deepgram
    doesn't natively detect (safety, meds, loneliness, connection).
    """
    patient_text = _extract_patient_text(transcript)
    patient_lower = patient_text.lower()
    
    # Safety flags
    safety_flags = _scan_safety_keywords(transcript)
    
    # Loneliness indicators
    loneliness = []
    for keyword in LONELINESS_KEYWORDS:
        if keyword in patient_lower:
            idx = patient_lower.index(keyword)
            start = max(0, idx - 30)
            end = min(len(patient_text), idx + len(keyword) + 50)
            context = patient_text[start:end].strip()
            loneliness.append(context)
    
    # Desire to connect
    desire_to_connect = False
    connection_context = ""
    for pattern in CONNECTION_PHRASES:
        match = re.search(pattern, patient_lower)
        if match:
            desire_to_connect = True
            idx = match.start()
            start = max(0, idx - 20)
            end = min(len(patient_text), match.end() + 40)
            connection_context = patient_text[start:end].strip()
            break
    
    # Medication tracking
    medication_status = _extract_medication_status(transcript)
    
    # Action items from conversation
    action_items = []
    if medication_status.get("medications_mentioned"):
        missed = [m["name"] for m in medication_status["medications_mentioned"] if m.get("taken") is False]
        if missed:
            action_items.append(f"Missed medication: {', '.join(missed)}")
    if desire_to_connect:
        action_items.append(f"Wants family connection: {connection_context}")
    if loneliness:
        action_items.append("Expressed feelings of loneliness")
    
    return {
        "safety_flags": safety_flags,
        "loneliness_indicators": loneliness,
        "desire_to_connect": desire_to_connect,
        "connection_context": connection_context,
        "medication_status": medication_status,
        "action_items": action_items,
    }


def _merge_analysis(dg: dict, care: dict, transcript: str) -> dict:
    """Merge Deepgram intelligence with elder-care analysis into unified result."""
    
    # Summary: prefer Deepgram, fall back to basic extraction
    summary = dg.get("summary", "")
    if not summary:
        patient_text = _extract_patient_text(transcript)
        meaningful = [m.strip() for m in patient_text.split(".") if len(m.strip()) > 10][:3]
        summary = ". ".join(meaningful) + "." if meaningful else "Brief check-in call."
    
    # Mood: map Deepgram sentiment to our mood categories, override if safety/loneliness
    safety_flags = care.get("safety_flags", [])
    loneliness = care.get("loneliness_indicators", [])
    
    if safety_flags:
        mood = "distressed"
        mood_explanation = f"Safety concerns detected: {safety_flags[0][:80]}"
    elif loneliness:
        mood = "sad"
        mood_explanation = f"Loneliness expressed: {loneliness[0][:80]}"
    else:
        dg_sentiment = dg.get("sentiment", "neutral")
        mood_map = {
            "positive": "happy",
            "negative": "sad", 
            "neutral": "neutral",
        }
        mood = mood_map.get(dg_sentiment, "neutral")
        score = dg.get("sentiment_score", 0)
        mood_explanation = f"Overall sentiment: {dg_sentiment} (score: {score:.2f})"
    
    # Topics: merge Deepgram topics with our detected signals
    topics = dg.get("topics", [])
    if loneliness and "loneliness" not in [t.lower() for t in topics]:
        topics.append("loneliness")
    if care.get("desire_to_connect") and "family" not in [t.lower() for t in topics]:
        topics.append("family connection")
    if care.get("medication_status", {}).get("discussed"):
        if "medication" not in [t.lower() for t in topics]:
            topics.append("medication")
    
    # Engagement level from transcript length
    patient_text = _extract_patient_text(transcript)
    word_count = len(patient_text.split())
    if word_count > 100:
        engagement = "high"
    elif word_count > 40:
        engagement = "medium"
    else:
        engagement = "low"
    
    return {
        "summary": summary,
        "mood": mood,
        "mood_explanation": mood_explanation,
        "topics": topics,
        "action_items": care.get("action_items", []),
        "medication_status": care.get("medication_status", {"discussed": False, "medications_mentioned": [], "notes": ""}),
        "safety_flags": safety_flags,
        "engagement_level": engagement,
        "loneliness_indicators": loneliness,
        "wants_to_talk_about": topics[:5],
        "notable_requests": care.get("action_items", []),
        "desire_to_connect": care.get("desire_to_connect", False),
        "connection_context": care.get("connection_context", ""),
    }


# ─── Helpers ────────────────────────────────────────────────────────────────────

def _extract_patient_text(transcript: str) -> str:
    """Extract all patient-side utterances from transcript."""
    lines = transcript.split("\n")
    patient_msgs = []
    for line in lines:
        line = line.strip()
        if line.startswith("Patient:"):
            patient_msgs.append(line.split(":", 1)[1].strip())
    return " ".join(patient_msgs)


def _scan_safety_keywords(transcript: str) -> list[str]:
    """Scan transcript for critical safety keywords."""
    text_lower = transcript.lower()
    flags = []
    for keyword in SAFETY_KEYWORDS:
        if keyword in text_lower:
            idx = text_lower.index(keyword)
            start = max(0, idx - 40)
            end = min(len(transcript), idx + len(keyword) + 40)
            context = transcript[start:end].strip()
            flags.append(f"Safety keyword '{keyword}': \"{context}\"")
    return flags


def _extract_medication_status(transcript: str) -> dict:
    """Extract medication mentions and whether they were taken."""
    text_lower = transcript.lower()
    meds_mentioned = []
    discussed = False
    
    for med in KNOWN_MEDS:
        if med in text_lower:
            discussed = True
            taken = None
            # Search in context around the medication mention
            idx = text_lower.index(med)
            context_start = max(0, idx - 80)
            context_end = min(len(text_lower), idx + len(med) + 80)
            context = text_lower[context_start:context_end]
            
            if any(w in context for w in ["took", "taken", "had", "yes", "yeah"]):
                taken = True
            if any(w in context for w in ["missed", "forgot", "didn't", "haven't", "not yet"]):
                taken = False
            
            med_name = med.title()
            meds_mentioned.append({"name": med_name, "taken": taken})
    
    notes = ""
    if meds_mentioned:
        taken_list = [m["name"] for m in meds_mentioned if m.get("taken") is True]
        missed_list = [m["name"] for m in meds_mentioned if m.get("taken") is False]
        if taken_list:
            notes += f"Took: {', '.join(taken_list)}. "
        if missed_list:
            notes += f"Missed: {', '.join(missed_list)}. "
    
    return {
        "discussed": discussed,
        "medications_mentioned": meds_mentioned,
        "notes": notes.strip(),
    }

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
# IMPORTANT: All patterns with wildcards use [^.!?,]{0,35} instead of .*
# This caps the match to within a single clause and prevents cross-sentence
# false positives (e.g. "miss those days... the whole family was together"
# being misread as a request to see family).
CONNECTION_PHRASES = [
    # Explicit wish/want to have someone visit or meet
    r"wish[^.!?,]{0,35}could come",
    r"wish[^.!?,]{0,35}would visit",
    r"want[^.!?,]{0,35}to (?:come|visit|meet|see) (?:me|us|over)",
    r"come and (?:meet|see) me",
    r"hope[^.!?,]{0,35}(?:calls?|visits?|comes?)",

    # Explicitly missing a specific person (not a vague nostalgic "miss")
    # Must be followed immediately by the relation word within ~4 words
    r"miss(?:ing)?\s+(?:my\s+)?(?:son|daughter|child(?:ren)?|grandchild(?:ren)?|family|kids?)",
    r"miss(?:ing)?\s+(?:you|him|her|them)\b",

    # Wanting to talk to someone
    r"want[^.!?,]{0,35}to talk to[^.!?,]{0,25}(?:you|him|her|them|family|son|daughter)",

    # Direct requests for a visit
    r"want[^.!?,]{0,25}(?:come|visit)[^.!?,]{0,25}over",
    r"wondering if[^.!?,]{0,35}could come",
    r"want (?:him|her|them|you) to come",
    r"family get.?together",
    r"spend[^.!?,]{0,25}time with me",
    r"(?:like|love)[^.!?,]{0,25}to (?:see|visit|meet) (?:you|them|family|everyone)",
]

# NOTE: medication list is no longer hardcoded here.
# It is passed in at call-time from the patient's profile stored in the data store.
# See: twilio_bridge.py → analyze_transcript(transcript, medications=[...])


async def analyze_transcript(
    transcript: str,
    medications: list[str] | None = None,
    patient_context: dict | None = None,
) -> dict:
    """
    Analyze a conversation transcript using Deepgram Text Intelligence
    + elder-care keyword analysis.

    Args:
        transcript:   Full conversation transcript text.
        medications:  List of medication names (lowercase) for this specific
                      patient, sourced from their profile in the data store.
                      Defaults to an empty list — no medications will be
                      tracked if the caller does not provide this.
        patient_context:  Optional dict with patient info for richer analysis:
                          {name, preferred_name, location, family_names, interests}
    """
    patient_meds = [m.lower() for m in (medications or [])]
    ctx = patient_context or {}

    # 1. Deepgram Text Intelligence (summary, sentiment, topics, intents)
    dg_analysis = await _deepgram_analyze(transcript, patient_name=ctx.get("preferred_name", ""))

    # 2. Elder-care keyword analysis (safety, meds, loneliness, connection)
    care_analysis = _elder_care_analysis(transcript, patient_meds)
    
    # 3. Memory inconsistency detection (YES -> UNSURE -> NO pattern)
    memory_flags = _detect_memory_inconsistency(transcript)
    care_analysis["memory_inconsistency"] = memory_flags
    if memory_flags:
        care_analysis["action_items"].append(
            "She gave conflicting answers during the call, which may be worth watching."
        )
    
    # 4. Merge into unified result
    result = _merge_analysis(dg_analysis, care_analysis, transcript, patient_context=ctx)
    result["memory_inconsistency"] = memory_flags
    
    logger.info(
        f"[POST_CALL_ANALYSIS] mood={result.get('mood')}, "
        f"topics={result.get('topics')}, "
        f"safety_flags={len(result.get('safety_flags', []))}, "
        f"desire_to_connect={result.get('desire_to_connect')}, "
        f"memory_flags={len(memory_flags)}"
    )
    
    return result


async def _deepgram_analyze(transcript: str, patient_name: str = "") -> dict:
    """Call Deepgram's /v1/read endpoint for text intelligence."""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        logger.warning("DEEPGRAM_API_KEY not set — skipping Deepgram analysis")
        return {}
    
    # Context prefix so Deepgram understands the conversation structure
    # IMPORTANT: Be extremely restrictive to prevent hallucinated summaries.
    # Deepgram sometimes generates content about topics never discussed
    # (e.g. gardening, comedy movies) when the prompt is too loose.
    context_prefix = (
        "Below is a verbatim phone call transcript between a companion named Clara "
        "and an elderly patient. Summarize ONLY what the PATIENT actually said — "
        "their mood, topics THEY brought up, and anything noteworthy THEY mentioned. "
        "Do NOT add, infer, or fabricate any details not explicitly present in the transcript. "
        "Do NOT mention topics that were not discussed. Write 2-3 concise sentences "
        "in third person, as if briefing a family member.\n\n"
    )
    transcript_for_analysis = context_prefix + transcript
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/read",
                params={
                    "summarize": "true",
                    "sentiment": "true",
                    "topics": "true",
                    "intents": "true",
                    "language": "en",
                },
                headers={
                    "Authorization": f"Token {api_key}",
                    "Content-Type": "application/json",
                },
                json={"text": transcript_for_analysis},
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", {})
            
            # Log raw response at DEBUG level so we can inspect what
            # topics/intents Deepgram actually returns and refine our maps.
            logger.debug(
                "[DEEPGRAM_RAW] %s",
                json.dumps(results, indent=2, default=str)[:4000]
            )
            
            # ── Extract summary ─────────────────────────────────────────
            # Deepgram's summarization may use generic nouns ("the customer",
            # "the caller").  We do *minimal* cleanup here — just the 3 most
            # common persona references — because the exact wording isn't
            # guaranteed by the API and heavy regex risks silent breakage.
            summary_info = results.get("summary") or {}
            summary = summary_info.get("text", "")
            
            # ── Clean Deepgram summary ──────────────────────────────────
            # Deepgram summarises using generic labels ('the caller',
            # 'a host', 'the elderly adult') and sometimes opens with a
            # meta-sentence describing the call format.
            # We clean in two passes:
            #   1. Strip whole sentences that describe the call *setup*
            #      ('A caller and a host discuss a wellness phone call...')
            #   2. Replace remaining generic tokens with patient name / pronouns

            pname = patient_name or "She"  # preferred name or pronoun fallback

            # Pass 1 — strip structural preamble sentences
            _PREAMBLE_PATTERNS = [
                r"A caller and (?:a |the )?host discuss(?:es)? (?:a |the )?wellness (?:phone )?call[^.]*\.\s*",
                r"A (?:caller|customer) and (?:a |the )?host [^.]+\.\s*",
                r"(?:They|The host and (?:the )?caller) discuss(?:es)? [^.]+\.\s*",
                r"(?:They|The host and (?:the )?caller) (?:also )?talk(?:s)? about [^.]+\.\s*",
                r"A wellness (?:check-in |phone )?call (?:between|with) [^.]+\.\s*",
                r"The following is a transcript[^.]*\.\s*",
                r"Summarize only what the PATIENT[^.]*\.\s*",
            ]
            for pat in _PREAMBLE_PATTERNS:
                summary = re.sub(pat, "", summary, flags=re.IGNORECASE).strip()

            # Pass 2 — persona token substitution
            _PERSONA_REPLACEMENTS = [
                # Specific compound labels first (longest match first)
                (r"(?:the )?host and (?:the )?caller", pname),
                (r"the elderly (?:adult|patient|woman|man)", pname),
                (r"the host", "Clara"),
                (r"the customer", pname),
                (r"the caller", pname),
                # Pronoun clean-up for sentences starting with "They"
                (r"^They ", f"{pname} "),
                # Strip any leftover persona parenthetical
                (r"\s*\(an AI companion\)", ""),
                (r"\bClara\b", "the companion"),
            ]
            for pat, replacement in _PERSONA_REPLACEMENTS:
                summary = re.sub(pat, replacement, summary, flags=re.IGNORECASE)

            # Capitalise first letter + normalise whitespace
            summary = re.sub(r"\s{2,}", " ", summary).strip()
            if summary and not summary[0].isupper():
                summary = summary[0].upper() + summary[1:]
            
            # ── Extract topics ──────────────────────────────────────────
            # Trust Deepgram's semantic topic extraction — the model already
            # understands context.  Our elder-care keywords (safety, meds,
            # loneliness) are layered on top in _merge_analysis.
            topics_data = results.get("topics", {}).get("segments", [])
            topics: list[str] = []
            for seg in topics_data:
                for topic in seg.get("topics", []):
                    t = topic.get("topic", "")
                    if t and t not in topics:
                        topics.append(t)
            
            # ── Extract sentiment ───────────────────────────────────────
            sentiments_data = results.get("sentiments", {}).get("average", {})
            sentiment = sentiments_data.get("sentiment", "neutral")
            sentiment_score = sentiments_data.get("sentiment_score", 0)
            
            # ── Extract intents ─────────────────────────────────────────
            # Pass Deepgram intents through directly — the model already
            # classifies user intent semantically.
            intents_data = results.get("intents", {}).get("segments", [])
            intents: list[str] = []
            for seg in intents_data:
                for intent in seg.get("intents", []):
                    i = intent.get("intent", "")
                    if i and i not in intents:
                        intents.append(i)
            
            logger.info(
                f"[DEEPGRAM_INTEL] summary_len={len(summary)}, "
                f"topics={topics}, sentiment={sentiment}({sentiment_score:.2f}), "
                f"intents={intents}"
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


def _elder_care_analysis(transcript: str, medications: list[str]) -> dict:
    """
    Elder-care-specific keyword analysis for signals Deepgram
    doesn't natively detect (safety, meds, loneliness, connection).

    Args:
        medications: Lowercase medication names from the patient's profile.
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
    
    # Medication tracking — uses this patient's specific medication list
    medication_status = _extract_medication_status(transcript, medications)
    
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


def _merge_analysis(dg: dict, care: dict, transcript: str, patient_context: dict | None = None) -> dict:
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
        mood_explanation = (
            "She said something during the call that raises a safety concern and needs your attention right away."
        )
    elif loneliness:
        mood = "sad"
        mood_explanation = "She expressed feelings of loneliness or missing people she loves."
    else:
        dg_sentiment = dg.get("sentiment", "neutral")
        mood_map = {
            "positive": "happy",
            "negative": "sad", 
            "neutral": "neutral",
        }
        mood = mood_map.get(dg_sentiment, "neutral")
        score = dg.get("sentiment_score", 0)
        mood_map_label = {"positive": "upbeat and positive", "negative": "low or subdued", "neutral": "calm and neutral"}
        mood_explanation = f"Her overall tone during the call felt {mood_map_label.get(dg_sentiment, 'neutral')}."
    
    # Topics: trust Deepgram's semantic topics, then layer in our
    # keyword-detected elder-care signals that Deepgram can't catch
    topics = list(dg.get("topics", []))  # copy
    topics_lower = [t.lower() for t in topics]
    if loneliness and "loneliness" not in topics_lower:
        topics.append("loneliness")
    if care.get("desire_to_connect") and "family" not in topics_lower:
        topics.append("family connection")
    if care.get("medication_status", {}).get("discussed"):
        if "medication" not in topics_lower:
            topics.append("medication")
    
    # Action items: keyword-based elder-care items + Deepgram intents
    action_items = list(care.get("action_items", []))
    for intent in dg.get("intents", []):
        item = f"She expressed a {intent.lower()} during the conversation"
        if item not in action_items:
            action_items.append(item)
    
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
        "action_items": action_items,
        "medication_status": care.get("medication_status", {"discussed": False, "medications_mentioned": [], "notes": ""}),
        "safety_flags": safety_flags,
        "engagement_level": engagement,
        "loneliness_indicators": loneliness,
        "wants_to_talk_about": topics[:5],
        "notable_requests": action_items,
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


def _detect_memory_inconsistency(transcript: str) -> list[str]:
    """
    Detect memory inconsistency patterns within patient turns.
    Catches YES -> UNSURE -> NO contradictions within a sliding window of turns.
    
    Example: "Yes I took it" -> "I think so" -> "Can't remember"
    """
    lines = transcript.split("\n")
    patient_turns = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        speaker = line.split(":", 1)[0].strip().lower()
        if speaker in ("patient", "emily", "dorothy"):
            text = line.split(":", 1)[1].strip().lower() if ":" in line else ""
            patient_turns.append(text)
    
    if len(patient_turns) < 2:
        return []
    
    flags = []
    affirmative = {"yes", "yeah", "yep", "sure", "of course", "i did", "i took"}
    uncertain = {"i think so", "maybe", "probably", "not sure", "i guess"}
    negative = {"no", "can't remember", "i don't know", "i forgot", "didn't", "haven't"}
    
    # Sliding window of 3-4 turns
    window_size = 4
    for i in range(len(patient_turns) - 1):
        window = patient_turns[i:i + window_size]
        
        has_affirm = any(any(a in turn for a in affirmative) for turn in window[:2])
        has_contradict = any(
            any(n in turn for n in negative) or any(u in turn for u in uncertain)
            for turn in window[1:]
        )
        
        if has_affirm and has_contradict:
            context = " → ".join(f'"{t[:50]}"' for t in window if t)
            flags.append(
                f"Patient changed from affirmative to uncertain/negative within {len(window)} turns: {context}"
            )
            break  # One flag per conversation is enough
    
    return flags


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


def _extract_medication_status(transcript: str, medications: list[str]) -> dict:
    """
    Extract medication mentions and whether they were taken.

    Strategy: scan EVERY mention of each medication in the transcript, track
    the signals found (positive / negative / indirect), and resolve using the
    LAST clear signal.  This handles the common "No… actually my pill box is
    empty" correction pattern without misclassifying it as 'not taken'.

    Args:
        medications: Lowercase medication names from the patient's profile.
                     An empty list means no medications are tracked.
    """
    text_lower = transcript.lower()
    meds_mentioned = []
    discussed = False

    # Positive signals — direct confirmation or indirect evidence
    _TAKEN_WORDS = [
        "took", "taken", "had my", "just took", "already took",
        "yes", "yeah", "yep", "i did", "i have",
    ]
    # Indirect / inferred confirmation (e.g. empty pill box means it was taken)
    _INDIRECT_TAKEN = [
        "pill box is empty", "pillbox is empty", "pill box empty",
        "pillbox empty", "it's empty", "its empty",
        "i must have taken", "must have taken", "already done",
    ]
    # Negative signals
    _MISSED_WORDS = [
        "missed", "forgot", "didn't take", "haven't taken",
        "not yet", "not taken", "no,", "no i", "no,\n",
    ]

    CONTEXT_WINDOW = 100  # chars on each side of a mention to check

    for med in medications:
        if med not in text_lower:
            continue

        discussed = True
        # Collect every start position where this medication appears
        positions = []
        start = 0
        while True:
            idx = text_lower.find(med, start)
            if idx == -1:
                break
            positions.append(idx)
            start = idx + 1

        # Evaluate signal at each position; keep a running 'last_signal'
        last_signal: bool | None = None
        was_corrected = False

        for idx in positions:
            ctx_start = max(0, idx - CONTEXT_WINDOW)
            ctx_end = min(len(text_lower), idx + len(med) + CONTEXT_WINDOW)
            ctx = text_lower[ctx_start:ctx_end]

            is_positive  = any(w in ctx for w in _TAKEN_WORDS)
            is_indirect  = any(w in text_lower for w in _INDIRECT_TAKEN)  # whole transcript
            is_negative  = any(w in ctx for w in _MISSED_WORDS)

            if is_indirect or is_positive:
                if last_signal is False:
                    was_corrected = True   # denial was reversed
                last_signal = True
            elif is_negative:
                last_signal = False
            # If neither, leave last_signal unchanged (ambiguous mention)

        taken = last_signal  # None if no clear signal at all

        # Build a human-readable note for this medication
        med_name = med.title()
        if taken is True and was_corrected:
            note = f"She initially said no to {med_name} but later confirmed she took it (pill box was empty)."
        elif taken is True:
            note = f"She confirmed she took her {med_name}."
        elif taken is False:
            note = f"She said she did not take her {med_name}."
        else:
            note = f"She mentioned {med_name} but didn't clearly confirm whether she took it."

        meds_mentioned.append({"name": med_name, "taken": taken, "note": note})

    # Aggregate notes
    notes = " ".join(m["note"] for m in meds_mentioned) if meds_mentioned else ""

    return {
        "discussed": discussed,
        "medications_mentioned": meds_mentioned,
        "notes": notes.strip(),
    }


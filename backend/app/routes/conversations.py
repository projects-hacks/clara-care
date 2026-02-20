"""
Conversation API Routes
Endpoints for conversation history and details
"""

import re
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# Data store and cognitive pipeline will be injected as dependencies
_data_store = None
_cognitive_pipeline = None


def get_data_store():
    """Dependency to get data store"""
    if _data_store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    return _data_store


def get_cognitive_pipeline():
    """Dependency to get cognitive pipeline"""
    return _cognitive_pipeline


def set_data_store(store):
    """Set the data store (called during app initialization)"""
    global _data_store
    _data_store = store


def set_cognitive_pipeline(pipeline):
    """Set the cognitive pipeline (called during app initialization)"""
    global _cognitive_pipeline
    _cognitive_pipeline = pipeline


# ---------------------------------------------------------------------------
# Summary normalizer — strips raw AI preamble from stored summaries
# ---------------------------------------------------------------------------

_SUMMARY_NOISE = [
    # "A wellness check-in phone call between Clara... "
    re.compile(r"A wellness check-in phone call between Clara[^.]+\.\s*", re.I),
    # "between Clara (an AI companion)..."
    re.compile(r"between Clara \(an AI companion\)[^,.]*, ?", re.I),
    # "Summarizing the call, Clara..." or just "Summarizing the call,"
    re.compile(r"Summarizing the call,?\s*Clara[^.]+\.\s*", re.I),
    re.compile(r"Summarizing the call,?\s*", re.I),
    # "discussed topics such as mood, stress..."
    re.compile(r"discussed topics such as [^.]+\.\s*", re.I),
    # "(an AI companion)"
    re.compile(r"\(an AI companion\)", re.I),
    # "Clara asks" sentence starts
    re.compile(r"^Clara asks[^.]+\.\s*", re.I | re.M),
    # "A customer named Clara talks to <name> about..." style preamble
    re.compile(r"A customer named Clara[^.]+\.\s*", re.I),
    # --- Deepgram generic-label structural preambles ---
    # "A caller and a host discuss a wellness phone call with an elderly adult."
    re.compile(r"A (?:caller|customer) and (?:a |the )?host discuss(?:es)?.*?\.\s*", re.I),
    # "They discuss the importance of..." / "They also talk about..."
    re.compile(r"(?:They|The host and (?:the )?caller) (?:also )?(?:discuss(?:es)?|talk(?:s)? about).*?\.\s*", re.I),
    # "They discuss" mid-sentence (leftover)
    re.compile(r"They discuss .*?\.\s*", re.I),
    # "Patient discussed:" fallback prefix
    re.compile(r"^Patient discussed:\s*", re.I),
    # "Topic: " prefix
    re.compile(r"^Topic:\s*", re.I),
]

# Inline Clara references → "the companion"
_CLARA_REF = re.compile(r"\bClara\b")

# Replace "the patient" with she/her based on position — subject vs object
_THE_PATIENT_SUBJECT = re.compile(r"\bThe patient\b")   # sentence-start (capitalised)
_THE_PATIENT_OBJECT  = re.compile(r"\bthe patient\b")   # mid-sentence (lowercase)

# Fix "their" when clearly referring to the patient
_THEIR_POSSESSIVE = re.compile(r"\btheir\b", re.I)




def _clean_summary(raw: str) -> str:
    """
    Strip AI-system preamble and persona references from a stored summary.
    Returns a clean, family-friendly third-person description.
    """
    if not raw:
        return raw

    text = raw.strip()
    
    # Transform Deepgram structural preambles into personalized summaries
    # Step 1: Remove generic openers entirely
    text = re.sub(
        r"A (?:caller|customer) and (?:a |the )?host discuss(?:es)? a wellness phone call "
        r"with an elderly (?:adult|patient|woman|man)\.\s*",
        "", text, flags=re.I
    )
    # "A caller named Summarizes a wellness phone call ..." — Deepgram treats verb as name
    # Also handles: "A caller named <Name> summarizes..."
    text = re.sub(
        r"A (?:caller|customer) named \w+\s+(?:a |the )?(?:wellness )?(?:phone )?(?:call|check-in)[^.]+\.\s*",
        "", text, flags=re.I
    )
    text = re.sub(
        r"A (?:caller|customer) named \w+ (?:summarizes|describes|discusses|talks about)[^.]+\.\s*",
        "", text, flags=re.I
    )
    # "A customer named Clara talks to <name> about..." — already in _SUMMARY_NOISE but reinforce
    text = re.sub(r"A customer named Clara[^.]+\.\s*", "", text, flags=re.I)

    # Step 2: Transform "They discuss the importance of X" → "She talked about X"
    text = re.sub(
        r"They discuss(?:es)? the importance of ",
        "She talked about ", text, flags=re.I
    )
    # Step 3: Transform "They also talk about the importance of X" → "She also mentioned X"
    text = re.sub(
        r"They also (?:talk|talked) about the importance of ",
        "She also mentioned ", text, flags=re.I
    )
    # Step 4: Transform remaining "They also talk/discuss/mention X" → "She also talked about X"
    text = re.sub(
        r"They also (?:talk|talked|discuss(?:es)?|mention(?:ed)?) (?:about )?",
        "She also talked about ", text, flags=re.I
    )
    # Step 5: Transform "They discuss X" → "She talked about X"
    text = re.sub(
        r"They discuss(?:es)? ",
        "She talked about ", text, flags=re.I
    )

    # Step 6: Replace impersonal role labels
    # "the representative" / "the host" → "Clara" (more natural than 'the companion')
    text = re.sub(r"\bthe representative\b", "Clara", text, flags=re.I)
    # NOTE: do NOT replace "Clara" with "the companion" — it garbles natural summaries
    # e.g. "Clara and Emily discussed lunch" should stay as-is

    # Step 7: Replace Deepgram generic patient labels → pronouns
    text = re.sub(r"\bthe elderly (?:adult|patient|woman|man)\b", "she", text, flags=re.I)
    text = re.sub(r"\bthe (?:caller|customer)\b", "she", text, flags=re.I)
    text = _THE_PATIENT_SUBJECT.sub("She", text)
    text = _THE_PATIENT_OBJECT.sub("her", text)
    text = _THEIR_POSSESSIVE.sub("her", text)

    # Step 8: Strip filler closing sentences
    text = re.sub(
        r"The call (?:ends|ended) with (?:her|she) (?:thanking|saying)[^.]+\.\s*",
        "", text, flags=re.I
    )

    # Step 9: Strip noise pattern list (iterative)
    changed = True
    while changed:
        changed = False
        for pattern in _SUMMARY_NOISE:
            new = pattern.sub("", text).strip()
            if new != text:
                text = new
                changed = True


    # Clean up spacing artefacts
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Capitalise first letter of each sentence  
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s[0].upper() + s[1:] if s else s for s in sentences]
    text = " ".join(sentences)

    # Ensure ends with a period
    if text and text[-1] not in (".", "!", "?"):
        text += "."

    return text


async def _normalize_conversation(conv: dict, store) -> dict:
    """Normalize a conversation record before serving it to the frontend."""
    if not conv:
        return conv

    summary = conv.get("summary", "")
    clean = _clean_summary(summary)
    
    # Fallback: if summary is missing or empty after cleaning (e.g. it was entirely noise)
    if not clean:
        try:
            digest = await store.get_latest_wellness_digest(conv.get("patient_id"))
            if digest and digest.get("conversation_id") == conv.get("id"):
                highlights = digest.get("highlights", [])
                if highlights:
                    from app.routes.wellness import _clean_highlight
                    clean_lines = [_clean_highlight(h) for h in highlights]
                    clean_lines = [line for line in clean_lines if len(line) > 10]
                    clean = " ".join(clean_lines)
        except Exception:
            pass

    # If we generated a fallback or cleaned an existing one, update the dict
    if clean != summary or not conv.get("summary"):
        conv = dict(conv)
        conv["summary"] = clean

    return conv


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("")
async def list_conversations(
    patient_id: str = Query(..., description="Patient ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get paginated list of conversations for a patient

    Query params:
        - patient_id: Patient identifier
        - limit: Max results (1-100, default 10)
        - offset: Pagination offset (default 0)
    """
    store = get_data_store()

    conversations = await store.get_conversations(patient_id, limit=limit, offset=offset)
    normalized_convs = []
    for c in conversations:
        normalized_convs.append(await _normalize_conversation(c, store))

    return {
        "patient_id": patient_id,
        "conversations": normalized_convs,
        "count": len(conversations),
        "limit": limit,
        "offset": offset
    }


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get full conversation details by ID

    Returns:
        - Full transcript
        - Cognitive metrics
        - Summary and mood
        - Timestamp and duration
    """
    store = get_data_store()

    conversation = await store.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return await _normalize_conversation(conversation, store)


@router.post("")
async def create_conversation(conversation: dict):
    """
    Create a new conversation record

    Body: Conversation object with transcript, metrics, etc.
    If cognitive pipeline is available, will run full analysis.

    Required fields:
        - patient_id
        - transcript
        - duration
    Optional fields:
        - summary
        - detected_mood
        - response_times
    """
    store = get_data_store()
    pipeline = get_cognitive_pipeline()

    # Validate required fields
    required_fields = ["patient_id", "transcript", "duration"]
    for field in required_fields:
        if field not in conversation:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )

    # If cognitive pipeline is available, run full analysis
    if pipeline:
        result = await pipeline.process_conversation(
            patient_id=conversation["patient_id"],
            transcript=conversation["transcript"],
            duration=conversation["duration"],
            summary=conversation.get("summary", ""),
            detected_mood=conversation.get("detected_mood", "neutral"),
            response_times=conversation.get("response_times"),
            conversation_id=conversation.get("id")
        )

        if result.get("success"):
            return {
                "success": True,
                "conversation_id": result["conversation_id"],
                "cognitive_score": result.get("cognitive_score"),
                "alerts_generated": result.get("alerts_generated", 0)
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Pipeline processing failed")
            )
    else:
        # Fallback: just save raw conversation (no cognitive analysis)
        conversation_id = await store.save_conversation(conversation)

        return {
            "success": True,
            "conversation_id": conversation_id,
            "note": "Saved without cognitive analysis (pipeline not available)"
        }

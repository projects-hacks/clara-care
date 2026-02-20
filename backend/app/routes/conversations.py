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
    re.compile(r"A (?:caller|customer) and (?:a |the )?host discuss(?:es)?[^.]+\.\s*", re.I),
    # "They discuss the importance of..." / "They also talk about..."
    re.compile(r"^(?:They|The host and (?:the )?caller) (?:also )?(?:discuss(?:es)?|talk(?:s)? about)[^.]+\.\s*", re.I | re.M),
    # "They discuss" mid-sentence (leftover)
    re.compile(r"^They discuss [^.]+\.\s*", re.I),
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

    # Strip leading noise phrases iteratively until none match
    changed = True
    while changed:
        changed = False
        for pattern in _SUMMARY_NOISE:
            new = pattern.sub("", text).strip()
            if new != text:
                text = new
                changed = True

    # Replace remaining inline "Clara" references
    text = _CLARA_REF.sub("the companion", text)
    # Replace Deepgram generic persona labels → pronouns
    text = re.sub(r"\bthe elderly (?:adult|patient|woman|man)\b", "she", text, flags=re.I)
    text = re.sub(r"\bthe (?:caller|customer|host and (?:the )?caller)\b", "she", text, flags=re.I)
    # Replace "The patient" (sentence start) → "She"
    text = _THE_PATIENT_SUBJECT.sub("She", text)
    # Replace "the patient" (mid-sentence) → "her"
    text = _THE_PATIENT_OBJECT.sub("her", text)
    # Replace "their" → "her" (patient is female)
    text = _THEIR_POSSESSIVE.sub("her", text)


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


def _normalize_conversation(conv: dict) -> dict:
    """Normalize a conversation record before serving it to the frontend."""
    if not conv:
        return conv

    summary = conv.get("summary", "")
    clean = _clean_summary(summary)
    if clean != summary:
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
    conversations = [_normalize_conversation(c) for c in conversations]

    return {
        "patient_id": patient_id,
        "conversations": conversations,
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

    return _normalize_conversation(conversation)


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

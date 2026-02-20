"""
Wellness & Cognitive Trends API Routes
Endpoints for wellness digests and cognitive trend data
"""

import re
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["wellness"])

# Data store will be injected as dependency
_data_store = None


def get_data_store():
    """Dependency to get data store"""
    if _data_store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    return _data_store


def set_data_store(store):
    """Set the data store (called during app initialization)"""
    global _data_store
    _data_store = store


# ---------------------------------------------------------------------------
# Legacy highlight/recommendation normalizer
# Rewrites old technical text in stored wellness digests at read-time.
# ---------------------------------------------------------------------------

_NOISE_PHRASES = [
    re.compile(r"Clara \(an AI companion\)", re.I),
    re.compile(r"between Clara and", re.I),
    re.compile(r"an AI companion", re.I),
    re.compile(r"Summarizing the call,?", re.I),
    re.compile(r"Safety concerns detected:\s*Safety keyword '[^']+': \"[^\"]*\"", re.I),
    re.compile(r"Loneliness expressed:\s*", re.I),
    re.compile(r"Overall sentiment:\s*\w+\s*\(score:\s*[\d.]+\)", re.I),
    re.compile(r"Low conversation coherence \([\d.]+\)", re.I),
    re.compile(r"Memory inconsistency detected[:\s]*", re.I),
    re.compile(r"Action needed:\s*Confabulation detected:.*", re.I),
    re.compile(r"Action needed:\s*Wants family connection:.*", re.I),
    re.compile(r"Engagement level:\s*\w+\.", re.I),
    re.compile(r"Medication discussed:", re.I),
]

_REPLACEMENT_MAP = [
    # Safety concerns — raw keyword dump → warm advisory
    (
        re.compile(r"Safety concerns detected:.*", re.I | re.DOTALL),
        "⚠️ She said something during this call that is a cause for concern. "
        "Please review the alert and consider reaching out to her soon."
    ),
    # Loneliness
    (
        re.compile(r"Loneliness expressed:\s*.+", re.I),
        "She expressed feelings of loneliness or missing people she loves."
    ),
    # Raw sentiment score
    (
        re.compile(r"Overall sentiment:\s*(\w+)\s*\(score:\s*[\d.+-]+\)", re.I),
        lambda m: {
            "positive": "Her overall tone during the call felt upbeat and positive.",
            "negative": "Her overall tone during the call felt low or subdued.",
        }.get(m.group(1).lower(), "Her overall tone during the call felt calm and neutral.")
    ),
    # Engagement level — raw enum
    (
        re.compile(r"Engagement level:\s*(\w+)\.", re.I),
        lambda m: {
            "high": "She was chatty and engaged throughout the call — a great sign.",
            "medium": "She had a comfortable, relaxed conversation today.",
            "low": "She was quieter than usual. A follow-up check-in might be helpful.",
        }.get(m.group(1).lower(), "")
    ),
    # Low coherence with raw number
    (
        re.compile(r"⚠️?\s*Low conversation coherence \([\d.]+\)[^.]*\.", re.I),
        "⚠️ Today's conversation was harder to follow than usual — she jumped between topics "
        "and had difficulty staying on one thread. This may be worth a gentle check-in."
    ),
    # Old memory inconsistency one-liner
    (
        re.compile(r"⚠️?\s*Memory inconsistency detected during conversation\.", re.I),
        "⚠️ She gave some conflicting answers during the conversation. "
        "This can sometimes be an early sign of short-term memory changes and is worth watching."
    ),
    # Action needed: confabulation / raw transcript
    (
        re.compile(r"Action needed:\s*Confabulation detected:.*", re.I),
        "⚠️ She gave some conflicting answers during the conversation — worth watching over time."
    ),
    (
        re.compile(r"Action needed:\s*Wants family connection:.*", re.I),
        "She expressed a desire to connect with family soon — a short call or visit would mean a lot."
    ),
    (
        re.compile(r"Action needed:\s*Expressed feelings of loneliness", re.I),
        "She mentioned feeling lonely. Reaching out with a call or visit soon would be meaningful."
    ),
    # Patient engagement — old phrasing
    (
        re.compile(r"Patient was highly engaged and talkative\.", re.I),
        "She was chatty and engaged throughout the call — a great sign."
    ),
    (
        re.compile(r"Patient had moderate engagement during the call\.", re.I),
        "She had a comfortable, relaxed conversation today."
    ),
    (
        re.compile(r"Patient was quieter than usual during the call\.", re.I),
        "She was quieter than usual. A follow-up check-in might be helpful."
    ),
    # Medication phrasing
    (
        re.compile(r"Medication discussed:", re.I),
        "Medication update:"
    ),
    (
        re.compile(r"Medication was discussed during the call\.", re.I),
        "Medication was briefly mentioned during the call."
    ),
    # Old recommendation phrasing — rewrite to concrete family actions
    (
        re.compile(r"Conversation coherence was low\..*", re.I),
        "Consider giving her a call yourself today — a familiar voice can help when she's having a harder time expressing herself."
    ),
    (
        re.compile(r"Conversation coherence has declined compared to baseline\..*", re.I),
        "This pattern has continued for a few calls — it may be worth bringing up at her next doctor's appointment."
    ),
    (
        re.compile(r"Vocabulary diversity has decreased compared to baseline\..*", re.I),
        "Her language has felt more limited lately. A call or visit where you share stories, photos, or news could give her something richer to engage with."
    ),
    (
        re.compile(r"Several word-finding pauses were noted\..*", re.I),
        "If this keeps happening over the next few days, mention it to her doctor at the next scheduled visit."
    ),
    (
        re.compile(r"Some repetition was detected\..*", re.I),
        "Try giving her a call and bringing up something new — upcoming family plans, a shared memory, or something she's looking forward to."
    ),
]
_NOISE_STRIP_PATTERNS = [
    # Full sentence: "A wellness check-in phone call between Clara (an AI companion) and an elderly patient discussed ..."
    re.compile(
        r"A wellness check-in phone call between Clara[^.]+\.\s*",
        re.I
    ),
    # Partial: "between Clara (an AI companion) and ..."
    re.compile(r"between Clara \(an AI companion\) and an elderly patient[,.]?\s*", re.I),
    # "Summarizing the call, Clara ..." — remove up to the end of that clause
    re.compile(r"Summarizing the call,?\s*Clara[^.]+\.\s*", re.I),
    # Bare "Summarizing the call,"
    re.compile(r"Summarizing the call,?\s*", re.I),
    # Deepgram caller and host
    re.compile(r"A (?:caller|customer) and (?:a |the )?host discuss(?:es)?[^.]+\.\s*", re.I),
    re.compile(r"(?:They|The host and (?:the )?caller) (?:also )?(?:discuss(?:es)?|talk(?:s)? about)[^.]+\.\s*", re.I),
    re.compile(r"They discuss [^.]+\.\s*", re.I),
]

_THE_PATIENT_SUBJECT = re.compile(r"\bThe patient\b")
_THE_PATIENT_OBJECT  = re.compile(r"\bthe patient\b")
_THEIR_POSSESSIVE = re.compile(r"\btheir\b", re.I)


def _clean_highlight(h: str) -> str:
    """Apply all normalisation rules to a single highlight string."""
    if not h:
        return h
    # First try the full replacement map
    for pattern, replacement in _REPLACEMENT_MAP:
        if pattern.search(h):
            if callable(replacement):
                m = pattern.search(h)
                return replacement(m)
            return replacement
    # Then strip noise phrases that are partial prefixes
    for pattern in _NOISE_STRIP_PATTERNS:
        h = pattern.sub("", h).strip()

    # Apply pronoun replacements
    h = _THE_PATIENT_SUBJECT.sub("She", h)
    h = _THE_PATIENT_OBJECT.sub("her", h)
    h = _THEIR_POSSESSIVE.sub("her", h)
    h = re.sub(r"\bthe elderly (?:adult|patient|woman|man)\b", "she", h, flags=re.I)
    h = re.sub(r"\bthe (?:caller|customer|host and (?:the )?caller)\b", "she", h, flags=re.I)

    # Capitalise and fix trailing punctuation
    if h and not h[0].isupper():
        h = h[0].upper() + h[1:]
    if h and not h.endswith(('.', '!', '?', '️')):
        h += '.'
    return h


def _normalize_digest(digest: dict) -> dict:
    """
    Normalize legacy highlights and recommendations in a stored digest.
    Returns a shallow-copy dict with cleaned lists; original is not mutated.
    """
    if not digest:
        return digest

    highlights = digest.get("highlights", [])
    recommendations = digest.get("recommendations", [])

    cleaned_highlights = []
    for h in highlights:
        c = _clean_highlight(h)
        # Drop empty or very short strings left after stripping
        if c and len(c) > 10:
            cleaned_highlights.append(c)

    cleaned_recs = []
    for r in recommendations:
        c = _clean_highlight(r)
        if c and len(c) > 10:
            cleaned_recs.append(c)

    if cleaned_highlights != highlights or cleaned_recs != recommendations:
        digest = dict(digest)
        digest["highlights"] = cleaned_highlights
        digest["recommendations"] = cleaned_recs

    return digest


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/wellness-digests")
async def list_wellness_digests(
    patient_id: str = Query(..., description="Patient ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get paginated list of wellness digests for a patient

    Query params:
        - patient_id: Patient identifier
        - limit: Max results (1-100, default 10)
        - offset: Pagination offset (default 0)
    """
    store = get_data_store()

    digests = await store.get_wellness_digests(patient_id, limit=limit, offset=offset)
    digests = [_normalize_digest(d) for d in digests]

    return {
        "patient_id": patient_id,
        "digests": digests,
        "count": len(digests),
        "limit": limit,
        "offset": offset
    }


@router.get("/wellness-digests/latest")
async def get_latest_digest(patient_id: str = Query(..., description="Patient ID")):
    """
    Get the most recent wellness digest for a patient
    """
    store = get_data_store()

    digest = await store.get_latest_wellness_digest(patient_id)

    if not digest:
        raise HTTPException(status_code=404, detail="No wellness digests found")

    return _normalize_digest(digest)


@router.get("/cognitive-trends")
async def get_cognitive_trends(
    patient_id: str = Query(..., description="Patient ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include")
):
    """
    Get time-series cognitive metrics for charting

    Returns data points for the last N days, suitable for Recharts or similar

    Query params:
        - patient_id: Patient identifier
        - days: Number of days to include (1-365, default 30)
    """
    store = get_data_store()

    # Get baseline for reference
    baseline = await store.get_cognitive_baseline(patient_id)

    # Get trends data
    data_points = await store.get_cognitive_trends(patient_id, days=days)

    return {
        "patient_id": patient_id,
        "period_days": days,
        "data_points": data_points,
        "baseline": {
            "vocabulary_diversity": baseline.get("vocabulary_diversity") if baseline else None,
            "topic_coherence": baseline.get("topic_coherence") if baseline else None,
            "repetition_rate": baseline.get("repetition_rate") if baseline else None
        } if baseline else None
    }

"""
Alerts API Routes
Endpoints for viewing and managing alerts
"""

import re
from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

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
# Legacy description normalizer
# Converts old technical alert descriptions to plain-English equivalents.
# This runs at read-time so any alert stored in Sanity before the code
# update is automatically upgraded when served to the dashboard.
# ---------------------------------------------------------------------------

_LEGACY_PATTERNS = [
    # Raw coherence score  e.g. "Low topic coherence detected (0.24)..."
    re.compile(r"low topic coherence detected", re.I),
    # Raw percentage change  e.g. "Topic coherence has declined by 72.2%..."
    re.compile(r"(vocabulary diversity|topic coherence|repetition rate|"
               r"word.finding pauses?|response latency) has (declined|increased) by \d", re.I),
    # Raw baseline score  e.g. "Repetition rate increased to 0.10 (baseline: 0.05)"
    re.compile(r"\bbaseline[:\s]", re.I),
    # Raw transcript dump  e.g. "Memory inconsistency detected: Patient changed…"
    re.compile(r"memory inconsistency detected:", re.I),
    # Raw numeric metric  e.g. "Vocabulary diversity dropped below baseline (0.52 vs 0.63 baseline)"
    re.compile(r"\(0\.\d+ vs 0\.\d+", re.I),
    # Latency in seconds  e.g. "Response latency increased to 2.4s"
    re.compile(r"response latency increased to \d+\.\d+s", re.I),
]

_PLAIN_DESCRIPTIONS = {
    "coherence_drop": (
        "Today's conversation was noticeably harder to follow than usual. "
        "She jumped between topics frequently and had difficulty staying on the same thread. "
        "This can be a sign of confusion or difficulty concentrating, "
        "and may be worth a gentle check-in."
    ),
    "vocabulary_shrinkage": (
        "She has been using a more limited range of words than usual across recent conversations. "
        "This can sometimes happen when someone is feeling tired, stressed, or experiencing "
        "subtle memory changes. It's worth keeping an eye on."
    ),
    "vocabulary_decline": (
        "She has been using a more limited range of words than usual across recent conversations. "
        "This can sometimes happen when someone is feeling tired, stressed, or experiencing "
        "subtle memory changes. It's worth keeping an eye on."
    ),
    "repetition_increase": (
        "She has been repeating certain stories or phrases more often than usual across recent "
        "conversations. Repetition can sometimes be a sign of something on her mind, or it may "
        "reflect short-term memory changes worth watching."
    ),
    "word_finding_difficulty": (
        "She has been stopping more often to search for words during recent conversations. "
        "You might notice phrases like \"um,\" \"you know,\" or sentences that trail off. "
        "While this can be normal with age, the increase compared to her usual pattern is worth noting."
    ),
    "response_delay": (
        "She has been taking longer than usual to respond in conversations. "
        "This can be a sign of fatigue, reduced concentration, or difficulty processing what was said."
    ),
    "response_latency": (
        "She has been taking longer than usual to respond in conversations. "
        "This can be a sign of fatigue, reduced concentration, or difficulty processing what was said."
    ),
    "cognitive_decline": (
        "During today's call, she gave conflicting answers to the same question — "
        "first agreeing, then expressing doubt or saying the opposite. "
        "This kind of inconsistency can sometimes be an early sign of short-term memory difficulty "
        "and is worth watching over the coming conversations."
    ),
}

_PLAIN_ACTIONS = {
    "coherence_drop": (
        "Call her yourself today. Keep it light and ask one thing at a time — "
        "a familiar voice makes a real difference."
    ),
    "vocabulary_shrinkage": (
        "Give her a call and chat about something she loves — "
        "a favourite memory, a family story, or what’s been on her mind."
    ),
    "vocabulary_decline": (
        "Give her a call and chat about something she loves — "
        "a favourite memory, a family story, or what’s been on her mind."
    ),
    "repetition_increase": (
        "Give her a ring and bring up something new — upcoming family plans, "
        "a shared memory, or something she’s looking forward to."
    ),
    "word_finding_difficulty": (
        "Call her and let the conversation flow at her pace. "
        "If this keeps happening, mention it to her doctor at the next visit."
    ),
    "response_delay": (
        "Check in with her — a short call to ask how she’s feeling today goes a long way."
    ),
    "response_latency": (
        "Check in with her — a short call to ask how she’s feeling today goes a long way."
    ),
    "cognitive_decline": (
        "Bring this up at her next doctor’s appointment — mention the dates and what you’ve noticed."
    ),
    "distress": (
        "Call her right away and let her know you’re thinking of her. "
        "If she seems very distressed, consider arranging a visit or contacting her caregiver."
    ),
    "mood_distress": (
        "Call her right away and let her know you’re thinking of her. "
        "If she seems very distressed, consider arranging a visit."
    ),
    "confusion_detected": (
        "Give her a reassuring call or, if possible, pop in for a visit. "
        "Let her doctor know if this is becoming more frequent."
    ),
    "social_connection": (
        "She’s missing you. Give her a call or plan a visit — "
        "even just 10 minutes together means a lot."
    ),
    "emergency": (
        "Call her immediately. If you can’t reach her, "
        "contact emergency services or her on-site caregiver."
    ),
    "fall": (
        "Call her immediately to confirm she is safe. "
        "If you can’t reach her, contact her caregiver or a neighbour right away."
    ),
}

_DEFAULT_ACTION = "Give her a call to check in, and mention this to her doctor if it keeps happening."


def _is_legacy_description(description: str) -> bool:
    """Return True if the description contains old technical jargon."""
    if not description:
        return False
    return any(p.search(description) for p in _LEGACY_PATTERNS)


def _normalize_alert(alert: dict) -> dict:
    """
    If an alert has a legacy technical description, replace it with plain English.
    Always refreshes suggested_action from _PLAIN_ACTIONS so stale Sanity values
    are overwritten with the latest family-member-appropriate advice.
    Returns a (possibly mutated copy of the) alert dict.
    """
    alert_type = alert.get("alert_type", "")
    description = alert.get("description", "")

    if _is_legacy_description(description):
        plain = _PLAIN_DESCRIPTIONS.get(alert_type)
        if plain:
            alert = dict(alert)  # shallow copy — don't mutate the store
            alert["description"] = plain

    # Always re-derive suggested_action — overwrites any stale Sanity value
    fresh_action = _PLAIN_ACTIONS.get(alert_type, _DEFAULT_ACTION)
    if alert.get("suggested_action") != fresh_action:
        alert = dict(alert)
        alert["suggested_action"] = fresh_action

    return alert


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("")
async def list_alerts(
    patient_id: str = Query(..., description="Patient ID"),
    severity: Optional[str] = Query(None, description="Filter by severity (low/medium/high)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get alerts for a patient

    Query params:
        - patient_id: Patient identifier
        - severity: Optional severity filter (low, medium, high)
        - limit: Max results (1-100, default 20)
        - offset: Pagination offset (default 0)
    """
    store = get_data_store()

    # Validate severity if provided
    if severity and severity not in ["low", "medium", "high"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid severity. Must be: low, medium, or high"
        )

    alerts = await store.get_alerts(
        patient_id,
        severity=severity,
        limit=limit,
        offset=offset
    )

    # Normalize any legacy alerts before returning to the dashboard
    alerts = [_normalize_alert(a) for a in alerts]

    return {
        "patient_id": patient_id,
        "alerts": alerts,
        "count": len(alerts),
        "severity_filter": severity,
        "limit": limit,
        "offset": offset
    }


@router.patch("/{alert_id}")
async def acknowledge_alert(alert_id: str, body: dict):
    """
    Mark an alert as acknowledged

    Body:
        - acknowledged_by: ID of person acknowledging (family member ID)
    """
    store = get_data_store()

    acknowledged_by = body.get("acknowledged_by")
    if not acknowledged_by:
        raise HTTPException(
            status_code=400,
            detail="acknowledged_by is required"
        )

    # Update alert
    updates = {
        "acknowledged": True,
        "acknowledged_at": datetime.now(UTC).isoformat(),
        "acknowledged_by": acknowledged_by
    }

    success = await store.update_alert(alert_id, updates)

    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {
        "success": True,
        "alert_id": alert_id,
        "acknowledged": True
    }

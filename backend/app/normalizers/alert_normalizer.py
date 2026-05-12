import re

_LEGACY_PATTERNS = [
    re.compile(r"low topic coherence detected", re.I),
    re.compile(r"(vocabulary diversity|topic coherence|repetition rate|word.finding pauses?|response latency) has (declined|increased) by \d", re.I),
    re.compile(r"\bbaseline[:\s]", re.I),
    re.compile(r"memory inconsistency detected:", re.I),
    re.compile(r"\(0\.\d+ vs 0\.\d+", re.I),
    re.compile(r"response latency increased to \d+\.\d+s", re.I),
]

_PLAIN_DESCRIPTIONS = {
    "coherence_drop": "Today's conversation was noticeably harder to follow than usual. She jumped between topics frequently and had difficulty staying on the same thread. This can be a sign of confusion or difficulty concentrating, and may be worth a gentle check-in.",
    "vocabulary_shrinkage": "She has been using a more limited range of words than usual across recent conversations. This can sometimes happen when someone is feeling tired, stressed, or experiencing subtle memory changes. It's worth keeping an eye on.",
    "vocabulary_decline": "She has been using a more limited range of words than usual across recent conversations. This can sometimes happen when someone is feeling tired, stressed, or experiencing subtle memory changes. It's worth keeping an eye on.",
    "repetition_increase": "She has been repeating certain stories or phrases more often than usual across recent conversations. Repetition can sometimes be a sign of something on her mind, or it may reflect short-term memory changes worth watching.",
    "word_finding_difficulty": "She has been stopping more often to search for words during recent conversations. You might notice phrases like \"um,\" \"you know,\" or sentences that trail off. While this can be normal with age, the increase compared to her usual pattern is worth noting.",
    "response_delay": "She has been taking longer than usual to respond in conversations. This can be a sign of fatigue, reduced concentration, or difficulty processing what was said.",
    "response_latency": "She has been taking longer than usual to respond in conversations. This can be a sign of fatigue, reduced concentration, or difficulty processing what was said.",
    "cognitive_decline": "During today's call, she gave conflicting answers to the same question — first agreeing, then expressing doubt or saying the opposite. This kind of inconsistency can sometimes be an early sign of short-term memory difficulty and is worth watching over the coming conversations.",
}

_PLAIN_ACTIONS = {
    "coherence_drop": "Call her yourself today. Keep it light and ask one thing at a time — a familiar voice makes a real difference.",
    "vocabulary_shrinkage": "Give her a call and chat about something she loves — a favourite memory, a family story, or what’s been on her mind.",
    "vocabulary_decline": "Give her a call and chat about something she loves — a favourite memory, a family story, or what’s been on her mind.",
    "repetition_increase": "Give her a ring and bring up something new — upcoming family plans, a shared memory, or something she’s looking forward to.",
    "word_finding_difficulty": "Call her and let the conversation flow at her pace. If this keeps happening, mention it to her doctor at the next visit.",
    "response_delay": "Check in with her — a short call to ask how she’s feeling today goes a long way.",
    "response_latency": "Check in with her — a short call to ask how she’s feeling today goes a long way.",
    "cognitive_decline": "Bring this up at her next doctor’s appointment — mention the dates and what you’ve noticed.",
    "distress": "Call her right away and let her know you’re thinking of her. If she seems very distressed, consider arranging a visit or contacting her caregiver.",
    "mood_distress": "Call her right away and let her know you’re thinking of her. If she seems very distressed, consider arranging a visit.",
    "confusion_detected": "Give her a reassuring call or, if possible, pop in for a visit. Let her doctor know if this is becoming more frequent.",
    "social_connection": "She’s missing you. Give her a call or plan a visit — even just 10 minutes together means a lot.",
    "emergency": "Call her immediately. If you can’t reach her, contact emergency services or her on-site caregiver.",
    "fall": "Call her immediately to confirm she is safe. If you can’t reach her, contact her caregiver or a neighbour right away.",
}

_DEFAULT_ACTION = "Give her a call to check in, and mention this to her doctor if it keeps happening."

def _is_legacy_description(description: str) -> bool:
    if not description:
        return False
    return any(p.search(description) for p in _LEGACY_PATTERNS)

def normalize_alert(alert: dict) -> dict:
    if not alert:
        return alert

    alert_type = alert.get("alert_type", "")
    description = alert.get("description", "")

    new_alert = dict(alert)

    if not description and alert_type == "social_connection":
        new_alert["description"] = "She asked to speak with you or a family member."
    elif _is_legacy_description(description):
        plain = _PLAIN_DESCRIPTIONS.get(alert_type)
        if plain:
            new_alert["description"] = plain

    action = _PLAIN_ACTIONS.get(alert_type, _DEFAULT_ACTION)
    if alert.get("suggested_action") != action:
        new_alert["suggested_action"] = action

    return new_alert

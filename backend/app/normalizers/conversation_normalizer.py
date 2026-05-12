import re

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
]

_SPEAKER_CLEANUP = [
    (re.compile(r"^(?:Speaker \d+|Clara|Caller|Host):\s*", re.I | re.M), ""),
]

def normalize_summary(raw_summary: str) -> str:
    """Removes AI preamble and robotic framing from summaries."""
    if not raw_summary:
        return ""
        
    cleaned = raw_summary
    for pattern in _SUMMARY_NOISE:
        cleaned = pattern.sub("", cleaned)
        
    cleaned = cleaned.replace("the patient", "she")
    cleaned = cleaned.replace("The patient", "She")
    
    # Capitalize first letter if needed
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
        
    return cleaned.strip()

def normalize_transcript(raw_transcript: str) -> str:
    """Cleans up raw transcript formatting for readability."""
    if not raw_transcript:
        return ""
        
    cleaned = raw_transcript
    for pattern, replacement in _SPEAKER_CLEANUP:
        cleaned = pattern.sub(replacement, cleaned)
        
    return cleaned.strip()

def normalize_conversation(conv: dict) -> dict:
    if not conv:
        return conv
        
    if "summary" in conv:
        conv["summary"] = normalize_summary(conv["summary"])
        
    if "transcript" in conv:
        conv["transcript"] = normalize_transcript(conv["transcript"])
        
    # We don't want to show raw float values in the UI, just the summary stats
    if "cognitive_metrics" in conv and conv["cognitive_metrics"]:
        # Round the metrics for cleaner UI display
        metrics = conv["cognitive_metrics"]
        for key in ["vocabulary_diversity", "topic_coherence", "repetition_rate"]:
            if metrics.get(key) is not None:
                metrics[key] = round(metrics[key], 2)
                
    return conv

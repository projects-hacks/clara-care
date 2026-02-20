"""
Shared utility functions for Cognitive Analysis
"""


# ── Pronoun helper ──────────────────────────────────────────────
# Returns a dict of pronoun forms derived from the patient's name.
# Used across pipeline, alerts, and notifications so nothing is
# hardcoded to a single gender.

_MALE_NAMES = {
    "mark", "james", "john", "robert", "michael", "william", "david",
    "richard", "joseph", "thomas", "charles", "christopher", "daniel",
    "matthew", "anthony", "andrew", "joshua", "kenneth", "kevin", "brian",
    "george", "edward", "ronald", "timothy", "jason", "jeffrey", "ryan",
    "jacob", "gary", "nicholas", "eric", "stephen", "larry", "justin",
    "scott", "brandon", "benjamin", "samuel", "raymond", "patrick", "frank",
    "henry", "jack", "peter", "paul", "carl", "roger", "albert", "arthur",
    "harry", "ralph", "eugene", "roy", "louis", "russell", "philip", "adam",
    "aaron", "sean", "howard", "fred", "tyler", "alan", "dylan", "bruce",
}

_FEMALE_NAMES = {
    "dorothy", "emily", "mary", "patricia", "jennifer", "linda", "barbara",
    "elizabeth", "susan", "jessica", "sarah", "karen", "nancy", "lisa",
    "betty", "margaret", "sandra", "ashley", "kimberly", "donna", "michelle",
    "carol", "amanda", "melissa", "deborah", "stephanie", "rebecca", "sharon",
    "laura", "cynthia", "kathleen", "amy", "shirley", "angela", "helen",
    "anna", "brenda", "pamela", "emma", "nicole", "katherine", "christine",
    "janet", "catherine", "maria", "heather", "diane", "ruth", "julie",
    "olivia", "joyce", "virginia", "victoria", "kelly", "lauren", "christina",
    "joan", "evelyn", "judith", "megan", "andrea", "cheryl", "hannah",
    "jacqueline", "martha", "gloria", "teresa", "ann", "sara", "madison",
    "frances", "kathryn", "janice", "jean", "abigail", "alice", "judy",
    "sophia", "grace", "denise", "amber", "doris", "marilyn", "danielle",
    "beverly", "isabella", "theresa", "diana", "natalie", "brittany", "charlotte",
    "marie", "kayla", "alexis", "lori", "clara",
}


def get_pronouns(patient_name: str | None = None) -> dict:
    """
    Return a dict of pronoun forms for the given patient name.

    Keys: sub, obj, pos, ref  (lowercase)
          Sub, Obj, Pos, Ref  (capitalized)

    Example for male:  {"sub": "he",  "obj": "him", "pos": "his",  "ref": "himself",
                        "Sub": "He",  "Obj": "Him", "Pos": "His",  "Ref": "Himself"}
    Example for female: {"sub": "she", "obj": "her", "pos": "her",  "ref": "herself",
                         "Sub": "She", "Obj": "Her", "Pos": "Her",  "Ref": "Herself"}
    """
    first = (patient_name or "").split()[0].strip().lower()

    if first in _MALE_NAMES:
        d = {"sub": "he", "obj": "him", "pos": "his", "ref": "himself"}
    elif first in _FEMALE_NAMES:
        d = {"sub": "she", "obj": "her", "pos": "her", "ref": "herself"}
    else:
        # Default to gender-neutral "they"
        d = {"sub": "they", "obj": "them", "pos": "their", "ref": "themselves"}

    # Capitalised variants
    d.update({k.capitalize(): v.capitalize() for k, v in d.items()})
    return d


def calculate_cognitive_score(metrics: dict) -> int:
    """
    Calculate composite cognitive score (0-100) from NLP metrics
    
    Formula (each component worth 25 points):
    - TTR component: vocabulary_diversity scaled 0.3-0.8 → 0-25 pts
    - Coherence component: topic_coherence scaled 0.4-1.0 → 0-25 pts  
    - Repetition component: repetition_rate (inverse) 0.0-0.3 → 25-0 pts
    - Word-finding component: word_finding_pauses (inverse) 0-10 → 25-0 pts
    
    Handles None values (from partial metrics) by using defaults
    
    Args:
        metrics: Dictionary with cognitive metrics
        
    Returns:
        Cognitive score (0-100)
    """
    # TTR score (higher is better) - use default 0.5 if None
    ttr = metrics.get("vocabulary_diversity")
    ttr = ttr if ttr is not None else 0.5
    ttr_score = max(0, min(25, ((ttr - 0.3) / 0.5) * 25))
    
    # Coherence score (higher is better) - use default 0.7 if None
    # Range widened to 0.15-0.85: phone conversations with short
    # responses ("Yeah", "Okay") naturally score low on embeddings
    coherence = metrics.get("topic_coherence")
    coherence = coherence if coherence is not None else 0.7
    coh_score = max(0, min(25, ((coherence - 0.15) / 0.70) * 25))
    
    # Repetition score (lower rate is better)
    # Range widened to 0.0-0.4: cross-conversation trigrams and
    # common phrases ("yeah yeah") inflate the rate for elderly speakers
    rep_rate = metrics.get("repetition_rate", 0.1)
    rep_score = max(0, min(25, ((1 - rep_rate - 0.6) / 0.4) * 25))
    
    # Word-finding score (fewer pauses is better)
    # Threshold raised to 15: elderly speakers use more fillers naturally
    pauses = metrics.get("word_finding_pauses", 0)
    wf_score = max(0, min(25, (1 - min(pauses / 15, 1.0)) * 25))
    
    total = int(ttr_score + coh_score + rep_score + wf_score)
    return max(0, min(100, total))

"""
Shared utility functions for Cognitive Analysis
"""


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

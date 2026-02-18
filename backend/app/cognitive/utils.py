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
    coherence = metrics.get("topic_coherence")
    coherence = coherence if coherence is not None else 0.7
    coh_score = max(0, min(25, ((coherence - 0.4) / 0.6) * 25))
    
    # Repetition score (lower rate is better)
    # Formula: (1 - rate - 0.7) normalizes 0.0-0.3 range to 0.3-0.0
    # The 0.7 constant is complement of max expected rate (1 - 0.3 = 0.7)
    # This maps: 0% repetition → 25 pts, 30% repetition → 0 pts
    rep_rate = metrics.get("repetition_rate", 0.1)
    rep_score = max(0, min(25, ((1 - rep_rate - 0.7) / 0.3) * 25))
    
    # Word-finding score (fewer pauses is better)
    pauses = metrics.get("word_finding_pauses", 0)
    wf_score = max(0, min(25, (1 - min(pauses / 10, 1.0)) * 25))
    
    total = int(ttr_score + coh_score + rep_score + wf_score)
    return max(0, min(100, total))

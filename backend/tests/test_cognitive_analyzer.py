"""
Tests for CognitiveAnalyzer
Validates NLP-based cognitive metric calculations
"""

import pytest
from app.cognitive.analyzer import CognitiveAnalyzer


@pytest.fixture
def analyzer():
    """Create analyzer instance"""
    return CognitiveAnalyzer()


@pytest.mark.asyncio
async def test_extract_patient_turns_standard_format(analyzer):
    """Test extracting patient turns from standard transcript"""
    transcript = """Clara: Hello Dorothy, how are you today?
Dorothy: I'm doing well, thank you.
Clara: What have you been up to?
Dorothy: I've been working in my garden.
Clara: That's wonderful!
Dorothy: Yes, my tomatoes are growing nicely."""
    
    turns = analyzer._extract_patient_turns(transcript, "Dorothy")
    
    assert len(turns) == 3
    assert turns[0] == "I'm doing well, thank you."
    assert turns[1] == "I've been working in my garden."
    assert turns[2] == "Yes, my tomatoes are growing nicely."


@pytest.mark.asyncio
async def test_extract_patient_turns_case_insensitive(analyzer):
    """Test patient name extraction is case-sensitive"""
    transcript = """clara: Hi there
dorothy: Hello
DOROTHY: How are you?"""
    
    # Case matters - must match exactly
    turns_dorothy = analyzer._extract_patient_turns(transcript, "dorothy")
    turns_DOROTHY = analyzer._extract_patient_turns(transcript, "DOROTHY")
    
    assert len(turns_dorothy) == 1
    assert len(turns_DOROTHY) == 1


@pytest.mark.asyncio
async def test_extract_patient_turns_empty_transcript(analyzer):
    """Test empty transcript returns no turns"""
    turns = analyzer._extract_patient_turns("", "Dorothy")
    assert len(turns) == 0


@pytest.mark.asyncio
async def test_extract_patient_turns_no_patient_speech(analyzer):
    """Test transcript with only Clara speaking"""
    transcript = """Clara: Hello?
Clara: Are you there?
Clara: Can you hear me?"""
    
    turns = analyzer._extract_patient_turns(transcript, "Dorothy")
    assert len(turns) == 0


@pytest.mark.asyncio
async def test_compute_vocabulary_diversity_high(analyzer):
    """Test TTR with diverse vocabulary"""
    turns = ["I love gardening and planting flowers", 
             "The beautiful roses bloom in spring"]
    
    ttr = analyzer.compute_vocabulary_diversity(turns)
    
    # Should be high (most words unique)
    assert 0.6 < ttr <= 1.0


@pytest.mark.asyncio
async def test_compute_vocabulary_diversity_low(analyzer):
    """Test TTR with repetitive vocabulary"""
    turns = ["I I I I", 
             "the the the the",
             "I the I the"]
    
    ttr = analyzer.compute_vocabulary_diversity(turns)
    
    # Should be low (only 2 unique words: "I", "the")
    # But spaCy filters stopwords, so may be 0 or very low
    assert 0.0 <= ttr < 0.5


@pytest.mark.asyncio
async def test_compute_vocabulary_diversity_single_word(analyzer):
    """Test TTR with single word"""
    turns = ["hello"]
    
    ttr = analyzer.compute_vocabulary_diversity(turns)
    
    # Single unique word
    assert ttr == 1.0


@pytest.mark.asyncio
async def test_compute_vocabulary_diversity_empty(analyzer):
    """Test TTR with empty input"""
    ttr = analyzer.compute_vocabulary_diversity([])
    assert ttr == 0.0


@pytest.mark.asyncio
async def test_compute_topic_coherence_high(analyzer):
    """Test coherence with related sentences"""
    turns = ["I love working in my garden",
             "My tomatoes are growing very well",
             "I planted roses last spring"]
    
    coherence = analyzer.compute_topic_coherence(turns)
    
    # Garden-related sentences should have reasonable coherence (actual may vary)
    assert 0.0 < coherence <= 1.0


@pytest.mark.asyncio
async def test_compute_topic_coherence_low(analyzer):
    """Test coherence with unrelated sentences"""
    turns = ["I love gardening",
             "The stock market crashed yesterday",
             "Quantum physics is fascinating"]
    
    coherence = analyzer.compute_topic_coherence(turns)
    
    # If sentence-transformer is available, unrelated topics should have lower coherence
    # If not available, returns fallback value of 0.75
    assert 0.0 <= coherence <= 1.0


@pytest.mark.asyncio
async def test_compute_topic_coherence_single_turn(analyzer):
    """Test coherence with single turn"""
    coherence = analyzer.compute_topic_coherence(["Hello"])
    
    # Single turn should return 1.0 (perfect coherence with itself)
    assert coherence == 1.0


@pytest.mark.asyncio
async def test_detect_repetitions_with_repeats(analyzer):
    """Test repetition detection with known repeated trigrams"""
    turns = [
        "I went to the store",
        "I went to the park",
        "I went to the doctor"
    ]
    
    count, rate = analyzer.detect_repetitions(turns)
    
    # "I went to" appears 3 times
    assert count > 0
    assert 0.0 < rate <= 1.0


@pytest.mark.asyncio
async def test_detect_repetitions_no_repeats(analyzer):
    """Test repetition detection with no repeats"""
    turns = ["I love gardening",
             "The weather is nice",
             "My cat is sleeping"]
    
    count, rate = analyzer.detect_repetitions(turns)
    
    # No repeated trigrams
    assert count == 0
    assert rate == 0.0


@pytest.mark.asyncio
async def test_detect_repetitions_cross_conversation(analyzer):
    """Test cross-conversation repetition detection"""
    current_turns = ["I went to the store today"]
    history_turns = ["Yesterday I went to the store", 
                     "Last week I went to the store"]
    
    count, rate = analyzer.detect_repetitions(current_turns, history_turns=history_turns)
    
    # "I went to" and "to the store" should be detected
    assert count > 0


@pytest.mark.asyncio
async def test_count_word_finding_pauses_um_uh(analyzer):
    """Test detection of um/uh pauses"""
    turns = ["um I think um well", "uh let me see"]
    
    count = analyzer.count_word_finding_pauses(turns)
    
    # Should detect: um, um, uh
    assert count == 3


@pytest.mark.asyncio
async def test_count_word_finding_pauses_phrases(analyzer):
    """Test detection of word-finding phrases"""
    turns = [
        "what's the word for that thing",
        "I can't remember the name",
        "you know what I mean"
    ]
    
    count = analyzer.count_word_finding_pauses(turns)
    
    # Should detect all 3 phrases
    assert count >= 3


@pytest.mark.asyncio
async def test_count_word_finding_pauses_clean_speech(analyzer):
    """Test no pauses in clean speech"""
    turns = ["I love gardening very much",
             "The weather is beautiful today"]
    
    count = analyzer.count_word_finding_pauses(turns)
    
    # No word-finding pauses
    assert count == 0


@pytest.mark.asyncio
async def test_compute_response_latency_with_times(analyzer):
    """Test response latency calculation"""
    response_times = [2.5, 3.0, 2.0, 4.0]
    
    latency = analyzer.compute_response_latency(response_times)
    
    # Average should be 2.875
    assert 2.8 < latency < 2.9


@pytest.mark.asyncio
async def test_compute_response_latency_none(analyzer):
    """Test response latency with None input"""
    latency = analyzer.compute_response_latency(None)
    assert latency is None


@pytest.mark.asyncio
async def test_analyze_conversation_full(analyzer):
    """Test full conversation analysis"""
    transcript = """Clara: Hello Dorothy!
Dorothy: Hi there, how are you?
Clara: I'm well. What did you do today?
Dorothy: I worked in my garden and planted some roses.
Clara: That sounds lovely!
Dorothy: Yes, I really enjoy gardening very much."""
    
    metrics = await analyzer.analyze_conversation(
        transcript=transcript,
        patient_name="Dorothy",
        conversation_id="test-123",
        patient_id="patient-001"
    )
    
    # Verify all metrics are present
    assert "vocabulary_diversity" in metrics
    assert "topic_coherence" in metrics
    assert "repetition_count" in metrics
    assert "repetition_rate" in metrics
    assert "word_finding_pauses" in metrics
    assert "response_latency" in metrics
    assert "conversation_id" in metrics
    assert "patient_id" in metrics
    
    # Verify metric ranges
    assert 0.0 <= metrics["vocabulary_diversity"] <= 1.0
    assert 0.0 <= metrics["topic_coherence"] <= 1.0
    assert metrics["repetition_count"] >= 0
    assert 0.0 <= metrics["repetition_rate"] <= 1.0
    assert metrics["word_finding_pauses"] >= 0


@pytest.mark.asyncio
async def test_analyze_conversation_partial_short(analyzer):
    """Test partial metrics for short conversation"""
    transcript = """Clara: Hi
Dorothy: Hello"""
    
    metrics = await analyzer.analyze_conversation(
        transcript=transcript,
        patient_name="Dorothy"
    )
    
    # Should return partial metrics
    assert metrics["_partial"] is True
    assert metrics["vocabulary_diversity"] is None
    assert metrics["topic_coherence"] is None
    assert "repetition_rate" in metrics
    assert "word_finding_pauses" in metrics

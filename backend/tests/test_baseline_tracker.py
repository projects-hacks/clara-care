"""
Tests for BaselineTracker
Validates baseline establishment and deviation detection
"""

import pytest
from app.cognitive.baseline import BaselineTracker
from app.storage.memory import InMemoryDataStore


@pytest.fixture
def data_store():
    """Create data store with seeded test patient"""
    return InMemoryDataStore()


@pytest.fixture
def tracker(data_store):
    """Create baseline tracker"""
    return BaselineTracker(data_store)


@pytest.mark.asyncio
async def test_check_baseline_ready_insufficient(data_store, tracker):
    """Test baseline not ready with < 7 conversations"""
    # New patient has no conversations
    test_patient_id = "patient-test-001"

    ready = await tracker.check_baseline_ready(test_patient_id)

    assert ready is False


@pytest.mark.asyncio
async def test_check_baseline_ready_sufficient(data_store, tracker):
    """Test baseline ready with >= 7 conversations"""
    patient_id = "patient-dorothy-001"

    # Dorothy has 7 conversations in seed data
    ready = await tracker.check_baseline_ready(patient_id)

    assert ready is True


@pytest.mark.asyncio
async def test_establish_baseline(data_store, tracker):
    """Test baseline establishment with 7 conversations"""
    patient_id = "patient-dorothy-001"

    baseline = await tracker.establish_baseline(patient_id)

    # Verify baseline structure
    assert baseline["patient_id"] == patient_id
    assert baseline["established"] is True
    assert baseline["conversation_count"] == 7

    # Verify all metrics are present
    assert "vocabulary_diversity" in baseline
    assert "topic_coherence" in baseline
    assert "repetition_rate" in baseline
    assert "word_finding_pauses" in baseline

    # Verify standard deviations
    assert "vocabulary_diversity_std" in baseline
    assert "topic_coherence_std" in baseline
    assert "repetition_rate_std" in baseline
    assert "word_finding_pauses_std" in baseline

    # Verify values are reasonable
    assert 0.0 < baseline["vocabulary_diversity"] < 1.0
    assert 0.0 < baseline["topic_coherence"] < 1.0
    assert 0.0 <= baseline["repetition_rate"] < 1.0
    assert baseline["word_finding_pauses"] >= 0


@pytest.mark.asyncio
async def test_establish_baseline_insufficient_data(data_store, tracker):
    """Test baseline returns not-established for new patient"""
    baseline = await tracker.establish_baseline("patient-test-001")

    assert baseline["established"] is False
    assert baseline["conversation_count"] == 0


@pytest.mark.asyncio
async def test_compare_to_baseline_no_deviation(data_store, tracker):
    """Test comparison with metrics within threshold"""
    patient_id = "patient-dorothy-001"

    baseline = await data_store.get_cognitive_baseline(patient_id)

    # Create metrics exactly matching baseline
    metrics = {
        "vocabulary_diversity": baseline["vocabulary_diversity"],
        "topic_coherence": baseline["topic_coherence"],
        "repetition_rate": baseline["repetition_rate"],
        "word_finding_pauses": baseline.get("word_finding_pauses", 1.0)
    }

    deviations = await tracker.compare_to_baseline(patient_id, metrics, baseline)

    assert len(deviations) == 0


@pytest.mark.asyncio
async def test_compare_to_baseline_with_deviation(data_store, tracker):
    """Test comparison with metrics outside threshold (>20% drop)"""
    patient_id = "patient-dorothy-001"

    baseline = await data_store.get_cognitive_baseline(patient_id)

    # 30% drop in vocabulary diversity
    metrics = {
        "vocabulary_diversity": baseline["vocabulary_diversity"] * 0.7,
        "topic_coherence": baseline["topic_coherence"],
        "repetition_rate": baseline["repetition_rate"],
        "word_finding_pauses": baseline.get("word_finding_pauses", 1.0)
    }

    deviations = await tracker.compare_to_baseline(patient_id, metrics, baseline)

    # Must detect vocabulary_diversity deviation
    assert len(deviations) > 0

    vocab_dev = next(d for d in deviations if d["metric_name"] == "vocabulary_diversity")
    assert vocab_dev["severity"] in ["low", "medium", "high"]
    assert vocab_dev["consecutive_count"] >= 1
    assert vocab_dev["deviation_percent"] < 0  # Negative = declined


@pytest.mark.asyncio
async def test_compare_to_baseline_consecutive_counter(data_store, tracker):
    """Test consecutive deviation counter increments"""
    patient_id = "patient-dorothy-001"

    baseline = await data_store.get_cognitive_baseline(patient_id)

    deviated_metrics = {
        "vocabulary_diversity": baseline["vocabulary_diversity"] * 0.7,
        "topic_coherence": baseline["topic_coherence"],
        "repetition_rate": baseline["repetition_rate"],
        "word_finding_pauses": baseline.get("word_finding_pauses", 1.0)
    }

    # First deviation
    deviations1 = await tracker.compare_to_baseline(patient_id, deviated_metrics, baseline)
    assert len(deviations1) > 0
    first_count = deviations1[0]["consecutive_count"]

    # Second consecutive deviation
    deviations2 = await tracker.compare_to_baseline(patient_id, deviated_metrics, baseline)
    assert len(deviations2) > 0
    second_count = deviations2[0]["consecutive_count"]

    # Counter must increment
    assert second_count == first_count + 1


@pytest.mark.asyncio
async def test_compare_to_baseline_severity_levels(data_store, tracker):
    """Test severity categorization: low (<30%), medium (30-50%), high (>50%)"""
    patient_id = "patient-dorothy-001"

    baseline = await data_store.get_cognitive_baseline(patient_id)

    # Low severity: 25% deviation
    metrics_low = {
        "vocabulary_diversity": baseline["vocabulary_diversity"] * 0.75,
        "topic_coherence": baseline["topic_coherence"],
        "repetition_rate": baseline["repetition_rate"],
        "word_finding_pauses": baseline.get("word_finding_pauses", 1.0)
    }
    deviations_low = await tracker.compare_to_baseline(patient_id, metrics_low, baseline)
    assert len(deviations_low) > 0
    assert deviations_low[0]["severity"] == "low"

    # High severity: 60% deviation
    metrics_high = {
        "vocabulary_diversity": baseline["vocabulary_diversity"] * 0.4,
        "topic_coherence": baseline["topic_coherence"],
        "repetition_rate": baseline["repetition_rate"],
        "word_finding_pauses": baseline.get("word_finding_pauses", 1.0)
    }
    deviations_high = await tracker.compare_to_baseline(patient_id, metrics_high, baseline)
    assert len(deviations_high) > 0

    vocab_dev = next(d for d in deviations_high if d["metric_name"] == "vocabulary_diversity")
    assert vocab_dev["severity"] == "high"


@pytest.mark.asyncio
async def test_compare_to_baseline_repetition_higher_is_worse(data_store, tracker):
    """Test that higher repetition rate triggers deviation"""
    patient_id = "patient-dorothy-001"

    baseline = await data_store.get_cognitive_baseline(patient_id)

    metrics = {
        "vocabulary_diversity": baseline["vocabulary_diversity"],
        "topic_coherence": baseline["topic_coherence"],
        "repetition_rate": baseline["repetition_rate"] * 1.5,  # 50% increase
        "word_finding_pauses": baseline.get("word_finding_pauses", 1.0)
    }

    deviations = await tracker.compare_to_baseline(patient_id, metrics, baseline)

    rep_devs = [d for d in deviations if d["metric_name"] == "repetition_rate"]
    assert len(rep_devs) > 0
    assert rep_devs[0]["deviation_percent"] > 0  # Positive = increased


@pytest.mark.asyncio
async def test_compare_to_baseline_word_finding_pauses(data_store, tracker):
    """Test word-finding pauses baseline comparison"""
    patient_id = "patient-dorothy-001"

    baseline = await data_store.get_cognitive_baseline(patient_id)

    baseline_wf = baseline.get("word_finding_pauses", 0.0)

    # Significantly higher word-finding pauses
    metrics = {
        "vocabulary_diversity": baseline["vocabulary_diversity"],
        "topic_coherence": baseline["topic_coherence"],
        "repetition_rate": baseline["repetition_rate"],
        "word_finding_pauses": max(baseline_wf * 2.5, 5.0)
    }

    deviations = await tracker.compare_to_baseline(patient_id, metrics, baseline)

    # With the fixed baseline (now includes word_finding_pauses), this should detect deviation
    if baseline_wf > 0:
        wf_devs = [d for d in deviations if d["metric_name"] == "word_finding_pauses"]
        assert len(wf_devs) > 0, "Should detect word-finding pause deviation when baseline exists"
    else:
        # If baseline is 0, comparison is skipped (division by zero guard)
        assert isinstance(deviations, list)


@pytest.mark.asyncio
async def test_compare_to_baseline_no_baseline_established(data_store, tracker):
    """Test comparison returns empty when no baseline exists"""
    metrics = {
        "vocabulary_diversity": 0.5,
        "topic_coherence": 0.8,
        "repetition_rate": 0.1,
        "word_finding_pauses": 2
    }

    deviations = await tracker.compare_to_baseline("patient-test-001", metrics)
    assert deviations == []

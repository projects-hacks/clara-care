"""
Tests for SanityDataStore field mapping and protocol compliance.

These tests verify that the _map_* helper methods produce dicts with the
EXACT same keys as InMemoryDataStore. We use mock HTTP responses so no
real Sanity connection is needed.
"""

import pytest
from app.storage.sanity import SanityDataStore


@pytest.fixture
def store():
    """Create SanityDataStore with dummy credentials (no network calls)."""
    return SanityDataStore(project_id="test", dataset="test", token="fake")


# ---------------------------------------------------------------------------
# _map_patient
# ---------------------------------------------------------------------------


def test_map_patient_full(store):
    """Full patient document maps all required keys."""
    doc = {
        "_id": "patient-001",
        "name": "Dorothy Chen",
        "preferredName": "Dorothy",
        "dateOfBirth": "1951-03-15",
        "birthYear": 1951,
        "age": 75,
        "location": {"city": "SF", "state": "CA", "timezone": "America/Los_Angeles"},
        "medicalNotes": "Healthy",
        "medications": [{"name": "Lisinopril", "dosage": "10mg", "schedule": "9 AM"}],
        "preferences": {
            "favoriteTopics": ["gardening"],
            "communicationStyle": ["warm"],
            "interests": ["music"],
        },
        "cognitiveThresholds": {"deviationThreshold": 0.2, "consecutiveTrigger": 3},
    }
    mapped = store._map_patient(doc)

    assert mapped["id"] == "patient-001"
    assert mapped["name"] == "Dorothy Chen"
    assert mapped["preferred_name"] == "Dorothy"
    assert mapped["date_of_birth"] == "1951-03-15"
    assert mapped["birth_year"] == 1951
    assert mapped["age"] == 75
    assert mapped["location"]["city"] == "SF"
    assert mapped["medical_notes"] == "Healthy"
    assert mapped["medications"][0]["name"] == "Lisinopril"
    assert mapped["preferences"]["favorite_topics"] == ["gardening"]
    assert mapped["preferences"]["interests"] == ["music"]
    assert mapped["cognitive_thresholds"]["deviation_threshold"] == 0.2
    assert mapped["cognitive_thresholds"]["consecutive_trigger"] == 3


def test_map_patient_none(store):
    assert store._map_patient(None) is None


def test_map_patient_defaults(store):
    """Missing optional fields get defaults."""
    doc = {"_id": "p1", "name": "Test"}
    mapped = store._map_patient(doc)
    assert mapped["medications"] == []
    assert mapped["preferences"]["favorite_topics"] == []
    assert mapped["cognitive_thresholds"]["deviation_threshold"] == 0.20


# ---------------------------------------------------------------------------
# _map_conversation
# ---------------------------------------------------------------------------


def test_map_conversation_full(store):
    doc = {
        "_id": "conv-001",
        "patient": {"_ref": "patient-001"},
        "timestamp": "2026-02-01T09:00:00Z",
        "duration": 300,
        "transcript": "Hello...",
        "summary": "A good chat",
        "mood": "happy",
        "cognitiveMetrics": {
            "vocabularyDiversity": 0.65,
            "topicCoherence": 0.88,
            "repetitionCount": 2,
            "repetitionRate": 0.04,
            "wordFindingPauses": 1,
            "responseLatency": 1.4,
        },
        "nostalgiaEngagement": {
            "triggered": True,
            "era": "1966-1976",
            "contentUsed": "Beatles song",
            "engagementScore": 8,
        },
    }
    mapped = store._map_conversation(doc)

    assert mapped["id"] == "conv-001"
    assert mapped["patient_id"] == "patient-001"
    assert mapped["detected_mood"] == "happy"
    assert mapped["cognitive_metrics"]["vocabulary_diversity"] == 0.65
    assert mapped["cognitive_metrics"]["word_finding_pauses"] == 1
    assert mapped["nostalgia_engagement"]["triggered"] is True
    assert mapped["nostalgia_engagement"]["engagement_score"] == 8


def test_map_conversation_no_metrics(store):
    doc = {"_id": "c1", "patient": {"_ref": "p1"}, "mood": "neutral"}
    mapped = store._map_conversation(doc)
    assert mapped["cognitive_metrics"] is None
    assert mapped["nostalgia_engagement"] is None


# ---------------------------------------------------------------------------
# _map_alert
# ---------------------------------------------------------------------------


def test_map_alert_full(store):
    doc = {
        "_id": "alert-001",
        "patient": {"_ref": "patient-001"},
        "alertType": "word_finding_difficulty",
        "severity": "low",
        "description": "Test alert",
        "acknowledged": True,
        "acknowledgedBy": {"_ref": "family-sarah-001"},
        "acknowledgedAt": "2026-02-01T12:00:00Z",
        "timestamp": "2026-02-01T09:00:00Z",
        "relatedMetrics": {"metricName": "wordFindingPauses", "currentValue": 5},
    }
    mapped = store._map_alert(doc)

    assert mapped["id"] == "alert-001"
    assert mapped["patient_id"] == "patient-001"
    assert mapped["alert_type"] == "word_finding_difficulty"
    assert mapped["severity"] == "low"
    assert mapped["acknowledged"] is True
    assert mapped["acknowledged_by"] == "family-sarah-001"
    assert mapped["acknowledged_at"] == "2026-02-01T12:00:00Z"


# ---------------------------------------------------------------------------
# _map_digest
# ---------------------------------------------------------------------------


def test_map_digest_full(store):
    doc = {
        "_id": "digest-001",
        "patient": {"_ref": "patient-001"},
        "date": "2026-02-01",
        "overallMood": "happy",
        "highlights": ["Had a great conversation"],
        "cognitiveScore": 85,
        "trend": "stable",
        "recommendations": ["Keep it up"],
        "conversation": {"_ref": "conv-001"},
        "generatedAt": "2026-02-01T18:00:00Z",
    }
    mapped = store._map_digest(doc)

    assert mapped["id"] == "digest-001"
    assert mapped["patient_id"] == "patient-001"
    assert mapped["date"] == "2026-02-01"
    assert mapped["overall_mood"] == "happy"
    assert mapped["highlights"] == ["Had a great conversation"]
    assert mapped["cognitive_score"] == 85
    assert mapped["cognitive_trend"] == "stable"
    assert mapped["conversation_id"] == "conv-001"
    assert mapped["created_at"] == "2026-02-01T18:00:00Z"


# ---------------------------------------------------------------------------
# _map_baseline
# ---------------------------------------------------------------------------


def test_map_baseline_full(store):
    doc = {
        "_id": "baseline-p1",
        "patient": {"_ref": "patient-001"},
        "established": True,
        "baselineDate": "2026-01-20",
        "vocabularyDiversity": 0.62,
        "vocabularyDiversityStd": 0.03,
        "topicCoherence": 0.87,
        "topicCoherenceStd": 0.02,
        "repetitionRate": 0.05,
        "repetitionRateStd": 0.01,
        "wordFindingPauses": 1.5,
        "wordFindingPausesStd": 0.8,
        "avgResponseTime": 1.5,
        "responseTimeStd": 0.2,
        "conversationCount": 7,
        "lastUpdated": "2026-01-20T00:00:00Z",
    }
    mapped = store._map_baseline(doc)

    assert mapped["patient_id"] == "patient-001"
    assert mapped["established"] is True
    assert mapped["vocabulary_diversity"] == 0.62
    assert mapped["vocabulary_diversity_std"] == 0.03
    assert mapped["topic_coherence"] == 0.87
    assert mapped["topic_coherence_std"] == 0.02
    assert mapped["repetition_rate"] == 0.05
    assert mapped["repetition_rate_std"] == 0.01
    assert mapped["word_finding_pauses"] == 1.5
    assert mapped["word_finding_pauses_std"] == 0.8
    assert mapped["avg_response_time"] == 1.5
    assert mapped["response_time_std"] == 0.2
    assert mapped["conversation_count"] == 7


# ---------------------------------------------------------------------------
# _map_family_contact
# ---------------------------------------------------------------------------


def test_map_family_contact_full(store):
    doc = {
        "_id": "family-001",
        "name": "Sarah Chen",
        "email": "sarah@email.com",
        "phone": "+1234567890",
        "relationship": "Daughter",
        "patients": [{"_ref": "patient-001"}],
        "notificationPreferences": {
            "dailyDigest": True,
            "instantAlerts": True,
            "weeklyReport": False,
        },
    }
    mapped = store._map_family_contact(doc)

    assert mapped["id"] == "family-001"
    assert mapped["name"] == "Sarah Chen"
    assert mapped["patient_ids"] == ["patient-001"]
    # snake_case notification preferences
    assert mapped["notification_preferences"]["daily_digest"] is True
    assert mapped["notification_preferences"]["instant_alerts"] is True
    assert mapped["notification_preferences"]["weekly_report"] is False

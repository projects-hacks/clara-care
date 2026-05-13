"""
Shared test fixtures and mock data.
All test files import from here to avoid duplication.
"""

from types import SimpleNamespace

# Fake authenticated user (simulates what get_current_user returns)
MOCK_USER = SimpleNamespace(id="test-user-001", email="test@claracare.ai")

# Sample patient
MOCK_PATIENT = {
    "id": "patient-test-001",
    "created_by": "test-user-001",
    "name": "Test Patient",
    "preferred_name": "Testy",
    "date_of_birth": "1950-01-01",
    "birth_year": 1950,
    "age": 76,
    "location": {"city": "San Jose", "state": "CA", "timezone": "America/Los_Angeles"},
    "medical_notes": "Test notes",
    "phone_number": "+14155551234",
    "medications": [{"name": "Aspirin", "dosage": "81mg", "schedule": "morning"}],
    "preferences": {
        "favorite_topics": ["gardening"],
        "communication_style": "warm",
        "interests": ["music"],
        "topics_to_avoid": [],
    },
    "cognitive_thresholds": {"deviation_threshold": 0.20, "consecutive_trigger": 3},
    "call_schedule": {"preferred_time": "10:00", "timezone": "America/Los_Angeles"},
}

# Sample conversation
MOCK_CONVERSATION = {
    "id": "conv-test-001",
    "patient_id": "patient-test-001",
    "timestamp": "2026-05-11T10:00:00Z",
    "duration": 180,
    "transcript": "Clara: Hello!\nPatient: Hi there!",
    "summary": "Brief greeting and check-in",
    "detected_mood": "happy",
    "cognitive_metrics": {
        "vocabulary_diversity": 0.75,
        "topic_coherence": 0.82,
        "repetition_count": 1,
        "repetition_rate": 0.05,
        "word_finding_pauses": 2,
        "response_latency": 1.5,
    },
    "nostalgia_engagement": None,
}

# Sample alert
MOCK_ALERT = {
    "id": "alert-test-001",
    "patient_id": "patient-test-001",
    "alert_type": "vocabulary_shrinkage",
    "severity": "medium",
    "description": "Test alert description",
    "suggested_action": "Call to check in",
    "acknowledged": False,
    "acknowledged_by": None,
    "acknowledged_at": None,
    "timestamp": "2026-05-11T10:00:00Z",
    "conversation_id": None,
    "related_metrics": {},
}

# Sample wellness digest
MOCK_DIGEST = {
    "id": "digest-test-001",
    "patient_id": "patient-test-001",
    "date": "2026-05-11",
    "overall_mood": "happy",
    "highlights": ["Had a great conversation about gardening"],
    "cognitive_score": 82,
    "cognitive_trend": "stable",
    "recommendations": ["Keep engaging in conversations about interests"],
    "conversation_id": "conv-test-001",
    "created_at": "2026-05-11T12:00:00Z",
}

# Sample cognitive baseline
MOCK_BASELINE = {
    "patient_id": "patient-test-001",
    "established": True,
    "baseline_date": "2026-04-15",
    "vocabulary_diversity": 0.75,
    "vocabulary_diversity_std": 0.05,
    "topic_coherence": 0.82,
    "topic_coherence_std": 0.04,
    "repetition_rate": 0.05,
    "repetition_rate_std": 0.02,
    "word_finding_pauses": 2.0,
    "word_finding_pauses_std": 0.5,
    "avg_response_time": 1.5,
    "response_time_std": 0.3,
    "conversation_count": 10,
    "last_updated": "2026-05-10T12:00:00Z",
}

# Sample insights
MOCK_INSIGHTS = {
    "cognitive_by_mood": {
        "happy": {
            "avg_vocabulary": 0.80,
            "avg_coherence": 0.85,
            "conversation_count": 3,
        },
        "neutral": {
            "avg_vocabulary": 0.72,
            "avg_coherence": 0.78,
            "conversation_count": 2,
        },
    },
    "nostalgia_effectiveness": {
        "with_nostalgia": {"avg_vocabulary": 0.82, "avg_coherence": 0.87, "count": 2},
        "without_nostalgia": {"avg_vocabulary": 0.72, "avg_coherence": 0.77, "count": 3},
        "improvement_pct": {"vocabulary": 13.9, "coherence": 13.0},
    },
    "alert_summary": {
        "total": 3,
        "by_severity": {"low": 1, "medium": 1, "high": 1},
        "most_common_type": "vocabulary_shrinkage",
        "acknowledged_count": 1,
    },
}

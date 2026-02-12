"""
Tests for Insights API Route and InMemoryDataStore.get_patient_insights
Validates the Sanity challenge showcase endpoint.

TestClient is synchronous -- do NOT use @pytest.mark.asyncio here.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client with lifespan triggered."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# get_patient_insights via InMemoryDataStore
# ---------------------------------------------------------------------------


def test_insights_endpoint_success(client):
    """GET /api/patients/{id}/insights returns structured insights."""
    resp = client.get("/api/patients/patient-dorothy-001/insights")
    assert resp.status_code == 200
    data = resp.json()

    assert data["patient_id"] == "patient-dorothy-001"
    assert data["patient_name"] == "Dorothy Chen"
    assert "insights" in data

    insights = data["insights"]
    assert "cognitive_by_mood" in insights
    assert "nostalgia_effectiveness" in insights
    assert "alert_summary" in insights


def test_insights_cognitive_by_mood(client):
    """Verify cognitive_by_mood groups conversations correctly."""
    resp = client.get("/api/patients/patient-dorothy-001/insights")
    insights = resp.json()["insights"]
    cbm = insights["cognitive_by_mood"]

    # Dorothy has nostalgic, neutral, and happy moods in seed data
    assert len(cbm) >= 2, "Should have at least 2 mood groups"

    # Each mood group must have the correct shape
    for mood, stats in cbm.items():
        assert "avg_vocabulary" in stats
        assert "avg_coherence" in stats
        assert "conversation_count" in stats
        assert stats["conversation_count"] >= 1
        assert 0 <= stats["avg_vocabulary"] <= 1
        assert 0 <= stats["avg_coherence"] <= 1


def test_insights_nostalgia_effectiveness(client):
    """Verify nostalgia effectiveness comparison."""
    resp = client.get("/api/patients/patient-dorothy-001/insights")
    ne = resp.json()["insights"]["nostalgia_effectiveness"]

    assert "with_nostalgia" in ne
    assert "without_nostalgia" in ne
    assert "improvement_pct" in ne

    # Dorothy has 2 conversations with nostalgia engagement in seed data
    assert ne["with_nostalgia"]["count"] >= 1
    assert ne["without_nostalgia"]["count"] >= 1

    assert "avg_vocabulary" in ne["with_nostalgia"]
    assert "avg_coherence" in ne["with_nostalgia"]
    assert "vocabulary" in ne["improvement_pct"]
    assert "coherence" in ne["improvement_pct"]


def test_insights_alert_summary(client):
    """Verify alert summary aggregation."""
    resp = client.get("/api/patients/patient-dorothy-001/insights")
    alerts = resp.json()["insights"]["alert_summary"]

    assert "total" in alerts
    assert alerts["total"] >= 1
    assert "by_severity" in alerts
    assert "most_common_type" in alerts
    assert "acknowledged_count" in alerts

    # Severity counts should have all three keys
    sev = alerts["by_severity"]
    assert "low" in sev
    assert "medium" in sev
    assert "high" in sev


def test_insights_patient_not_found(client):
    """Insights for nonexistent patient returns 404."""
    resp = client.get("/api/patients/patient-nonexistent-999/insights")
    assert resp.status_code == 404

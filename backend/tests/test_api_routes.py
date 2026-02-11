"""
Tests for API Routes
Validates REST API endpoints

Note: TestClient is synchronous - do NOT use @pytest.mark.asyncio here.
We use `with TestClient(app) as client:` to trigger the lifespan context
manager which initializes the data store and cognitive pipeline.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client with lifespan triggered (initializes data store)"""
    with TestClient(app) as c:
        yield c


# ---- Patient routes ----


def test_get_patient_exists(client):
    """Test GET /api/patients/{id} for existing patient"""
    response = client.get("/api/patients/patient-dorothy-001")

    assert response.status_code == 200
    data = response.json()

    # Response shape: {"patient": {...}, "baseline": ..., "latest_digest": ..., "recent_conversations": [...]}
    assert "patient" in data
    assert data["patient"]["id"] == "patient-dorothy-001"
    assert data["patient"]["name"] == "Dorothy Chen"
    assert "baseline" in data
    assert "latest_digest" in data
    assert "recent_conversations" in data


def test_get_patient_not_found(client):
    """Test GET /api/patients/{id} for nonexistent patient"""
    response = client.get("/api/patients/patient-nonexistent-999")

    assert response.status_code == 404


def test_update_patient_preferences(client):
    """Test PATCH /api/patients/{id}"""
    update_data = {
        "preferences": {
            "favorite_topics": ["cooking", "travel"],
            "preferred_contact_time": "morning"
        }
    }

    response = client.patch(
        "/api/patients/patient-dorothy-001",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "patient" in data


def test_update_patient_not_found(client):
    """Test PATCH /api/patients/{id} for nonexistent patient"""
    response = client.patch(
        "/api/patients/patient-nonexistent-999",
        json={"preferences": {"favorite_topics": ["music"]}}
    )
    assert response.status_code == 404


# ---- Conversation routes ----


def test_list_conversations(client):
    """Test GET /api/conversations with patient_id"""
    response = client.get("/api/conversations?patient_id=patient-dorothy-001&limit=5")

    assert response.status_code == 200
    data = response.json()

    assert data["patient_id"] == "patient-dorothy-001"
    assert "conversations" in data
    assert "count" in data
    assert len(data["conversations"]) <= 5


def test_list_conversations_pagination(client):
    """Test pagination on conversations"""
    # First page
    response1 = client.get("/api/conversations?patient_id=patient-dorothy-001&limit=3&offset=0")
    data1 = response1.json()

    # Second page
    response2 = client.get("/api/conversations?patient_id=patient-dorothy-001&limit=3&offset=3")
    data2 = response2.json()

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Should have different conversations (if enough data exists)
    if data1["conversations"] and data2["conversations"]:
        ids1 = {c["id"] for c in data1["conversations"]}
        ids2 = {c["id"] for c in data2["conversations"]}
        assert ids1.isdisjoint(ids2), "Paginated results should not overlap"


def test_get_conversation_details(client):
    """Test GET /api/conversations/{id}"""
    # First get a conversation ID from Dorothy's conversations
    response_list = client.get("/api/conversations?patient_id=patient-dorothy-001&limit=1")
    conversations = response_list.json()["conversations"]

    assert len(conversations) > 0, "Dorothy should have seeded conversations"

    convo_id = conversations[0]["id"]
    response = client.get(f"/api/conversations/{convo_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == convo_id
    assert "transcript" in data
    assert "cognitive_metrics" in data


def test_get_conversation_not_found(client):
    """Test GET /api/conversations/{id} for nonexistent conversation"""
    response = client.get("/api/conversations/conversation-nonexistent-999")
    assert response.status_code == 404


def test_create_conversation_with_pipeline(client):
    """Test POST /api/conversations with cognitive pipeline"""
    conversation_data = {
        "patient_id": "patient-dorothy-001",
        "transcript": "Clara: Hello Dorothy!\nDorothy: Hi Clara! I'm doing well today.\nClara: What did you do?\nDorothy: I worked in my garden and planted some beautiful roses.",
        "duration": 120,
        "summary": "Discussed gardening",
        "detected_mood": "happy"
    }

    response = client.post("/api/conversations", json=conversation_data)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "conversation_id" in data
    assert "cognitive_score" in data


def test_create_conversation_missing_fields(client):
    """Test POST /api/conversations with missing required fields"""
    response = client.post("/api/conversations", json={"patient_id": "patient-dorothy-001"})
    assert response.status_code == 400


# ---- Wellness routes ----


def test_get_wellness_digests(client):
    """Test GET /api/wellness-digests"""
    response = client.get("/api/wellness-digests?patient_id=patient-dorothy-001&limit=5")

    assert response.status_code == 200
    data = response.json()

    assert data["patient_id"] == "patient-dorothy-001"
    assert "digests" in data
    assert len(data["digests"]) > 0


def test_get_latest_wellness_digest(client):
    """Test GET /api/wellness-digests/latest"""
    response = client.get("/api/wellness-digests/latest?patient_id=patient-dorothy-001")

    assert response.status_code == 200
    data = response.json()

    # The route returns the raw digest dict from the data store
    assert "id" in data
    assert "cognitive_score" in data
    assert "overall_mood" in data


def test_get_latest_digest_not_found(client):
    """Test GET /api/wellness-digests/latest for patient with no digests"""
    response = client.get("/api/wellness-digests/latest?patient_id=patient-nonexistent-999")
    assert response.status_code == 404


def test_get_cognitive_trends(client):
    """Test GET /api/cognitive-trends"""
    response = client.get("/api/cognitive-trends?patient_id=patient-dorothy-001&days=30")

    assert response.status_code == 200
    data = response.json()

    assert data["patient_id"] == "patient-dorothy-001"
    assert "data_points" in data
    assert "baseline" in data

    # Verify data point structure if points exist
    if data["data_points"]:
        point = data["data_points"][0]
        assert "date" in point
        assert "vocabulary_diversity" in point
        assert "topic_coherence" in point
        assert "cognitive_score" in point


# ---- Alert routes ----


def test_get_alerts(client):
    """Test GET /api/alerts"""
    response = client.get("/api/alerts?patient_id=patient-dorothy-001")

    assert response.status_code == 200
    data = response.json()

    assert data["patient_id"] == "patient-dorothy-001"
    assert "alerts" in data
    assert len(data["alerts"]) > 0, "Dorothy should have seeded alerts"


def test_get_alerts_filter_by_severity(client):
    """Test GET /api/alerts with severity filter"""
    response = client.get("/api/alerts?patient_id=patient-dorothy-001&severity=high")

    assert response.status_code == 200
    data = response.json()

    # All returned alerts should be high severity (may be empty)
    for alert in data["alerts"]:
        assert alert["severity"] == "high"


def test_get_alerts_invalid_severity(client):
    """Test GET /api/alerts with invalid severity filter"""
    response = client.get("/api/alerts?patient_id=patient-dorothy-001&severity=critical")
    assert response.status_code == 400


def test_acknowledge_alert(client):
    """Test PATCH /api/alerts/{id}"""
    # Get an unacknowledged alert
    response_list = client.get("/api/alerts?patient_id=patient-dorothy-001")
    alerts = response_list.json()["alerts"]

    assert len(alerts) > 0, "Dorothy should have seeded alerts"

    # Use the alert "id" field (not "alert_id")
    alert_id = alerts[0]["id"]

    response = client.patch(
        f"/api/alerts/{alert_id}",
        json={"acknowledged_by": "family-sarah-001"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["alert_id"] == alert_id
    assert data["acknowledged"] is True


def test_acknowledge_alert_missing_body(client):
    """Test PATCH /api/alerts/{id} without acknowledged_by"""
    response = client.patch("/api/alerts/alert-001", json={})
    assert response.status_code == 400


def test_acknowledge_alert_not_found(client):
    """Test PATCH /api/alerts/{id} for nonexistent alert"""
    response = client.patch(
        "/api/alerts/alert-nonexistent-999",
        json={"acknowledged_by": "family-sarah-001"}
    )
    assert response.status_code == 404


# ---- Health check ----


def test_health_check(client):
    """Test GET / health check"""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["service"] == "ClaraCare Backend"
    assert data["status"] == "running"


def test_detailed_health_check(client):
    """Test GET /health"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"

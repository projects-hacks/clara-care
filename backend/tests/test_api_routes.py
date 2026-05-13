"""
Tests for API Routes
Validates REST API endpoints using mock repositories.
"""

import pytest
from unittest.mock import MagicMock
from app.main import app
from app.dependencies import get_patient_service, get_conversation_repo, get_alert_repo
from tests.fixtures import MOCK_PATIENT, MOCK_CONVERSATION, MOCK_ALERT


# ---- Patient routes ----

def test_get_patient_exists(client):
    """Test GET /api/patients/{id} for existing patient"""
    response = client.get("/api/patients/patient-test-001")

    assert response.status_code == 200
    data = response.json()

    assert "patient" in data
    assert data["patient"]["id"] == "patient-test-001"
    assert data["patient"]["name"] == "Test Patient"
    assert "baseline" in data
    assert "latest_digest" in data
    assert "recent_conversations" in data


def test_get_patient_not_found(client):
    """Test GET /api/patients/{id} for nonexistent patient"""
    svc = MagicMock()
    svc.get_detail.return_value = None
    app.dependency_overrides[get_patient_service] = lambda: svc

    response = client.get("/api/patients/patient-nonexistent-999")
    assert response.status_code == 404


def test_update_patient_preferences(client):
    """Test PATCH /api/patients/{id}"""
    update_data = {
        "preferences": {
            "favorite_topics": ["cooking", "travel"],
            "communication_style": "warm",
            "interests": ["music"],
            "topics_to_avoid": []
        }
    }

    response = client.patch(
        "/api/patients/patient-test-001",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "patient" in data


def test_update_patient_not_found(client):
    """Test PATCH /api/patients/{id} for nonexistent patient"""
    svc = MagicMock()
    svc.get_detail.return_value = None
    app.dependency_overrides[get_patient_service] = lambda: svc

    response = client.patch(
        "/api/patients/patient-nonexistent-999",
        json={"preferences": {"favorite_topics": ["music"]}}
    )
    assert response.status_code == 404


# ---- Conversation routes ----

def test_list_conversations(client):
    """Test GET /api/conversations with patient_id"""
    response = client.get("/api/conversations?patient_id=patient-test-001&limit=5")

    assert response.status_code == 200
    data = response.json()

    assert data["patient_id"] == "patient-test-001"
    assert "conversations" in data
    assert "count" in data
    assert len(data["conversations"]) <= 5


def test_list_conversations_pagination(client):
    """Test pagination on conversations"""
    # Just testing that the endpoint handles offset correctly
    response = client.get("/api/conversations?patient_id=patient-test-001&limit=3&offset=3")
    assert response.status_code == 200


def test_list_conversations_missing_patient(client):
    """Test GET /api/conversations without patient_id"""
    response = client.get("/api/conversations")
    assert response.status_code == 422  # Validation error (missing required query param)


def test_get_conversation_details(client):
    """Test GET /api/conversations/{id}"""
    response = client.get(f"/api/conversations/{MOCK_CONVERSATION['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == MOCK_CONVERSATION['id']
    assert "transcript" in data


def test_get_conversation_not_found(client):
    """Test GET /api/conversations/{id} for nonexistent"""
    repo = MagicMock()
    repo.get_by_id.return_value = None
    app.dependency_overrides[get_conversation_repo] = lambda: repo

    response = client.get("/api/conversations/conv-nonexistent-999")
    assert response.status_code == 404


def test_create_conversation(client):
    """Test POST /api/conversations"""
    # This will return 422 because we mocked get_cognitive_pipeline to return None, 
    # but let's test the endpoint response. Actually, if pipeline is None, the dependency 
    # might just inject None and the route might crash or return 500 if not handled.
    # The route actually uses the pipeline. Let's provide a dummy pipeline for this test.
    from app.dependencies import get_cognitive_pipeline
    
    async def mock_process(*args, **kwargs):
        return {
            "success": True,
            "conversation_id": "new-conv-001",
            "alerts_generated": 0
        }
        
    pipeline = MagicMock()
    pipeline.process_conversation = mock_process
    app.dependency_overrides[get_cognitive_pipeline] = lambda: pipeline

    payload = {
        "patient_id": "patient-test-001",
        "transcript": "Hello there",
        "duration": 60
    }

    response = client.post("/api/conversations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "conversation_id" in data


# ---- Wellness routes ----

def test_get_wellness_digests(client):
    """Test GET /api/wellness-digests"""
    response = client.get("/api/wellness-digests?patient_id=patient-test-001&limit=5")

    assert response.status_code == 200
    data = response.json()
    assert "digests" in data
    assert "patient_id" in data


def test_get_latest_wellness_digest(client):
    """Test GET /api/wellness-digests/latest"""
    response = client.get("/api/wellness-digests/latest?patient_id=patient-test-001")

    assert response.status_code == 200
    data = response.json()
    assert "cognitive_score" in data
    assert "overall_mood" in data


def test_get_latest_wellness_digest_not_found(client):
    """Test GET /api/wellness-digests/latest when none exist"""
    from app.dependencies import get_wellness_repo
    repo = MagicMock()
    repo.get_latest_digest.return_value = None
    app.dependency_overrides[get_wellness_repo] = lambda: repo

    response = client.get("/api/wellness-digests/latest?patient_id=patient-test-001")
    assert response.status_code == 404


# ---- Alert routes ----

def test_get_alerts(client):
    """Test GET /api/alerts"""
    response = client.get("/api/alerts?patient_id=patient-test-001&limit=5")

    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "count" in data


def test_get_alerts_with_severity(client):
    """Test GET /api/alerts with severity filter"""
    response = client.get("/api/alerts?patient_id=patient-test-001&severity=high")

    assert response.status_code == 200
    data = response.json()
    assert data["severity_filter"] == "high"


def test_get_alerts_invalid_severity(client):
    """Test GET /api/alerts with invalid severity"""
    response = client.get("/api/alerts?patient_id=patient-test-001&severity=critical")
    assert response.status_code == 400


def test_acknowledge_alert(client):
    """Test PATCH /api/alerts/{id}"""
    payload = {"acknowledged_by": "Test Family Member"}
    response = client.patch(f"/api/alerts/{MOCK_ALERT['id']}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["acknowledged"] is True


def test_acknowledge_alert_not_found(client):
    """Test PATCH /api/alerts/{id} for nonexistent alert"""
    repo = MagicMock()
    repo.get_by_id.return_value = None
    app.dependency_overrides[get_alert_repo] = lambda: repo

    payload = {"acknowledged_by": "Test Family Member"}
    response = client.patch("/api/alerts/alert-nonexistent-999", json=payload)

    assert response.status_code == 404

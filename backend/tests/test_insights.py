"""
Tests for Insights Routes
Validates the aggregation and insights endpoints using mocks.
"""

import pytest
from app.main import app
from app.dependencies import get_patient_repo
from unittest.mock import MagicMock
from tests.fixtures import MOCK_PATIENT, MOCK_INSIGHTS


def test_get_patient_insights(client):
    """Test GET /api/patients/{id}/insights"""
    response = client.get("/api/patients/patient-test-001/insights")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["patient_id"] == "patient-test-001"
    assert data["patient_name"] == "Test Patient"
    assert "insights" in data
    
    insights = data["insights"]
    assert "cognitive_by_mood" in insights
    assert "nostalgia_effectiveness" in insights
    assert "alert_summary" in insights


def test_get_patient_insights_not_found(client):
    """Test GET /api/patients/{id}/insights for nonexistent patient"""
    repo = MagicMock()
    repo.get_by_id.return_value = None
    app.dependency_overrides[get_patient_repo] = lambda: repo
    
    response = client.get("/api/patients/patient-nonexistent-999/insights")
    assert response.status_code == 404


def test_get_cognitive_trends(client):
    """Test GET /api/cognitive-trends"""
    response = client.get("/api/cognitive-trends?patient_id=patient-test-001&days=30")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["patient_id"] == "patient-test-001"
    assert "data_points" in data
    assert "baseline" in data


def test_get_cognitive_trends_missing_patient(client):
    """Test GET /api/cognitive-trends missing patient_id"""
    response = client.get("/api/cognitive-trends")
    assert response.status_code == 422


def test_get_cognitive_trends_not_found(client):
    """Test GET /api/cognitive-trends for nonexistent patient"""
    repo = MagicMock()
    repo.get_by_id.return_value = None
    app.dependency_overrides[get_patient_repo] = lambda: repo
    
    response = client.get("/api/cognitive-trends?patient_id=patient-nonexistent-999")
    assert response.status_code == 404

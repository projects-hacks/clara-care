"""
Tests for Reports API route.
Uses TestClient (synchronous) with InMemoryDataStore fallback.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_download_cognitive_report(client):
    """GET /api/reports/{patient_id}/cognitive-report returns PDF bytes."""
    resp = client.get("/api/reports/patient-dorothy-001/cognitive-report?days=30")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 0
    # Should be a valid PDF (starts with %PDF-)
    assert resp.content[:5] == b"%PDF-"


def test_download_report_default_days(client):
    """Default days parameter should work."""
    resp = client.get("/api/reports/patient-dorothy-001/cognitive-report")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_download_report_custom_days(client):
    """Custom days parameter within range."""
    resp = client.get("/api/reports/patient-dorothy-001/cognitive-report?days=7")
    assert resp.status_code == 200

    resp2 = client.get("/api/reports/patient-dorothy-001/cognitive-report?days=90")
    assert resp2.status_code == 200


def test_download_report_invalid_days(client):
    """Days outside 7-90 range should fail validation."""
    resp = client.get("/api/reports/patient-dorothy-001/cognitive-report?days=3")
    assert resp.status_code == 422  # FastAPI validation error

    resp2 = client.get("/api/reports/patient-dorothy-001/cognitive-report?days=100")
    assert resp2.status_code == 422

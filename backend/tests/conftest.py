"""
Shared test configuration.
Overrides all auth and repository dependencies with mocks
so tests run without a database connection.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.auth import get_current_user, get_verified_patient_id
from app.dependencies import (
    get_patient_repo,
    get_contact_repo,
    get_conversation_repo,
    get_alert_repo,
    get_wellness_repo,
    get_cognitive_repo,
    get_patient_service,
    get_invite_service,
    get_onboarding_service,
    get_cognitive_pipeline,
)

from tests.fixtures import (
    MOCK_USER,
    MOCK_PATIENT,
    MOCK_CONVERSATION,
    MOCK_ALERT,
    MOCK_DIGEST,
    MOCK_BASELINE,
    MOCK_INSIGHTS,
)


def _mock_patient_repo():
    repo = MagicMock()
    repo.get_by_id.return_value = MOCK_PATIENT
    repo.get_for_user.return_value = [MOCK_PATIENT]
    repo.update.return_value = True
    repo.create.return_value = MOCK_PATIENT
    return repo


def _mock_contact_repo():
    repo = MagicMock()
    repo.get_for_patient.return_value = []
    return repo


def _mock_conversation_repo():
    repo = MagicMock()
    repo.get_for_patient.return_value = [MOCK_CONVERSATION]
    repo.get_by_id.return_value = MOCK_CONVERSATION
    repo.save.return_value = "conv-test-001"
    return repo


def _mock_alert_repo():
    repo = MagicMock()
    repo.get_for_patient.return_value = [MOCK_ALERT]
    repo.get_by_id.return_value = MOCK_ALERT
    repo.update.return_value = True
    return repo


def _mock_wellness_repo():
    repo = MagicMock()
    repo.get_digests.return_value = [MOCK_DIGEST]
    repo.get_latest_digest.return_value = MOCK_DIGEST
    return repo


def _mock_cognitive_repo():
    repo = MagicMock()
    repo.get_baseline.return_value = MOCK_BASELINE
    repo.get_trends.return_value = []
    repo.get_patient_insights.return_value = MOCK_INSIGHTS
    return repo


def _mock_patient_service():
    svc = MagicMock()
    svc.get_for_user.return_value = [MOCK_PATIENT]
    svc.get_detail.return_value = dict(MOCK_PATIENT)
    return svc


@pytest.fixture
def client():
    """
    TestClient with all auth and repository dependencies overridden.
    Every route thinks it has an authenticated user and a working database.
    """
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    app.dependency_overrides[get_patient_repo] = _mock_patient_repo
    app.dependency_overrides[get_contact_repo] = _mock_contact_repo
    app.dependency_overrides[get_conversation_repo] = _mock_conversation_repo
    app.dependency_overrides[get_alert_repo] = _mock_alert_repo
    app.dependency_overrides[get_wellness_repo] = _mock_wellness_repo
    app.dependency_overrides[get_cognitive_repo] = _mock_cognitive_repo
    app.dependency_overrides[get_patient_service] = _mock_patient_service
    app.dependency_overrides[get_cognitive_pipeline] = lambda: None
    def _mock_verified_patient_id(patient_id: str):
        if "nonexistent" in patient_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient_id

    app.dependency_overrides[get_verified_patient_id] = _mock_verified_patient_id

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

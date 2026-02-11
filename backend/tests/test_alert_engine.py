"""
Tests for Alert Engine
Validates alert generation, severity categorization, and notification dispatch
"""

import pytest
from app.cognitive.alerts import AlertEngine
from app.storage.memory import InMemoryDataStore


@pytest.fixture
def data_store():
    """Create data store (sync - InMemoryDataStore.__init__ is sync)"""
    return InMemoryDataStore()


@pytest.fixture
def notification_service():
    """Mock notification service"""
    class MockNotifier:
        def __init__(self):
            self.sent_alerts = []

        async def send_alert_notification(self, patient_id, alert):
            self.sent_alerts.append((patient_id, alert))

    return MockNotifier()


@pytest.fixture
def alert_engine(data_store, notification_service):
    """Create alert engine"""
    return AlertEngine(data_store, notification_service)


@pytest.mark.asyncio
async def test_check_and_alert_no_deviations(alert_engine, notification_service):
    """Test no alerts when no deviations"""
    patient_id = "patient-dorothy-001"
    metrics = {"vocabulary_diversity": 0.65, "topic_coherence": 0.85}
    deviations = []

    alerts = await alert_engine.check_and_alert(patient_id, metrics, deviations)

    assert len(alerts) == 0
    assert len(notification_service.sent_alerts) == 0


@pytest.mark.asyncio
async def test_check_and_alert_insufficient_consecutive(alert_engine):
    """Test no alert when consecutive_count < 3 (threshold)"""
    patient_id = "patient-dorothy-001"  # Must exist in data store
    metrics = {"vocabulary_diversity": 0.4, "topic_coherence": 0.85}
    deviations = [{
        "metric_name": "vocabulary_diversity",
        "current_value": 0.4,
        "baseline_value": 0.65,
        "deviation_percent": -38.5,
        "severity": "medium",
        "consecutive_count": 2,  # Less than threshold of 3
    }]

    alerts = await alert_engine.check_and_alert(patient_id, metrics, deviations)

    # No alert generated (need 3 consecutive)
    assert len(alerts) == 0


@pytest.mark.asyncio
async def test_check_and_alert_sufficient_consecutive(alert_engine, notification_service):
    """Test alert generated when consecutive_count >= 3"""
    patient_id = "patient-dorothy-001"
    metrics = {
        "vocabulary_diversity": 0.4,
        "topic_coherence": 0.85,
        "repetition_rate": 0.05,
        "word_finding_pauses": 1
    }
    deviations = [{
        "metric_name": "vocabulary_diversity",
        "current_value": 0.4,
        "baseline_value": 0.65,
        "deviation_percent": -38.5,
        "severity": "medium",
        "consecutive_count": 3,  # Meets threshold
    }]

    alerts = await alert_engine.check_and_alert(patient_id, metrics, deviations)

    # Alert should be generated
    assert len(alerts) == 1

    alert = alerts[0]
    assert alert["patient_id"] == patient_id
    assert alert["severity"] == "medium"
    assert alert["alert_type"] == "vocabulary_shrinkage"  # mapped from vocabulary_diversity
    assert alert["acknowledged"] is False
    assert "id" in alert
    assert "description" in alert

    # Related metrics should contain the original deviation info
    assert alert["related_metrics"]["metric_name"] == "vocabulary_diversity"

    # Notification should be sent
    assert len(notification_service.sent_alerts) > 0


@pytest.mark.asyncio
async def test_check_and_alert_severity_mapping(alert_engine):
    """Test severity levels are correctly passed through"""
    patient_id = "patient-dorothy-001"

    metrics = {"vocabulary_diversity": 0.3, "topic_coherence": 0.85, "repetition_rate": 0.05, "word_finding_pauses": 1}
    deviations_high = [{
        "metric_name": "vocabulary_diversity",
        "current_value": 0.3,
        "baseline_value": 0.65,
        "deviation_percent": -53.8,
        "severity": "high",
        "consecutive_count": 3,
    }]

    alerts_high = await alert_engine.check_and_alert(patient_id, metrics, deviations_high)
    assert len(alerts_high) == 1
    assert alerts_high[0]["severity"] == "high"


@pytest.mark.asyncio
async def test_create_realtime_alert(data_store, alert_engine):
    """Test real-time alert creation (e.g., from voice trigger)"""
    patient_id = "patient-dorothy-001"

    alert = await alert_engine.create_realtime_alert(
        patient_id=patient_id,
        alert_type="confusion_detected",
        severity="high",
        message="Patient expressed confusion about current location"
    )

    assert alert["patient_id"] == patient_id
    assert alert["alert_type"] == "confusion_detected"
    assert alert["description"] == "Patient expressed confusion about current location"
    assert alert["severity"] == "high"
    assert "id" in alert
    assert alert["acknowledged"] is False

    # Should be saved in data store (check via get_alerts)
    saved_alerts = await data_store.get_alerts(patient_id, severity="high")
    alert_ids = [a["id"] for a in saved_alerts]
    assert alert["id"] in alert_ids


@pytest.mark.asyncio
async def test_create_realtime_alert_low_severity_no_notification(alert_engine, notification_service):
    """Test low severity real-time alerts don't immediately dispatch notifications"""
    alert = await alert_engine.create_realtime_alert(
        patient_id="patient-dorothy-001",
        alert_type="minor_confusion",
        severity="low",
        message="Minor confusion noted"
    )

    # Low severity doesn't trigger immediate notification dispatch
    assert len(notification_service.sent_alerts) == 0


@pytest.mark.asyncio
async def test_acknowledge_alert(data_store, alert_engine):
    """Test acknowledging an alert"""
    patient_id = "patient-dorothy-001"

    # Create an alert first
    alert = await alert_engine.create_realtime_alert(
        patient_id=patient_id,
        alert_type="test_alert",
        severity="low",
        message="Test alert"
    )

    alert_id = alert["id"]

    # Acknowledge it
    success = await alert_engine.acknowledge_alert(alert_id, acknowledged_by="family-sarah-001")
    assert success is True


@pytest.mark.asyncio
async def test_acknowledge_alert_nonexistent(alert_engine):
    """Test acknowledging a nonexistent alert"""
    success = await alert_engine.acknowledge_alert("alert-nonexistent-999", acknowledged_by="Dr. Smith")
    assert success is False


@pytest.mark.asyncio
async def test_alert_description_generation(alert_engine):
    """Test alert description is human-readable"""
    deviation = {
        "metric_name": "vocabulary_diversity",
        "current_value": 0.45,
        "baseline_value": 0.65,
        "deviation_percent": -30.8,
        "severity": "medium",
        "consecutive_count": 3
    }

    description = alert_engine._generate_alert_description(deviation)

    # Should mention the metric and direction
    assert "Vocabulary diversity" in description
    assert "declined" in description
    assert "30.8%" in description
    assert "3 consecutive" in description


@pytest.mark.asyncio
async def test_multiple_deviations_multiple_alerts(alert_engine):
    """Test multiple deviations generate multiple alerts"""
    patient_id = "patient-dorothy-001"
    metrics = {
        "vocabulary_diversity": 0.4,
        "topic_coherence": 0.5,
        "repetition_rate": 0.05,
        "word_finding_pauses": 1
    }
    deviations = [
        {
            "metric_name": "vocabulary_diversity",
            "current_value": 0.4,
            "baseline_value": 0.65,
            "deviation_percent": -38.5,
            "severity": "medium",
            "consecutive_count": 3,
        },
        {
            "metric_name": "topic_coherence",
            "current_value": 0.5,
            "baseline_value": 0.85,
            "deviation_percent": -41.2,
            "severity": "medium",
            "consecutive_count": 3,
        }
    ]

    alerts = await alert_engine.check_and_alert(patient_id, metrics, deviations)

    # Should generate 2 alerts
    assert len(alerts) == 2

    alert_types = [a["alert_type"] for a in alerts]
    assert "vocabulary_shrinkage" in alert_types
    assert "coherence_drop" in alert_types

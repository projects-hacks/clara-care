"""
Tests for Foxit PDF client and Report Generator.
Uses mocked Foxit API.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from app.reports.foxit_client import FoxitClient
from app.reports.generator import ReportGenerator
from app.storage.memory import InMemoryDataStore


# ---------------------------------------------------------------------------
# FoxitClient tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_foxit_mock_pdf_generation():
    """Without API credentials, generates mock PDF."""
    client = FoxitClient()  # No credentials -> mock mode
    pdf = await client.generate_cognitive_report_pdf({
        "patient_name": "Dorothy Chen",
        "report_date": "2026-02-10",
        "cognitive_score": 85,
        "memory_score": 80,
        "language_score": 90,
        "attention_score": 82,
    })

    assert isinstance(pdf, bytes)
    assert len(pdf) > 0
    # Check it starts with PDF header
    assert pdf[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_foxit_close_without_client():
    """close() should not raise when no API client."""
    client = FoxitClient()
    await client.close()  # Should not raise


# ---------------------------------------------------------------------------
# ReportGenerator tests
# ---------------------------------------------------------------------------


@pytest.fixture
def data_store():
    """Sync fixture -- InMemoryDataStore.__init__ is sync."""
    return InMemoryDataStore()


@pytest.fixture
def foxit_client():
    """FoxitClient without credentials (mock mode)."""
    return FoxitClient()


@pytest.fixture
def report_gen(data_store, foxit_client):
    return ReportGenerator(data_store, foxit_client)


@pytest.mark.asyncio
async def test_report_generator_basic(report_gen):
    """Generates a PDF report for existing patient."""
    pdf = await report_gen.generate_cognitive_report("patient-dorothy-001", days=30)

    assert isinstance(pdf, bytes)
    assert len(pdf) > 0
    assert pdf[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_report_generator_patient_not_found(report_gen):
    """Returns error PDF for nonexistent patient."""
    pdf = await report_gen.generate_cognitive_report("patient-nonexistent-999")

    assert isinstance(pdf, bytes)
    assert len(pdf) > 0  # Error PDF should still be valid bytes


@pytest.mark.asyncio
async def test_report_calculate_trend_insufficient_data(report_gen):
    """Trend with < 4 data points returns 'insufficient_data'."""
    result = report_gen._calculate_trend_direction([
        {"vocabulary_diversity": 0.6, "topic_coherence": 0.8},
        {"vocabulary_diversity": 0.6, "topic_coherence": 0.8},
    ])
    assert result == "insufficient_data"


@pytest.mark.asyncio
async def test_report_calculate_trend_stable(report_gen):
    """Stable metrics should return 'stable'."""
    trends = [
        {"vocabulary_diversity": 0.62, "topic_coherence": 0.85},
        {"vocabulary_diversity": 0.63, "topic_coherence": 0.86},
        {"vocabulary_diversity": 0.62, "topic_coherence": 0.85},
        {"vocabulary_diversity": 0.63, "topic_coherence": 0.86},
    ]
    result = report_gen._calculate_trend_direction(trends)
    assert result == "stable"


@pytest.mark.asyncio
async def test_report_generate_recommendations(report_gen):
    """Recommendations are generated as a non-empty string."""
    trends = [
        {"vocabulary_diversity": 0.6, "topic_coherence": 0.8, "repetition_rate": 0.05},
    ]
    alerts = []
    baseline = {"established": True, "vocabulary_diversity": 0.6}
    recs = report_gen._generate_recommendations(trends, alerts, baseline)
    assert isinstance(recs, str)
    assert len(recs) > 0

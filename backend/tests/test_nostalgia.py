"""
Tests for Nostalgia Engine (era calculation + YouComClient)
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.nostalgia.era import calculate_golden_years, get_era_label, get_decade_from_year
from app.nostalgia.youcom_client import YouComClient


# ---------------------------------------------------------------------------
# Era calculation tests (synchronous)
# ---------------------------------------------------------------------------


def test_golden_years_typical():
    """1951 birth -> golden years 1966-1976."""
    assert calculate_golden_years(1951) == (1966, 1976)


def test_golden_years_1940s():
    """1943 birth -> golden years 1958-1968."""
    assert calculate_golden_years(1943) == (1958, 1968)


def test_golden_years_1930s():
    """1935 birth -> golden years 1950-1960."""
    assert calculate_golden_years(1935) == (1950, 1960)


def test_era_label_different_decades():
    """1966-1976 spans two decades -> '1960s-1970s'."""
    assert get_era_label(1966, 1976) == "1960s-1970s"


def test_era_label_same_decade():
    """1962-1968 same decade -> '1960s'."""
    assert get_era_label(1962, 1968) == "1960s"


def test_get_decade_from_year():
    assert get_decade_from_year(1963) == "1960s"
    assert get_decade_from_year(1970) == "1970s"
    assert get_decade_from_year(1959) == "1950s"


# ---------------------------------------------------------------------------
# YouComClient tests (async, mocked)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_youcom_fallback_no_api_key():
    """Without API key, should return fallback nostalgia content."""
    client = YouComClient(api_key=None)  # No key -> fallback mode
    result = await client.search_nostalgia(birth_year=1951)

    assert "music" in result
    assert "events" in result
    assert "culture" in result
    assert "era" in result
    assert len(result["music"]) >= 1
    assert len(result["events"]) >= 1


@pytest.mark.asyncio
async def test_youcom_fallback_realtime_no_key():
    """Without API key, realtime search returns fallback."""
    client = YouComClient(api_key=None)
    result = await client.search_realtime("weather today")

    assert "answer" in result
    assert "results" in result
    assert isinstance(result["results"], list)


@pytest.mark.asyncio
async def test_youcom_nostalgia_default_era():
    """Without birth_year, defaults to 1960s era content."""
    client = YouComClient(api_key=None)
    result = await client.search_nostalgia(birth_year=None)

    assert "era" in result
    # Default range is 1965-1975
    assert "1965" in result["era"] or "1960" in result["era"]


@pytest.mark.asyncio
async def test_youcom_fallback_content_by_decade():
    """Fallback content should vary by decade."""
    client = YouComClient(api_key=None)

    result_50s = await client.search_nostalgia(birth_year=1935)  # golden: 1950-1960
    result_60s = await client.search_nostalgia(birth_year=1945)  # golden: 1960-1970

    # Different decades should have different content
    assert result_50s["era"] != result_60s["era"]


@pytest.mark.asyncio
async def test_youcom_close_without_client():
    """close() should not raise when no client."""
    client = YouComClient(api_key=None)
    await client.close()  # Should not raise

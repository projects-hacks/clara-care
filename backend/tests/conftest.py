"""
Shared test configuration.

Ensures tests always use InMemoryDataStore by clearing Sanity env vars
before any TestClient or lifespan initialization.
"""

import os
import pytest


@pytest.fixture(autouse=True)
def _force_inmemory_store(monkeypatch):
    """
    Remove Sanity credentials from env so main.py falls back
    to InMemoryDataStore during tests.  Applied to ALL tests automatically.
    """
    monkeypatch.delenv("SANITY_PROJECT_ID", raising=False)
    monkeypatch.delenv("SANITY_DATASET", raising=False)
    monkeypatch.delenv("SANITY_TOKEN", raising=False)

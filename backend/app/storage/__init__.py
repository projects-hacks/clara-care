"""
Storage Module
Data abstraction layer for patient data, conversations, and cognitive metrics
Supports in-memory (testing) and Supabase PostgreSQL (production)
"""

from .base import DataStore
from .memory import InMemoryDataStore
from .supabase_store import SupabaseDataStore

__all__ = [
    "DataStore",
    "InMemoryDataStore",
    "SupabaseDataStore"
]

"""
Storage Module
Data abstraction layer for patient data, conversations, and cognitive metrics
"""

from .base import DataStore
from .memory import InMemoryDataStore

__all__ = [
    "DataStore",
    "InMemoryDataStore"
]

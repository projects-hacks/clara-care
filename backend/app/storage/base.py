"""
DataStore Protocol
Abstract interface for data storage - allows swapping between in-memory, Sanity, or other backends
"""

from typing import Protocol, Optional


class DataStore(Protocol):
    """
    Protocol defining the interface for patient data storage
    Implementations: InMemoryDataStore, SanityDataStore
    """
    
    async def get_patient(self, patient_id: str) -> Optional[dict]:
        """
        Retrieve patient profile
        
        Returns:
            Patient dict with profile, preferences, medications, etc. or None if not found
        """
        ...
    
    async def update_patient(self, patient_id: str, updates: dict) -> bool:
        """
        Update patient profile (e.g., preferences, thresholds)
        
        Returns:
            True if successful, False otherwise
        """
        ...
    
    async def get_conversations(
        self, 
        patient_id: str, 
        limit: int = 10,
        offset: int = 0
    ) -> list[dict]:
        """
        Get paginated list of conversations for a patient
        
        Returns:
            List of conversation dicts, ordered by timestamp desc
        """
        ...
    
    async def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """
        Get full conversation details by ID
        
        Returns:
            Conversation dict with transcript, metrics, etc. or None if not found
        """
        ...
    
    async def save_conversation(self, conversation: dict) -> str:
        """
        Save a conversation with transcript, summary, and cognitive metrics
        
        Returns:
            The conversation_id (generated or provided)
        """
        ...
    
    async def get_cognitive_baseline(self, patient_id: str) -> Optional[dict]:
        """
        Get the cognitive baseline for a patient
        
        Returns:
            Baseline dict or None if not established yet
        """
        ...
    
    async def save_cognitive_baseline(self, patient_id: str, baseline: dict) -> None:
        """
        Save or update cognitive baseline for a patient
        """
        ...
    
    async def get_wellness_digests(
        self,
        patient_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> list[dict]:
        """
        Get paginated wellness digests for a patient
        
        Returns:
            List of digest dicts, ordered by date desc
        """
        ...
    
    async def get_latest_wellness_digest(self, patient_id: str) -> Optional[dict]:
        """
        Get the most recent wellness digest
        
        Returns:
            Latest digest dict or None
        """
        ...
    
    async def save_wellness_digest(self, digest: dict) -> str:
        """
        Save a wellness digest
        
        Returns:
            The digest_id (generated or provided)
        """
        ...
    
    async def get_alerts(
        self,
        patient_id: str,
        severity: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[dict]:
        """
        Get alerts for a patient, optionally filtered by severity
        
        Returns:
            List of alert dicts, ordered by timestamp desc
        """
        ...
    
    async def save_alert(self, alert: dict) -> str:
        """
        Save an alert
        
        Returns:
            The alert_id (generated or provided)
        """
        ...
    
    async def update_alert(self, alert_id: str, updates: dict) -> bool:
        """
        Update an alert (e.g., mark as acknowledged)
        
        Returns:
            True if successful, False otherwise
        """
        ...
    
    async def get_family_contacts(self, patient_id: str) -> list[dict]:
        """
        Get family contacts for a patient
        
        Returns:
            List of family contact dicts
        """
        ...
    
    async def get_consecutive_deviations(self, patient_id: str) -> dict:
        """
        Get consecutive deviation counters for cognitive metrics
        
        Returns:
            Dict mapping metric names to consecutive deviation counts
            Example: {"vocabulary_diversity": 3, "topic_coherence": 0}
        """
        ...
    
    async def update_consecutive_deviations(
        self,
        patient_id: str,
        deviations: dict
    ) -> None:
        """
        Update consecutive deviation counters
        
        Args:
            deviations: Dict mapping metric names to counts
        """
        ...
    
    async def get_cognitive_trends(
        self,
        patient_id: str,
        days: int = 30
    ) -> list[dict]:
        """
        Get time-series cognitive metrics for charting
        
        Returns:
            List of dicts with date and metrics, ordered by date asc
        """
        ...

    async def get_patient_insights(self, patient_id: str) -> dict:
        """
        Get structured content insights for a patient.
        Leverages cross-document references and typed field aggregation.
        
        Showcase for Sanity challenge: features impossible with flat files.
        
        Returns:
            Dict with:
            - cognitive_by_mood: {mood: {avg_vocabulary, avg_coherence, conversation_count}}
            - nostalgia_effectiveness: {with_nostalgia, without_nostalgia, improvement_pct}
            - alert_summary: {total, by_severity, most_common_type, acknowledged_count}
        """
        ...

"""
Pydantic Models for Cognitive Analysis
All data structures for cognitive metrics, baselines, alerts, and digests
"""

from datetime import datetime, date
from typing import Literal, Optional
from pydantic import BaseModel, Field


class CognitiveMetrics(BaseModel):
    """
    Cognitive analysis metrics extracted from a single conversation
    """
    vocabulary_diversity: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Type-Token Ratio (TTR): unique lemmas / total lemmas"
    )
    topic_coherence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Average pairwise cosine similarity of consecutive turns"
    )
    repetition_count: int = Field(
        ...,
        ge=0,
        description="Absolute count of repeated trigrams"
    )
    repetition_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Ratio of repeated trigrams to total trigrams"
    )
    word_finding_pauses: int = Field(
        ...,
        ge=0,
        description="Count of word-finding difficulty indicators (um, uh, what's the word, etc.)"
    )
    response_latency: Optional[float] = Field(
        None,
        ge=0.0,
        description="Average response time in seconds (None if unavailable)"
    )
    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of analysis"
    )
    conversation_id: Optional[str] = None
    patient_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "vocabulary_diversity": 0.62,
                "topic_coherence": 0.84,
                "repetition_count": 3,
                "repetition_rate": 0.05,
                "word_finding_pauses": 2,
                "response_latency": 1.8,
                "analyzed_at": "2026-02-15T10:30:00Z"
            }
        }


class CognitiveBaseline(BaseModel):
    """
    Baseline cognitive metrics for a patient (established from 7+ conversations)
    """
    patient_id: str
    established: bool = False
    baseline_date: Optional[date] = None
    
    # Mean values
    vocabulary_diversity: float = 0.0
    topic_coherence: float = 0.0
    repetition_rate: float = 0.0
    avg_response_time: Optional[float] = None
    
    # Standard deviations
    vocabulary_diversity_std: float = 0.0
    topic_coherence_std: float = 0.0
    repetition_rate_std: float = 0.0
    response_time_std: Optional[float] = None
    
    conversation_count: int = Field(
        0,
        description="Number of conversations used to establish this baseline"
    )
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "patient-dorothy-001",
                "established": True,
                "baseline_date": "2026-02-01",
                "vocabulary_diversity": 0.62,
                "vocabulary_diversity_std": 0.08,
                "topic_coherence": 0.87,
                "topic_coherence_std": 0.05,
                "repetition_rate": 0.05,
                "repetition_rate_std": 0.02,
                "avg_response_time": 1.5,
                "response_time_std": 0.3,
                "conversation_count": 7
            }
        }


class BaselineDeviation(BaseModel):
    """
    Represents a deviation from baseline for a specific metric
    """
    metric_name: str
    baseline_value: float
    current_value: float
    deviation_percent: float = Field(
        ...,
        description="Percentage deviation from baseline (positive = increase, negative = decrease)"
    )
    severity: Literal["low", "medium", "high"] = Field(
        ...,
        description="Severity based on deviation magnitude: 20-30%=low, 30-50%=medium, >50%=high"
    )
    consecutive_count: int = Field(
        0,
        description="How many consecutive calls this metric has been flagged"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "vocabulary_diversity",
                "baseline_value": 0.62,
                "current_value": 0.45,
                "deviation_percent": -27.4,
                "severity": "medium",
                "consecutive_count": 3
            }
        }


class Alert(BaseModel):
    """
    Alert generated from cognitive analysis or real-time voice triggers
    """
    id: str
    patient_id: str
    alert_type: str = Field(
        ...,
        description="Type: cognitive_decline, word_finding_difficulty, coherence_drop, vocabulary_shrinkage, distress, fall, etc."
    )
    severity: Literal["low", "medium", "high"]
    description: str
    related_metrics: Optional[dict] = Field(
        None,
        description="Relevant metrics or context for this alert"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert-001",
                "patient_id": "patient-dorothy-001",
                "alert_type": "cognitive_decline",
                "severity": "medium",
                "description": "Vocabulary diversity has declined 27% over the last 3 conversations",
                "related_metrics": {
                    "vocabulary_diversity": 0.45,
                    "baseline": 0.62,
                    "deviation": -27.4
                },
                "timestamp": "2026-02-15T10:30:00Z",
                "acknowledged": False
            }
        }


class WellnessDigest(BaseModel):
    """
    Daily wellness summary for family members
    """
    id: str
    patient_id: str
    date: date
    
    overall_mood: str = Field(
        ...,
        description="happy, neutral, sad, confused, distressed, nostalgic"
    )
    highlights: list[str] = Field(
        default_factory=list,
        description="Key points from the conversation"
    )
    
    # Cognitive health
    cognitive_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Composite cognitive score (0-100)"
    )
    cognitive_trend: Literal["improving", "stable", "declining"]
    
    recommendations: list[str] = Field(
        default_factory=list,
        description="Suggested actions for family members"
    )
    
    conversation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "digest-001",
                "patient_id": "patient-dorothy-001",
                "date": "2026-02-15",
                "overall_mood": "nostalgic",
                "highlights": [
                    "Shared fond memories of the 1960s",
                    "Mentioned upcoming lunch with neighbor",
                    "Slight word-finding difficulty with medication name"
                ],
                "cognitive_score": 85,
                "cognitive_trend": "stable",
                "recommendations": [
                    "Continue monitoring word-finding patterns",
                    "Consider scheduling doctor appointment if trend continues"
                ],
                "conversation_id": "conversation-001"
            }
        }


class FamilyContact(BaseModel):
    """
    Family member contact information for notifications
    """
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    relationship: str
    patient_ids: list[str] = Field(default_factory=list)
    notification_preferences: dict = Field(
        default_factory=lambda: {
            "daily_digest": True,
            "instant_alerts": True,
            "weekly_report": True
        }
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "family-sarah-001",
                "name": "Sarah Chen",
                "email": "sarah.chen@email.com",
                "phone": "+1-415-555-0123",
                "relationship": "Daughter",
                "patient_ids": ["patient-dorothy-001"],
                "notification_preferences": {
                    "daily_digest": True,
                    "instant_alerts": True,
                    "weekly_report": True
                }
            }
        }

"""
Pydantic request/response models for API routes.
Provides automatic validation + input sanitization.
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# Strip HTML tags to prevent XSS / injection into Sanity
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _sanitize(value: str) -> str:
    """Remove HTML tags and excessive whitespace."""
    if not value:
        return value
    value = _HTML_TAG_RE.sub("", value)
    value = re.sub(r"\s{3,}", "  ", value)  # collapse excessive spacing
    return value.strip()


class CreateConversationRequest(BaseModel):
    """Validated request body for POST /api/conversations."""
    patient_id: str = Field(..., min_length=1, max_length=100)
    transcript: str = Field(..., min_length=1, max_length=100_000)
    duration: int = Field(..., ge=0, le=86400)  # max 24 hours
    summary: str = Field(default="", max_length=5000)
    detected_mood: str = Field(default="neutral", max_length=50)
    response_times: Optional[list[float]] = None
    id: Optional[str] = Field(default=None, max_length=100)

    @field_validator("transcript", "summary", mode="before")
    @classmethod
    def sanitize_text(cls, v):
        return _sanitize(v) if isinstance(v, str) else v

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
            raise ValueError("patient_id must be alphanumeric with dashes/underscores/dots")
        return v

    @field_validator("detected_mood")
    @classmethod
    def validate_mood(cls, v):
        allowed = {"happy", "sad", "neutral", "anxious", "confused", "angry", "calm"}
        if v and v.lower() not in allowed:
            return "neutral"  # graceful fallback
        return v.lower()


class AcknowledgeAlertRequest(BaseModel):
    """Validated request body for PATCH /api/alerts/{id}."""
    acknowledged_by: str = Field(..., min_length=1, max_length=200)

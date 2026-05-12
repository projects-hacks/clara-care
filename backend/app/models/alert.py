from pydantic import BaseModel, Field

class AcknowledgeAlertRequest(BaseModel):
    """Validated request body for PATCH /api/alerts/{id}."""
    acknowledged_by: str = Field(..., min_length=1, max_length=200)

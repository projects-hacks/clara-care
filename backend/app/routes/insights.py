"""
Insights API Routes
Showcase endpoint for Sanity challenge - demonstrates structured content features
"""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/patients", tags=["insights"])

# Data store will be injected as dependency
_data_store = None


def get_data_store():
    """Dependency to get data store"""
    if _data_store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    return _data_store


def set_data_store(store):
    """Set the data store (called during app initialization)"""
    global _data_store
    _data_store = store


@router.get("/{patient_id}/insights")
async def get_patient_insights(patient_id: str):
    """
    Get structured content insights for a patient
    
    **SHOWCASE ENDPOINT for Sanity Challenge**
    
    Demonstrates features IMPOSSIBLE with flat files:
    - Cross-document reference traversal
    - Typed field aggregation (enums, booleans, numbers)
    - Relationship-based queries
    
    Features:
    - **Cognitive by Mood**: Groups conversations by mood enum, aggregates numeric metrics
    - **Nostalgia Effectiveness**: Filters by boolean trigger, compares metric averages
    - **Alert Summary**: Traverses Patient → Conversation → Alert references
    
    Returns:
        Dict with:
        - cognitive_by_mood: Vocabulary/coherence stats grouped by mood
        - nostalgia_effectiveness: Comparison of metrics with/without nostalgia
        - alert_summary: Cross-document alert statistics
    """
    store = get_data_store()
    
    # Verify patient exists
    patient = await store.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get insights using structured content queries
    insights = await store.get_patient_insights(patient_id)
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.get("name"),
        "insights": insights,
        "note": "These insights are only possible with structured content and typed fields"
    }

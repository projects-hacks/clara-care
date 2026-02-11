"""
Conversation API Routes
Endpoints for conversation history and details
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# Data store and cognitive pipeline will be injected as dependencies
_data_store = None
_cognitive_pipeline = None


def get_data_store():
    """Dependency to get data store"""
    if _data_store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    return _data_store


def get_cognitive_pipeline():
    """Dependency to get cognitive pipeline"""
    return _cognitive_pipeline


def set_data_store(store):
    """Set the data store (called during app initialization)"""
    global _data_store
    _data_store = store


def set_cognitive_pipeline(pipeline):
    """Set the cognitive pipeline (called during app initialization)"""
    global _cognitive_pipeline
    _cognitive_pipeline = pipeline


@router.get("")
async def list_conversations(
    patient_id: str = Query(..., description="Patient ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get paginated list of conversations for a patient
    
    Query params:
        - patient_id: Patient identifier
        - limit: Max results (1-100, default 10)
        - offset: Pagination offset (default 0)
    """
    store = get_data_store()
    
    conversations = await store.get_conversations(patient_id, limit=limit, offset=offset)
    
    return {
        "patient_id": patient_id,
        "conversations": conversations,
        "count": len(conversations),
        "limit": limit,
        "offset": offset
    }


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get full conversation details by ID
    
    Returns:
        - Full transcript
        - Cognitive metrics
        - Summary and mood
        - Timestamp and duration
    """
    store = get_data_store()
    
    conversation = await store.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.post("")
async def create_conversation(conversation: dict):
    """
    Create a new conversation record
    
    Body: Conversation object with transcript, metrics, etc.
    If cognitive pipeline is available, will run full analysis.
    
    Required fields:
        - patient_id
        - transcript
        - duration
    Optional fields:
        - summary
        - detected_mood
        - response_times
    """
    store = get_data_store()
    pipeline = get_cognitive_pipeline()
    
    # Validate required fields
    required_fields = ["patient_id", "transcript", "duration"]
    for field in required_fields:
        if field not in conversation:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # If cognitive pipeline is available, run full analysis
    if pipeline:
        result = await pipeline.process_conversation(
            patient_id=conversation["patient_id"],
            transcript=conversation["transcript"],
            duration=conversation["duration"],
            summary=conversation.get("summary", ""),
            detected_mood=conversation.get("detected_mood", "neutral"),
            response_times=conversation.get("response_times"),
            conversation_id=conversation.get("id")
        )
        
        if result.get("success"):
            return {
                "success": True,
                "conversation_id": result["conversation_id"],
                "cognitive_score": result.get("cognitive_score"),
                "alerts_generated": result.get("alerts_generated", 0)
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Pipeline processing failed")
            )
    else:
        # Fallback: just save raw conversation (no cognitive analysis)
        conversation_id = await store.save_conversation(conversation)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "note": "Saved without cognitive analysis (pipeline not available)"
        }

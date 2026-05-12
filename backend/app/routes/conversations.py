"""
Conversation API Routes
Endpoints for conversation history and details
"""

import re
from fastapi import APIRouter, HTTPException, Query, Depends

from app.dependencies import get_cognitive_pipeline, get_conversation_repo, get_patient_repo, get_contact_repo
from app.auth import get_current_user, verify_patient_access
from app.models.conversation import CreateConversationRequest
from app.normalizers import normalize_conversation

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("")
async def list_conversations(
    patient_id: str = Query(..., description="Patient ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    conversation_repo=Depends(get_conversation_repo),
    patient_repo=Depends(get_patient_repo),
    contact_repo=Depends(get_contact_repo),
):
    """
    Get paginated list of conversations for a patient
    """
    # Verify access
    await verify_patient_access(patient_repo, contact_repo, user.id, patient_id)

    conversations = conversation_repo.get_for_patient(patient_id, limit=limit, offset=offset)
    normalized_convs = [normalize_conversation(c) for c in conversations]

    return {
        "patient_id": patient_id,
        "conversations": normalized_convs,
        "count": len(conversations),
        "limit": limit,
        "offset": offset
    }


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user=Depends(get_current_user),
    conversation_repo=Depends(get_conversation_repo),
    patient_repo=Depends(get_patient_repo),
    contact_repo=Depends(get_contact_repo),
):
    """
    Get full conversation details by ID
    """
    conversation = conversation_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Verify access
    await verify_patient_access(patient_repo, contact_repo, user.id, conversation.get("patient_id"))

    return normalize_conversation(conversation)


@router.post("")
async def create_conversation(
    conversation: CreateConversationRequest,
    conversation_repo=Depends(get_conversation_repo),
    pipeline=Depends(get_cognitive_pipeline),
):
    """
    Create a new conversation record.
    If cognitive pipeline is available, will run full analysis.
    """
    conv_data = conversation.model_dump()

    # If cognitive pipeline is available, run full analysis
    if pipeline:
        result = await pipeline.process_conversation(
            patient_id=conv_data["patient_id"],
            transcript=conv_data["transcript"],
            duration=conv_data["duration"],
            summary=conv_data.get("summary", ""),
            detected_mood=conv_data.get("detected_mood", "neutral"),
            response_times=conv_data.get("response_times"),
            conversation_id=conv_data.get("id")
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
        # Fallback: just save raw conversation
        conversation_id = conversation_repo.save(conv_data)

        return {
            "success": True,
            "conversation_id": conversation_id,
            "note": "Saved without cognitive analysis (pipeline not available)"
        }

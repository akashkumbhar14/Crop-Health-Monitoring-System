import uuid
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.core.auth import get_current_farmer
from app.ai.graph.crop_pipeline import crop_pipeline
from app.memory.conversation_memory import ConversationMemory

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., example="How do I treat red rot in sugarcane?")
    plant_name: str | None = Field(
        default=None,
        example="sugarcane",
        description="Optional. If not provided, extracted from message or asked via follow-up."
    )
    language: str = Field(default="english", example="marathi")
    session_id: str | None = Field(default=None)


@router.post("/chat/message")
async def chat_message(
    payload: ChatRequest,
    farmer=Depends(get_current_farmer),
):
    """
    Text-only chat with the crop advisor.
    plant_name is optional — extracted from message by guardrail/intent agent.
    If plant cannot be determined, follow-up question is returned.
    """
    user_id = str(farmer["_id"])
    session_id = payload.session_id or str(uuid.uuid4())

    # Try to extract plant name from message if not provided
    plant_name = (payload.plant_name or "").strip().lower()

    # Common plant name extraction from message
    if not plant_name:
        message_lower = payload.message.lower()
        known_plants = ["sugarcane", "tomato", "wheat", "rice", "grape"]
        for plant in known_plants:
            if plant in message_lower:
                plant_name = plant
                break

    # Load conversation memory
    conversation_summary = await ConversationMemory.get_summary(user_id)

    initial_state = {
        "user_id": user_id,
        "session_id": session_id,
        "request_type": "chat",
        "user_input": payload.message,
        "plant_name": plant_name,
        "image_path": None,
        "image_url": None,
        "messages": [],
        "conversation_summary": conversation_summary,
        "user_language": payload.language.lower().strip(),
        "is_safe": True,
        "guardrail_flag": None,
        "rejection_reason": None,
        "intent": None,
        "extracted_entities": {},
        "requires_follow_up": False,
        "follow_up_message": None,
        "pending_intent": None,
        "requires_general_response": False,
        "specialist_agent": None,
        "ml_model_handler": None,
        "run_ml_model": False,
        "predicted_disease": None,
        "ml_confidence": None,
        "analysis_focus": [],
        "rag_query": None,
        "rag_context": None,
        "functional_prompt": None,
        "treatment_plan": None,
        "disease_analysis": None,
        "final_response": None,
        "error": None,
    }

    try:
        result = await crop_pipeline.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Chat pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    final_response = result.get("final_response", {})

    # Save to conversation memory
    if final_response.get("success"):
        await ConversationMemory.update(
            user_id=user_id,
            question=payload.message,
            answer=final_response.get("summary") or str(final_response.get("message", "")),
        )

    return {
        "session_id": session_id,
        "user_id": user_id,
        **final_response,
    }


@router.delete("/chat/memory")
async def clear_memory(farmer=Depends(get_current_farmer)):
    """Clear conversation memory for the current farmer."""
    user_id = str(farmer["_id"])
    await ConversationMemory.clear(user_id)
    return {"success": True, "message": "Conversation memory cleared."}


@router.get("/chat/memory")
async def get_memory(farmer=Depends(get_current_farmer)):
    """Get current conversation summary for the farmer."""
    user_id = str(farmer["_id"])
    summary = await ConversationMemory.get_summary(user_id)
    return {
        "user_id": user_id,
        "has_memory": summary is not None,
        "summary": summary,
    }
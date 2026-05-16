import os
import uuid
import logging
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.config import settings
from app.core.auth import get_current_farmer
from app.ai.graph.crop_pipeline import crop_pipeline
from app.memory.conversation_memory import ConversationMemory

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


@router.post("/predictions/analyze")
async def analyze_crop(
    file: UploadFile = File(...),
    plant_name: str = Form(...),
    user_query: str = Form(default="Analyze this crop image"),
    language: str = Form(default="english"),
    farmer=Depends(get_current_farmer),
):
    """
    Predict crop disease from uploaded image.
    Runs full pipeline: guardrail → intent → orchestrator → planner → specialist → response.
    """
    user_id = str(farmer["_id"])
    session_id = str(uuid.uuid4())

    # Save image locally
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image format. Use jpg, png, or webp.")

    local_filename = f"{session_id}.{file_ext}"
    local_path = os.path.join(UPLOAD_DIR, local_filename)

    with open(local_path, "wb") as f:
        f.write(await file.read())

    # Upload to Cloudinary
    image_url = None
    try:
        upload_result = cloudinary.uploader.upload(
            local_path,
            folder=settings.CLOUDINARY_FOLDER,
            public_id=session_id,
        )
        image_url = upload_result.get("secure_url")
        logger.info(f"Cloudinary upload success: {image_url}")
    except Exception as e:
        logger.warning(f"Cloudinary upload failed (non-blocking): {e}")

    # Load conversation memory
    conversation_summary = await ConversationMemory.get_summary(user_id)

    # Build initial state
    initial_state = {
        "user_id": user_id,
        "session_id": session_id,
        "request_type": "predict",
        "user_input": user_query,
        "plant_name": plant_name.lower().strip(),
        "image_path": local_path,
        "image_url": image_url,
        "messages": [],
        "conversation_summary": conversation_summary,
        "user_language": language.lower().strip(),
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
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up local file after pipeline completes
        if os.path.exists(local_path):
            os.remove(local_path)

    final_response = result.get("final_response", {})

    # Save to conversation memory
    if final_response.get("success"):
        await ConversationMemory.update(
            user_id=user_id,
            question=user_query,
            answer=final_response.get("summary") or str(final_response.get("message", "")),
        )

    return {
        "session_id": session_id,
        "user_id": user_id,
        "image_url": image_url,
        **final_response,
    }
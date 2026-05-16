import json
import logging
import importlib
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.services.agent_state import AgentState
from app.registry.plant_registry import get_supported_diseases, get_plant_info
from app.config import settings
from app.ai.llm import get_llm

logger = logging.getLogger(__name__)



class PlannerResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rag_query: str = Field(
        description=(
            "Precise search query for knowledge base vector store. "
            "Include disease name + crop + specific aspect. "
            "Example: 'red rot sugarcane stem causes treatment fungicide'"
        )
    )
    analysis_focus: List[str] = Field(
        description=(
            "Ordered list of aspects specialist agent must cover. "
            "Example: ['disease_causes', 'severity_assessment', "
            "'immediate_treatment', 'fertilizer_advice', 'pesticide_advice', 'prevention']"
        )
    )
    functional_prompt: str = Field(
        description=(
            "Domain-specific instruction injected into specialist agent system prompt. "
            "Include: disease context, farmer urgency, language instruction, focus areas."
        )
    )
    immediate_steps: List[str] = Field(
        description="Urgent actions farmer must take right now."
    )
    fertilizers: List[str] = Field(
        description="Recommended fertilizers with dosage. Use locally available Indian products."
    )
    pesticides: List[str] = Field(
        description="Recommended pesticides with dosage. Use locally available Indian products."
    )
    prevention: List[str] = Field(
        description="Preventive measures to avoid disease recurrence."
    )
    follow_up_days: int = Field(
        description="Days after which farmer should re-check the crop."
    )
    response_tone: str = Field(
        description="One of: urgent | advisory | informational"
    )


SYSTEM_PROMPT = """
Role:
You are an expert Crop Treatment Planner for AgroAssist — an AI-powered crop disease detection system for Indian farmers.

You receive the ML model's disease prediction and create a precise execution plan
that guides the specialist agent on what to fetch from the knowledge base and what to analyze.

[CROP KNOWLEDGE]
Plant: {plant_name}
Known diseases: {known_diseases}
Crop info: {crop_info}

[CONVERSATION MEMORY]
{conversation_summary}

[ML MODEL OUTPUT]
Detected Disease: {predicted_disease}
ML Confidence: {ml_confidence}

[REQUEST CONTEXT]
Intent: {intent}
Farmer Query: {user_input}
Extracted Entities: {extracted_entities}
Farmer Language: {user_language}

=============================================================
TASK 1 — RAG QUERY
=============================================================
Build a precise vector search query for the knowledge base.
- Include disease name + crop + aspects needed
- Add location if mentioned (affects pesticide availability)
- Example: "red rot sugarcane stem symptoms treatment fungicide Maharashtra"

=============================================================
TASK 2 — ANALYSIS FOCUS
=============================================================
Define what specialist agent must cover based on:
- Detected disease and confidence level
- Farmer's specific question
- Urgency from extracted entities
- What was already covered in conversation memory (avoid repetition)

=============================================================
TASK 3 — FUNCTIONAL PROMPT
=============================================================
Write instruction for specialist agent system prompt:
- What disease/topic to focus on
- Detail level needed based on urgency
- Always instruct to respond in: {user_language}

=============================================================
TASK 4 — TREATMENT PLAN
=============================================================
Based on agricultural knowledge for Indian farmers:
- immediate_steps: what to do RIGHT NOW
- fertilizers: locally available Indian products with dosage
- pesticides: locally available Indian products with dosage
- prevention: future prevention measures
- follow_up_days: when to re-check

=============================================================
TASK 5 — RESPONSE TONE
=============================================================
- urgent       : High confidence disease, severe symptoms, immediate crop loss risk
- advisory     : Disease detected, moderate severity, needs treatment soon
- informational: General advice, no immediate crisis

=============================================================
OUTPUT
=============================================================
Return ONLY valid JSON matching PlannerResult schema. No extra text.
"""


def _run_ml_model(state: AgentState) -> AgentState:
    """
    Runs the ML model if orchestrator flagged run_ml_model=True.
    Updates state with predicted_disease and ml_confidence.
    """
    ml_model_handler = state.get("ml_model_handler", "")
    image_path = state.get("image_path")

    if not ml_model_handler or not image_path:
        logger.info("Planner: skipping ML — no handler or image")
        return state

    try:
        module_path, class_name = ml_model_handler.rsplit(".", 1)
        module = importlib.import_module(module_path)
        predictor_class = getattr(module, class_name)
        predictor = predictor_class.get_instance()
        result = predictor.predict(image_path)

        predicted_disease = result.get("disease")
        ml_confidence = result.get("confidence", 0.0)

        logger.info(f"Planner ML result: disease={predicted_disease} confidence={ml_confidence}")

        # Block low confidence
        if ml_confidence < settings.ML_CONFIDENCE_THRESHOLD:
            return {
                **state,
                "is_safe": False,
                "rejection_reason": (
                    "Image quality too low for confident detection. "
                    "Please upload a clearer crop photo."
                ),
            }

        return {
            **state,
            "predicted_disease": predicted_disease,
            "ml_confidence": ml_confidence,
        }

    except Exception as e:
        logger.error(f"Planner ML execution failed: {e}", exc_info=True)
        return {**state, "error": f"ML model failed: {str(e)}"}


def planner_agent(state: AgentState) -> AgentState:
    """
    Phase A: Run ML model (if orchestrator flagged run_ml_model=True)
    Phase B: Build execution plan for specialist agent
    Phase C: Store plan in state for specialist agent to consume
    """
    logger.info("=" * 50)
    logger.info("Planner agent start")
    logger.info(f"  user: {state.get('user_id')}")
    logger.info(f"  run_ml_model: {state.get('run_ml_model')}")
    logger.info(f"  specialist_agent: {state.get('specialist_agent')}")
    logger.info("=" * 50)

    # Phase A — Run ML model
    if state.get("run_ml_model"):
        state = _run_ml_model(state)
        # If ML blocked due to low confidence, return early
        if not state.get("is_safe", True):
            return state
        if state.get("error"):
            return state

    user_input = state.get("user_input", "")
    plant_name = state.get("plant_name", "")
    intent = state.get("intent", "general_advice")
    predicted_disease = state.get("predicted_disease")
    ml_confidence = state.get("ml_confidence", 0.0)
    extracted_entities = state.get("extracted_entities", {})
    conversation_summary = state.get("conversation_summary", "")
    user_language = state.get("user_language", "english")

    known_diseases = ", ".join(get_supported_diseases(plant_name)) or "unknown"
    crop_info = get_plant_info(plant_name) or {}

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Build the execution plan for the specialist agent.")
    ])

    try:
        chain = prompt | get_llm().with_structured_output(
            PlannerResult,
            method="function_calling"
        )

        result: PlannerResult = chain.invoke({
            "plant_name": plant_name,
            "known_diseases": known_diseases,
            "crop_info": json.dumps(crop_info),
            "conversation_summary": conversation_summary or "No previous conversation.",
            "intent": intent,
            "predicted_disease": predicted_disease or "not detected",
            "ml_confidence": f"{ml_confidence:.0%}" if ml_confidence else "N/A",
            "user_input": user_input,
            "extracted_entities": json.dumps(extracted_entities),
            "user_language": user_language,
        })

        treatment_plan = {
            "immediate_steps": result.immediate_steps,
            "fertilizers": result.fertilizers,
            "pesticides": result.pesticides,
            "prevention": result.prevention,
            "follow_up_days": result.follow_up_days,
            "response_tone": result.response_tone,
        }

        logger.info("=" * 50)
        logger.info("Planner agent end")
        logger.info(f"  rag_query: {result.rag_query}")
        logger.info(f"  analysis_focus: {result.analysis_focus}")
        logger.info(f"  response_tone: {result.response_tone}")
        logger.info(f"  follow_up_days: {result.follow_up_days}")
        logger.info("=" * 50)

        # Fetch RAG context using the built query
        rag_context = fetch_rag_context(result.rag_query)

        return {
            **state,
            "rag_query": result.rag_query,
            "rag_context": rag_context,
            "analysis_focus": result.analysis_focus,
            "functional_prompt": result.functional_prompt,
            "treatment_plan": treatment_plan,
        }

    except Exception as e:
        logger.error(f"Planner agent error: {e}", exc_info=True)
        return {
            **state,
            "rag_query": f"{predicted_disease or 'disease'} {plant_name} treatment",
            "analysis_focus": ["disease_causes", "immediate_treatment", "prevention_measures"],
            "functional_prompt": f"Analyze {predicted_disease or 'crop disease'} for {plant_name}. Respond in {user_language}.",
            "treatment_plan": {
                "immediate_steps": [],
                "fertilizers": [],
                "pesticides": [],
                "prevention": [],
                "follow_up_days": 7,
                "response_tone": "advisory",
            },
            "error": str(e),
        }


def fetch_rag_context(rag_query: str) -> str:
    """Fetch RAG context from Chroma. Returns empty string if RAG not ready."""
    try:
        from app.ai.rag.rag_pipeline import RagPipeline
        rag = RagPipeline.get_instance()
        return rag.retrieve(rag_query)
    except Exception as e:
        logger.warning(f"RAG fetch failed (non-blocking): {e}")
        return ""
import json
import logging
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.services.agent_state import AgentState
from app.registry.plant_registry import (
    get_specialist_agent,
    get_model_handler,
    get_active_plants,
    get_plant_info,
)
from app.config import settings
from app.ai.llm import get_llm

logger = logging.getLogger(__name__)



class OrchestratorResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    specialist_agent: str = Field(
        description="Exact specialist agent key from plant registry. e.g. 'sugarcane_agent'"
    )
    ml_model_handler: str = Field(
        description="Exact ML model handler path from plant registry."
    )
    run_ml_model: bool = Field(
        description="True only if intent is disease_check AND image is provided."
    )
    skip_reason: str | None = Field(
        default=None,
        description="Why ML is skipped. Null if running."
    )


ROUTING_PROMPT = """
Role:
You are the Master Orchestrator for AgroAssist.
Your ONLY job is to decide which specialist agent and ML model to call.
You do NOT run models. You do NOT create plans. You do NOT analyze diseases.
You only route.

Instructions:
1. Read the intent from query intent agent output.
2. Match plant_name to the correct entry in [PLANT REGISTRY].
3. Decide if ML model should run:
   - run_ml_model = True  ONLY if intent = "disease_check" AND image is provided.
   - run_ml_model = False if intent = "general_advice" OR no image.
4. Return exact specialist_agent and ml_model_handler keys from registry.
5. Never hallucinate keys. Only use what exists in registry.

[PLANT REGISTRY]
{plant_registry}

[QUERY INTENT AGENT OUTPUT]
Intent: {intent}
Plant: {plant_name}
Has Image: {has_image}
Extracted Entities: {extracted_entities}

Output: Strict JSON matching OrchestratorResult schema. No extra text.
"""


def orchestrator_node(state: AgentState) -> AgentState:
    """
    ONLY responsibility: decide which ML model and specialist agent to call.
    Output stored in state for planner to execute.
    """
    logger.info("=" * 50)
    logger.info("Orchestrator start")
    logger.info(f"  user: {state.get('user_id')}")
    logger.info(f"  intent: {state.get('intent')}")
    logger.info(f"  plant: {state.get('plant_name')}")
    logger.info("=" * 50)

    # Safety check
    if not state.get("is_safe", True):
        logger.warning("Orchestrator blocked — is_safe=False")
        return state

    intent = state.get("intent", "general_advice")
    plant_name = (state.get("plant_name") or "").lower().strip()
    image_path = state.get("image_path")
    extracted_entities = state.get("extracted_entities", {})

    # Build registry context for LLM
    active_plants = get_active_plants()
    plant_registry = {
        p: {
            "specialist_agent": get_specialist_agent(p),
            "ml_model_handler": get_model_handler(p),
            "supported_diseases": get_plant_info(p).get("supported_diseases", []),
        }
        for p in active_plants
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTING_PROMPT),
        ("human", "Determine which agent and model to call.")
    ])

    try:
        chain = prompt | get_llm().with_structured_output(
            OrchestratorResult,
            method="function_calling"
        )

        result: OrchestratorResult = chain.invoke({
            "plant_registry": json.dumps(plant_registry, indent=2),
            "intent": intent,
            "plant_name": plant_name,
            "has_image": "yes" if image_path else "no",
            "extracted_entities": json.dumps(extracted_entities),
        })

        logger.info("=" * 50)
        logger.info("Orchestrator end")
        logger.info(f"  specialist_agent: {result.specialist_agent}")
        logger.info(f"  ml_model_handler: {result.ml_model_handler}")
        logger.info(f"  run_ml_model: {result.run_ml_model}")
        logger.info(f"  skip_reason: {result.skip_reason}")
        logger.info("=" * 50)

        return {
            **state,
            "specialist_agent": result.specialist_agent,
            "ml_model_handler": result.ml_model_handler,
            "run_ml_model": result.run_ml_model,
        }

    except Exception as e:
        logger.error(f"Orchestrator error: {e}", exc_info=True)
        # Fallback — use registry directly
        return {
            **state,
            "specialist_agent": get_specialist_agent(plant_name) or "sugarcane_agent",
            "ml_model_handler": get_model_handler(plant_name) or "",
            "run_ml_model": bool(image_path) and intent == "disease_check",
            "error": str(e),
        }
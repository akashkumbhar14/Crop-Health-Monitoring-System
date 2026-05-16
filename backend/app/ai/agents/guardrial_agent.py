import logging
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.services.agent_state import AgentState
from app.registry.plant_registry import is_plant_supported, get_active_plants
from app.config import settings
from app.ai.llm import get_llm

logger = logging.getLogger(__name__)



SUPPORTED_LANGUAGES = ["english", "marathi", "hindi"]


class GuardrailResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_safe: bool
    guardrail_flag: str = Field(
        description="One of: safe | vague | blocked"
    )
    next_node: str = Field(
        description="One of: intent_agent | blocked"
    )
    user_input: str = Field(
        description="Cleaned and rephrased version of raw query for downstream agents."
    )
    user_language: str = Field(
        description=(
            "Detected language of the farmer query. "
            "One of: english | marathi | hindi. "
            "Detect from script and vocabulary. "
            "Devanagari script = marathi or hindi. "
            "Default to english if uncertain."
        )
    )
    rejection_reason: str | None = Field(
        default=None,
        description="Reason for blocking. Null if not blocked."
    )
    requires_follow_up: bool = Field(
        description="True if query is vague and needs clarification."
    )
    follow_up_message: str | None = Field(
        default=None,
        description=(
            "Clarification question in the farmer's detected language. "
            "Null if not needed."
        )
    )
    extracted_entities: dict = Field(
        description="Extracted entities: plant, symptoms, location, urgency."
    )


SYSTEM_PROMPT = """
Role:
You are a strict Safety and Validation Guardrail for AgroAssist — an AI-powered crop disease detection app built for Indian farmers.

[RECENT CONVERSATION]
{conversation_history}

[SUPPORTED CROPS]
{supported_crops}

[SUPPORTED LANGUAGES]
- english
- marathi
- hindi

Your responsibilities:

1. LANGUAGE DETECTION
   - Detect the language of the farmer query.
   - Devanagari script (e.g. मराठी, हिंदी) → identify as marathi or hindi based on vocabulary.
   - Roman script with Marathi/Hindi words (e.g. "maza oos", "meri fasal") → marathi or hindi.
   - Default to english if uncertain.
   - All your rejection_reason and follow_up_message must be written in the detected language.

2. SAFETY CHECK
   - Block offensive, abusive, or hate speech queries. Set is_safe=False, next_node=blocked.
   - Block queries completely unrelated to farming, crops, agriculture, weather, or soil.

3. CROP VALIDATION
   - If plant name is not in supported crops → blocked.
   - If plant name is missing → blocked.

4. INTENT CLASSIFICATION
   - "safe"    : query is clear, crop supported, language supported → next_node=intent_agent
   - "vague"   : farming-related but unclear → requires_follow_up=True, ask in farmer's language
   - "blocked" : unsafe, irrelevant, unsupported crop → next_node=blocked

5. QUERY CLEANING
   - Rephrase user_input into clean unambiguous English for downstream agents.
   - Always output cleaned query in English regardless of input language.
   - Resolve pronouns from conversation history.
   - Preserve all symptoms, locations, and constraints.
   - Do NOT answer the query.

6. ENTITY EXTRACTION
   - plant      : crop name
   - symptoms   : visible symptoms described
   - location   : farm location if mentioned
   - urgency    : high | medium | low

7. STALE STATE RESET
   - Always reset downstream fields to prevent stale values leaking.

[FARMER REQUEST]
Plant: {plant_name}
Query: {user_input}
Has Image: {has_image}
Request Type: {request_type}

Output strictly as JSON matching GuardrailResult schema. No extra text.
"""


def guardrail_agent(state: AgentState) -> AgentState:
    """
    First checkpoint in the pipeline.
    Detects farmer language.
    Validates safety, crop support, query clarity.
    Cleans query to English for downstream agents.
    Resets stale state on every run.
    """
    plant_name = (state.get("plant_name") or "").strip()
    user_input = (state.get("user_input") or "").strip()
    image_path = state.get("image_path")
    request_type = state.get("request_type", "chat")

    logger.info("=" * 50)
    logger.info("Guardrail agent start")
    logger.info(f"  user: {state.get('user_id')}")
    logger.info(f"  plant: {plant_name}")
    logger.info(f"  query: {user_input[:80]}")
    logger.info("=" * 50)

    # Build conversation history
    raw_messages = state.get("messages", [])
    history_lines = []
    for msg in raw_messages[-6:]:
        if isinstance(msg, tuple):
            role, content = msg[0], str(msg[1])[:200]
            history_lines.append(f"{role.upper()}: {content}")
        elif hasattr(msg, "type") and hasattr(msg, "content"):
            history_lines.append(f"{msg.type.upper()}: {str(msg.content)[:200]}")
    conversation_history = "\n".join(history_lines) or "No previous conversation."

    # Stale state reset fields
    reset_fields = {
        "intent": None,
        "predicted_disease": None,
        "ml_confidence": None,
        "rag_context": None,
        "disease_analysis": None,
        "treatment_plan": None,
        "final_response": None,
        "error": None,
    }

    # Hard block — empty input
    if not plant_name and not user_input:
        logger.warning(f"Guardrail hard block — empty input for user: {state.get('user_id')}")
        return {
            **state,
            **reset_fields,
            "is_safe": False,
            "guardrail_flag": "blocked",
            "next_node": "blocked",
            "user_language": "english",
            "rejection_reason": "Please provide a crop name and your question.",
            "requires_follow_up": False,
            "follow_up_message": None,
            "extracted_entities": {},
        }

    # Hard block — unsupported crop
    if plant_name and not is_plant_supported(plant_name):
        active = ", ".join(get_active_plants())
        logger.warning(f"Guardrail blocked unsupported crop: {plant_name}")
        return {
            **state,
            **reset_fields,
            "is_safe": False,
            "guardrail_flag": "blocked",
            "next_node": "blocked",
            "user_language": "english",
            "rejection_reason": f"'{plant_name}' is not supported yet. Currently supported: {active}.",
            "requires_follow_up": False,
            "follow_up_message": None,
            "extracted_entities": {},
        }

    active_crops = "\n".join([f"- {p}" for p in get_active_plants()])

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Validate, detect language, and clean this farmer request.")
    ])

    try:
        chain = prompt | get_llm().with_structured_output(
            GuardrailResult,
            method="function_calling"
        )

        result: GuardrailResult = chain.invoke({
            "conversation_history": conversation_history,
            "supported_crops": active_crops,
            "plant_name": plant_name or "not provided",
            "user_input": user_input or "not provided",
            "has_image": "yes" if image_path else "no",
            "request_type": request_type,
        })

        # Normalize detected language
        detected_language = result.user_language.lower().strip()
        if detected_language not in SUPPORTED_LANGUAGES:
            detected_language = "english"

        logger.info("=" * 50)
        logger.info("Guardrail agent end")
        logger.info(f"  flag: {result.guardrail_flag}")
        logger.info(f"  next: {result.next_node}")
        logger.info(f"  language: {detected_language}")
        logger.info(f"  cleaned_query: {result.user_input[:80]}")
        logger.info("=" * 50)

        return {
            **state,
            **reset_fields,
            "is_safe": result.is_safe,
            "guardrail_flag": result.guardrail_flag,
            "next_node": result.next_node,
            "user_input": result.user_input,       # cleaned English query
            "user_language": detected_language,     # detected language
            "rejection_reason": result.rejection_reason,
            "requires_follow_up": result.requires_follow_up,
            "follow_up_message": result.follow_up_message,
            "extracted_entities": result.extracted_entities,
        }

    except Exception as e:
        logger.error(f"Guardrail error: {e}", exc_info=True)
        return {
            **state,
            **reset_fields,
            "is_safe": False,
            "guardrail_flag": "blocked",
            "next_node": "blocked",
            "user_language": "english",
            "rejection_reason": "Unable to validate request. Please try again.",
            "requires_follow_up": False,
            "follow_up_message": None,
            "extracted_entities": {},
            "error": str(e),
        }
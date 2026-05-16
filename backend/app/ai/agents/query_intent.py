import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.prompts import ChatPromptTemplate
from app.services.agent_state import AgentState
from app.registry.plant_registry import get_supported_diseases
from app.ai.llm import get_llm

logger = logging.getLogger(__name__)


class IntentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str = Field(
        description="Primary intent. One of: disease_check | general_advice | chitchat"
    )
    requires_image: bool = Field(
        description="True if intent is disease_check but no image was provided."
    )
    requires_follow_up: bool = Field(
        description="True only if query cannot proceed without more info from farmer."
    )
    follow_up_message: Optional[str] = Field(
        default=None,
        description="One short clarification question in farmer's language. Null if not needed."
    )
    pending_intent: Optional[str] = Field(
        default=None,
        description="Preserved intent if follow-up needed. Restored on next turn."
    )
    extracted_entities: Dict[str, Any] = Field(
        description="Entities: plant_name, symptoms, affected_part, location, disease_name, urgency."
    )
    refined_query: str = Field(
        description="Clean specific actionable English query for downstream agents."
    )
    requires_general_response: bool = Field(
        description="True if chitchat — skip ML and RAG entirely."
    )


SYSTEM_PROMPT = """
Role:
You are an expert Query Intent Classifier for AgroAssist — an AI-powered crop disease detection app for Indian farmers.

[FARMER LANGUAGE]
{user_language}
Note: Write follow_up_message in this language. Write refined_query always in English.

[RECENT CONVERSATION]
{conversation_history}

[PREVIOUS BOT QUESTION]
{last_bot_message}

[PREVIOUS EXTRACTED ENTITIES]
{existing_entities}

[CROP CONTEXT]
Plant: {plant_name}
Known diseases for this crop: {known_diseases}
Has image attached: {has_image}

[CURRENT FARMER QUERY]
{user_input}

=============================================================
TASK 1 — INTENT CLASSIFICATION
=============================================================
Classify into exactly one intent:

- "disease_check":
  * Farmer uploaded a crop image
  * Farmer describes visible symptoms (yellow leaves, black spots, wilting, rotting, drying)
  * Farmer asks "what disease is this?" or "is my crop healthy?"
  * If no image provided → set requires_image=True, ask farmer to upload image in {user_language}

- "general_advice":
  * Questions about fertilizers, pesticides, irrigation, soil, weather
  * Prevention, yield improvement, crop calendar, sowing, harvesting
  * Follow-up questions after disease was already detected

- "chitchat":
  * Greetings, thank you, off-topic messages
  * Set requires_general_response=True

=============================================================
TASK 2 — ENTITY EXTRACTION
=============================================================
Extract ALL available entities. Merge with existing — never drop previous ones.

- plant_name    : Crop name
- symptoms      : Visible symptoms (e.g. "yellow leaves, black spots")
- affected_part : Plant part affected (e.g. "leaves", "stem", "roots")
- location      : Farm location if mentioned
- disease_name  : If farmer already suspects a disease
- urgency       : high | medium | low
  * high   = crop dying, spreading fast, immediate loss
  * medium = visible symptoms, crop stable
  * low    = preventive, general advice

=============================================================
TASK 3 — QUERY REFINEMENT
=============================================================
Rewrite query as precise actionable English for downstream agents.
- Use all extracted entities to make it specific
- Resolve pronouns from conversation history
- Always output in English
- Example: "maza oos kharab disat aahe" →
  "Sugarcane plant showing yellowing and wilting in Maharashtra,
   farmer needs urgent disease identification and treatment advice"

=============================================================
TASK 4 — FOLLOW-UP DECISION
=============================================================
Set requires_follow_up=True ONLY if query genuinely cannot proceed:
- disease_check with no image → ask for image in farmer's language
- Symptoms too vague → ask what farmer sees in farmer's language
- Do NOT ask follow-up if enough info exists

=============================================================
OUTPUT
=============================================================
Return ONLY valid JSON matching IntentResult schema. No extra text.
"""


def intent_agent(state: AgentState) -> AgentState:
    """
    Classifies farmer query intent.
    Merges and enriches extracted entities.
    Refines query in English for downstream agents.
    Writes follow-up messages in farmer's detected language.
    Graph handles all routing — this node only classifies.
    """
    user_input = state.get("user_input", "")
    plant_name = state.get("plant_name", "")
    image_path = state.get("image_path")
    existing_entities = state.get("extracted_entities", {})
    paused_intent = state.get("pending_intent")
    last_bot_message = state.get("follow_up_message", "")
    user_language = state.get("user_language", "english")

    logger.info("=" * 50)
    logger.info("Intent agent start")
    logger.info(f"  user: {state.get('user_id')}")
    logger.info(f"  language: {user_language}")
    logger.info(f"  query: {user_input[:80]}")
    logger.info(f"  pending_intent: {paused_intent}")
    logger.info(f"  existing_entities: {existing_entities}")
    logger.info("=" * 50)

    # Fresh query — clear stale entities so previous turn doesn't pollute
    if not paused_intent:
        logger.info("Fresh query — clearing stale entity memory")
        existing_entities = {}
        last_bot_message = ""

    # Build conversation history
    raw_messages = state.get("messages", [])
    history_lines = []
    for msg in raw_messages[-6:]:
        if isinstance(msg, tuple):
            role, content = msg[0], str(msg[1])[:300]
            history_lines.append(f"{role.upper()}: {content}")
        elif hasattr(msg, "type") and hasattr(msg, "content"):
            history_lines.append(f"{msg.type.upper()}: {str(msg.content)[:300]}")
    conversation_history = "\n".join(history_lines) or "No previous conversation."

    known_diseases = ", ".join(get_supported_diseases(plant_name)) or "unknown"

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Classify intent and extract entities from this farmer query.")
    ])

    try:
        chain = prompt | get_llm().with_structured_output(
            IntentResult,
            method="function_calling"
        )

        result: IntentResult = chain.invoke({
            "user_language": user_language,
            "conversation_history": conversation_history,
            "last_bot_message": last_bot_message or "None",
            "existing_entities": json.dumps(existing_entities),
            "plant_name": plant_name,
            "known_diseases": known_diseases,
            "has_image": "yes" if image_path else "no",
            "user_input": user_input,
        })

        # Merge new entities with existing for follow-up continuity
        merged_entities = {**existing_entities, **result.extracted_entities}

        logger.info("=" * 50)
        logger.info("Intent agent end")
        logger.info(f"  intent: {result.intent}")
        logger.info(f"  requires_image: {result.requires_image}")
        logger.info(f"  pending_intent: {result.pending_intent}")
        logger.info(f"  merged_entities: {merged_entities}")
        logger.info("=" * 50)

        return {
            **state,
            "intent": result.intent,
            "user_input": result.refined_query,
            "extracted_entities": merged_entities,
            "requires_follow_up": result.requires_follow_up,
            "follow_up_message": result.follow_up_message,
            "pending_intent": result.pending_intent,
            "requires_general_response": result.requires_general_response,
        }

    except Exception as e:
        logger.error(f"Intent agent error: {e}", exc_info=True)
        return {
            **state,
            "intent": "general_advice",
            "extracted_entities": existing_entities,
            "requires_follow_up": False,
            "follow_up_message": None,
            "pending_intent": None,
            "requires_general_response": False,
            "error": str(e),
        }
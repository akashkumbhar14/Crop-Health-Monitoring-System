import logging
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.prompts import ChatPromptTemplate
from app.services.agent_state import AgentState
from app.ai.llm import get_llm

logger = logging.getLogger(__name__)



class ResponseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(
        description=(
            "Short 2-3 sentence summary of the findings. "
            "Simple language a farmer can understand. "
            "Must be in the farmer's language."
        )
    )
    main_message: str = Field(
        description=(
            "The most important thing the farmer needs to know right now. "
            "One clear sentence. In farmer's language."
        )
    )
    what_to_do_now: str = Field(
        description=(
            "Immediate action in one or two sentences. "
            "Practical and specific. In farmer's language."
        )
    )
    follow_up_advice: str = Field(
        description=(
            "What to do in the next few days. "
            "In farmer's language."
        )
    )


SYSTEM_PROMPT = """
Role:
You are the Final Response Builder for AgroAssist — an AI crop disease detection app for Indian farmers.

Your job is to take the full analysis from the specialist agent and treatment plan from the planner,
and build a clean, simple, farmer-friendly final response.

[RESPONSE RULES]
1. Write EVERYTHING in {user_language} — farmer must understand every word.
2. Use simple vocabulary — farmer may have low literacy.
3. Be direct — tell the farmer exactly what to do.
4. Never use technical jargon without explanation.
5. Tone must match: {response_tone}
   - urgent       : Use strong language, emphasize urgency, act NOW
   - advisory     : Calm but clear, act soon
   - informational: Friendly and helpful, no panic

[DISEASE ANALYSIS FROM SPECIALIST AGENT]
{disease_analysis}

[TREATMENT PLAN FROM PLANNER]
Immediate Steps: {immediate_steps}
Fertilizers: {fertilizers}
Pesticides: {pesticides}
Prevention: {prevention}
Follow-up in: {follow_up_days} days

[FARMER CONTEXT]
Query: {user_input}
Language: {user_language}
Urgency: {urgency}

=============================================================
OUTPUT
=============================================================
Return ONLY valid JSON matching ResponseResult schema. No extra text.
"""


def response_builder_agent(state: AgentState) -> AgentState:
    """
    Final agent in the pipeline.
    Handles all exit paths:
    - Blocked by guardrail
    - Follow-up needed
    - Chitchat
    - Successful disease analysis
    - General advice
    Builds clean structured final_response in farmer's language.
    """
    logger.info("=" * 50)
    logger.info("Response builder start")
    logger.info(f"  user: {state.get('user_id')}")
    logger.info(f"  intent: {state.get('intent')}")
    logger.info(f"  language: {state.get('user_language')}")
    logger.info("=" * 50)

    user_language = state.get("user_language", "english")
    intent = state.get("intent")
    user_input = state.get("user_input", "")
    extracted_entities = state.get("extracted_entities", {})
    urgency = extracted_entities.get("urgency", "medium")

    # Exit path 1 — Blocked by guardrail
    if not state.get("is_safe", True):
        rejection = state.get("rejection_reason", "Unable to process your request.")
        logger.info(f"Response builder: blocked — {rejection}")
        return {
            **state,
            "final_response": {
                "success": False,
                "type": "blocked",
                "message": rejection,
                "follow_up_question": state.get("follow_up_message"),
                "disease": None,
                "summary": None,
                "analysis": None,
                "treatment_plan": None,
            }
        }

    # Exit path 2 — Follow-up needed
    if state.get("requires_follow_up"):
        follow_up = state.get("follow_up_message", "Could you provide more details?")
        logger.info(f"Response builder: follow-up needed — {follow_up}")
        return {
            **state,
            "final_response": {
                "success": True,
                "type": "follow_up",
                "message": follow_up,
                "follow_up_question": follow_up,
                "disease": None,
                "summary": None,
                "analysis": None,
                "treatment_plan": None,
            }
        }

    # Exit path 3 — Error
    if state.get("error"):
        logger.info(f"Response builder: error — {state.get('error')}")
        return {
            **state,
            "final_response": {
                "success": False,
                "type": "error",
                "message": (
                    "काहीतरी चूक झाली. कृपया पुन्हा प्रयत्न करा."
                    if user_language == "marathi"
                    else "कुछ गलत हो गया। कृपया पुनः प्रयास करें।"
                    if user_language == "hindi"
                    else "Something went wrong. Please try again."
                ),
                "disease": None,
                "summary": None,
                "analysis": None,
                "treatment_plan": None,
            }
        }

    # Exit path 4 — Chitchat
    if state.get("requires_general_response"):
        logger.info("Response builder: chitchat response")
        return {
            **state,
            "final_response": {
                "success": True,
                "type": "chitchat",
                "message": (
                    "नमस्कार! मी AgroAssist आहे. तुमच्या पिकाबद्दल मला विचारा."
                    if user_language == "marathi"
                    else "नमस्ते! मैं AgroAssist हूं। अपनी फसल के बारे में पूछें।"
                    if user_language == "hindi"
                    else "Hello! I am AgroAssist. Ask me anything about your crops."
                ),
                "disease": None,
                "summary": None,
                "analysis": None,
                "treatment_plan": None,
            }
        }

    # Main path — Build full response using LLM
    disease_analysis = state.get("disease_analysis", {})
    treatment_plan = state.get("treatment_plan", {})
    predicted_disease = state.get("predicted_disease")
    ml_confidence = state.get("ml_confidence", 0.0)
    response_tone = treatment_plan.get("response_tone", "advisory")

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Build the final farmer-friendly response.")
    ])

    try:
        chain = prompt | get_llm().with_structured_output(
            ResponseResult,
            method="function_calling"
        )

        result: ResponseResult = chain.invoke({
            "user_language": user_language,
            "response_tone": response_tone,
            "disease_analysis": str(disease_analysis),
            "immediate_steps": treatment_plan.get("immediate_steps", []),
            "fertilizers": treatment_plan.get("fertilizers", []),
            "pesticides": treatment_plan.get("pesticides", []),
            "prevention": treatment_plan.get("prevention", []),
            "follow_up_days": treatment_plan.get("follow_up_days", 7),
            "user_input": user_input,
            "urgency": urgency,
        })

        final_response = {
            "success": True,
            "type": intent,
            "language": user_language,
            "disease": {
                "name": predicted_disease,
                "confidence": f"{ml_confidence:.0%}" if ml_confidence else None,
            } if predicted_disease else None,
            "message": result.main_message,
            "summary": result.summary,
            "what_to_do_now": result.what_to_do_now,
            "follow_up_advice": result.follow_up_advice,
            "analysis": disease_analysis,
            "treatment_plan": {
                "immediate_steps": treatment_plan.get("immediate_steps", []),
                "fertilizers": treatment_plan.get("fertilizers", []),
                "pesticides": treatment_plan.get("pesticides", []),
                "prevention": treatment_plan.get("prevention", []),
                "follow_up_days": treatment_plan.get("follow_up_days", 7),
            },
        }

        logger.info("=" * 50)
        logger.info("Response builder end")
        logger.info(f"  type: {intent}")
        logger.info(f"  language: {user_language}")
        logger.info(f"  disease: {predicted_disease}")
        logger.info("=" * 50)

        return {**state, "final_response": final_response}

    except Exception as e:
        logger.error(f"Response builder error: {e}", exc_info=True)
        return {
            **state,
            "final_response": {
                "success": False,
                "type": "error",
                "message": "Unable to build response. Please try again.",
                "disease": None,
                "summary": None,
                "analysis": None,
                "treatment_plan": None,
            }
        }
import logging
from pydantic import BaseModel, ConfigDict, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.services.agent_state import AgentState
from app.config import settings
from app.ai.llm import get_llm

logger = logging.getLogger(__name__)




class SugarcaneAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    disease_name: str = Field(
        description="Full name of the detected disease."
    )
    disease_causes: str = Field(
        description="Why this disease occurs. Causes and conditions that trigger it."
    )
    severity_assessment: str = Field(
        description="How serious is the current situation based on symptoms and confidence."
    )
    affected_parts: str = Field(
        description="Which parts of the sugarcane plant are affected."
    )
    spread_risk: str = Field(
        description="Risk of spreading to other plants or fields. High | Medium | Low."
    )
    immediate_action: str = Field(
        description="What the farmer must do RIGHT NOW before full treatment."
    )
    detailed_analysis: str = Field(
        description=(
            "Full detailed analysis covering all focus areas from the planner. "
            "Written in simple farmer-friendly language. "
            "Must be in the farmer's language."
        )
    )
    yield_impact: str = Field(
        description="Expected impact on harvest if untreated."
    )
    recovery_timeline: str = Field(
        description="Approximate time for crop to recover with proper treatment."
    )


SYSTEM_PROMPT = """
Role:
You are an expert Sugarcane Crop Disease Advisor for AgroAssist — an AI system helping Indian farmers.

Your job is to analyze the detected disease and provide accurate, practical, farmer-friendly advice.
You are given a plan by the planner agent — follow it exactly.

[PLANNER INSTRUCTIONS]
{functional_prompt}

[ANALYSIS FOCUS AREAS]
Cover these topics in order:
{analysis_focus}

[KNOWLEDGE BASE CONTEXT]
The following information is retrieved from the sugarcane agricultural knowledge base.
Use this as your primary reference for accuracy:
{rag_context}

[CONVERSATION MEMORY]
Previous interactions with this farmer:
{conversation_summary}

[DISEASE DETECTION]
Disease: {predicted_disease}
ML Confidence: {ml_confidence}
Affected Plant: Sugarcane

[FARMER DETAILS]
Query: {user_input}
Location entities: {location}
Urgency: {urgency}
Response Language: {user_language}

=============================================================
INSTRUCTIONS
=============================================================
1. Use RAG context as primary knowledge source — do not hallucinate facts.
2. If RAG context is insufficient, use your agricultural training knowledge.
3. Cover ALL focus areas from planner in the detailed_analysis field.
4. Write detailed_analysis in {user_language} — farmer must understand it.
5. Keep language simple — farmer may have low literacy.
6. Use local Indian product names for fertilizers and pesticides where possible.
7. Do not repeat advice already given in conversation memory.
8. Severity assessment must reflect ML confidence:
   - confidence > 0.90 → high severity language
   - confidence 0.75-0.90 → moderate severity
   - confidence 0.60-0.75 → possible disease, suggest precaution

=============================================================
OUTPUT
=============================================================
Return ONLY valid JSON matching SugarcaneAnalysisResult schema. No extra text.
"""


def sugarcane_agent(state: AgentState) -> AgentState:
    """
    Specialist agent for sugarcane disease analysis.
    Uses planner's functional_prompt and analysis_focus.
    Uses RAG context from Chroma knowledge base.
    Uses conversation memory to avoid repetition.
    Responds in farmer's detected language.
    """
    logger.info("=" * 50)
    logger.info("Sugarcane agent start")
    logger.info(f"  user: {state.get('user_id')}")
    logger.info(f"  disease: {state.get('predicted_disease')}")
    logger.info(f"  confidence: {state.get('ml_confidence')}")
    logger.info(f"  language: {state.get('user_language')}")
    logger.info("=" * 50)

    predicted_disease = state.get("predicted_disease", "unknown")
    ml_confidence = state.get("ml_confidence", 0.0)
    user_input = state.get("user_input", "")
    rag_context = state.get("rag_context", "")
    conversation_summary = state.get("conversation_summary", "")
    functional_prompt = state.get("functional_prompt", "")
    analysis_focus = state.get("analysis_focus", [])
    extracted_entities = state.get("extracted_entities", {})
    user_language = state.get("user_language", "english")

    location = extracted_entities.get("location", "not specified")
    urgency = extracted_entities.get("urgency", "medium")

    # Format analysis focus as numbered list for prompt
    focus_list = "\n".join([f"{i+1}. {f}" for i, f in enumerate(analysis_focus)]) \
        or "1. disease_causes\n2. immediate_treatment\n3. prevention_measures"

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Analyze this sugarcane disease and provide detailed advice for the farmer.")
    ])

    try:
        chain = prompt | get_llm().with_structured_output(
            SugarcaneAnalysisResult,
            method="function_calling"
        )

        result: SugarcaneAnalysisResult = chain.invoke({
            "functional_prompt": functional_prompt or f"Analyze {predicted_disease} disease in sugarcane.",
            "analysis_focus": focus_list,
            "rag_context": rag_context or "No additional knowledge base context available.",
            "conversation_summary": conversation_summary or "No previous conversation.",
            "predicted_disease": predicted_disease,
            "ml_confidence": f"{ml_confidence:.0%}" if ml_confidence else "N/A",
            "user_input": user_input,
            "location": location,
            "urgency": urgency,
            "user_language": user_language,
        })

        # Build full disease analysis string for response builder
        disease_analysis = {
            "disease_name": result.disease_name,
            "disease_causes": result.disease_causes,
            "severity_assessment": result.severity_assessment,
            "affected_parts": result.affected_parts,
            "spread_risk": result.spread_risk,
            "immediate_action": result.immediate_action,
            "detailed_analysis": result.detailed_analysis,
            "yield_impact": result.yield_impact,
            "recovery_timeline": result.recovery_timeline,
        }

        logger.info("=" * 50)
        logger.info("Sugarcane agent end")
        logger.info(f"  disease_name: {result.disease_name}")
        logger.info(f"  severity: {result.severity_assessment[:60]}")
        logger.info(f"  spread_risk: {result.spread_risk}")
        logger.info("=" * 50)

        return {
            **state,
            "disease_analysis": disease_analysis,
        }

    except Exception as e:
        logger.error(f"Sugarcane agent error: {e}", exc_info=True)
        return {
            **state,
            "disease_analysis": {
                "disease_name": predicted_disease,
                "detailed_analysis": (
                    "Unable to complete analysis. "
                    "Please consult your local agricultural extension officer."
                ),
            },
            "error": str(e),
        }
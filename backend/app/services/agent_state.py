from typing import TypedDict, Optional, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):

    # ZONE 1: Intake & Conversational Memory
    # Populated by: API route before pipeline starts
    user_id: str
    session_id: str
    request_type: str                        # "predict" | "chat"
    user_input: str                          # cleaned by guardrail → refined by intent
    plant_name: str
    image_path: Optional[str]               # None for chat, set for predict
    image_url: Optional[str]                # Cloudinary URL after upload
    messages: Annotated[list, add_messages] # LangGraph appends, never overwrites
    conversation_summary: Optional[str]     # last 5 Q&A summary from MongoDB
    user_language: str                       # "english" | "marathi" | "hindi"

    # ZONE 2: Triage & Intent
    # Populated by: GuardrailAgent, IntentAgent
    is_safe: bool
    guardrail_flag: Optional[str]           # "safe" | "vague" | "blocked"
    rejection_reason: Optional[str]
    intent: Optional[str]                   # "disease_check" | "general_advice" | "chitchat"
    extracted_entities: Dict[str, Any]      # symptoms, location, urgency, disease_name
    requires_follow_up: Optional[bool]
    follow_up_message: Optional[str]        # written in farmer's language
    pending_intent: Optional[str]           # preserved across follow-up turns
    requires_general_response: Optional[bool]

    # ZONE 3: Orchestrator & Planner
    # Populated by: OrchestratorAgent, PlannerAgent
    specialist_agent: Optional[str]         # set by orchestrator — used by graph to route
    ml_model_handler: Optional[str]         # ML model path from registry
    run_ml_model: Optional[bool]            # True if disease_check + image present
    predicted_disease: Optional[str]
    ml_confidence: Optional[float]
    analysis_focus: List[str]
    rag_query: Optional[str]
    functional_prompt: Optional[str]
    treatment_plan: Optional[dict]

    # ZONE 4: Specialist Agent & RAG
    # Populated by: SugarcaneAgent, RagPipeline
    rag_context: Optional[str]
    disease_analysis: Optional[dict]

    # ZONE 5: Response Builder
    # Populated by: ResponseBuilderAgent
    final_response: Optional[dict]

    # ZONE 6: Error Tracking
    error: Optional[str]
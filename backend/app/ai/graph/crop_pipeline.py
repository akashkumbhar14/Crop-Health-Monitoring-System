import logging
from langgraph.graph import StateGraph, END
from app.services.agent_state import AgentState
from app.ai.agents.guardrial_agent import guardrail_agent
from app.ai.agents.query_intent import intent_agent
from app.ai.agents.orchestrator import orchestrator_node
from app.ai.agents.planner import planner_agent
from app.ai.agents.sugarcane_agent import sugarcane_agent
from app.ai.agents.response import response_builder_agent

logger = logging.getLogger(__name__)


def route_after_guardrail(state: AgentState) -> str:
    """Guardrail blocked → response. Safe → intent agent."""
    if not state.get("is_safe", True):
        return "response"
    if state.get("requires_follow_up"):
        return "response"
    return "query_intent"


def route_after_intent(state: AgentState) -> str:
    """Chitchat or follow-up → response. Otherwise → orchestrator."""
    if state.get("requires_follow_up"):
        return "response"
    if state.get("requires_general_response"):
        return "response"
    return "orchestrator"


def route_after_orchestrator(state: AgentState) -> str:
    """Error → response. Otherwise → planner."""
    if state.get("error"):
        return "response"
    if not state.get("is_safe", True):
        return "response"
    return "planner"


def route_after_planner(state: AgentState) -> str:
    """Error or low confidence → response. Otherwise → specialist agent."""
    if state.get("error"):
        return "response"
    if not state.get("is_safe", True):
        return "response"
    specialist = state.get("specialist_agent", "sugarcane_agent")
    return specialist


def build_crop_pipeline():
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("guardrail", guardrail_agent)
    workflow.add_node("query_intent", intent_agent)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("sugarcane_agent", sugarcane_agent)
    workflow.add_node("response", response_builder_agent)

    # Entry point
    workflow.set_entry_point("guardrail")

    # guardrail → query_intent | response
    workflow.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "query_intent": "query_intent",
            "response": "response",
        }
    )

    # query_intent → orchestrator | response
    workflow.add_conditional_edges(
        "query_intent",
        route_after_intent,
        {
            "orchestrator": "orchestrator",
            "response": "response",
        }
    )

    # orchestrator → planner | response
    workflow.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "planner": "planner",
            "response": "response",
        }
    )

    # planner → sugarcane_agent | response
    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "sugarcane_agent": "sugarcane_agent",
            "response": "response",
        }
    )

    # sugarcane_agent → response
    workflow.add_edge("sugarcane_agent", "response")

    # response → END
    workflow.add_edge("response", END)

    return workflow.compile()


crop_pipeline = build_crop_pipeline()
logger.info("Crop pipeline compiled successfully")
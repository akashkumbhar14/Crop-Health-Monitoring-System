AGENT_REGISTRY: dict = {
    "sugarcane_agent": "app.ai.agents.sugarcane_agent.sugarcane_agent",
    # "tomato_agent": "app.ai.agents.tomato_agent.tomato_agent",
    # "wheat_agent": "app.ai.agents.wheat_agent.wheat_agent",
    # "rice_agent": "app.ai.agents.rice_agent.rice_agent",
    # "grape_agent": "app.ai.agents.grape_agent.grape_agent",
}


def get_agent_for_plant(plant_name: str) -> str | None:
    """
    Returns agent handler path for a given plant.
    Uses lazy import to avoid circular import with plant_registry.
    """
    from app.registry.plant_registry import get_specialist_agent
    specialist = get_specialist_agent(plant_name)
    if not specialist:
        return None
    return AGENT_REGISTRY.get(specialist)
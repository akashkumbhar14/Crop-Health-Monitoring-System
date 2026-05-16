from typing import Optional


PLANT_REGISTRY: dict = {
    "sugarcane": {
        "display_name": "Sugarcane",
        "model_handler": "app.ai.ml.sugarcane_predictor.SugarcanePredictor",
        "specialist_agent": "sugarcane_agent",
        "supported_diseases": ["RedRot", "RedRust", "Healthy"],
        "languages": ["english", "marathi", "hindi"],
        "is_active": True,
    },
}


def is_plant_supported(plant_name: str) -> bool:
    plant = PLANT_REGISTRY.get(plant_name.lower().strip())
    return plant is not None and plant.get("is_active", False)


def get_plant_info(plant_name: str) -> Optional[dict]:
    return PLANT_REGISTRY.get(plant_name.lower().strip())


def get_specialist_agent(plant_name: str) -> Optional[str]:
    info = get_plant_info(plant_name)
    return info.get("specialist_agent") if info else None


def get_model_handler(plant_name: str) -> Optional[str]:
    info = get_plant_info(plant_name)
    return info.get("model_handler") if info else None


def get_active_plants() -> list[str]:
    return [
        name for name, info in PLANT_REGISTRY.items()
        if info.get("is_active", False)
    ]


def get_supported_diseases(plant_name: str) -> list[str]:
    info = get_plant_info(plant_name)
    return info.get("supported_diseases", []) if info else []
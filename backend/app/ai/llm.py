from langchain_groq import ChatGroq
from app.config import settings

_llm = None


def get_llm() -> ChatGroq:
    """
    Lazy LLM initialization using Groq.
    Only creates ChatGroq when first called — not at import time.
    Prevents crash if GROQ_API_KEY is missing at startup.
    """
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            api_key=settings.GROQ_API_KEY,
        )
    return _llm
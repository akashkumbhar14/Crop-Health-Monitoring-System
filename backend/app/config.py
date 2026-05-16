from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):

    # ── App ───────────────────────────────────────────────────────────────
    APP_NAME: str = "AgroAssist"
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # ── Security ──────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── MongoDB ───────────────────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "agroassist"

    # ── Twilio (OTP) ──────────────────────────────────────────────────────
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # ── LLM (OpenAI) ──────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.2

    # ── Weather ───────────────────────────────────────────────────────────
    WEATHER_API_KEY: str = ""
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # ── Cloudinary (image uploads) ────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    CLOUDINARY_FOLDER: str = "agroassist/crop_images"

    # ── ML Model ──────────────────────────────────────────────────────────
    ML_MODEL_PATH: str = "app/ai/ml/models/DenseNetSVM_Model.h5"
    ML_IMAGE_SIZE: int = 224                   # DenseNet input size
    ML_CONFIDENCE_THRESHOLD: float = 0.60      # below this = uncertain

    # ── RAG (Chroma vector store) ─────────────────────────────────────────
    CHROMA_DB_PATH: str = "app/ai/rag/chroma_db"
    RAG_COLLECTION_NAME: str = "sugarcane_knowledge"
    RAG_TOP_K: int = 4
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50

    # ── Conversation Memory (stored in MongoDB) ───────────────────────────
    MEMORY_MAX_TURNS: int = 5                  # last 5 Q&A pairs
    MEMORY_TTL_SECONDS: int = 86400            # auto-delete after 24hrs

    # ── CORS ──────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8081"

    def get_allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings — reads .env once at startup.
    Usage:
        from app.config import get_settings
        settings = get_settings()
    """
    return Settings()


settings = get_settings()
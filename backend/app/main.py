from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.config import settings
from app.db.mongodb import connect_db, close_db
from app.api.v1.routes.auth_routes import router as auth_router
from app.api.v1.routes.predications import router as prediction_router
from app.api.v1.routes.chat import router as chat_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} [{settings.APP_ENV}]...")

    # Connect MongoDB
    await connect_db()
    logger.info("MongoDB connected")

    # Preload ML model so first request isn't slow
    try:
        from app.ai.ml.sugarcane_predictor import SugarcanePredictor
        SugarcanePredictor.get_instance()
        logger.info("ML model loaded")
    except Exception as e:
        logger.warning(f"ML model load failed: {e}")

    # Preload RAG Chroma vector store
    try:
        from app.ai.rag.rag_pipeline import RagPipeline
        RagPipeline.get_instance()
        logger.info("RAG pipeline loaded")
    except Exception as e:
        logger.warning(f"RAG pipeline load failed: {e}")

    # Setup MongoDB TTL index for conversation memory
    try:
        from app.memory.conversation_memory import ConversationMemory
        await ConversationMemory.ensure_ttl_index()
        logger.info("Conversation memory TTL index ready")
    except Exception as e:
        logger.warning(f"Memory TTL index setup failed: {e}")

    yield

    # Shutdown
    await close_db()
    logger.info("MongoDB connection closed")


# Hide docs in production
app = FastAPI(
    title=f"{settings.APP_NAME} API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Catch all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "Something went wrong",
        },
    )


# Routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(prediction_router, prefix="/api/v1", tags=["Prediction"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])


@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check for deployment services."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
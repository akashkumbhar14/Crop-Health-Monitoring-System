from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.mongodb import connect_db, close_db
# from app.api.v1.routes import auth
from app.api.v1.routes.auth import router as auth_router
# import logging

# ─── Logging Setup ─────────────────────────────────────────────────────────────
# logging.basicConfig(
#     level=logging.DEBUG if settings.DEBUG else logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
# )
# logger = logging.getLogger(__name__)


# ─── Lifespan (startup + shutdown) ─────────────────────────────────────────────
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     logger.info(f"Starting {settings.APP_NAME} [{settings.APP_ENV}]")
#     await connect_db()
#     logger.info("Startup complete. Ready to serve requests.")
#     yield
#     # Shutdown
#     await close_db()
#     logger.info("Shutdown complete.")


# ─── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgroAssist API",
    version="1.0.0",
    docs_url="/docs",          # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",        # ReDoc UI at http://localhost:8000/redoc
    openapi_url="/openapi.json",
    # lifespan=lifespan,
)


# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)


# ─── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Quick check to confirm the server is running."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "version": "1.0.0",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }
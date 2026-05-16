from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


async def connect_db():
    """Called once at app startup."""
    global _client, _db

    _client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        maxPoolSize=10,
        minPoolSize=2,
    )

    _db = _client[settings.MONGODB_DB_NAME]
    await _client.admin.command("ping")
    logger.info(f"MongoDB connected — database: '{settings.MONGODB_DB_NAME}'")

    await _create_indexes()


async def close_db():
    """Called once at app shutdown."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """
    Dependency injected into FastAPI routes.
    Usage:
        async def my_route(db = Depends(get_db)):
    """
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _db


async def _create_indexes():
    """Create all indexes at startup. Safe to run multiple times."""
    db = get_db()

    # farmers
    await db.farmers.create_index("phone", unique=True)
    await db.farmers.create_index("created_at")
    await db.farmers.create_index([("farm.location", "2dsphere")])

    # otp_store — auto-expire after 10 minutes
    await db.otp_store.create_index("phone", unique=True)
    await db.otp_store.create_index("created_at", expireAfterSeconds=600)

    # disease_detections
    await db.disease_detections.create_index([("farmer_id", 1), ("detected_at", -1)])

    # advisories
    await db.advisories.create_index([("farmer_id", 1), ("created_at", -1)])

    # conversation_memory — auto-expire after configured TTL
    await db.conversation_memory.create_index("user_id", unique=True)
    await db.conversation_memory.create_index(
        "expires_at", expireAfterSeconds=0
    )

    logger.info("MongoDB indexes created/verified")
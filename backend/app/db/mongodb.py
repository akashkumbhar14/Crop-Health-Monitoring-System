from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global client instance (reused across requests)
_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


async def connect_db():
    """
    Called once at app startup.
    Creates MongoDB connection and builds all indexes.
    """
    global _client, _db

    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    _client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,    # fail fast if mongo is down
        maxPoolSize=10,
        minPoolSize=2,
    )

    _db = _client[settings.MONGODB_DB_NAME]

    # Verify connection
    await _client.admin.command("ping")
    logger.info(f"MongoDB connected — database: '{settings.MONGODB_DB_NAME}'")

    # Build indexes on startup
    await _create_indexes()


async def close_db():
    """Called once at app shutdown."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed.")


def get_db() -> AsyncIOMotorDatabase:
    """
    Dependency injected into FastAPI routes.
    Usage:
        from app.db.mongodb import get_db
        async def my_route(db = Depends(get_db)):
    """
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _db


async def _create_indexes():
    """
    Create all MongoDB indexes.
    Run once at startup — idempotent (safe to run multiple times).
    """
    db = get_db()

    # farmers collection
    await db.farmers.create_index("phone", unique=True)
    await db.farmers.create_index("created_at")
    await db.farmers.create_index(
        [("farm.location", "2dsphere")]   # geo queries — find farmers near a point
    )

    # otp_store collection — auto-expire after 10 minutes
    await db.otp_store.create_index("phone", unique=True)
    await db.otp_store.create_index(
        "created_at",
        expireAfterSeconds=600            # MongoDB TTL index — auto-deletes expired OTPs
    )

    # ndvi_records collection
    await db.ndvi_records.create_index([("farmer_id", 1), ("captured_at", -1)])

    # advisories collection
    await db.advisories.create_index([("farmer_id", 1), ("created_at", -1)])

    # disease_detections collection
    await db.disease_detections.create_index([("farmer_id", 1), ("detected_at", -1)])

    logger.info("MongoDB indexes created/verified.")
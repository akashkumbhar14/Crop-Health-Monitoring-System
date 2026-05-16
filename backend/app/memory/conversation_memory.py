from datetime import datetime, timedelta
from typing import Optional
from app.db.mongodb import get_db
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ConversationMemory:

    COLLECTION = "conversation_memory"

    @staticmethod
    async def ensure_ttl_index():
        """Create TTL index on expires_at. Called once at startup."""
        db = get_db()
        await db[ConversationMemory.COLLECTION].create_index(
            "expires_at",
            expireAfterSeconds=0
        )
        await db[ConversationMemory.COLLECTION].create_index(
            "user_id",
            unique=True
        )
        logger.info("Conversation memory indexes ready")

    @staticmethod
    async def get_summary(user_id: str) -> Optional[str]:
        """
        Fetch last N Q&A summary for a user.
        Returns None if no memory exists yet.
        Injected into AgentState.conversation_summary before pipeline runs.
        """
        db = get_db()
        doc = await db[ConversationMemory.COLLECTION].find_one(
            {"user_id": user_id}
        )
        if doc:
            return doc.get("summary")
        return None

    @staticmethod
    async def update(user_id: str, question: str, answer: str):
        """
        Add new Q&A turn after pipeline completes.
        Keeps only last MEMORY_MAX_TURNS turns.
        Rebuilds summary string for next LLM call.
        """
        db = get_db()
        doc = await db[ConversationMemory.COLLECTION].find_one(
            {"user_id": user_id}
        )

        turns = doc.get("turns", []) if doc else []

        # Append new turn
        turns.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep only last N turns
        turns = turns[-settings.MEMORY_MAX_TURNS:]

        # Build compressed summary for LLM context
        summary_lines = []
        for i, turn in enumerate(turns, 1):
            summary_lines.append(f"Q{i}: {turn['question']}")
            # Truncate long answers to avoid token bloat
            summary_lines.append(f"A{i}: {turn['answer'][:300]}")

        summary = "\n".join(summary_lines)

        expires_at = datetime.utcnow() + timedelta(
            seconds=settings.MEMORY_TTL_SECONDS
        )

        await db[ConversationMemory.COLLECTION].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "turns": turns,
                    "summary": summary,
                    "updated_at": datetime.utcnow(),
                    "expires_at": expires_at,
                }
            },
            upsert=True
        )
        logger.info(f"Memory updated for user: {user_id} — {len(turns)} turns stored")

    @staticmethod
    async def clear(user_id: str):
        """Clear all memory for a user."""
        db = get_db()
        await db[ConversationMemory.COLLECTION].delete_one({"user_id": user_id})
        logger.info(f"Memory cleared for user: {user_id}")
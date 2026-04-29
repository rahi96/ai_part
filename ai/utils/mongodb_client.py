"""
Async MongoDB client using Motor.
Connects to the shared MongoDB instance for chat message persistence.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ai.config import settings

logger = logging.getLogger(__name__)

# Global client instance (initialized once)
_mongo_client: AsyncIOMotorClient | None = None
_mongo_db: AsyncIOMotorDatabase | None = None


async def get_db() -> AsyncIOMotorDatabase:
    """Return the MongoDB database, initializing the client if needed."""
    global _mongo_client, _mongo_db
    if _mongo_db is None:
        uri = settings.mongodb_uri
        if not uri:
            raise RuntimeError("MONGODB_URI is not configured")
        _mongo_client = AsyncIOMotorClient(uri)
        # Parse database name from URI or default to "ronijenkins"
        _mongo_db = _mongo_client.get_default_database()
        if _mongo_db is None:
            _mongo_db = _mongo_client["ronijenkins"]
        logger.info("MongoDB client connected")
    return _mongo_db


async def close_mongo_client() -> None:
    """Close the MongoDB client connection."""
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        logger.info("MongoDB client closed")


async def insert_chat_message(
    customer_id: str,
    thread_id: str,
    role: str,
    message: str,
    confidence_score: float | None = None,
    intent: str | None = None,
    sources: list[str] | None = None,
) -> str:
    """Insert a single chat message into the chat_messages collection."""
    db = await get_db()
    doc: dict[str, Any] = {
        "customerId": customer_id,
        "threadId": thread_id,
        "role": role,
        "message": message,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    if confidence_score is not None:
        doc["confidenceScore"] = confidence_score
    if intent is not None:
        doc["intent"] = intent
    if sources is not None:
        doc["sources"] = sources

    result = await db["chat_messages"].insert_one(doc)
    logger.debug("Inserted chat message %s for thread %s", result.inserted_id, thread_id)
    return str(result.inserted_id)


async def get_thread_messages(thread_id: str) -> list[dict]:
    """Retrieve all messages for a given thread, sorted by creation time."""
    db = await get_db()
    cursor = (
        db["chat_messages"]
        .find({"threadId": thread_id})
        .sort("createdAt", 1)
    )
    messages = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["createdAt"] = doc["createdAt"].isoformat() if "createdAt" in doc else None
        doc["updatedAt"] = doc["updatedAt"].isoformat() if "updatedAt" in doc else None
        messages.append(doc)
    return messages


async def clear_thread_messages(thread_id: str) -> int:
    """Delete all messages for a given thread. Returns number of deleted documents."""
    db = await get_db()
    result = await db["chat_messages"].delete_many({"threadId": thread_id})
    logger.info("Cleared %d messages for thread %s", result.deleted_count, thread_id)
    return result.deleted_count

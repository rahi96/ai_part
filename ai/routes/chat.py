"""
Navelle AI Module — Chat Routes
Powered by LangGraph 4-node workflow + RAG pipeline.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Body, HTTPException, Query

from ai.services.analytics_service import AnalyticsService
from ai.utils.backend_client import backend_client
from ai.workflows.chat_workflow import run_chat_workflow

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/chat", tags=["Chat"])

_analytics = AnalyticsService()


@router.post("/message")
async def chat_message(
    user_id: str = Body(..., embed=True, description="MongoDB ObjectId of the user"),
    message: str = Body(..., embed=True, description="The user's message"),
    thread_id: str | None = Body(None, embed=True, description="Existing thread ID (optional)"),
    days: int = Query(30, ge=1, le=365, description="Health data lookback window"),
):
    """
    Send a message to the Mennie™ AI assistant.

    - If `thread_id` is omitted, a new 30-day conversation thread is created.
    - Health context is automatically fetched from the backend.
    - Responses are powered by LangGraph + GPT-4 general knowledge.
    - A healthcare disclaimer is appended to every response.
    """
    if not message or not message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    # Fetch health data for personalisation (non-blocking failure)
    health_data = await backend_client.get_user_health_overview(user_id, days=days)

    # Run the LangGraph workflow
    result = await run_chat_workflow(
        user_id=user_id,
        message=message.strip(),
        health_data=health_data,
        thread_id=thread_id,
    )

    # Record analytics (fire-and-forget)
    try:
        _analytics.record_query(
            question_text=message.strip(),
            user_id=user_id,
            confidence_score=result.get("confidence"),
            intent=result.get("intent"),
            response_source=result.get("response_source"),
        )
    except Exception as exc:
        logger.warning("Analytics record failed (non-critical): %s", exc)

    # Get AI model info for transparency
    from ai.config import settings
    from ai.utils.langchain_rag import get_ai_attribution_header
    from ai.utils.bedrock_llm import bedrock_llm
    from ai.models.schemas import SourceReference
    
    # Check which LLM is actually being used
    if bedrock_llm.is_available():
        ai_model = bedrock_llm.get_model()
    else:
        ai_model = settings.openai_model if settings.openai_api_key else "AI Language Model"
    
    # Transform retrieved_docs into SourceReference objects with URLs
    source_references = []
    for doc in result.get("retrieved_docs", []):
        source_references.append(SourceReference(
            topic=doc.get("topic", "Unknown"),
            url=doc.get("source_url", ""),
            source_name=doc.get("source_name", "Medical Knowledge Base")
        ))
    
    return {
        "user_id": user_id,
        "thread_id": result["thread_id"],
        "is_new_thread": result["is_new_thread"],
        "message": message.strip(),
        "response": result["response"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "sources": source_references,  # Now returns SourceReference objects with URLs
        "response_source": result["response_source"],
        # App Store Compliance: Explicit AI attribution
        "ai_model": ai_model,
        "ai_attribution": get_ai_attribution_header(),
        "is_ai_generated": True,
        "medical_disclaimer": "This is AI-generated educational content, not medical advice. Always consult your healthcare provider.",
    }


@router.get("/thread/{thread_id}/history")
async def get_thread_history(thread_id: str):
    """
    Retrieve the conversation history for a specific thread.
    """
    from ai.workflows.chat_workflow import _thread_store
    thread = _thread_store.get(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found or expired.")
    return {
        "thread_id": thread_id,
        "created_at": thread["created_at"].isoformat(),
        "message_count": len(thread["history"]),
        "history": thread["history"],
    }


@router.delete("/thread/{thread_id}")
async def clear_thread(thread_id: str):
    """
    Clear a conversation thread (e.g., user requests fresh start).
    """
    from ai.workflows.chat_workflow import _thread_store
    if thread_id in _thread_store:
        del _thread_store[thread_id]
        return {"message": "Thread cleared successfully.", "thread_id": thread_id}
    raise HTTPException(status_code=404, detail="Thread not found.")

"""
Navelle AI Module — Chat Routes
Powered by LangGraph 4-node workflow + RAG pipeline.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Body, HTTPException, Query

from ai.utils.backend_client import backend_client
from ai.workflows.chat_workflow import run_chat_workflow
from ai.services.document_service import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/chat", tags=["Chat"])

_doc_service = DocumentService()


@router.post("/message")
async def chat_message(
    user_id: str = Body(..., embed=True, description="MongoDB ObjectId of the user"),
    message: str = Body(..., embed=True, description="The user's message"),
    thread_id: str | None = Body(None, embed=True, description="Existing thread ID (optional)"),
    days: int = Query(30, ge=1, le=365, description="Health data lookback window"),
):


  
    if not message or not message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")


    health_data = await backend_client.get_user_health_overview(user_id, days=days)

    # Fetch user document chunks for AI context (non-blocking failure)
    try:
        doc_result = await _doc_service.ingest_user_documents(user_id)
        retrieved_docs = doc_result.get("chunks", [])
    except Exception as exc:
        logger.warning("Document ingestion failed (non-critical): %s", exc)
        retrieved_docs = []

    result = await run_chat_workflow(
        user_id=user_id,
        message=message.strip(),
        health_data=health_data,
        retrieved_docs=retrieved_docs,
        thread_id=thread_id,
    )
    
    return {
        "user_id": user_id,
        "thread_id": result["thread_id"],
        "is_new_thread": result["is_new_thread"],
        "message": message.strip(),
        "response": result["response"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "sources": result["sources"],
        "response_source": result["response_source"],
    }


@router.get("/thread/{thread_id}/history")
async def get_thread_history(thread_id: str):

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

    from ai.workflows.chat_workflow import _thread_store
    if thread_id in _thread_store:
        del _thread_store[thread_id]
        return {"message": "Thread cleared successfully.", "thread_id": thread_id}
    raise HTTPException(status_code=404, detail="Thread not found.")



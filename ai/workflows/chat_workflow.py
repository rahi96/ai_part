"""
Navelle AI Module — LangGraph Chat Workflow
4-node state machine: classify → respond → disclaimer → thread_check

State:
    user_id, thread_id, message, health_data, intent,
    retrieved_docs, response, confidence, disclaimer_added,
    conversation_history, thread_created_at, response_source
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from ai.utils.langchain_rag import DISCLAIMER, intent_classifier, rag_pipeline
from ai.utils.mongodb_client import get_thread_messages, insert_chat_message

logger = logging.getLogger(__name__)


async def _get_or_create_thread(thread_id: str | None) -> tuple[str, list[dict], bool]:
    """
    Return (thread_id, conversation_history, is_new).
    Fetches history from MongoDB; creates a new thread if not found.
    """
    if thread_id:
        history = await get_thread_messages(thread_id)
        if history:
            # Convert MongoDB docs to conversation_history format
            convo = [{"role": m["role"], "content": m["message"]} for m in history]
            return thread_id, convo, False

    # Create new thread
    new_id = thread_id or str(uuid.uuid4())
    return new_id, [], True


# ── LangGraph State ────────────────────────────────────────────────────────────

class ChatState(TypedDict):
    user_id: str
    thread_id: str
    message: str
    health_data: dict
    intent: str
    retrieved_docs: list[dict]
    response: str
    confidence: float
    response_source: str  # "general_knowledge" | "template" | "clarification" | "greeting"
    disclaimer_added: bool
    conversation_history: list[dict]
    thread_created_at: str
    is_new_thread: bool


# ── Node 1: Classify Intent ────────────────────────────────────────────────────

def node_classify_intent(state: ChatState) -> ChatState:
    """Classify the user's message intent."""
    intent = intent_classifier.classify(state["message"])
    logger.debug("Intent classified: %s for message: %s", intent, state["message"][:50])
    return {**state, "intent": intent}


# ── Node 2: Generate Response ──────────────────────────────────────────────────

async def node_generate_response(state: ChatState) -> ChatState:
    """Generate AI response using rag_pipeline for all intents."""
    intent = state["intent"]
    message = state["message"]
    health_data = state.get("health_data", {})
    history = state.get("conversation_history", [])
    retrieved_docs = state.get("retrieved_docs", [])

    result = await rag_pipeline.generate(
        user_message=message,
        health_data=health_data,
        retrieved_docs=retrieved_docs,
        conversation_history=history,
    )

    return {
        **state,
        "retrieved_docs": retrieved_docs,
        "response": result["response"],
        "confidence": result["confidence"],
        "response_source": "ai_generated",
    }


# ── Node 3: Inject Disclaimer ──────────────────────────────────────────────────

def node_inject_disclaimer(state: ChatState) -> ChatState:
    """Ensure healthcare disclaimer is present in every response."""
    response = state["response"]
    # Only add if not already present (RAG pipeline already includes it)
    if DISCLAIMER.strip() not in response:
        response = response + DISCLAIMER
    return {**state, "response": response, "disclaimer_added": True}


# ── Node 4: Thread Expiry Check ────────────────────────────────────────────────

def node_check_thread(state: ChatState) -> ChatState:
    """Pass-through node; MongoDB persistence handled in run_chat_workflow."""
    return state


# ── Build the Graph ────────────────────────────────────────────────────────────

def _build_graph() -> Any:
    graph = StateGraph(ChatState)

    graph.add_node("classify_intent", node_classify_intent)
    graph.add_node("generate_response", node_generate_response)
    graph.add_node("inject_disclaimer", node_inject_disclaimer)
    graph.add_node("check_thread", node_check_thread)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "generate_response")
    graph.add_edge("generate_response", "inject_disclaimer")
    graph.add_edge("inject_disclaimer", "check_thread")
    graph.add_edge("check_thread", END)

    return graph.compile()


_chat_graph = _build_graph()


# ── Public Entry Point ─────────────────────────────────────────────────────────

async def run_chat_workflow(
    user_id: str,
    message: str,
    health_data: dict | None = None,
    retrieved_docs: list[dict] | None = None,
    thread_id: str | None = None,
) -> dict:
    """
    Execute the full chat workflow.

    Returns:
        {
            "response": str,
            "thread_id": str,
            "intent": str,
            "confidence": float,
            "sources": list[str],
            "response_source": str,
            "is_new_thread": bool,
        }
    """
    # Resolve thread
    resolved_thread_id, history, is_new = await _get_or_create_thread(thread_id)

    initial_state: ChatState = {
        "user_id": user_id,
        "thread_id": resolved_thread_id,
        "message": message,
        "health_data": health_data or {},
        "intent": "",
        "retrieved_docs": retrieved_docs or [],
        "response": "",
        "confidence": 0.0,
        "response_source": "",
        "disclaimer_added": False,
        "conversation_history": history,
        "thread_created_at": datetime.now(timezone.utc).isoformat(),
        "is_new_thread": is_new,
    }

    try:
        final_state = await _chat_graph.ainvoke(initial_state)
    except Exception as exc:
        logger.error("Chat workflow failed: %s", exc)
        # Safe fallback
        return {
            "response": (
                "I'm sorry, I encountered an unexpected error. "
                "Please try again or contact support." + DISCLAIMER
            ),
            "thread_id": resolved_thread_id,
            "intent": "error",
            "confidence": 0.0,
            "sources": [],
            "response_source": "error",
            "is_new_thread": is_new,
        }

    # Persist user message and assistant response to MongoDB
    try:
        await insert_chat_message(
            customer_id=user_id,
            thread_id=resolved_thread_id,
            role="user",
            message=message,
        )
        await insert_chat_message(
            customer_id=user_id,
            thread_id=resolved_thread_id,
            role="assistant",
            message=final_state["response"],
            confidence_score=final_state.get("confidence"),
            intent=final_state.get("intent"),
            sources=[d.get("document_title", d.get("topic", "unknown")) for d in final_state.get("retrieved_docs", [])],
        )
    except Exception as exc:
        logger.warning("Failed to persist chat messages to MongoDB: %s", exc)

    return {
        "response": final_state["response"],
        "thread_id": resolved_thread_id,
        "intent": final_state["intent"],
        "confidence": final_state["confidence"],
        "sources": [d.get("document_title", d.get("topic", "unknown")) for d in final_state.get("retrieved_docs", [])],
        "response_source": final_state["response_source"],
        "is_new_thread": is_new,
    }

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
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from ai.utils.langchain_rag import DISCLAIMER, intent_classifier, rag_pipeline

logger = logging.getLogger(__name__)

# ── Thread store (in-memory, 30-day TTL) ──────────────────────────────────────
# { thread_id: { "created_at": datetime, "history": list[dict] } }
_thread_store: dict[str, dict] = {}
THREAD_TTL_DAYS = 30


def _get_or_create_thread(thread_id: str | None) -> tuple[str, list[dict], bool]:
    """
    Return (thread_id, conversation_history, is_new).
    Cleans up expired threads on every call.
    """
    _cleanup_expired_threads()

    if thread_id and thread_id in _thread_store:
        entry = _thread_store[thread_id]
        return thread_id, entry["history"], False

    # Create new thread
    new_id = thread_id or str(uuid.uuid4())
    _thread_store[new_id] = {
        "created_at": datetime.now(timezone.utc),
        "history": [],
    }
    return new_id, [], True


def _cleanup_expired_threads() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=THREAD_TTL_DAYS)
    expired = [tid for tid, data in _thread_store.items() if data["created_at"] < cutoff]
    for tid in expired:
        del _thread_store[tid]
    if expired:
        logger.info("Cleaned up %d expired threads", len(expired))


def _append_to_thread(thread_id: str, role: str, content: str) -> None:
    if thread_id in _thread_store:
        _thread_store[thread_id]["history"].append({"role": role, "content": content})
        # Keep last 20 turns
        _thread_store[thread_id]["history"] = _thread_store[thread_id]["history"][-20:]


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

def node_generate_response(state: ChatState) -> ChatState:
    """Generate AI response using rag_pipeline for all intents."""
    intent = state["intent"]
    message = state["message"]
    health_data = state.get("health_data", {})
    history = state.get("conversation_history", [])
    retrieved_docs = state.get("retrieved_docs", [])

    result = rag_pipeline.generate(
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
    """Update conversation history and check thread health."""
    thread_id = state["thread_id"]
    message = state["message"]
    response = state["response"]

    # Append this turn to thread history
    _append_to_thread(thread_id, "user", message)
    _append_to_thread(thread_id, "assistant", response)

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
    resolved_thread_id, history, is_new = _get_or_create_thread(thread_id)

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

    return {
        "response": final_state["response"],
        "thread_id": resolved_thread_id,
        "intent": final_state["intent"],
        "confidence": final_state["confidence"],
        "sources": [d.get("document_title", d.get("topic", "unknown")) for d in final_state.get("retrieved_docs", [])],
        "response_source": final_state["response_source"],
        "is_new_thread": is_new,
    }

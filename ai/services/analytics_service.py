"""
Navelle AI Module — Analytics Service
Tracks chat query analytics using a JSON file store.
Persists across server restarts with zero extra dependencies.
"""
from __future__ import annotations

import json
import logging
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)

# ── File store ─────────────────────────────────────────────────────────────────
_STORE_PATH = Path(__file__).parent.parent.parent / "analytics_store.json"
_lock = Lock()  # thread-safe writes


def _load_store() -> dict:
    """Load analytics from the JSON file, or return a fresh store."""
    if _STORE_PATH.exists():
        try:
            with open(_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning("Could not read analytics store: %s — starting fresh", exc)
    return {"queries": [], "chat_messages": []}


def _save_store(store: dict) -> None:
    """Persist the analytics store to disk."""
    try:
        with open(_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, default=str)
    except Exception as exc:
        logger.error("Could not write analytics store: %s", exc)


class AnalyticsService:
    """Analytics tracking backed by a lightweight JSON file store."""

    # ── Write ──────────────────────────────────────────────────────────────────

    def record_query(
        self,
        question_text: str,
        user_id: str | None = None,
        confidence_score: float | None = None,
        intent: str | None = None,
        response_source: str | None = None,  # "rag" | "template" | "clarification"
    ) -> None:
        """Append a query record to the store."""
        record = {
            "question_text": question_text,
            "user_id": user_id,
            "confidence_score": confidence_score,
            "intent": intent,
            "response_source": response_source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            store = _load_store()
            store["queries"].append(record)
            # Keep only last 10,000 entries
            store["queries"] = store["queries"][-10_000:]
            _save_store(store)

    def record_chat_message(self, user_id: str, role: str, content: str, thread_id: str) -> None:
        """Store a chat message (user or assistant) for analytics."""
        record = {
            "user_id": user_id,
            "thread_id": thread_id,
            "role": role,
            "content_length": len(content),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with _lock:
            store = _load_store()
            store.setdefault("chat_messages", []).append(record)
            store["chat_messages"] = store["chat_messages"][-10_000:]
            _save_store(store)

    # ── Read ───────────────────────────────────────────────────────────────────

    def get_most_used_questions(self, limit: int = 10) -> list[dict]:
        """Return the most frequently asked question topics."""
        store = _load_store()
        queries = store.get("queries", [])

        if not queries:
            return []

        counter: Counter = Counter(q.get("question_text", "")[:100] for q in queries)
        return [
            {"question": q, "count": c}
            for q, c in counter.most_common(limit)
        ]

    def get_recent_queries(self, limit: int = 20) -> list[dict]:
        """Return the most recent queries."""
        store = _load_store()
        queries = store.get("queries", [])
        return list(reversed(queries[-limit:]))

    def get_analytics_summary(self) -> dict:
        """Return high-level aggregate statistics."""
        store = _load_store()
        queries = store.get("queries", [])
        messages = store.get("chat_messages", [])

        total = len(queries)
        if total == 0:
            return {
                "total_queries": 0,
                "avg_confidence_score": None,
                "top_intent": None,
                "rag_usage_pct": 0.0,
                "template_usage_pct": 0.0,
                "total_chat_messages": len(messages),
            }

        # Confidence average (exclude None)
        scores = [q["confidence_score"] for q in queries if q.get("confidence_score") is not None]
        avg_score = round(sum(scores) / len(scores), 3) if scores else None

        # Intent distribution
        intents = Counter(q.get("intent", "unknown") for q in queries)
        top_intent = intents.most_common(1)[0][0] if intents else None

        # Source breakdown
        sources = Counter(q.get("response_source", "unknown") for q in queries)
        rag_pct = round(sources.get("rag", 0) / total * 100, 1)
        tmpl_pct = round(sources.get("template", 0) / total * 100, 1)

        return {
            "total_queries": total,
            "avg_confidence_score": avg_score,
            "top_intent": top_intent,
            "intent_distribution": dict(intents.most_common()),
            "rag_usage_pct": rag_pct,
            "template_usage_pct": tmpl_pct,
            "total_chat_messages": len(messages),
        }

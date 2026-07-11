"""
Navelle AI Module — Analytics Routes
Admin dashboard endpoints backed by JSON file store.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Query

from ai.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/analytics", tags=["Analytics"])

_service = AnalyticsService()


@router.get("/most-used-questions")
async def most_used_questions(
    limit: int = Query(10, ge=1, le=50, description="Number of top questions to return"),
):
    """Return the most frequently asked questions across all users."""
    return {
        "questions": _service.get_most_used_questions(limit=limit),
        "limit": limit,
    }


@router.get("/recent-queries")
async def recent_queries(
    limit: int = Query(20, ge=1, le=100, description="Number of recent queries to return"),
):
    """Return the most recent chat queries."""
    return {
        "queries": _service.get_recent_queries(limit=limit),
        "limit": limit,
    }


@router.get("/summary")
async def analytics_summary():
    """Return high-level aggregate statistics for the admin dashboard."""
    return _service.get_analytics_summary()

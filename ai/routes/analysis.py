"""
Navelle AI Module — Analysis Routes
All data comes from the Navelle backend via BackendClient.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from ai.services.analysis_service import AnalysisService
from ai.utils.backend_client import BackendClientError, backend_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/analyze", tags=["Analysis"])

_service = AnalysisService()


async def _get_health_data(user_id: str, days: int = 30) -> dict:
    """Fetch health data from backend, raise 503 on failure."""
    try:
        return await backend_client.get_user_health_overview(user_id, days=days)
    except BackendClientError as exc:
        logger.error("Backend unavailable for user %s: %s", user_id, exc)
        raise HTTPException(status_code=503, detail="Backend service temporarily unavailable.")


@router.get("/wellness-dashboard/{user_id}")
async def wellness_dashboard(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
):
    """Return a full wellness dashboard summary for the user."""
    health_data = await _get_health_data(user_id, days=days)
    return _service.get_wellness_dashboard(user_id, health_data)


@router.get("/symptom-trend/{user_id}")
async def symptom_trend(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
):
    """Return daily symptom severity trends over the requested window."""
    health_data = await _get_health_data(user_id, days=days)
    return _service.get_symptom_trend(user_id, health_data, days=days)


@router.get("/top-symptoms/{user_id}")
async def top_symptoms(
    user_id: str,
    limit: int = Query(5, ge=1, le=20),
    days: int = Query(30, ge=1, le=365),
):
    """Return the most frequently logged symptoms with severity stats."""
    health_data = await _get_health_data(user_id, days=days)
    return _service.get_top_symptoms(user_id, health_data, limit=limit)


@router.post("/trigger-warnings/{user_id}")
async def trigger_warnings(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
):
    """Identify high-severity or recurring symptoms that need attention."""
    health_data = await _get_health_data(user_id, days=days)
    warnings = _service.get_trigger_warnings(user_id, health_data)
    return {
        "user_id": user_id,
        "warnings": warnings,
        "total_warnings": len(warnings),
        "disclaimer": (
            "⚕️ These insights are for informational purposes only. "
            "Please consult your healthcare provider for medical advice."
        ),
    }

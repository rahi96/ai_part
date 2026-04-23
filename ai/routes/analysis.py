from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException, Query
from ai.services.analysis_service import AnalysisService
from ai.utils.backend_client import BackendClientError, backend_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/analyze", tags=["Analysis"])

_service = AnalysisService()

DEFAULT_INCLUDE_FIELDS = "user,symptoms,menstrual_trackers,medical_histories,lab_histories,chat_messages"
VALID_HEALTH_FIELDS = {
    "user",
    "symptoms",
    "menstrual_trackers",
    "medical_histories",
    "lab_histories",
    "chat_messages",
}


async def _get_health_data(user_id: str, days: int = 30) -> dict:
    
    try:
        return await backend_client.get_user_health_overview(user_id, days=days)
    except BackendClientError as exc:
        logger.error("Backend unavailable for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=503,
            detail="Backend service temporarily unavailable.",
        )


@router.get("/wellness-dashboard/{user_id}")
async def wellness_dashboard(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
) -> dict:
    health_data = await _get_health_data(user_id, days=days)
    return _service.get_wellness_dashboard(user_id, health_data)


@router.get("/symptom-intensity-trend/{user_id}")
async def symptom_intensity_trend(
    user_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to trend"),
) -> list[dict]:
    health_data = await _get_health_data(user_id, days=days)
    return _service.generate_symptom_intensity_trend(user_id, health_data, days=days)


@router.get("/trigger-warnings/{user_id}")
async def trigger_warnings(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
) -> dict:
    health_data = await _get_health_data(user_id, days=days)
    tip = _service.generate_trigger_tip(user_id, health_data)
    return {
        "user_id": user_id,
        "tip": tip,
    }


@router.get("/top-symptom-analysis/{user_id}")
async def top_symptom_analysis(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
) -> dict:
    health_data = await _get_health_data(user_id, days=days)
    top_symptoms = _service.generate_top_symptom_analysis(user_id, health_data)
    return {
        "user_id": user_id,
        "top_symptoms": top_symptoms,
    }


@router.get("/humor-break/{user_id}")
async def humor_break(user_id: str):
    health_data = await _get_health_data(user_id, days=30)
    return _service.generate_humor_break(user_id, health_data)


@router.get("/health-overview/{user_id}")
async def health_overview(
    user_id: str,
    days: int = Query(7, ge=1, le=365, description="Lookback window in days"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
    include: str = Query(
        DEFAULT_INCLUDE_FIELDS,
        description="Comma-separated list of data types to include (all by default)",
    ),
) -> dict:
   
    health_data = await _get_health_data(user_id, days=days)

    include_fields = [f.strip() for f in include.split(",") if f.strip()]
    filtered_data = {
        field: health_data.get(field, [])
        for field in include_fields
        if field in VALID_HEALTH_FIELDS
    }

    return {
        "user_id": user_id,
        "days_window": days,
        "limit": limit,
        "included_fields": list(filtered_data.keys()),
        "data": filtered_data,
    }

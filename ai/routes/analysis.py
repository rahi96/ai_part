from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException, Query, Body
from ai.services.analysis_service import AnalysisService
from ai.utils.backend_client import BackendClientError, backend_client
from ai.models.schemas import ChatInsightsResponse

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


@router.post("/wellness-dashboard/{user_id}")
async def wellness_dashboard(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
) -> dict:
    health_data = await _get_health_data(user_id, days=days)
    return await _service.get_wellness_dashboard(user_id, health_data)


@router.post("/symptom-intensity-trend/{user_id}")
async def symptom_intensity_trend(
    user_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to trend"),
) -> list[dict]:
    health_data = await _get_health_data(user_id, days=days)
    return await _service.generate_symptom_intensity_trend(user_id, health_data, days=days)


@router.post("/trigger-warnings/{user_id}")
async def trigger_warnings(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
) -> dict:
    health_data = await _get_health_data(user_id, days=days)
    tip = await _service.generate_trigger_tip(user_id, health_data)
    return {
        "user_id": user_id,
        "tip": tip,
    }


@router.post("/top-symptom-analysis/{user_id}")
async def top_symptom_analysis(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
) -> dict:
    health_data = await _get_health_data(user_id, days=days)
    top_symptoms = await _service.generate_top_symptom_analysis(user_id, health_data)
    return {
        "user_id": user_id,
        "top_symptoms": top_symptoms,
    }


@router.post("/humor-break/{user_id}")
async def humor_break(user_id: str):
    health_data = await _get_health_data(user_id, days=30)
    return await _service.generate_humor_break(user_id, health_data)


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


@router.post("/chat-insights", response_model=ChatInsightsResponse)
async def chat_insights() -> dict:
    """
    Fetch global chat history across all users, then use AI to synthesize
    dashboard data for Most Used Questions and Recent Queries.
    """
    try:
        insights = await _service.generate_chat_insights()
        return insights
    except Exception as exc:
        logger.error("Failed to generate chat insights: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to generate chat insights")

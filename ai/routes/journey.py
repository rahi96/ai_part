"""
Navelle AI Module — Journey Routes
Endpoint for creating health goals and generating perimenopause journey plans.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Body, Path

from ai.models.schemas import HealthGoalCreateRequest, JourneyPlanResponse
from ai.services.journey_service import JourneyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/journey", tags=["Journey"])

_service = JourneyService()

@router.post("/create-plan/{user_id}", response_model=JourneyPlanResponse)
async def create_journey_plan(
    user_id: str = Path(..., description="The MongoDB ObjectId of the user"),
    request: HealthGoalCreateRequest = Body(...)
):
    """
    Create a new health goal and receive a personalised perimenopause journey plan.
    
    This endpoint fetches the user's latest health overview (including lab histories)
    from the backend and uses AWS Bedrock Claude to generate a tailored wellness journey.
    
    The AI analyzes:
    - User's health goal and measurements
    - Current and target values
    - Recent lab reports and medical documents
    - Clinical context and perimenopause symptoms
    
    Returns a comprehensive journey plan with personalized recommendations.
    """
    return await _service.create_journey_plan(user_id, request)

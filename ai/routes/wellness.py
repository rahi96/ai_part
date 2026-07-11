"""
Navelle AI Module — Wellness Routes
Mood check-in and humor break. Fully stateless — no database required.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Body

from ai.services.wellness_service import WellnessService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["Wellness"])

_service = WellnessService()


@router.post("/mood/select")
async def select_mood(
    user_id: str = Body(..., embed=True, description="MongoDB ObjectId of the user"),
    mood: str = Body(..., embed=True, description="great | good | okay | low | awful"),
):
    """
    Record a mood check-in and receive an instant personalised response.
    """
    result = _service.select_mood(user_id=user_id, mood=mood)
    return result


@router.get("/humor-break/{user_id}")
async def humor_break(user_id: str):
    """
    Return a perimenopause-themed joke and an evidence-based wellness tip.
    Great for breaking tension during hard symptom days.
    """
    return _service.get_humor_break(user_id=user_id)

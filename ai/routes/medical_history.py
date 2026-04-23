"""
Navelle AI Module — Medical History Routes
Routes for analyzing medical history and identifying related conditions.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from ai.models.schemas import (
    MedicalHistoryAnalysisRequest,
    MedicalHistoryAnalysisResponse,
)
from ai.services.medical_history_service import MedicalHistoryService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/medical-history", tags=["Medical History"])

_service = MedicalHistoryService()


@router.post("/{user_id}/analyze", response_model=MedicalHistoryAnalysisResponse)
async def analyze_medical_history(
    user_id: str,
    request: MedicalHistoryAnalysisRequest,
) -> MedicalHistoryAnalysisResponse:
    """Analyze medical history and identify related conditions with AI insights."""
    try:
        logger.info(
            f"Received medical history analysis for user: {user_id}, "
            f"condition: {request.medical_history.condition_name}"
        )
        
        # Call service to analyze medical history
        analysis_response = await _service.analyze_medical_history(request)
        
        logger.info(
            f"Successfully analyzed {request.medical_history.condition_name} "
            f"for user {user_id}"
        )
        return analysis_response
        
    except ValueError as exc:
        logger.error(f"Invalid request format: {str(exc)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid medical history data: {str(exc)}",
        )
    except Exception as exc:
        logger.error(f"Medical history analysis failed for user {user_id}: {str(exc)}")
        raise HTTPException(
            status_code=500,
            detail="AI analysis failed. Please try again later.",
        )

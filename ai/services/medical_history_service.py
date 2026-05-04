"""
Navelle AI Module — Medical History Analysis Service
Provides medical history analysis using AI/LLM to identify related conditions
and symptom overlaps based on user's medical history.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from ai.models.schemas import (
    MedicalHistoryAnalysisRequest,
    MedicalHistoryAnalysisResponse,
)
from ai.utils.llm_call import llm_call
from ai.utils.llm_response_parser import LLMResponseParser

logger = logging.getLogger(__name__)

# System prompt for medical history analysis
MEDICAL_HISTORY_SYSTEM_PROMPT = """You are an advanced medical analysis AI assistant specializing in women's health, 
particularly perimenopause, menopause, hormonal conditions, and related health issues. 

Your task is to analyze a patient's medical history entry and RETURN ONLY VALID JSON (no other text).

CRITICAL: Return ONLY the JSON response, nothing else. No markdown, no explanations, just pure JSON.

Analyze and provide:
1. A professional title for the analysis (e.g., "Conditions That Matter: Understanding PCOS")
2. A brief description of potential symptom overlaps
3. Symptom overlap percentages across relevant categories (0-100)
4. A list of 5-6 related conditions with match percentages and severity levels

REQUIREMENTS:
- Base all analysis on evidence-based medical knowledge
- Consider hormonal, metabolic, mental health, and immune system aspects
- Provide realistic match percentages (0-100)
- Use evidence-supported severity levels
- Return ONLY valid JSON in the exact format specified
- Do not include markdown formatting or explanations
- Severity should be: "low" (0-30%), "medium" (31-70%), "high" (71-100%)
- Color codes: use "red", "orange", "yellow", "gray", "pink", "blue"

Remember: RETURN ONLY JSON, NO OTHER TEXT."""


class MedicalHistoryService:
    """Service for analyzing medical history using AI."""

    def __init__(self):
        self.llm_response_parser = LLMResponseParser()

    async def analyze_medical_history(
        self, request: MedicalHistoryAnalysisRequest
    ) -> MedicalHistoryAnalysisResponse:
        """
        Analyze medical history entry and return AI-generated analysis
        with related conditions and symptom overlaps.
        
        Args:
            request: MedicalHistoryAnalysisRequest with medical history data
            
        Returns:
            MedicalHistoryAnalysisResponse with AI analysis
            
        Raises:
            ValueError: If AI response is invalid or cannot be parsed
            Exception: If LLM call fails
        """
        try:
            # Extract medical history data
            med_hist = request.medical_history
            
            # Build detailed prompt for LLM
            user_prompt = self._build_analysis_prompt(med_hist)
            
            logger.info(
                f"Analyzing medical history for condition: {med_hist.condition_name}"
            )
            
            # Call LLM
            llm_response = await llm_call.chat_completion(
                messages=[
                    {"role": "system", "content": MEDICAL_HISTORY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            logger.info(f"LLM response received for {med_hist.condition_name}")
            
            # Parse LLM response
            parsed_response = self._parse_llm_response(llm_response)
            
            # Validate and construct response
            response = self._construct_response(parsed_response)
            
            logger.info(
                f"Successfully analyzed medical history: {med_hist.condition_name}"
            )
            return response
            
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse LLM JSON response: {str(exc)}")
            raise ValueError(f"Invalid AI response format: {str(exc)}")
        except Exception as exc:
            logger.error(f"Medical history analysis failed: {str(exc)}", exc_info=True)
            raise

    def _build_analysis_prompt(self, med_hist: Any) -> str:
        """Build detailed prompt for LLM analysis."""
        return f"""Analyze the following medical history entry and provide a comprehensive 
medical analysis with related conditions and symptom overlaps.

PATIENT MEDICAL HISTORY:
- Condition: {med_hist.condition_name}
- Category: {med_hist.category}
- Start Date: {med_hist.start}
- Date Diagnosed: {med_hist.date_diagnosed}
- Notes: {med_hist.notes}

Based on this medical history, please provide:

1. A professional title for the analysis (e.g., "Conditions That Matter, Menopause")
2. A brief description of potential symptom overlaps
3. Symptom overlap percentages across relevant categories:
   - Hormonal (0-100)
   - Mental (0-100)
   - Metabolic (0-100)
   - Fatigue (0-100)
   - Immune (0-100)
   - And the specific condition category percentage
4. A list of 5-6 related conditions with:
   - Name of the condition
   - Match percentage (0-100) - how likely this condition overlaps
   - Severity level (low/medium/high based on impact)
   - UI color code
   - Shared symptoms (3-4 relevant symptoms)

Return the response STRICTLY in this JSON format (NO other text):
{{
  "analysis": {{
    "title": "string",
    "description": "string",
    "symptom_overlap": {{
      "Hormonal": integer,
      "Mental": integer,
      "Metabolic": integer,
      "Fatigue": integer,
      "Immune": integer,
      "{med_hist.category}": integer
    }},
    "conditions": [
      {{
        "name": "string",
        "match_percentage": integer,
        "severity": "low|medium|high",
        "color": "string",
        "shared_symptoms": ["string", "string", "string"]
      }}
    ]
  }}
}}"""

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM JSON response."""
        try:
            # Try to parse as JSON
            data = json.loads(response)
            
            # Validate structure
            if "analysis" not in data:
                raise ValueError("Missing 'analysis' key in response")
            
            analysis = data["analysis"]
            required_keys = ["title", "description", "symptom_overlap", "conditions"]
            for key in required_keys:
                if key not in analysis:
                    raise ValueError(f"Missing required key in analysis: {key}")
            
            return data
            
        except json.JSONDecodeError as exc:
            logger.error(f"JSON parsing error: {str(exc)}")
            # Try to extract JSON from response if it contains extra text
            try:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except Exception:
                pass
            raise ValueError(f"Cannot parse LLM response as JSON: {str(exc)}")

    def _construct_response(self, parsed_data: Dict[str, Any]) -> MedicalHistoryAnalysisResponse:
        """Construct validated response from parsed LLM data."""
        try:
            # Build response object
            response = MedicalHistoryAnalysisResponse(**parsed_data)
            return response
        except Exception as exc:
            logger.error(f"Response construction failed: {str(exc)}")
            raise ValueError(f"Failed to construct response: {str(exc)}")

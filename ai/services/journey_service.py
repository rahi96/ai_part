from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from ai.models.schemas import HealthGoalCreateRequest, JourneyPlanResponse, GoalProgressItem
from ai.utils.backend_client import backend_client
from ai.utils.document_processor import _download_file, _extract_text
from ai.utils.llm_call import llm_call
from ai.utils.llm_response_parser import llm_parser

logger = logging.getLogger(__name__)

class JourneyService:
    """Service to manage perimenopause journey plans and goals using LLM logic."""

    async def create_journey_plan(self, user_id: str, request: HealthGoalCreateRequest) -> JourneyPlanResponse:
        """
        Generate a comprehensive journey plan based on the user's health goal and actual lab report files.
        Fetches data from the backend, reads PDF report content, and uses OpenAI for clinical analysis.
        """
        logger.info(f"Generating enhanced journey plan for user_id: {user_id}")

        # 1. Fetch health overview from backend
        health_data = await backend_client.get_user_health_overview(user_id, days=30)
        lab_histories = health_data.get("lab_histories", [])
        user_info = health_data.get("user", {})
        # Robust name extraction: try all keys, fall back to "Valued User" if none found
        username = user_info.get("name") or user_info.get("fullName") or user_info.get("username") or "Valued User"
        if username == "Unknown": username = "Valued User"

        # 2. Extract and Read Lab Report Files
        lab_context_parts = []
        for i, lab in enumerate(lab_histories[:2]): # Process last 2 reports for context
            notes = lab.get("notes", "No notes")
            file_url = lab.get("file_url")
            
            report_text = ""
            if file_url:
                logger.info(f"Processing lab file: {file_url}")
                try:
                    data = _download_file(file_url)
                    if data:
                        # Try to get a filename from the URL or use a default
                        from urllib.parse import urlparse
                        parsed = urlparse(file_url)
                        file_name = parsed.path.split('/')[-1] or "report.pdf"
                        extracted = _extract_text(file_name, data)
                        report_text = extracted or ""
                except Exception as exc:
                    logger.warning(f"Failed to extract text from {file_url}: {exc}")
            
            part = f"Report {i+1} Date: {lab.get('date', 'Unknown')}\n"
            part += f"Clinical Notes: {notes}\n"
            if report_text:
                part += f"Extracted Document Text:\n--- START ---\n{report_text[:2000]}\n--- END ---\n"
            
            lab_context_parts.append(part)

        full_lab_context = "\n\n".join(lab_context_parts) if lab_context_parts else "No recent lab reports or medical files available."

        # 3. Prepare the prompt for real predictions
        system_prompt = """You are a senior clinical health planner for Navelle. 
You specialize in analyzing hormonal lab reports (FSH, Estradiol, Thyroid, etc.) to create 100% realistic perimenopause wellness plans.
Your goal is to provide real predictions and actionable medical-wellness steps based on the ACTUAL clinical data and the user's personal goals."""

        user_prompt = f"""
USER CLINICAL DATA:
Username: {username}
Goal: {request.goal_title}
Measurement: {request.measurement}
Current Value: {request.current_value}, Target Value: {request.target_value}
User's Personal Notes: {request.notes or 'None'}

LAB REPORTS & DOCUMENTS ANALYSIS:
{full_lab_context}

INSTRUCTIONS:
1. Carefully review the 'Extracted Document Text' from the lab reports.
2. Provide a 100% REAL prediction of how their current hormone levels (if present) relate to their symptoms and goal.
3. Generate a personalized Journey Plan with specific, evidence-based recommendations.
4. Calculate 'progress_percentage' logically.

Return a JSON object matching the JourneyPlanResponse structure:
{{
  "plan_title": "EMPOWER YOUR PERIMENOPAUSE JOURNEY",
  "username": "{username}",
  "created_at": "{datetime.now().strftime('%B %dth, %Y')}",
  "welcome_message": "An empathetic greeting referencing the specific findings in their lab reports.",
  "why_plan_description": "Clinical reasoning for this plan based on their lab documents.",
  "goals": [
    {{ 
      "title": "{request.goal_title}", 
      "target_description": "Target: {request.target_value} {request.measurement}", 
      "current_value": {request.current_value}, 
      "target_value": {request.target_value}, 
      "progress_percentage": 0 
    }},
    {{ "title": "Secondary Clinical Goal", "target_description": "...", "current_value": 0, "target_value": 0, "progress_percentage": 0 }}
  ],
  "recommended_actions": ["Specific action 1", "Specific action 2", "Specific action 3"],
  "next_review_date": "..."
}}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # 4. Execute LLM call with a larger token limit for the document context
            raw_response = await llm_call.chat_completion(
                messages=messages,
                max_tokens=1500
            )
            
            # 5. Parse and return
            return llm_parser.to_pydantic(raw_response, JourneyPlanResponse)

        except Exception as exc:
            logger.error(f"Enhanced journey generation failed: {exc}")
            return self._fallback_plan(username, request)

    def _fallback_plan(self, username: str, request: HealthGoalCreateRequest) -> JourneyPlanResponse:
        """Simple template-based fallback if LLM generation fails."""
        return JourneyPlanResponse(
            username=username,
            created_at=datetime.now().strftime("%B %dth, %Y"),
            welcome_message=f"Welcome, {username}! We've created this plan to help you reach your goal: {request.goal_title}.",
            why_plan_description="Regularly tracking your progress is key to managing perimenopause symptoms effectively.",
            goals=[
                GoalProgressItem(
                    title=request.goal_title,
                    target_description=f"Target: {request.target_value} {request.measurement}",
                    current_value=request.current_value,
                    target_value=request.target_value,
                    progress_percentage=0.0
                )
            ],
            recommended_actions=[
                "Maintain a consistent daily routine.",
                "Review your progress in two weeks."
            ],
            next_review_date=(datetime.now() + timedelta(days=14)).strftime("%B %dth, %Y").upper()
        )

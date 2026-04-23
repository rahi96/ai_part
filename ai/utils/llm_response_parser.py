"""
Navelle AI Module — LLM Response Parser
Helpers for parsing and validating LLM outputs.
"""
import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class LLMResponseParser:
    """Parses raw LLM strings into structured data or Pydantic models."""

    @staticmethod
    def parse_json(content: str) -> Dict[str, Any]:
        """Parse raw string into a dictionary."""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw content: {content}")
            raise ValueError("Invalid JSON response from LLM.")

    @staticmethod
    def to_pydantic(content: str, model_class: Type[T]) -> T:
        """Parse raw string directly into a Pydantic model."""
        data = LLMResponseParser.parse_json(content)
        try:
            return model_class(**data)
        except Exception as e:
            logger.error(f"Failed to map LLM response to {model_class.__name__}: {e}")
            raise e

# Singleton-like access
llm_parser = LLMResponseParser()

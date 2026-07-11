"""
Navelle AI Module — LLM Call Wrapper
Standardized way to execute LLM calls across the application.
Uses AWS Bedrock (Claude) as the LLM backend.
"""
import logging
from typing import List, Dict, Optional

from ai.utils.bedrock_llm import bedrock_llm

logger = logging.getLogger(__name__)


class LLMCall:
    """Handles execution of LLM completions via AWS Bedrock."""

    @staticmethod
    async def chat_completion(
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, str]] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Execute a chat completion call with standardized logging and error handling.
        Uses AWS Bedrock Claude model.

        Note: `response_format` is accepted for interface compatibility but is
        not natively supported by Bedrock. Ensure your prompt instructs the
        model to return JSON when structured output is needed.
        """
        target_model = model or bedrock_llm.get_model()

        logger.info(f"Executing LLM call with model: {target_model}")

        try:
            content = await bedrock_llm.async_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                model=target_model,
            )

            if not content:
                logger.warning("LLM returned an empty response.")
                return ""

            return content

        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise e


# Singleton-like access
llm_call = LLMCall()

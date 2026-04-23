"""
Navelle AI Module — LLM Call Wrapper
Standardized way to execute LLM calls across the application.
"""
import logging
from typing import List, Dict, Any, Optional
from ai.utils.openai_llm import openai_llm

logger = logging.getLogger(__name__)

class LLMCall:
    """Handles execution of LLM completions."""

    @staticmethod
    async def chat_completion(
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, str]] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Execute a chat completion call with standardized logging and error handling.
        """
        client = openai_llm.get_client()
        target_model = model or openai_llm.get_model()
        
        logger.info(f"Executing LLM call with model: {target_model}")
        
        try:
            # Note: client.chat.completions.create is synchronous in current openai lib version used, 
            # but we can wrap it or just use it as is if it's not a heavy load.
            # Using synchronous call since the project doesn't seem to use async openai client yet.
            response = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )
            
            content = response.choices[0].message.content
            if not content:
                logger.warning("LLM returned an empty response.")
                return ""
                
            return content.strip()

        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise e

# Singleton-like access
llm_call = LLMCall()

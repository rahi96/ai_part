"""
Navelle AI Module — OpenAI LLM Wrapper
Initializes and provides the OpenAI client.
"""
import logging
from openai import OpenAI
from ai.config import settings

logger = logging.getLogger(__name__)

class OpenAILLM:
    """Wrapper for OpenAI client and model configurations."""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        
        if not self.api_key:
            logger.error("OpenAI API key is missing in configuration!")
            raise ValueError("OPENAI_API_KEY must be set.")
            
        self.client = OpenAI(api_key=self.api_key)

    def get_client(self) -> OpenAI:
        return self.client

    def get_model(self) -> str:
        return self.model

# Singleton instance
openai_llm = OpenAILLM()

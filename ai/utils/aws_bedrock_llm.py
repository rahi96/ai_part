"""
Navelle AI Module — AWS Bedrock LLM Wrapper
Initializes and provides the AWS Bedrock Claude client.
"""
import logging
import json
import boto3
from ai.config import settings

logger = logging.getLogger(__name__)

class AWSBedrockLLM:
    """Wrapper for AWS Bedrock Claude client and model configurations."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize only once."""
        if AWSBedrockLLM._initialized:
            return
        
        self.model_id = settings.bedrock_model_id
        self.region = settings.aws_region
        
        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            logger.error("AWS credentials are missing in configuration!")
            raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set.")
        
        if not self.model_id:
            logger.error("Bedrock model ID is missing in configuration!")
            raise ValueError("BEDROCK_MODEL_ID must be set.")
        
        try:
            # Initialize Bedrock runtime client
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=self.region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            logger.info(f"AWS Bedrock LLM initialized with model: {self.model_id}")
            AWSBedrockLLM._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock client: {str(e)}")
            raise

    def get_client(self):
        """Get the Bedrock runtime client."""
        if not hasattr(self, 'client'):
            raise RuntimeError("AWS Bedrock client not initialized")
        return self.client

    def get_model(self) -> str:
        """Get the configured model ID."""
        if not hasattr(self, 'model_id'):
            raise RuntimeError("Model ID not initialized")
        return self.model_id

# Lazy-load singleton instance
def get_bedrock_llm():
    """Get or create the singleton Bedrock LLM instance."""
    try:
        return AWSBedrockLLM()
    except Exception as e:
        logger.error(f"Error getting Bedrock LLM: {str(e)}")
        raise

# Create instance at module level with error handling
try:
    bedrock_llm = get_bedrock_llm()
except Exception as e:
    logger.error(f"Failed to initialize Bedrock LLM at import time: {str(e)}")
    bedrock_llm = None

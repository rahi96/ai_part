"""
Navelle AI Module — AWS Bedrock LLM Wrapper
Provides Claude model calls via AWS Bedrock with lazy initialisation.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import boto3

from ai.config import settings

logger = logging.getLogger(__name__)


class BedrockLLM:
    """Wrapper for AWS Bedrock Claude client with lazy initialisation."""

    def __init__(self) -> None:
        self._client = None
        self._ready = False

    # ── Initialisation ─────────────────────────────────────────────────────────

    def _init_client(self) -> bool:
        """Lazy-init the boto3 bedrock-runtime client."""
        if self._ready:
            return True

        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            logger.error("AWS credentials are missing — Bedrock unavailable")
            return False

        try:
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
            self._ready = True
            logger.info(
                "Bedrock client initialised — model: %s, region: %s",
                settings.bedrock_model_id,
                settings.aws_region,
            )
            return True
        except Exception as exc:
            logger.error("Failed to initialise Bedrock client: %s", exc)
            return False

    def is_available(self) -> bool:
        """Check whether the Bedrock client can be initialised."""
        return self._init_client()

    def get_model(self) -> str:
        return settings.bedrock_model_id

    # ── Chat Completion ────────────────────────────────────────────────────────

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        model: Optional[str] = None,
    ) -> str:
        """
        Synchronous chat completion using Bedrock Claude.

        Accepts OpenAI-style messages (with "system" role) and converts
        them to the Bedrock Messages API format automatically.

        Returns the assistant's text response.
        """
        if not self._init_client():
            raise RuntimeError("Bedrock client not available — check AWS credentials")

        target_model = model or settings.bedrock_model_id

        # ── Separate system messages from conversation messages ────────────
        system_parts: list[str] = []
        conversation_messages: list[dict] = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
            else:
                conversation_messages.append(
                    {"role": msg["role"], "content": msg["content"]}
                )

        # Bedrock Claude requires at least one user message
        if not conversation_messages:
            conversation_messages.append(
                {"role": "user", "content": "Hello"}
            )

        # ── Build request body (Bedrock Messages API) ──────────────────────
        body: Dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": conversation_messages,
        }
        if system_parts:
            body["system"] = "\n\n".join(system_parts)

        logger.info(
            "Bedrock call — model: %s, messages: %d",
            target_model,
            len(conversation_messages),
        )

        response = self._client.invoke_model(
            modelId=target_model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        result = json.loads(response["body"].read())
        text = result["content"][0]["text"] if result.get("content") else ""

        if not text:
            logger.warning("Bedrock returned an empty response")

        return text.strip()

    # ── Async wrapper ──────────────────────────────────────────────────────────

    async def async_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        model: Optional[str] = None,
    ) -> str:
        """Async wrapper — runs the synchronous Bedrock call in a thread."""
        return await asyncio.to_thread(
            self.chat_completion,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
        )


# ── Lazy singleton (does NOT crash at import time) ─────────────────────────────
bedrock_llm = BedrockLLM()

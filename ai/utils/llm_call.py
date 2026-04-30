"""
Navelle AI Module — LLM Call Wrapper
Standardized way to execute LLM calls across the application.

Uses the AWS Bedrock Converse API — the modern unified API that works with
ALL Bedrock model families (Claude, Llama, Mistral, Titan, etc.) without
needing to know model-specific request/response body formats.

Key advantages of Converse API:
  - Single consistent interface for all models
  - Native system prompt support
  - No anthropic_version or model-specific prompt templates needed
  - boto3 converse() is synchronous; we run it in a thread-pool executor
    so it never blocks the asyncio event loop.
"""
import asyncio
import functools
import json
import logging
from typing import Any, Dict, List, Optional

from ai.utils.aws_bedrock_llm import bedrock_llm

logger = logging.getLogger(__name__)


class LLMCall:
    """Handles execution of LLM completions via the AWS Bedrock Converse API."""

    @staticmethod
    def _build_converse_messages(
        messages: List[Dict[str, str]],
    ) -> tuple[Optional[List[Dict]], List[Dict]]:
        """
        Convert OpenAI-style messages to Bedrock Converse API format.

        Returns:
            (system_blocks, conversation_messages)
            system_blocks: List of {"text": "..."} dicts for the system param, or None.
            conversation_messages: List of Converse-format message dicts.
        """
        system_parts: List[str] = []
        conversation: List[Dict[str, Any]] = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_parts.append(content)
            elif role in ("user", "assistant"):
                conversation.append({
                    "role": role,
                    "content": [{"text": content}],
                })

        # Converse API requires the conversation to start with a user message
        if not conversation:
            conversation = [{"role": "user", "content": [{"text": "Hello"}]}]

        system_blocks = [{"text": "\n\n".join(system_parts)}] if system_parts else None
        return system_blocks, conversation

    @staticmethod
    async def chat_completion(
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, str]] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Execute a chat completion call via the AWS Bedrock Converse API.

        Accepts the OpenAI-style message format (system / user / assistant roles).
        Works with any Bedrock model (Claude, Llama, Mistral, etc.) without
        any model-specific formatting logic.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
                      Supports "system", "user", and "assistant" roles.
            temperature: Sampling temperature (0.0–1.0).
            max_tokens: Maximum tokens in the response.
            response_format: Ignored (kept for API compatibility).
            model: Optional model ID override.

        Returns:
            The assistant's text response as a plain string.

        Raises:
            RuntimeError: If the Bedrock client is not initialized.
            Exception: Propagated from the Bedrock API on non-recoverable errors.
        """
        if bedrock_llm is None:
            logger.error("AWS Bedrock LLM not initialized")
            raise RuntimeError(
                "AWS Bedrock LLM failed to initialize. Check AWS credentials."
            )

        try:
            client = bedrock_llm.get_client()
            target_model = model or bedrock_llm.get_model()

            system_blocks, conversation = LLMCall._build_converse_messages(messages)

            logger.info(
                "LLM call via Converse API — model: %s | system: %s | turns: %d",
                target_model,
                "yes" if system_blocks else "no",
                len(conversation),
            )
            logger.debug("Conversation turns: %s", json.dumps(conversation)[:400])

            # Build Converse API kwargs
            converse_kwargs: Dict[str, Any] = {
                "modelId": target_model,
                "messages": conversation,
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                },
            }
            if system_blocks:
                converse_kwargs["system"] = system_blocks

            # ── Invoke via thread pool (boto3 is synchronous) ─────────────────
            # Running a blocking call directly inside an async handler stalls
            # the event loop for the full LLM latency (2–10 s per request).
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(client.converse, **converse_kwargs),
            )

            logger.info("Bedrock Converse API call successful")

            # ── Parse response (same format for all models) ───────────────────
            output_message = response.get("output", {}).get("message", {})
            content_blocks = output_message.get("content", [])

            if not content_blocks:
                logger.warning("Bedrock returned empty content. Full response: %s", response)
                return ""

            # Concatenate all text blocks (usually just one)
            text = " ".join(
                block.get("text", "")
                for block in content_blocks
                if block.get("type", "text") == "text" or "text" in block
            ).strip()

            if not text:
                logger.warning("Bedrock content blocks had no text: %s", content_blocks)
                return ""

            usage = response.get("usage", {})
            logger.info(
                "LLM response received — length: %d | in_tokens: %s | out_tokens: %s",
                len(text),
                usage.get("inputTokens", "?"),
                usage.get("outputTokens", "?"),
            )
            return text

        except json.JSONDecodeError as exc:
            logger.error("Failed to parse Bedrock response JSON: %s", exc)
            raise
        except Exception as exc:
            logger.error("LLM call failed: %s", exc, exc_info=True)
            raise


# ── Singleton ─────────────────────────────────────────────────────────────────
llm_call = LLMCall()

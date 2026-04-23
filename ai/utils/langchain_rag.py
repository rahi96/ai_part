"""
Navelle AI Module — LangChain RAG Pipeline
Generates personalised GPT-4 responses using health context and
direct document chunks (no vector database).
"""
from __future__ import annotations

import logging
from typing import Any

from ai.config import settings

logger = logging.getLogger(__name__)

# ── Healthcare Disclaimer ──────────────────────────────────────────────────────
DISCLAIMER = (
    "\n\n---\n"
    "⚕️ *This information is for educational purposes only and is not a substitute "
    "for professional medical advice, diagnosis, or treatment. Always consult your "
    "qualified healthcare provider before making any health decisions.*"
)

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Mennie™, a compassionate and knowledgeable AI wellness companion \
for the Navelle perimenopause support platform.

Your role:
- Provide accurate, evidence-based information about perimenopause and menopause
- Personalise responses using the user's health data provided
- Be warm, empathetic, and supportive — this journey can be overwhelming
- Always recommend consulting a healthcare provider for medical decisions
- Cite the sources provided in your response when relevant
- Keep responses clear, concise, and actionable

You MUST NOT:
- Diagnose conditions
- Prescribe medications or specific dosages
- Replace professional medical advice
- Make absolute claims about treatments

Language: Be conversational but professional. Avoid overly clinical language."""


def _build_health_context(health_data: dict) -> str:
    """Summarise the user's health data as a context block for GPT-4."""
    if not health_data:
        return "No health data available for this user."

    user = health_data.get("user", {})
    symptoms = health_data.get("symptoms", [])
    menstrual = health_data.get("menstrual_trackers", [])
    medical = health_data.get("medical_histories", [])
    labs = health_data.get("lab_histories", [])

    lines = []

    if user:
        lines.append(f"**User Profile:** {user.get('name', 'Unknown')}")
        if user.get("health_condition") and user["health_condition"] != "NONE":
            lines.append(f"**Health Condition:** {user['health_condition']}")
        if user.get("dob"):
            lines.append(f"**Date of Birth:** {user['dob']}")

    if symptoms:
        recent = symptoms[:5]  # last 5 symptoms
        sym_list = ", ".join(
            f"{s.get('symptom_name', '?')} (severity {s.get('severity_level', '?')}/10)"
            for s in recent
        )
        lines.append(f"**Recent Symptoms:** {sym_list}")

    if menstrual:
        last = menstrual[0]
        lines.append(
            f"**Last Menstrual Log:** {last.get('start_date', '?')} to {last.get('end_date', '?')}, "
            f"flow: {last.get('flow_intensity', '?')}"
        )

    if medical:
        conditions = ", ".join(m.get("condition", "?") for m in medical)
        lines.append(f"**Medical History:** {conditions}")

    if labs:
        most_recent = labs[0]  # Assume sorted by date, newest first
        lab_notes = most_recent.get("notes", "")
        lab_date = most_recent.get("date", "")
        lines.append(f"**Recent Lab Results ({lab_date}):** {lab_notes}")
        if most_recent.get("file_url"):
            lines.append(f"Lab document: {most_recent['file_url']}")

    return "\n".join(lines) if lines else "Minimal health data available."


def _build_rag_context(retrieved_docs: list[dict]) -> str:
    """Format retrieved documents as a context block."""
    if not retrieved_docs:
        return ""

    lines = ["**Relevant Documents:**"]
    for i, doc in enumerate(retrieved_docs, 1):
        title = doc.get("topic") or doc.get("document_title", "Untitled")
        content = doc.get("content") or doc.get("content_preview", "")
        lines.append(f"\n[Source {i}: {title}]\n{content}")

    return "\n".join(lines)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline using GPT-4.
    Falls back gracefully if OpenAI is unavailable.
    """

    def __init__(self) -> None:
        self._client = None
        self._ready = False

    def _init_client(self) -> bool:
        if self._ready:
            return True
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured — RAG unavailable")
            return False
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.openai_api_key)
            self._ready = True
            logger.info("RAG pipeline initialised with model: %s", settings.openai_model)
            return True
        except Exception as exc:
            logger.error("Failed to initialise OpenAI client: %s", exc)
            return False

    def generate(
        self,
        user_message: str,
        health_data: dict | None = None,
        retrieved_docs: list[dict] | None = None,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """
        Generate a RAG-powered response.

        Returns:
            {
                "response": str,
                "sources": list[str],
                "model": str,
                "confidence": float,
                "fallback_used": bool
            }
        """
        if not self._init_client():
            return self._fallback_response(user_message)

        health_ctx = _build_health_context(health_data or {})
        rag_ctx = _build_rag_context(retrieved_docs or [])

        # Build the messages
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history (last 6 turns for context window efficiency)
        if conversation_history:
            messages.extend(conversation_history[-6:])

        # Build user message with context
        user_content_parts = [f"**User Question:** {user_message}"]
        if health_ctx:
            user_content_parts.append(f"\n**User Health Context:**\n{health_ctx}")
        if rag_ctx:
            user_content_parts.append(f"\n{rag_ctx}")
        user_content_parts.append(
            "\nPlease provide a personalised, evidence-based response. "
            "If referencing sources, mention the topic name."
        )

        messages.append({"role": "user", "content": "\n".join(user_content_parts)})

        try:
            response = self._client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )

            answer = response.choices[0].message.content or ""
            sources = [doc["topic"] for doc in (retrieved_docs or [])]

            # Estimate confidence from retrieval scores
            if retrieved_docs:
                avg_score = sum(d.get("score", 0) for d in retrieved_docs) / len(retrieved_docs)
                confidence = round(min(avg_score, 1.0), 3)
            else:
                confidence = 0.5  # reasonable baseline for template answers

            return {
                "response": answer + DISCLAIMER,
                "sources": sources,
                "model": settings.openai_model,
                "confidence": confidence,
                "fallback_used": False,
            }

        except Exception as exc:
            logger.error("GPT-4 generation failed: %s", exc)
            return self._generate_general_knowledge_response(
                user_message, health_data, conversation_history
            )

    def _generate_general_knowledge_response(
        self,
        user_message: str,
        health_data: dict | None = None,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """
        Generate response using LLM general knowledge when RAG fails.
        This provides helpful answers even without retrieved documents.
        """
        if not self._init_client():
            # Only return error if OpenAI itself is unavailable
            return {
                "response": (
                    "I'm having trouble connecting to my knowledge base right now. "
                    "Please try again in a moment, or contact your healthcare provider "
                    "directly for immediate support." + DISCLAIMER
                ),
                "sources": [],
                "model": "fallback",
                "confidence": 0.0,
                "fallback_used": True,
            }

        health_ctx = _build_health_context(health_data or {})

        # System prompt for general knowledge mode
        general_knowledge_prompt = """You are Mennie™, a compassionate and knowledgeable AI wellness companion \
for the Navelle perimenopause support platform.

Your role:
- Provide accurate, evidence-based information about perimenopause and menopause using your medical knowledge
- Personalise responses using the user's health data provided
- Be warm, empathetic, and supportive
- Always recommend consulting a healthcare provider for medical decisions
- Keep responses clear, concise, and actionable

Important: If you are uncertain about specific details, acknowledge the uncertainty and suggest the user consult their healthcare provider. Do not make up specific medical facts.

You MUST NOT:
- Diagnose conditions
- Prescribe medications or specific dosages
- Replace professional medical advice"""

        messages: list[dict] = [{"role": "system", "content": general_knowledge_prompt}]

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-6:])

        # Build user message
        user_content_parts = [f"**User Question:** {user_message}"]
        if health_ctx:
            user_content_parts.append(f"\n**User Health Context:**\n{health_ctx}")
        user_content_parts.append(
            "\nPlease provide a helpful, evidence-based response using your medical knowledge. "
            "If you're uncertain about specific details, acknowledge this and suggest consulting a healthcare provider."
        )

        messages.append({"role": "user", "content": "\n".join(user_content_parts)})

        try:
            response = self._client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )

            answer = response.choices[0].message.content or ""

            return {
                "response": answer + DISCLAIMER,
                "sources": [],  # No RAG sources when using general knowledge
                "model": settings.openai_model,
                "confidence": 0.7,  # Good confidence for general knowledge
                "fallback_used": False,  # This is not a fallback - it's general knowledge mode
            }

        except Exception as exc:
            logger.error("General knowledge generation failed: %s", exc)
            # Last resort: return the generic error
            return {
                "response": (
                    "I'm having trouble connecting to my knowledge base right now. "
                    "Please try again in a moment, or contact your healthcare provider "
                    "directly for immediate support." + DISCLAIMER
                ),
                "sources": [],
                "model": "fallback",
                "confidence": 0.0,
                "fallback_used": True,
            }

    def _fallback_response(
        self,
        user_message: str,
        health_data: dict | None = None,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """Legacy fallback - redirects to general knowledge mode."""
        logger.info("RAG failed - using general knowledge mode instead of template fallback")
        return self._generate_general_knowledge_response(
            user_message, health_data, conversation_history
        )


class IntentClassifier:
    """
    Lightweight rule-based intent classifier.
    Used by LangGraph to route messages without an LLM call.
    """

    MEDICAL_KEYWORDS = {
        "hot flash", "hot flush", "night sweat", "mood swing", "brain fog", "memory",
        "sleep", "insomnia", "anxiety", "depression", "fatigue", "tired", "weight",
        "period", "cycle", "menstrual", "bleeding", "discharge", "vaginal", "libido",
        "sex", "joint", "pain", "bone", "osteoporosis", "hrt", "hormone", "estrogen",
        "progesterone", "testosterone", "perimenopause", "menopause", "symptom",
        "treatment", "medication", "supplement", "doctor", "test", "blood test",
        "fsh", "estradiol", "thyroid", "headache", "migraine", "palpitation",
    }

    CLARIFICATION_TRIGGERS = {
        "help", "not feeling well", "something's wrong", "i don't know",
        "everything", "all of it", "many things", "lots of things",
    }

    GREETING_KEYWORDS = {
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "how are you", "what can you do", "who are you",
    }

    def classify(self, message: str) -> str:
        """
        Returns one of: 'medical_query' | 'needs_clarification' | 'greeting' | 'general'
        """
        msg_lower = message.lower().strip()

        # Too vague — needs clarification
        if len(msg_lower.split()) <= 3 or any(t in msg_lower for t in self.CLARIFICATION_TRIGGERS):
            if not any(k in msg_lower for k in self.MEDICAL_KEYWORDS):
                return "needs_clarification"

        # Greeting
        if any(g in msg_lower for g in self.GREETING_KEYWORDS):
            return "greeting"

        # Medical keywords
        if any(k in msg_lower for k in self.MEDICAL_KEYWORDS):
            return "medical_query"

        return "general"


# ── Singletons ─────────────────────────────────────────────────────────────────
rag_pipeline = RAGPipeline()
intent_classifier = IntentClassifier()

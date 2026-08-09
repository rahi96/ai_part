"""
Navelle AI Module — LangChain RAG Pipeline
Embeds user queries, retrieves relevant medical context from Pinecone,
and generates personalised GPT-4 responses.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from ai.config import settings
from ai.utils.bedrock_llm import bedrock_llm
from ai.utils.pinecone_client import pinecone_client

logger = logging.getLogger(__name__)

# ── AI Attribution & Healthcare Disclaimer ─────────────────────────────────────

def get_ai_attribution_header() -> str:
    """Returns the AI model being used for transparency."""
    # Check which LLM is actually being used, not which API key exists
    if bedrock_llm.is_available():
        model = bedrock_llm.get_model()
        if "claude" in model.lower():
            return "🤖 **AI Response** (Powered by Anthropic Claude)"
        else:
            return f"🤖 **AI Response** (Powered by AWS Bedrock: {model})"
    else:
        # Fallback to OpenAI if Bedrock isn't available
        return "🤖 **AI Response** (Powered by OpenAI GPT-4)"


AI_DISCLAIMER = (
    "\n\n---\n"
    "### ⚕️ Important Medical Disclaimer\n\n"
    "**This is an AI-generated response and NOT medical advice.**\n\n"
    "• **AI Model:** {ai_model}\n"
    "• **Medical Sources:** Peer-reviewed research on perimenopause/menopause wellness\n"
    "• **Purpose:** Educational support and general wellness information only\n"
    "• **Not a substitute for:** Professional medical advice, diagnosis, or treatment\n\n"
    "**Always consult your qualified healthcare provider before making health decisions.**\n\n"
    "🚨 **Emergency:** If experiencing severe symptoms or crisis, contact emergency services (911) "
    "or the 988 Suicide & Crisis Lifeline immediately.\n"
    "---"
)

# Legacy simple disclaimer for backwards compatibility
DISCLAIMER = (
    "\n\n---\n"
    "⚕️ *This information is for educational purposes only and is not a substitute "
    "for professional medical advice, diagnosis, or treatment. Always consult your "
    "qualified healthcare provider before making any health decisions.*"
)

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Mennie™, a warm, supportive, and compassionate AI mood-tracking and wellness companion for the Navelle perimenopause support platform.

Your goals:
- Listen first. Reflect the user's feelings and experience back to her warmly before giving any advice or information.
- Use soft, natural, and conversational language. Avoid clinical jargon, cold terminology, or robotic/repetitive phrasing.
- Never judge, minimize, or rush past what she shares. Create a safe, validated space.
- Ask at most one gentle follow-up question at a time to encourage her to share or track her mood.
- Keep responses short and concise (2-4 sentences) to keep the conversation manageable, unless she explicitly asks for detailed information.
- Never diagnose any conditions. If she describes symptoms of depression, anxiety, or other mental health conditions, gently suggest talking to a professional instead of naming a specific diagnosis.
- If she expresses self-harm, suicidal thoughts, or crisis symptoms, respond with deep care and immediately provide crisis resources (e.g., 'If you're in distress, please contact the 988 Suicide & Crisis Lifeline or call emergency services right away. You are not alone.') — do not wait, deflect, or ignore it.
- Avoid generic, repetitive empathetic phrases like 'I understand' or 'I hear you'. Vary your empathy naturally so it feels genuine and unscripted."""


def _build_health_context(health_data: dict) -> str:
    """Summarise the user's health data as a context block for GPT-4."""
    if not health_data:
        return "No health data available for this user."

    user = health_data.get("user", {})
    symptoms = health_data.get("symptoms", [])
    menstrual = health_data.get("menstrual_trackers", [])
    medical = health_data.get("medical_histories", [])

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

    return "\n".join(lines) if lines else "Minimal health data available."


def _build_rag_context(retrieved_docs: list[dict]) -> str:
    """Format retrieved Pinecone documents as a context block."""
    if not retrieved_docs:
        return ""

    lines = ["**Relevant Medical Knowledge:**"]
    for i, doc in enumerate(retrieved_docs, 1):
        lines.append(f"\n[Source {i}: {doc['topic']}]\n{doc['content']}")

    return "\n".join(lines)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline using Pinecone + GPT-4.
    Falls back gracefully if OpenAI or Pinecone is unavailable.
    Includes mandatory AI attribution for app store compliance.
    """

    def __init__(self) -> None:
        self._ready = False

    def _init_client(self) -> bool:
        if self._ready:
            return True
        if not bedrock_llm.is_available():
            logger.warning("Bedrock not available — RAG pipeline unavailable")
            return False
        self._ready = True
        logger.info("RAG pipeline initialised with Bedrock model: %s", bedrock_llm.get_model())
        return True

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
            answer = bedrock_llm.chat_completion(
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )

            sources = [doc["topic"] for doc in (retrieved_docs or [])]

            # Formulate sources section for App Store compliance
            sources_text = ""
            if sources:
                sources_text = "\n\n**Medical Sources Referenced:** " + ", ".join(sources)

            # Estimate confidence from retrieval scores
            if retrieved_docs:
                avg_score = sum(d.get("score", 0) for d in retrieved_docs) / len(retrieved_docs)
                confidence = round(min(avg_score, 1.0), 3)
            else:
                confidence = 0.5  # reasonable baseline for template answers

            # Get AI model info for attribution
            model_name = bedrock_llm.get_model()
            ai_header = get_ai_attribution_header()
            
            # Format disclaimer with actual model info
            disclaimer = AI_DISCLAIMER.format(
                ai_model=model_name if model_name else "AI Language Model"
            )

            # Prepend AI attribution header for transparency
            full_response = f"{ai_header}\\n\\n{answer}{sources_text}{disclaimer}"

            return {
                "response": full_response,
                "sources": sources,
                "model": model_name,
                "confidence": confidence,
                "fallback_used": False,
                "ai_attribution": ai_header,  # Expose for UI display
            }

        except Exception as exc:
            logger.error("Bedrock generation failed: %s", exc)
            return self._generate_general_knowledge_response(
                user_message, health_data, conversation_history, retrieved_docs
            )

    def _generate_general_knowledge_response(
        self,
        user_message: str,
        health_data: dict | None = None,
        conversation_history: list[dict] | None = None,
        retrieved_docs: list[dict] | None = None,
    ) -> dict:
        """
        Generate response using LLM general knowledge when RAG fails.
        This provides helpful answers even without Pinecone context.
        """
        if not self._init_client():
            # Only return error if Bedrock itself is unavailable
            ai_header = "🤖 **System Message**"
            disclaimer = AI_DISCLAIMER.format(ai_model="AI Service Unavailable")
            error_msg = (
                "I'm having trouble connecting to my knowledge base right now. "
                "Please try again in a moment, or contact your healthcare provider "
                "directly for immediate support."
            )
            return {
                "response": f"{ai_header}\\n\\n{error_msg}{disclaimer}",
                "sources": [],
                "model": "unavailable",
                "confidence": 0.0,
                "fallback_used": True,
                "ai_attribution": ai_header,
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
            answer = bedrock_llm.chat_completion(
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )

            sources = [doc["topic"] for doc in (retrieved_docs or [])]
            sources_text = ""
            if sources:
                sources_text = "\n\n**Medical Sources Referenced:** " + ", ".join(sources)

            # Get AI model info for attribution
            model_name = bedrock_llm.get_model()
            ai_header = get_ai_attribution_header()
            
            # Format disclaimer with actual model info
            disclaimer = AI_DISCLAIMER.format(
                ai_model=model_name if model_name else "AI Language Model (General Knowledge Mode)"
            )

            # Prepend AI attribution header for transparency
            full_response = f"{ai_header}\\n\\n{answer}{sources_text}{disclaimer}"

            return {
                "response": full_response,
                "sources": sources,
                "model": model_name,
                "confidence": 0.7,  # Good confidence for general knowledge
                "fallback_used": False,  # This is not a fallback - it's general knowledge mode
                "ai_attribution": ai_header,
            }

        except Exception as exc:
            logger.error("General knowledge generation failed: %s", exc)
            # Last resort: return the generic error
            ai_header = "🤖 **System Message**"
            disclaimer = AI_DISCLAIMER.format(ai_model="AI Service Error")
            error_msg = (
                "I'm having trouble connecting to my knowledge base right now. "
                "Please try again in a moment, or contact your healthcare provider "
                "directly for immediate support."
            )
            return {
                "response": f"{ai_header}\\n\\n{error_msg}{disclaimer}",
                "sources": [],
                "model": "error",
                "confidence": 0.0,
                "fallback_used": True,
                "ai_attribution": ai_header,
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

        # Medical keywords (check first so greetings prefixed to medical queries are not intercepted)
        if any(k in msg_lower for k in self.MEDICAL_KEYWORDS):
            return "medical_query"

        # Greeting — check using word boundaries to avoid matching "hi" inside "history" or "high"
        greeting_pattern = r"\b(" + "|".join(re.escape(g) for g in self.GREETING_KEYWORDS) + r")\b"
        if re.search(greeting_pattern, msg_lower):
            return "greeting"

        # Too vague — needs clarification (only trigger if the message is short and contains triggers, or is extremely short)
        words_count = len(msg_lower.split())
        if words_count <= 4:
            if words_count <= 2 or any(re.search(r"\b" + re.escape(t) + r"\b", msg_lower) for t in self.CLARIFICATION_TRIGGERS):
                return "needs_clarification"

        return "general"


# ── Singletons ─────────────────────────────────────────────────────────────────
rag_pipeline = RAGPipeline()
intent_classifier = IntentClassifier()

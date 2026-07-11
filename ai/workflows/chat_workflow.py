"""
Navelle AI Module — LangGraph Chat Workflow
4-node state machine: classify → respond → disclaimer → thread_check

State:
    user_id, thread_id, message, health_data, intent,
    retrieved_docs, response, confidence, disclaimer_added,
    conversation_history, thread_created_at, response_source
"""
from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from ai.utils.langchain_rag import DISCLAIMER, intent_classifier, rag_pipeline

logger = logging.getLogger(__name__)

# ── Thread store (in-memory, 30-day TTL) ──────────────────────────────────────
# { thread_id: { "created_at": datetime, "history": list[dict] } }
_thread_store: dict[str, dict] = {}
THREAD_TTL_DAYS = 30


def _get_or_create_thread(thread_id: str | None) -> tuple[str, list[dict], bool]:
    """
    Return (thread_id, conversation_history, is_new).
    Cleans up expired threads on every call.
    """
    _cleanup_expired_threads()

    if thread_id and thread_id in _thread_store:
        entry = _thread_store[thread_id]
        return thread_id, entry["history"], False

    # Create new thread
    new_id = thread_id or str(uuid.uuid4())
    _thread_store[new_id] = {
        "created_at": datetime.now(timezone.utc),
        "history": [],
    }
    return new_id, [], True


def _cleanup_expired_threads() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=THREAD_TTL_DAYS)
    expired = [tid for tid, data in _thread_store.items() if data["created_at"] < cutoff]
    for tid in expired:
        del _thread_store[tid]
    if expired:
        logger.info("Cleaned up %d expired threads", len(expired))


def _append_to_thread(thread_id: str, role: str, content: str) -> None:
    if thread_id in _thread_store:
        _thread_store[thread_id]["history"].append({"role": role, "content": content})
        # Keep last 20 turns
        _thread_store[thread_id]["history"] = _thread_store[thread_id]["history"][-20:]


# ── Fallback templates (20 Q&A pairs) ─────────────────────────────────────────
FALLBACK_TEMPLATES: list[dict] = [
    # Greetings
    {
        "intent": "greeting",
        "triggers": ["hello", "hi", "hey", "good morning", "good afternoon"],
        "response": (
            "Hello! 👋 I'm Mennie™, your Navelle wellness companion. "
            "You can ask me about symptoms like hot flashes, sleep, mood, brain fog, "
            "or anything else you're experiencing. What's on your mind today?"
        ),
    },
    # Hot Flashes
    {
        "intent": "hot_flash",
        "triggers": ["hot flash", "hot flush", "sweating", "feel hot", "overheating"],
        "response": (
            "Hot flashes are one of the most common perimenopause symptoms, affecting up to 80% of women. "
            "They're caused by falling estrogen levels confusing your hypothalamus (your body's thermostat). "
            "\n\n**Quick relief strategies:**\n"
            "• Cool your wrists under cold running water\n"
            "• Wear breathable, layered clothing\n"
            "• Keep a small fan nearby\n"
            "• Identify your triggers: caffeine, alcohol, spicy food, and stress are the most common\n\n"
            "If hot flashes are severely affecting your quality of life, HRT (Hormone Replacement Therapy) "
            "reduces them by 75–90% and is safe for most women. Discuss this with your doctor."
        ),
    },
    # Night Sweats
    {
        "intent": "night_sweats",
        "triggers": ["night sweat", "wake up sweating", "drenched at night", "night time sweating"],
        "response": (
            "Night sweats are nocturnal hot flashes and can seriously disrupt your sleep. "
            "\n\n**Tonight's toolkit:**\n"
            "• Set your bedroom to 18–20°C\n"
            "• Use moisture-wicking bamboo sheets\n"
            "• Keep a cold glass of water on your bedside table\n"
            "• Shower with cool water before bed\n"
            "• Avoid alcohol within 3 hours of bedtime — it significantly worsens night sweats\n\n"
            "If they're happening multiple times a night, please speak to your GP — "
            "HRT or other treatments can provide significant relief."
        ),
    },
    # Sleep
    {
        "intent": "sleep",
        "triggers": ["can't sleep", "insomnia", "sleep problem", "not sleeping", "waking up", "poor sleep"],
        "response": (
            "Sleep disruption affects 40–60% of women during perimenopause. "
            "Both estrogen and progesterone help regulate sleep, and as they decline, sleep suffers. "
            "\n\n**Evidence-based strategies:**\n"
            "• Same sleep/wake time every day (even weekends)\n"
            "• No caffeine after 2pm\n"
            "• Cool, dark bedroom (18–20°C)\n"
            "• CBT for Insomnia (CBT-I) has the strongest evidence — ask your GP for a referral\n"
            "• Avoid scrolling devices 1 hour before bed\n\n"
            "If insomnia is severe, your doctor can discuss options including HRT, "
            "which improves sleep by reducing night sweats and restoring progesterone's calming effect."
        ),
    },
    # Mood
    {
        "intent": "mood",
        "triggers": ["mood swing", "irritable", "emotional", "crying", "tearful", "anger", "grumpy"],
        "response": (
            "Mood swings during perimenopause are real and are caused by fluctuating estrogen "
            "affecting serotonin and dopamine pathways in your brain — not a character flaw. "
            "\n\n**What helps:**\n"
            "• Aerobic exercise (even 20 min walking) boosts mood-regulating neurotransmitters\n"
            "• Mindfulness and journalling help identify patterns\n"
            "• Reduce caffeine and alcohol\n"
            "• CBT is highly effective for mood dysregulation\n"
            "• HRT can stabilise hormone fluctuations and significantly improve mood\n\n"
            "If mood swings are affecting relationships or work, please reach out to your doctor. "
            "You deserve support."
        ),
    },
    # Anxiety
    {
        "intent": "anxiety",
        "triggers": ["anxious", "anxiety", "worry", "panic", "panic attack", "nervous", "scared"],
        "response": (
            "Anxiety is one of the most underrecognised symptoms of perimenopause — "
            "many women don't connect it to hormones. The HPA (stress axis) becomes dysregulated "
            "as estrogen declines. You are not 'going mad'. "
            "\n\n**Evidence-based help:**\n"
            "• Diaphragmatic (belly) breathing: in for 4 counts, hold 4, out for 6\n"
            "• Regular exercise is as effective as medication for mild-moderate anxiety\n"
            "• Mindfulness-Based Stress Reduction (MBSR) has strong clinical evidence\n"
            "• Limit caffeine and alcohol — both worsen anxiety\n\n"
            "If anxiety is persistent, speak to your GP. SSRIs, SNRIs, and HRT are all "
            "effective treatment options depending on your circumstances."
        ),
    },
    # Brain Fog
    {
        "intent": "brain_fog",
        "triggers": ["brain fog", "memory", "forget", "concentration", "focus", "can't think", "confused"],
        "response": (
            "Brain fog — difficulty concentrating, word-finding problems, and memory lapses — "
            "peaks during the menopausal transition and improves for most women afterwards. "
            "It's caused by hormonal changes, sleep disruption, and anxiety all interacting. "
            "\n\n**Strategies that work:**\n"
            "• Aerobic exercise increases BDNF (brain growth factor) and measurably improves memory\n"
            "• Omega-3 fatty acids (1–2g EPA/DHA daily) — oily fish or supplements\n"
            "• Mediterranean diet (leafy greens, berries, olive oil)\n"
            "• Write things down — it's not weakness, it's strategy\n"
            "• Prioritise sleep above all else\n\n"
            "HRT can also significantly improve cognitive symptoms — worth discussing with your doctor."
        ),
    },
    # Weight
    {
        "intent": "weight",
        "triggers": ["weight gain", "putting on weight", "belly fat", "metabolism", "can't lose weight"],
        "response": (
            "Weight changes during perimenopause are driven by hormonal shifts — especially "
            "estrogen's declining effect on fat distribution, which moves fat to the abdomen. "
            "Metabolic rate also slows. This is biology, not failure. "
            "\n\n**What actually works:**\n"
            "• Strength/resistance training 2–3x per week — builds muscle and raises metabolic rate\n"
            "• 150 min moderate cardio per week\n"
            "• Protein: 1.2–1.6g per kg of body weight preserves muscle\n"
            "• Reduce refined carbs and ultra-processed foods\n"
            "• Alcohol significantly worsens weight gain — worth cutting back\n\n"
            "A registered dietitian can help create a personalised plan."
        ),
    },
    # Joint Pain
    {
        "intent": "joint_pain",
        "triggers": ["joint pain", "aches", "stiffness", "joints hurt", "arthritis", "achy"],
        "response": (
            "Joint pain (arthralgia) affects up to 60% of perimenopausal women. "
            "Estrogen has anti-inflammatory properties, so as it declines, joints become more sensitive. "
            "\n\n**Relief strategies:**\n"
            "• Low-impact exercise: swimming, cycling, yoga — maintains mobility without strain\n"
            "• Anti-inflammatory foods: oily fish, turmeric, berries, olive oil\n"
            "• Strength training: builds muscle that supports and protects joints\n"
            "• HRT can reduce arthralgia in some women\n\n"
            "If joint pain is severe or asymmetric, please see your doctor to rule out "
            "rheumatoid arthritis or other conditions."
        ),
    },
    # Fatigue
    {
        "intent": "fatigue",
        "triggers": ["fatigue", "exhausted", "tired", "no energy", "worn out", "drained"],
        "response": (
            "Perimenopausal fatigue is multi-layered: sleep disruption, hormonal changes, "
            "possible anaemia, thyroid issues, and depression can all contribute. "
            "\n\n**First steps:**\n"
            "• Ask your GP to check: full blood count (anaemia), thyroid, ferritin, vitamin D, B12\n"
            "• Treat the root cause — iron deficiency or thyroid issues have simple fixes\n"
            "• Aerobic exercise paradoxically reduces fatigue — start with 10-minute walks\n"
            "• Protect sleep ruthlessly\n"
            "• HRT improves energy for many women\n\n"
            "Don't just push through — get checked."
        ),
    },
    # HRT Questions
    {
        "intent": "hrt",
        "triggers": ["hrt", "hormone replacement", "hormones", "should i take hrt", "is hrt safe"],
        "response": (
            "HRT (Hormone Replacement Therapy) is the most effective treatment for most perimenopausal symptoms. "
            "Modern guidelines (NICE 2023, BMS, IMS) support HRT for most healthy women. "
            "\n\n**Key facts:**\n"
            "• Reduces hot flashes by 75–90%\n"
            "• Improves sleep, mood, energy, and cognitive function\n"
            "• Protects bones and reduces cardiovascular risk when started before 60\n"
            "• Transdermal (patch/gel) carries lower clot risk than oral tablets\n"
            "• Small breast cancer risk with combined HRT after 5+ years — similar to drinking 1–2 units of alcohol daily\n\n"
            "The old 2002 WHI study significantly overstated risks. Current evidence is much more reassuring. "
            "Request a menopause specialist appointment to discuss your individual situation."
        ),
    },
    # Periods / Menstrual
    {
        "intent": "periods",
        "triggers": ["period", "cycle", "menstrual", "irregular", "missed period", "no period", "spotting"],
        "response": (
            "Irregular periods are the hallmark sign of perimenopause. Cycles may become shorter or longer, "
            "flow heavier or lighter, and periods may be skipped altogether. This is normal. "
            "\n\n**Important notes:**\n"
            "• Pregnancy is still possible until 12 months after your last period — use contraception if needed\n"
            "• Track your cycles in an app or diary — patterns help your doctor\n"
            "• Heavy bleeding (soaking a pad per hour, or clots larger than a 50p coin) warrants a GP visit\n"
            "• Bleeding between periods or after sex should always be checked\n\n"
            "Menopause is confirmed when you've had no period for 12 consecutive months."
        ),
    },
    # Needs Clarification
    {
        "intent": "needs_clarification",
        "triggers": [],  # matched by classifier
        "response": (
            "I'm here to help with your perimenopause journey! 💜 "
            "To give you the most useful information, could you tell me a bit more? "
            "\n\nFor example, are you experiencing:\n"
            "• Hot flashes or night sweats?\n"
            "• Mood changes or anxiety?\n"
            "• Sleep problems?\n"
            "• Brain fog or memory issues?\n"
            "• Weight changes?\n"
            "• Something else?\n\n"
            "The more you share, the better I can support you."
        ),
    },
    # General
    {
        "intent": "general",
        "triggers": [],
        "response": (
            "That's a great question! While I specialise in perimenopause wellness, "
            "I'll do my best to help. Could you share a bit more about what you're experiencing? "
            "I'm here to listen and support you. 💙"
        ),
    },
]


def _get_fallback_response(intent: str, message: str) -> str:
    """Pick the best matching fallback template."""
    msg_lower = message.lower()

    # Keyword-based match first
    for tmpl in FALLBACK_TEMPLATES:
        if any(trigger in msg_lower for trigger in tmpl.get("triggers", [])):
            return tmpl["response"]

    # Intent-based match
    for tmpl in FALLBACK_TEMPLATES:
        if tmpl["intent"] == intent:
            return tmpl["response"]

    # Default
    return FALLBACK_TEMPLATES[-1]["response"]


# ── LangGraph State ────────────────────────────────────────────────────────────

class ChatState(TypedDict):
    user_id: str
    thread_id: str
    message: str
    health_data: dict
    intent: str
    retrieved_docs: list[dict]
    response: str
    confidence: float
    response_source: str  # "general_knowledge" | "template" | "clarification" | "greeting"
    disclaimer_added: bool
    conversation_history: list[dict]
    thread_created_at: str
    is_new_thread: bool


# ── Node 1: Classify Intent ────────────────────────────────────────────────────

def node_classify_intent(state: ChatState) -> ChatState:
    """Classify the user's message intent."""
    intent = intent_classifier.classify(state["message"])
    logger.debug("Intent classified: %s for message: %s", intent, state["message"][:50])
    return {**state, "intent": intent}


# ── Node 2: Generate Response ──────────────────────────────────────────────────

def node_generate_response(state: ChatState) -> ChatState:
    """Route to RAG or fallback template based on intent."""
    intent = state["intent"]
    message = state["message"]
    health_data = state.get("health_data", {})
    history = state.get("conversation_history", [])

    if intent == "medical_query":
        # Use LLM general knowledge for medical queries
        # (No Pinecone RAG - simplified architecture)
        result = rag_pipeline.generate(
            user_message=message,
            health_data=health_data,
            retrieved_docs=[],  # No RAG
            conversation_history=history,
        )

        return {
            **state,
            "retrieved_docs": [],
            "response": result["response"],
            "confidence": result["confidence"],
            "response_source": "general_knowledge",
        }

    elif intent in ("needs_clarification",):
        response = _get_fallback_response("needs_clarification", message)
        return {
            **state,
            "retrieved_docs": [],
            "response": response,
            "confidence": 1.0,
            "response_source": "clarification",
        }

    elif intent == "greeting":
        response = _get_fallback_response("greeting", message)
        return {
            **state,
            "retrieved_docs": [],
            "response": response,
            "confidence": 1.0,
            "response_source": "greeting",
        }

    else:
        # General — try keyword fallback
        response = _get_fallback_response(intent, message)
        return {
            **state,
            "retrieved_docs": [],
            "response": response,
            "confidence": 0.8,
            "response_source": "template",
        }


# ── Node 3: Inject Disclaimer ──────────────────────────────────────────────────

def node_inject_disclaimer(state: ChatState) -> ChatState:
    """Ensure healthcare disclaimer is present in every response."""
    response = state["response"]
    # Only add if not already present (RAG pipeline adds it, templates don't)
    if DISCLAIMER.strip() not in response:
        response = response + DISCLAIMER
    return {**state, "response": response, "disclaimer_added": True}


# ── Node 4: Thread Expiry Check ────────────────────────────────────────────────

def node_check_thread(state: ChatState) -> ChatState:
    """Update conversation history and check thread health."""
    thread_id = state["thread_id"]
    message = state["message"]
    response = state["response"]

    # Append this turn to thread history
    _append_to_thread(thread_id, "user", message)
    _append_to_thread(thread_id, "assistant", response)

    return state


# ── Build the Graph ────────────────────────────────────────────────────────────

def _build_graph() -> Any:
    graph = StateGraph(ChatState)

    graph.add_node("classify_intent", node_classify_intent)
    graph.add_node("generate_response", node_generate_response)
    graph.add_node("inject_disclaimer", node_inject_disclaimer)
    graph.add_node("check_thread", node_check_thread)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "generate_response")
    graph.add_edge("generate_response", "inject_disclaimer")
    graph.add_edge("inject_disclaimer", "check_thread")
    graph.add_edge("check_thread", END)

    return graph.compile()


_chat_graph = _build_graph()


# ── Public Entry Point ─────────────────────────────────────────────────────────

async def run_chat_workflow(
    user_id: str,
    message: str,
    health_data: dict | None = None,
    thread_id: str | None = None,
) -> dict:
    """
    Execute the full chat workflow.

    Returns:
        {
            "response": str,
            "thread_id": str,
            "intent": str,
            "confidence": float,
            "sources": list[str],
            "response_source": str,
            "is_new_thread": bool,
        }
    """
    # Resolve thread
    resolved_thread_id, history, is_new = _get_or_create_thread(thread_id)

    initial_state: ChatState = {
        "user_id": user_id,
        "thread_id": resolved_thread_id,
        "message": message,
        "health_data": health_data or {},
        "intent": "",
        "retrieved_docs": [],
        "response": "",
        "confidence": 0.0,
        "response_source": "",
        "disclaimer_added": False,
        "conversation_history": history,
        "thread_created_at": datetime.now(timezone.utc).isoformat(),
        "is_new_thread": is_new,
    }

    try:
        final_state = await _chat_graph.ainvoke(initial_state)
    except Exception as exc:
        logger.error("Chat workflow failed: %s", exc)
        # Safe fallback
        return {
            "response": (
                "I'm sorry, I encountered an unexpected error. "
                "Please try again or contact support." + DISCLAIMER
            ),
            "thread_id": resolved_thread_id,
            "intent": "error",
            "confidence": 0.0,
            "sources": [],
            "response_source": "error",
            "is_new_thread": is_new,
        }

    return {
        "response": final_state["response"],
        "thread_id": resolved_thread_id,
        "intent": final_state["intent"],
        "confidence": final_state["confidence"],
        "sources": [d["topic"] for d in final_state.get("retrieved_docs", [])],
        "response_source": final_state["response_source"],
        "is_new_thread": is_new,
    }

"""
Navelle AI Module — Wellness Service
Stateless mood check-in and humor tips — no database required.
"""
from __future__ import annotations

import logging
import random
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── Mood options ───────────────────────────────────────────────────────────────
VALID_MOODS = ["great", "good", "okay", "low", "awful"]

MOOD_MESSAGES: dict[str, str] = {
    "great": "🌟 That's wonderful! Keep up whatever you're doing.",
    "good": "😊 Good to hear! Small wins matter — well done.",
    "okay": "🙂 Okay is perfectly fine. Take it one step at a time.",
    "low": "💙 Sorry to hear you're feeling low. Be gentle with yourself today.",
    "awful": "💜 I'm really sorry. Please reach out to someone you trust, or contact your healthcare provider.",
}

# ── Humor library ─────────────────────────────────────────────────────────────
HUMOR_TIPS: list[dict] = [
    {
        "joke": "Why did the hot flash cross the road? To get to the other side — where there's air conditioning! 😂",
        "tip": "Cooling your wrists under cold water can quickly reduce the sensation of a hot flash.",
    },
    {
        "joke": "I'm not 'forgetting things' — I'm operating on a selective memory upgrade. 🧠✨",
        "tip": "Brain fog is real. Try the 'name it to tame it' technique: speak your tasks aloud to anchor them.",
    },
    {
        "joke": "My thermostat and I have a complicated relationship. I say cold, it says hot. 🌡️",
        "tip": "Keep a small portable fan at your desk. A drop of peppermint oil on a handkerchief can also help.",
    },
    {
        "joke": "Perimenopause: when you can go from a cardigan to a bikini in under 30 seconds. 🏖️",
        "tip": "Layering lightweight, breathable fabrics gives you fast temperature control throughout the day.",
    },
    {
        "joke": "Night sweats: nature's way of reminding you that you're HOT — literally! 🔥",
        "tip": "A cooling mattress pad and moisture-wicking sheets can dramatically improve sleep quality.",
    },
    {
        "joke": "Why do I need a mood ring? I am the mood ring. 💍",
        "tip": "Tracking mood patterns alongside your cycle can reveal hormonal connections you can share with your doctor.",
    },
    {
        "joke": "My brain has too many tabs open and the WiFi is down. 📡",
        "tip": "The Pomodoro technique — 25 minutes of focus, 5-minute breaks — is clinically shown to help with concentration.",
    },
    {
        "joke": "Perimenopause is like a software update you didn't ask for. Restarting now… please wait. 💻",
        "tip": "Regular aerobic exercise (even 20 minutes of walking) significantly reduces cognitive symptoms.",
    },
    {
        "joke": "Hot flash? More like a surprise preview of the Sahara desert. 🌵",
        "tip": "Identify your personal triggers: alcohol, spicy food, stress, and caffeine are the most common culprits.",
    },
    {
        "joke": "I'm not moody — I'm a multidimensional emotional experience. ✨",
        "tip": "Journalling for 5 minutes daily has been shown to reduce anxiety and help you spot emotional patterns.",
    },
    {
        "joke": "Asked my doctor about memory loss. She said it's normal. I forgot what I asked about. 🤷‍♀️",
        "tip": "Writing lists is not a weakness — it's a smart cognitive strategy used by neuroscientists worldwide.",
    },
    {
        "joke": "Sleep? I remember that. We used to be close. 😴",
        "tip": "Going to bed and waking at the same time every day — even weekends — is the single best sleep hygiene habit.",
    },
]


class WellnessService:
    """Stateless wellness interactions."""

    def select_mood(self, user_id: str, mood: str) -> dict:
        """
        Record a mood check-in. Stateless — returns an immediate personalised response.
        """
        mood_lower = mood.lower().strip()
        if mood_lower not in VALID_MOODS:
            return {
                "success": False,
                "message": f"Invalid mood. Choose from: {', '.join(VALID_MOODS)}",
                "user_id": user_id,
                "mood": mood,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        message = MOOD_MESSAGES[mood_lower]
        return {
            "success": True,
            "user_id": user_id,
            "mood": mood_lower,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_humor_break(self, user_id: str) -> dict:
        """
        Return a random perimenopause-themed joke + wellness tip.
        """
        pick = random.choice(HUMOR_TIPS)
        return {
            "user_id": user_id,
            "joke": pick["joke"],
            "wellness_tip": pick["tip"],
            "disclaimer": "Remember: laughter is good medicine, but always consult your healthcare provider for medical advice. 💜",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

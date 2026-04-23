from __future__ import annotations
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from ai.config import settings
from ai.utils.helpers import calculate_percentage_change, format_date_range

logger = logging.getLogger(__name__)

# ── Severity mapping (1-10 scale) ─────────────────────────────────────────────
SEVERITY_LABELS = {
    range(1, 4): "mild",
    range(4, 7): "moderate",
    range(7, 11): "severe",
}


def _severity_label(level: int) -> str:
    for r, label in SEVERITY_LABELS.items():
        if level in r:
            return label
    return "unknown"


def _parse_dt(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


class AnalysisService:
    """Business logic for symptom analysis — database-free."""

    # ── Wellness Dashboard ─────────────────────────────────────────────────────

    def get_wellness_dashboard(self, user_id: str, health_data: dict) -> dict:
        """
        Return AI-generated overall wellness score (1-100) and
        data-driven average symptom severity.
        """
        symptoms: list[dict] = health_data.get("symptoms", [])
        menstrual: list[dict] = health_data.get("menstrual_trackers", [])
        medical: list[dict] = health_data.get("medical_histories", [])
        labs: list[dict] = health_data.get("lab_histories", [])
        user: dict = health_data.get("user", {})

        total_logs = len(symptoms)
        avg_severity = (
            round(sum(s.get("severity_level", 0) for s in symptoms) / total_logs, 1)
            if total_logs
            else 0.0
        )

        score, _ = self._generate_wellness_score(
            user, symptoms, menstrual, medical, labs, total_logs, avg_severity
        )

        return {
            "overall_wellness_score": score,
            "average_severity": avg_severity,
        }

    # ── Symptom Trend ──────────────────────────────────────────────────────────

    def get_symptom_trend(self, user_id: str, health_data: dict, days: int = 30) -> dict:
        """
        Return daily symptom severity averages over the requested window.
        """
        symptoms: list[dict] = health_data.get("symptoms", [])

        # Group by date
        daily: dict[str, list[int]] = defaultdict(list)
        for s in symptoms:
            ts = _parse_dt(s.get("timestamp"))
            if ts:
                date_key = ts.strftime("%Y-%m-%d")
                daily[date_key].append(s.get("severity_level", 0))

        trend = [
            {
                "date": date,
                "average_severity": round(sum(lvls) / len(lvls), 1),
                "log_count": len(lvls),
            }
            for date, lvls in sorted(daily.items())
        ]

        # Week-over-week change
        if len(trend) >= 14:
            prev_avg = sum(t["average_severity"] for t in trend[-14:-7]) / 7
            curr_avg = sum(t["average_severity"] for t in trend[-7:]) / 7
            change = calculate_percentage_change(prev_avg, curr_avg)
        else:
            change = 0.0

        return {
            "user_id": user_id,
            "days_window": days,
            "trend": trend,
            "week_over_week_change_pct": change,
            "total_logs": len(symptoms),
        }

    # ── Symptom Intensity Trend ───────────────────────────────────────────────

    def generate_symptom_intensity_trend(self, user_id: str, health_data: dict, days: int = 7) -> list[dict]:
        """
        Generate AI-powered symptom intensity scores for charting.
        Returns ONLY a list of intensity values (0-10), nothing else.
        """
        symptoms: list[dict] = health_data.get("symptoms", [])
        medical: list[dict] = health_data.get("medical_histories", [])
        user: dict = health_data.get("user", {})

        # Compute daily average severity from real data
        daily: dict[str, list[int]] = defaultdict(list)
        for s in symptoms:
            ts = _parse_dt(s.get("timestamp"))
            if ts:
                date_key = ts.strftime("%Y-%m-%d")
                daily[date_key].append(s.get("severity_level", 0))

        sorted_dates = sorted(daily.keys())
        recent_dates = sorted_dates[-days:] if len(sorted_dates) > days else sorted_dates

        real_trend = [
            {
                "day_name": _parse_dt(date).strftime("%a") if _parse_dt(date) else date,
                "intensity": round(sum(daily[date]) / len(daily[date]), 1),
            }
            for date in recent_dates
        ]

        # Build prompt
        lines = [
            f"User: {user.get('name', 'there')}",
            f"Return exactly {len(real_trend)} intensity scores (0-10 scale), one per day.",
            "",
            "Real daily averages:",
        ]
        for point in real_trend:
            lines.append(f"  {point['day_name']}: {point['intensity']}/10")

        if medical:
            lines.append("\nMedications:")
            for m in medical[-3:]:
                lines.append(f"  - {m.get('condition', 'unknown')}: {m.get('medication', 'N/A')}")

        lines.append("\nReturn ONLY a JSON array of numbers. No keys, no objects, no commentary.")
        lines.append('Example: [3.2, 4.5, 5.1, 2.8, 3.9, 4.2, 3.5]')

        prompt = "\n".join(lines)

        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a health data engine. Return ONLY a JSON array of decimal numbers. No extra text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.2,
        )

        import json
        raw = response.choices[0].message.content or "[]"
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0]

        try:
            scores = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            scores = [p["intensity"] for p in real_trend]

        # Ensure correct length and clamp to 0-10
        if not isinstance(scores, list):
            scores = [p["intensity"] for p in real_trend]

        result = []
        for i in range(min(len(real_trend), len(scores))):
            val = float(scores[i]) if isinstance(scores[i], (int, float, str)) else real_trend[i]["intensity"]
            result.append({"intensity": round(max(0.0, min(10.0, val)), 1)})

        # Pad if AI returned fewer values
        while len(result) < len(real_trend):
            result.append({"intensity": real_trend[len(result)]["intensity"]})

        return result

    # ── Top Symptoms ───────────────────────────────────────────────────────────

    def get_top_symptoms(self, user_id: str, health_data: dict, limit: int = 5) -> list[dict]:
       
        symptoms: list[dict] = health_data.get("symptoms", [])

        grouped: dict[str, list[int]] = defaultdict(list)
        for s in symptoms:
            name = s.get("symptom_name", "UNKNOWN")
            grouped[name].append(s.get("severity_level", 0))

        result = []
        for name, levels in sorted(grouped.items(), key=lambda x: -len(x[1])):
            avg_sev = round(sum(levels) / len(levels), 1) if levels else 0.0
            result.append(
                {
                    "symptom_name": name,
                    "frequency": len(levels),
                    "average_severity": avg_sev,
                    "severity_label": _severity_label(int(avg_sev)),
                    "max_severity": max(levels) if levels else 0,
                }
            )

        return result[:limit]

    # ── Trigger Warnings ──────────────────────────────────────────────────────

    def generate_trigger_tip(self, user_id: str, health_data: dict) -> str:
        user = health_data.get("user", {})
        symptoms = health_data.get("symptoms", [])
        menstrual = health_data.get("menstrual_trackers", [])
        medical = health_data.get("medical_histories", [])
        labs = health_data.get("lab_histories", [])

        prompt_parts = [
            "You are Mennie, a warm and knowledgeable perimenopause wellness companion.",
            "Look at the user's health data below and generate ONE short, personalized observation with a single actionable tip.",
            "Use the user's name. Be conversational, warm, and evidence-based. Keep it to 1-2 sentences max.",
            "Example tone: 'Sarah, I noticed your sleep quality dips on nights you log high caffeine intake after 3 PM. Reducing this might help with those early waking episodes.'",
            "",
            "User Data:",
            f"Name: {user.get('name', 'there')}",
        ]

        if symptoms:
            symptom_lines = [f"- {s.get('symptom_name')}: severity {s.get('severity_level')}/10 on {s.get('timestamp', 'unknown date')}" for s in symptoms[-10:]]
            prompt_parts.append("Recent symptoms:")
            prompt_parts.extend(symptom_lines)

        if menstrual:
            m = menstrual[-1]
            prompt_parts.append(f"Last cycle: {m.get('start_date')} to {m.get('end_date')}, flow: {m.get('flow_intensity')}, variation: {m.get('variation')}")

        if medical:
            prompt_parts.append(f"Medical conditions: {', '.join(m.get('condition', 'unknown') for m in medical)}")

        if labs:
            lab_notes = [l.get('notes', '') for l in labs if l.get('notes')]
            if lab_notes:
                prompt_parts.append(f"Recent lab notes: {'; '.join(lab_notes)}")

        prompt_parts.append("")
        prompt_parts.append("Now write the short personalized tip:")

        prompt = "\n".join(prompt_parts)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a concise, warm perimenopause wellness assistant. Write exactly one short personalized tip (1-2 sentences)."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )
            tip = response.choices[0].message.content or ""
            return tip.strip()
        except Exception as exc:
            logger.error("OpenAI failed for user %s, using data-driven fallback: %s", user_id, exc)
            return self._generate_fallback_tip(user, symptoms, menstrual, medical, labs)

    def generate_top_symptom_analysis(self, user_id: str, health_data: dict) -> list[dict]:
        symptoms: list[dict] = health_data.get("symptoms", [])
        if not symptoms:
            return []

        # Compute per-symptom week-over-week stats for the prompt
        now = datetime.now(timezone.utc)
        def _week_of(ts_str):
            ts = _parse_dt(ts_str)
            if not ts:
                return None
            return (now - ts).days // 7

        grouped: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
        for s in symptoms:
            w = _week_of(s.get("timestamp"))
            if w is not None:
                name = s.get("symptom_name", "UNKNOWN")
                grouped[name][str(w)].append(s.get("severity_level", 0))

        symptom_stats = []
        for name, weeks in grouped.items():
            avg_by_week = {w: round(sum(v)/len(v), 2) for w, v in weeks.items()}
            this_week = avg_by_week.get("0", None)
            last_week = avg_by_week.get("1", None)
            if this_week is not None and last_week is not None:
                change = round(calculate_percentage_change(last_week, this_week), 1)
            else:
                change = None
            symptom_stats.append({
                "name": name,
                "total_logs": sum(len(v) for v in weeks.values()),
                "this_week_avg": this_week,
                "last_week_avg": last_week,
                "change_pct": change,
                "max_severity": max((max(v) for v in weeks.values()), default=0),
            })

        symptom_stats.sort(key=lambda x: (-x["total_logs"], -x.get("max_severity", 0)))

        # Build prompt
        prompt_lines = [
            "You are Mennie, a perimenopause wellness data analyst.",
            "Based on the user's symptom tracking data below, identify the TOP 3 most impactful symptoms.",
            "For each symptom, decide:",
            "  - trend: 'IMPROVEMENT FROM LAST WEEK' if change_pct < 0, otherwise 'WORSENING'",
            "  - change_pct: the percentage change from last week to this week",
            "Return ONLY valid JSON in this exact format (no markdown, no commentary):",
            "",
            '[{"rank": 1, "name": "...", "trend": "IMPROVEMENT FROM LAST WEEK", "change_pct": -15}, '
            '{"rank": 2, "name": "...", "trend": "WORSENING", "change_pct": 5}, '
            '{"rank": 3, "name": "...", "trend": "IMPROVEMENT FROM LAST WEEK", "change_pct": -22}]',
            "",
            "Symptom data:",
        ]
        for s in symptom_stats:
            prompt_lines.append(f"  {s['name']}: {s['total_logs']} logs, this_week_avg={s['this_week_avg']}, last_week_avg={s['last_week_avg']}, change_pct={s['change_pct']}, max_severity={s['max_severity']}")

        prompt = "\n".join(prompt_lines)

        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a health data analyst. Return ONLY the requested JSON array. No extra text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
            temperature=0.3,
        )
        raw = response.choices[0].message.content or "[]"
        import json
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0]
        result = json.loads(cleaned.strip())
        # Ensure rank field
        for i, item in enumerate(result):
            item["rank"] = i + 1
        return result[:3]

    def generate_humor_break(self, user_id: str, health_data: dict) -> dict:
        name = health_data.get("user", {}).get("name", "there")
        symptoms = health_data.get("symptoms", [])
        recent_symptom = symptoms[-1].get("symptom_name", "symptoms") if symptoms else "perimenopause"

        prompt = (
            f"You are Mennie, a witty and warm perimenopause wellness companion. "
            f"Write a short, funny 'Humor Break' for {name} about {recent_symptom.lower()}. "
            f"Format exactly like this with no extra commentary:\n\n"
            f"Quote: <one funny perimenopause-themed one-liner (1-2 sentences)>\n"
            f"Suggested: <one gentle self-care suggestion (1 sentence)>"
        )

        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a warm, witty perimenopause wellness companion. Keep responses very short and fun."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
            temperature=0.9,
        )
        content = response.choices[0].message.content or ""
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        quote = next((l.replace("Quote:", "").strip() for l in lines if l.startswith("Quote:")), lines[0] if lines else "")
        suggested = next((l.replace("Suggested:", "").strip() for l in lines if l.startswith("Suggested:")), lines[-1] if len(lines) > 1 else "Treat yourself to a little self-care today!")
        return {"quote": quote, "suggested": suggested}

    def _generate_wellness_score(
        self,
        user: dict,
        symptoms: list,
        menstrual: list,
        medical: list,
        labs: list,
        total_logs: int,
        avg_severity: float,
    ) -> tuple[int, str]:
        """
        Call OpenAI to generate an overall wellness score (1-100) and a brief
        reason based on the user's complete health overview.
        Returns (score, reason).
        """
        lines = [
            f"Name: {user.get('name', 'there')}",
            f"Total symptom logs (last 30 days): {total_logs}",
            f"Average symptom severity (1-10): {avg_severity}",
        ]

        if symptoms:
            lines.append(f"Recent symptoms ({len(symptoms)}):")
            for s in symptoms[-5:]:
                lines.append(f"  - {s.get('symptom_name')}: severity {s.get('severity_level')}/10")
        if medical:
            lines.append(f"Medical conditions: {', '.join(m.get('condition', 'unknown') for m in medical)}")
        if menstrual:
            m = menstrual[-1]
            lines.append(f"Last cycle: {m.get('start_date')} to {m.get('end_date')}, flow {m.get('flow_intensity')}")
        if labs:
            lab_notes = [l.get('notes', '') for l in labs if l.get('notes')]
            if lab_notes:
                lines.append(f"Recent lab notes: {'; '.join(lab_notes)}")

        prompt = (
            "You are a perimenopause wellness scoring engine. "
            "Analyze the user's health summary below and produce ONLY a score and a 1-sentence reason in this exact format:\n\n"
            "Score: <integer 1-100>\n"
            "Reason: <1 sentence explaining why, warm and encouraging tone>\n\n"
            "Higher score = better overall wellness. Consider symptom severity, frequency, medical history, cycle regularity, and engagement.\n\n"
            "User Summary:\n"
        ) + "\n".join(lines)

        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a concise health scoring engine. Return ONLY 'Score: N' and 'Reason: ...' on separate lines. No extra text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=80,
            temperature=0.3,
        )
        content = response.choices[0].message.content or ""
        score = 50
        reason = "Tracking data is being analyzed for personalized insights."
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("Score:"):
                try:
                    score = int(line.replace("Score:", "").strip().split()[0])
                    score = max(1, min(100, score))
                except (ValueError, IndexError):
                    pass
            elif line.startswith("Reason:"):
                reason = line.replace("Reason:", "").strip() or reason
        return score, reason

    def _generate_fallback_tip(self, user: dict, symptoms: list, menstrual: list, medical: list, labs: list) -> str:
        name = user.get("name", "there")

        if symptoms:
            high_sev = [s for s in symptoms if s.get("severity_level", 0) >= 7]
            if high_sev:
                s = high_sev[-1]
                return f"Hi {name}, I see you've logged {s.get('symptom_name', 'a symptom')} at severity {s.get('severity_level')}/10 recently. Tracking patterns and discussing severe symptoms with your doctor can really help."
            recent = symptoms[-1]
            return f"Hi {name}, I noticed your recent {recent.get('symptom_name', 'symptom')} log. Keep tracking your symptoms daily — it helps identify patterns and triggers over time."

        if medical:
            conditions = [m.get("condition", "") for m in medical if m.get("condition")]
            if conditions:
                return f"Hi {name}, I see you have {conditions[0]} in your medical history. Staying consistent with your care plan and logging any new symptoms will help us support you better."

        if menstrual:
            return f"Hi {name}, tracking your cycle regularly is great. If you notice any big changes in flow or timing, keep logging them — they can reveal important patterns."

        if labs:
            return f"Hi {name}, your lab results are on file. Reviewing them with your doctor periodically helps keep your wellness plan up to date."

        return f"Hi {name}, I'm here to support your perimenopause journey. Start logging your symptoms daily so I can spot patterns and offer personalized tips."

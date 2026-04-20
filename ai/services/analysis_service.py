"""
Navelle AI Module — Analysis Service
Works with health_data dict fetched from the backend REST API.

health_data shape:
    {
        "user": { user_id, name, email, dob, health_condition },
        "symptoms": [{ _id, symptom_name, severity_level, timestamp, notes }],
        "menstrual_trackers": [{ _id, start_date, end_date, flow_intensity, variation, timestamp }],
        "medical_histories": [{ _id, condition, category, date_diagnosed, notes }],
        "lab_histories": [],
        "chat_messages": []
    }
"""
from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

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
        Build a wellness dashboard summary from real backend data.
        """
        symptoms: list[dict] = health_data.get("symptoms", [])
        menstrual: list[dict] = health_data.get("menstrual_trackers", [])
        user: dict = health_data.get("user", {})

        total_logs = len(symptoms)
        avg_severity = (
            round(sum(s.get("severity_level", 0) for s in symptoms) / total_logs, 1)
            if total_logs
            else 0.0
        )

        # Most common symptom
        if symptoms:
            counter = Counter(s.get("symptom_name", "UNKNOWN") for s in symptoms)
            most_common_symptom, most_common_count = counter.most_common(1)[0]
        else:
            most_common_symptom = "None logged"
            most_common_count = 0

        # Last menstrual cycle
        last_cycle = None
        if menstrual:
            sorted_cycles = sorted(
                menstrual,
                key=lambda m: _parse_dt(m.get("start_date")) or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )
            c = sorted_cycles[0]
            start = _parse_dt(c.get("start_date"))
            end = _parse_dt(c.get("end_date"))
            last_cycle = {
                "start_date": c.get("start_date"),
                "end_date": c.get("end_date"),
                "flow_intensity": c.get("flow_intensity", "UNKNOWN"),
                "variation": c.get("variation"),
                "duration_days": (end - start).days if start and end else None,
            }

        return {
            "user_id": user_id,
            "user_name": user.get("name", ""),
            "health_condition": user.get("health_condition", "NONE"),
            "total_symptom_logs": total_logs,
            "average_severity": avg_severity,
            "most_common_symptom": most_common_symptom,
            "most_common_count": most_common_count,
            "last_menstrual_cycle": last_cycle,
            "total_menstrual_logs": len(menstrual),
            "medical_conditions": [
                m.get("condition") for m in health_data.get("medical_histories", [])
            ],
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

    # ── Top Symptoms ───────────────────────────────────────────────────────────

    def get_top_symptoms(self, user_id: str, health_data: dict, limit: int = 5) -> list[dict]:
        """
        Return the most frequently logged symptoms with severity stats.
        """
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

    def get_trigger_warnings(self, user_id: str, health_data: dict) -> list[dict]:
        """
        Identify high-severity or frequently recurring symptoms that need attention.
        """
        symptoms: list[dict] = health_data.get("symptoms", [])
        warnings = []

        grouped: dict[str, list[dict]] = defaultdict(list)
        for s in symptoms:
            grouped[s.get("symptom_name", "UNKNOWN")].append(s)

        for name, entries in grouped.items():
            avg_sev = sum(e.get("severity_level", 0) for e in entries) / len(entries)
            max_sev = max(e.get("severity_level", 0) for e in entries)
            freq = len(entries)

            # Trigger: high severity OR frequent occurrence
            if max_sev >= 7 or freq >= 5:
                level = "high" if max_sev >= 7 else "moderate"
                warnings.append(
                    {
                        "symptom_name": name,
                        "warning_level": level,
                        "frequency": freq,
                        "average_severity": round(avg_sev, 1),
                        "max_severity": max_sev,
                        "recommendation": _get_recommendation(name, level),
                    }
                )

        return sorted(warnings, key=lambda w: -w["max_severity"])


def _get_recommendation(symptom: str, level: str) -> str:
    """Return a short evidence-based recommendation for a symptom trigger."""
    recs: dict[str, str] = {
        "HOT_FLASHES": "Consider keeping a trigger diary. Avoiding caffeine, alcohol, and spicy foods can reduce frequency.",
        "MENTAL_FOG": "Prioritise sleep hygiene and aerobic exercise. Omega-3 supplementation may help — consult your doctor.",
        "NIGHT_SWEATS": "Keep your bedroom cool (18–20°C), wear moisture-wicking fabrics, and discuss HRT options with your GP.",
        "MOOD_SWINGS": "Mindfulness, CBT, and regular physical activity are first-line approaches. Discuss with a mental health professional.",
        "SLEEP_DISTURBANCES": "Practice consistent sleep schedules and limit screen time. CBT-I has strong evidence for menopausal insomnia.",
        "ANXIETY": "Breathing exercises and structured physical activity are well-evidenced. Consider speaking with a counsellor.",
        "FATIGUE": "Blood tests to rule out thyroid or iron issues are recommended. Pace yourself and prioritise rest.",
        "JOINT_PAIN": "Low-impact exercise (swimming, cycling) maintains mobility. Anti-inflammatory diet may help.",
        "HEADACHES": "Stay hydrated, manage stress, and track hormonal patterns. Discuss prescription options with your doctor.",
        "WEIGHT_GAIN": "Resistance training and a protein-rich diet help counter menopausal metabolic changes.",
    }
    base = recs.get(symptom, "Log your triggers carefully and discuss patterns with your healthcare provider.")
    if level == "high":
        base = "⚠️ " + base + " Given the severity, please consult your doctor promptly."
    return base

"""
Utility functions for the AI module
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random


def get_last_n_days(n: int) -> List[str]:
    """Get last n days in format 'Tue', 'Wed', etc."""
    days_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    days = []
    for i in range(n):
        date = datetime.utcnow() - timedelta(days=n-i-1)
        day_name = days_abbr[date.weekday()]
        days.append(day_name)
    return days


def calculate_wellness_score(symptom_logs: List[Any]) -> int:
    """
    Calculate overall wellness score from symptom logs (0-101 scale)
    Logic: Higher severity = lower score
    """
    if not symptom_logs:
        return 101
    
    avg_severity = sum(log.severity_level for log in symptom_logs) / len(symptom_logs)
    # Convert severity (0-10) to score (101-0)
    score = max(0, 101 - (avg_severity * 10))
    return int(score)


def calculate_trend_percentage(current_count: int, previous_count: int) -> str:
    """Calculate trend percentage change"""
    if previous_count == 0:
        if current_count > 0:
            return "↑100%"
        return "stable"
    
    change = ((current_count - previous_count) / previous_count) * 100
    if change > 0:
        return f"↑{int(change)}%"
    elif change < 0:
        return f"↓{int(abs(change))}%"
    else:
        return "→0%"


def group_by_day(symptom_logs: List[Any]) -> Dict[str, List[Any]]:
    """Group symptom logs by day"""
    grouped = {}
    for log in symptom_logs:
        day = log.timestamp.strftime("%a")  # "Mon", "Tue", etc.
        if day not in grouped:
            grouped[day] = []
        grouped[day].append(log)
    return grouped


def generate_confidence_score() -> float:
    """Generate a mock confidence score (0-1)"""
    return round(random.uniform(0.75, 1.0), 2)


def format_trigger_warning(symptom: str, trigger_factor: str) -> str:
    """Format AI-generated trigger warning text"""
    templates = [
        f"Based on your logs, we noticed {symptom} tends to spike after {trigger_factor}. Consider reducing this to see improvement.",
        f"Your {symptom} pattern shows correlation with {trigger_factor} intake. Try adjusting your {trigger_factor} schedule.",
        f"We detected that {symptom} increases on days with high {trigger_factor}. Managing {trigger_factor} might help.",
        f"Data suggests {symptom} is triggered by {trigger_factor}. Pay attention to this pattern over the next few days.",
    ]
    return random.choice(templates)


def calculate_percentage_change(previous: float, current: float) -> float:
    """Calculate percentage change between two values. Returns 0.0 if previous is 0."""
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)


def format_date_range(start: str, end: str) -> str:
    """Format a date range as a human-readable string."""
    try:
        s = datetime.fromisoformat(start.replace("Z", "+00:00"))
        e = datetime.fromisoformat(end.replace("Z", "+00:00"))
        return f"{s.strftime('%b %d')} – {e.strftime('%b %d, %Y')}"
    except Exception:
        return f"{start} – {end}"

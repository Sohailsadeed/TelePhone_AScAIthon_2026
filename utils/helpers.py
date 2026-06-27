"""
Helper utilities for FocusLens.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from utils.constants import *


def format_time(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_duration(seconds: int) -> str:
    """Convert seconds to readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def get_focus_level(score: int) -> str:
    """Get focus level based on score."""
    if score >= FOCUS_SCORE_HIGH:
        return FOCUS_LEVEL_HIGH
    elif score >= FOCUS_SCORE_MEDIUM:
        return FOCUS_LEVEL_MEDIUM
    else:
        return FOCUS_LEVEL_LOW


def parse_gemini_response(response_text: str) -> Dict[str, Any]:
    """Parse Gemini response JSON."""
    try:
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        pass

    # Default response if parsing fails
    return {
        "study_state": STUDY_STATE_IDLE,
        "focus_score": 50,
        "voice_message": "Unable to analyze. Please continue.",
        "dashboard_message": "Analyzing your study session.",
        "recommended_action": "Continue",
        "event": "ANALYSIS_FAILED",
    }


def should_trigger_cooldown(last_event_time: Optional[datetime], cooldown_seconds: int) -> bool:
    """Check if cooldown period has elapsed."""
    if last_event_time is None:
        return False
    return datetime.now() < (last_event_time + timedelta(seconds=cooldown_seconds))


def calculate_session_statistics(
    study_duration: int,
    break_duration: int,
    focus_scores: List[int],
    distractions: List[str],
) -> Dict[str, Any]:
    """Calculate session statistics."""
    avg_focus = sum(focus_scores) / len(focus_scores) if focus_scores else 0
    
    return {
        "total_study_time": format_duration(study_duration),
        "total_break_time": format_duration(break_duration),
        "average_focus_score": round(avg_focus, 2),
        "max_focus_score": max(focus_scores) if focus_scores else 0,
        "min_focus_score": min(focus_scores) if focus_scores else 0,
        "distraction_count": len(distractions),
        "unique_distractions": list(set(distractions)),
    }


def get_time_of_day() -> str:
    """Get current time of day."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def generate_session_id() -> str:
    """Generate unique session ID."""
    import uuid
    return str(uuid.uuid4())[:8]


def get_motivational_message(focus_score: int, study_duration: int) -> str:
    """Get motivational message based on performance."""
    if focus_score >= 90:
        return "🔥 Exceptional focus! You're in the zone!"
    elif focus_score >= 80:
        return "💪 Great job! Maintain this momentum!"
    elif focus_score >= 70:
        return "✅ Good focus! Keep it up!"
    elif focus_score >= 50:
        return "⏸️ You could do better. Try minimizing distractions."
    else:
        return "😴 Low focus. Consider taking a short break."


def get_time_until_break(start_time: datetime, break_interval: int) -> int:
    """Get minutes until break is recommended."""
    elapsed = (datetime.now() - start_time).total_seconds() / 60
    time_left = break_interval - elapsed
    return max(0, int(time_left))


def object_to_readable(obj_name: str) -> str:
    """Convert object name to readable format."""
    return obj_name.replace("_", " ").title()

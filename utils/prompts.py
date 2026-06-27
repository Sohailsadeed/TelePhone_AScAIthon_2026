"""
Prompts for Gemini API interactions.
"""

from typing import List, Dict, Any
from utils.constants import DETECTABLE_OBJECTS
from utils.helpers import object_to_readable


def get_vision_analysis_prompt(detected_objects: List[str], head_pose: Dict[str, Any]) -> str:
    """Generate prompt for vision analysis."""
    objects_str = ", ".join([object_to_readable(obj) for obj in detected_objects])
    
    prompt = f"""Analyze this study session based on detected objects and environment.

Detected Objects: {objects_str if objects_str else "None"}

Head Pose Data:
- Is Looking: {head_pose.get('is_looking', 'Unknown')}
- Pose Angle: {head_pose.get('pose_angle', 'N/A')}
- Fatigue Level: {head_pose.get('fatigue_level', 'Normal')}

Based on this data, provide a JSON response with:
1. study_state: "Focused", "Distracted", "Break", "Fatigued", or "Idle"
2. focus_score: 0-100
3. voice_message: A natural, brief AI response (1-2 sentences max)
4. dashboard_message: A message for the dashboard
5. recommended_action: "Continue", "Break", "Refocus", or "Rest"
6. event: The type of event ("FOCUS", "DISTRACTION", "BREAK", etc.)

Return ONLY valid JSON, no other text."""

    return prompt


def get_session_summary_prompt(
    session_data: Dict[str, Any],
) -> str:
    """Generate prompt for session summary."""
    prompt = f"""Summarize this study session and provide insights:

Session Duration: {session_data.get('duration_str', 'N/A')}
Average Focus Score: {session_data.get('avg_focus_score', 0)}
Total Distractions: {session_data.get('distraction_count', 0)}
Phone Detections: {session_data.get('phone_detections', 0)}
Break Time: {session_data.get('break_time_str', 'N/A')}

Provide a JSON response with:
1. summary: A brief summary of the session (2-3 sentences)
2. achievements: List of positive achievements
3. areas_for_improvement: List of areas to improve
4. suggestions: List of 3-4 actionable suggestions
5. overall_rating: Rating from 1-10

Return ONLY valid JSON, no other text."""

    return prompt


def get_weekly_report_prompt(
    stats: Dict[str, Any],
) -> str:
    """Generate prompt for weekly report."""
    prompt = f"""Generate a weekly study report based on these statistics:

Total Study Hours: {stats.get('total_hours', 0)}
Average Daily Focus: {stats.get('avg_daily_focus', 0)}
Most Productive Day: {stats.get('most_productive_day', 'N/A')}
Total Distractions: {stats.get('total_distractions', 0)}
Sessions Completed: {stats.get('sessions_count', 0)}

Provide a JSON response with:
1. week_summary: Overall weekly summary (3-4 sentences)
2. productivity_trend: "Improving", "Declining", or "Stable"
3. key_insights: List of important insights
4. top_distractions: List of most common distractions
5. recommendations: List of personalized recommendations
6. motivation: A motivational message

Return ONLY valid JSON, no other text."""

    return prompt


def get_distraction_response_prompt(distraction_type: str) -> str:
    """Generate prompt for distraction response."""
    prompt = f"""A student has been distracted by: {distraction_type}

Provide a JSON response with:
1. voice_message: A natural, encouraging message to redirect focus (1 sentence)
2. tip: A quick tip to avoid this distraction
3. emoji: An appropriate emoji

The response should be motivating, not scolding.

Return ONLY valid JSON, no other text."""

    return prompt


def get_break_recommendation_prompt(
    study_duration_minutes: int,
    focus_score: int,
    fatigue_level: str,
) -> str:
    """Generate prompt for break recommendation."""
    prompt = f"""Recommend a break based on study session data:

Study Duration: {study_duration_minutes} minutes
Current Focus Score: {focus_score}
Fatigue Level: {fatigue_level}

Provide a JSON response with:
1. should_break: true or false
2. break_reason: Why a break is (or isn't) recommended
3. break_duration: Recommended break duration in minutes
4. activity: Suggested activity during break
5. voice_message: A natural message about the break (1-2 sentences)

Return ONLY valid JSON, no other text."""

    return prompt


def get_focus_coaching_prompt(
    session_history: List[Dict[str, Any]],
) -> str:
    """Generate prompt for personalized focus coaching."""
    avg_score = sum(s.get('focus_score', 0) for s in session_history) / len(session_history) if session_history else 0
    peak_time = max(session_history, key=lambda x: x.get('focus_score', 0)) if session_history else {}
    
    prompt = f"""Provide personalized focus coaching based on study history:

Number of Sessions: {len(session_history)}
Average Focus Score: {avg_score:.1f}
Peak Performance: {peak_time.get('focus_score', 0)} at {peak_time.get('time', 'Unknown')}

Provide a JSON response with:
1. coaching_message: Personalized coaching message (2-3 sentences)
2. strength_area: What the student does well
3. challenge_area: What needs improvement
4. micro_habits: List of 2-3 micro-habits to build
5. next_session_goal: A specific goal for the next session

Return ONLY valid JSON, no other text."""

    return prompt

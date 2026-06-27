"""
Focus service for focus analysis and tracking.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from services.logger_service import LoggerService
from utils.constants import FOCUS_SCORE_HIGH, FOCUS_SCORE_MEDIUM, FOCUS_LEVEL_HIGH, FOCUS_LEVEL_MEDIUM, FOCUS_LEVEL_LOW
from utils.helpers import get_focus_level

logger = LoggerService.get_logger(__name__)


class FocusService:
    """Manages focus analysis and tracking."""

    def __init__(self):
        """Initialize focus service."""
        self.focus_history: List[Dict[str, Any]] = []
        self.focus_trends: List[float] = []
        self.focus_threshold = FOCUS_SCORE_HIGH

    def analyze_focus(
        self,
        detected_objects: List[str],
        is_looking: bool,
        fatigue_level: str,
        study_state: str,
    ) -> int:
        """Analyze and calculate focus score based on environment."""
        score = 100  # Start with perfect score

        # Reduce score for distracting objects
        distracting_objects = ["phone", "coffee_cup", "backpack"]
        for obj in detected_objects:
            if obj in distracting_objects:
                score -= 15
            elif obj == "book" or obj == "notebook":
                score += 5  # Boost for study materials
            elif obj == "keyboard" or obj == "mouse":
                score += 3  # Slight boost for input devices

        # Reduce score if not looking at screen
        if not is_looking:
            score -= 20

        # Reduce score based on fatigue
        if fatigue_level == "High":
            score -= 25
        elif fatigue_level == "Medium":
            score -= 15
        elif fatigue_level == "Low":
            score += 5

        # Ensure score is within bounds
        score = max(0, min(100, score))

        # Record in history
        self.focus_history.append({
            "timestamp": datetime.now(),
            "score": score,
            "study_state": study_state,
            "detected_objects": detected_objects,
        })

        # Update trends
        self.focus_trends.append(score)
        if len(self.focus_trends) > 100:
            self.focus_trends.pop(0)

        logger.debug(f"Focus score: {score}")
        return score

    def get_focus_level(self, score: int) -> str:
        """Get focus level from score."""
        return get_focus_level(score)

    def get_trend(self, window: int = 10) -> float:
        """Get focus trend (average of recent scores)."""
        if not self.focus_trends:
            return 0.0

        recent = self.focus_trends[-window:]
        return sum(recent) / len(recent) if recent else 0.0

    def is_focus_improving(self, window: int = 10) -> bool:
        """Check if focus is improving."""
        if len(self.focus_trends) < window * 2:
            return False

        first_half = self.focus_trends[-window*2:-window]
        second_half = self.focus_trends[-window:]

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        return second_avg > first_avg

    def get_focus_stats(self, session_focus_scores: List[int]) -> Dict[str, Any]:
        """Get focus statistics."""
        if not session_focus_scores:
            return {
                "average": 0,
                "peak": 0,
                "low": 0,
                "trend": "stable",
                "level": FOCUS_LEVEL_LOW,
            }

        average = sum(session_focus_scores) / len(session_focus_scores)
        peak = max(session_focus_scores)
        low = min(session_focus_scores)

        # Determine trend
        if len(session_focus_scores) > 5:
            first_half_avg = sum(session_focus_scores[:len(session_focus_scores)//2]) / (len(session_focus_scores)//2)
            second_half_avg = sum(session_focus_scores[len(session_focus_scores)//2:]) / (len(session_focus_scores) - len(session_focus_scores)//2)
            if second_half_avg > first_half_avg + 5:
                trend = "improving"
            elif second_half_avg < first_half_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "average": round(average, 2),
            "peak": peak,
            "low": low,
            "trend": trend,
            "level": self.get_focus_level(int(average)),
        }

    def estimate_break_need(
        self,
        study_duration_minutes: int,
        focus_score: int,
        fatigue_level: str,
    ) -> Dict[str, Any]:
        """Estimate if a break is needed."""
        needs_break = False
        urgency = "none"
        reason = ""

        # Check time-based break need
        if study_duration_minutes >= 40:
            needs_break = True
            urgency = "high"
            reason = "You've studied for a while. Time for a break!"

        # Check focus-based break need
        if focus_score < 50:
            needs_break = True
            urgency = "high" if urgency == "high" else "medium"
            reason = "Your focus is dropping. Take a short break."

        # Check fatigue-based break need
        if fatigue_level == "High":
            needs_break = True
            urgency = "critical"
            reason = "You seem tired. Take a rest!"

        return {
            "needs_break": needs_break,
            "urgency": urgency,
            "reason": reason,
            "recommended_duration": 5 if focus_score < 30 else 10 if focus_score < 50 else 5,
        }

    def get_focus_insights(self, session_focus_scores: List[int]) -> List[str]:
        """Generate focus insights."""
        insights = []

        if not session_focus_scores:
            return ["Session just started. Keep focusing!"]

        stats = self.get_focus_stats(session_focus_scores)

        # Generate insights
        if stats["average"] >= FOCUS_SCORE_HIGH:
            insights.append("🔥 Excellent focus! You're in the zone!")
        elif stats["average"] >= FOCUS_SCORE_MEDIUM:
            insights.append("💪 Good focus! Keep it up!")
        else:
            insights.append("⏸️ Focus could be better. Minimize distractions.")

        if stats["trend"] == "improving":
            insights.append("📈 Your focus is improving. Great effort!")
        elif stats["trend"] == "declining":
            insights.append("📉 Your focus is declining. Consider a break.")

        if stats["peak"] >= 90:
            insights.append(f"🎯 Peak focus reached: {stats['peak']}!")

        return insights

    def clear_history(self):
        """Clear focus history."""
        self.focus_history.clear()
        self.focus_trends.clear()
        logger.info("Focus history cleared")

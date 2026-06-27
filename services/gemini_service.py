"""
Gemini service for AI reasoning and analysis.
"""

from google import genai
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from config import Config
from services.logger_service import LoggerService
from utils.prompts import (
    get_vision_analysis_prompt,
    get_session_summary_prompt,
    get_weekly_report_prompt,
    get_distraction_response_prompt,
    get_break_recommendation_prompt,
)
from utils.helpers import parse_gemini_response

logger = LoggerService.get_logger(__name__)


class GeminiService:
    """Handles AI reasoning using Google Gemini."""

    def __init__(self):
        """Initialize Gemini service."""
        if Config.GEMINI_API_KEY:
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        else:
            logger.warning("Gemini API key not configured")
            self.client = None

    def _ensure_initialized(self) -> bool:
        """Ensure model is initialized."""
        if not self.client:
            logger.error("Gemini model not initialized")
            return False
        return True

    def analyze_vision(
        self,
        detected_objects: List[str],
        head_pose: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze vision data and return study state."""
        if not self._ensure_initialized():
            return self._get_default_analysis()

        try:
            prompt = get_vision_analysis_prompt(detected_objects, head_pose)
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            result = parse_gemini_response(response.text)
            logger.debug(f"Vision analysis: {result.get('study_state')}")
            return result
        except Exception as e:
            logger.error(f"Gemini vision analysis error: {e}")
            return self._get_default_analysis()

    def generate_session_summary(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate session summary."""
        if not self._ensure_initialized():
            return self._get_default_summary()

        try:
            prompt = get_session_summary_prompt(session_data)
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            result = parse_gemini_response(response.text)
            logger.debug("Session summary generated")
            return result
        except Exception as e:
            logger.error(f"Gemini session summary error: {e}")
            return self._get_default_summary()

    def generate_weekly_report(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate weekly report."""
        if not self._ensure_initialized():
            return self._get_default_report()

        try:
            prompt = get_weekly_report_prompt(stats)
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            result = parse_gemini_response(response.text)
            logger.debug("Weekly report generated")
            return result
        except Exception as e:
            logger.error(f"Gemini weekly report error: {e}")
            return self._get_default_report()

    def get_distraction_response(self, distraction_type: str) -> Dict[str, Any]:
        """Get response to distraction."""
        if not self._ensure_initialized():
            return {
                "voice_message": f"I noticed {distraction_type}. Let's refocus.",
                "tip": "Keep your workspace organized.",
                "emoji": "🎯",
            }

        try:
            prompt = get_distraction_response_prompt(distraction_type)
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            result = parse_gemini_response(response.text)
            logger.debug(f"Distraction response: {distraction_type}")
            return result
        except Exception as e:
            logger.error(f"Gemini distraction response error: {e}")
            return {
                "voice_message": "Let's refocus on your studies.",
                "tip": "Minimize distractions.",
                "emoji": "🎯",
            }

    def get_break_recommendation(
        self,
        study_duration_minutes: int,
        focus_score: int,
        fatigue_level: str,
    ) -> Dict[str, Any]:
        """Get break recommendation."""
        if not self._ensure_initialized():
            return self._get_default_break_rec()

        try:
            prompt = get_break_recommendation_prompt(
                study_duration_minutes, focus_score, fatigue_level
            )
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            result = parse_gemini_response(response.text)
            logger.debug(f"Break recommendation: should_break={result.get('should_break')}")
            return result
        except Exception as e:
            logger.error(f"Gemini break recommendation error: {e}")
            return self._get_default_break_rec()

    def stream_response(self, prompt: str) -> str:
        """Stream response from Gemini."""
        if not self._ensure_initialized():
            return "Analysis unavailable"

        try:
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini stream error: {e}")
            return "Error generating response"

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis response."""
        return {
            "study_state": "Idle",
            "focus_score": 50,
            "voice_message": "Let's begin your study session.",
            "dashboard_message": "Ready to start studying.",
            "recommended_action": "Continue",
            "event": "IDLE",
        }

    def _get_default_summary(self) -> Dict[str, Any]:
        """Get default session summary."""
        return {
            "summary": "Study session completed.",
            "achievements": ["Started session"],
            "areas_for_improvement": ["Minimize distractions"],
            "suggestions": ["Take regular breaks", "Stay hydrated"],
            "overall_rating": 5,
        }

    def _get_default_report(self) -> Dict[str, Any]:
        """Get default weekly report."""
        return {
            "week_summary": "Weekly study summary.",
            "productivity_trend": "Stable",
            "key_insights": ["Consistent effort"],
            "top_distractions": [],
            "recommendations": ["Maintain routine"],
            "motivation": "Great job studying this week!",
        }

    def _get_default_break_rec(self) -> Dict[str, Any]:
        """Get default break recommendation."""
        return {
            "should_break": False,
            "break_reason": "Continue focusing",
            "break_duration": 5,
            "activity": "Walk around",
            "voice_message": "Keep going!",
        }

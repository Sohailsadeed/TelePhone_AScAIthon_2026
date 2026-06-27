"""
Analytics service for generating reports and insights.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from database.database import Database
from models.session import Report
from services.logger_service import LoggerService
from services.gemini_service import GeminiService
from utils.helpers import format_duration

logger = LoggerService.get_logger(__name__)


class AnalyticsService:
    """Generates analytics and reports."""

    def __init__(self, db: Database, gemini_service: GeminiService):
        """Initialize analytics service."""
        self.db = db
        self.gemini = gemini_service

    def generate_session_report(
        self,
        session_id: str,
        study_duration: int,
        break_duration: int,
        average_focus_score: float,
        peak_focus_score: int,
        low_focus_score: int,
        distractions_count: int,
        phone_detections: int,
        break_count: int,
        events: List[Any],
    ) -> Optional[Report]:
        """Generate session report."""
        try:
            report_id = str(uuid4())[:8]

            # Prepare session data for Gemini
            session_data = {
                "duration_str": format_duration(study_duration),
                "avg_focus_score": round(average_focus_score, 2),
                "distraction_count": distractions_count,
                "phone_detections": phone_detections,
                "break_time_str": format_duration(break_duration),
            }

            # Get Gemini analysis
            gemini_summary = self.gemini.generate_session_summary(session_data)

            # Create report
            report = Report(
                report_id=report_id,
                session_id=session_id,
                report_type="session",
                generated_at=datetime.now(),
                study_duration_str=format_duration(study_duration),
                average_focus_score=round(average_focus_score, 2),
                peak_focus_score=peak_focus_score,
                low_focus_score=low_focus_score,
                distractions_count=distractions_count,
                phone_detections=phone_detections,
                break_count=break_count,
                summary=gemini_summary.get("summary", "Session completed."),
                achievements=gemini_summary.get("achievements", []),
                areas_for_improvement=gemini_summary.get("areas_for_improvement", []),
                suggestions=gemini_summary.get("suggestions", []),
                overall_rating=gemini_summary.get("overall_rating", 5),
            )

            # Save to database
            self.db.create_report(
                report_id=report_id,
                session_id=session_id,
                report_type="session",
                summary=report.summary,
                achievements=report.achievements,
                areas_for_improvement=report.areas_for_improvement,
                suggestions=report.suggestions,
                study_duration_str=report.study_duration_str,
                average_focus_score=report.average_focus_score,
                peak_focus_score=report.peak_focus_score,
                low_focus_score=report.low_focus_score,
                distractions_count=report.distractions_count,
                phone_detections=report.phone_detections,
                break_count=report.break_count,
                overall_rating=report.overall_rating,
            )

            logger.info(f"Session report generated: {report_id}")
            return report
        except Exception as e:
            logger.error(f"Error generating session report: {e}")
            return None

    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily report."""
        try:
            sessions = self.db.get_today_sessions()

            if not sessions:
                return {"date": datetime.now().strftime("%Y-%m-%d"), "sessions": 0}

            total_study_time = sum(int(s.get("study_duration", 0) or 0) for s in sessions)
            total_break_time = sum(int(s.get("break_duration", 0) or 0) for s in sessions)
            avg_focus = sum(float(s.get("average_focus_score", 0) or 0) for s in sessions) / len(sessions)
            total_distractions = sum(int(s.get("phone_detections", 0) or 0) for s in sessions)

            stats = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "sessions": len(sessions),
                "total_study_time": format_duration(total_study_time),
                "total_break_time": format_duration(total_break_time),
                "average_focus_score": round(avg_focus, 2),
                "total_distractions": total_distractions,
            }

            logger.info(f"Daily report generated: {stats['sessions']} sessions")
            return stats
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return {}

    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly report."""
        try:
            # Get last 7 days of sessions
            seven_days_ago = datetime.now() - timedelta(days=7)
            all_sessions = self.db.get_all_sessions(limit=100)

            # Filter for last 7 days
            week_sessions = [
                s for s in all_sessions
                if datetime.fromisoformat(s.get("start_time", "")) > seven_days_ago
            ]

            if not week_sessions:
                return {"week": datetime.now().strftime("%Y-W%W"), "sessions": 0}

            total_hours = sum(int(s.get("study_duration", 0) or 0) for s in week_sessions) / 3600
            avg_focus = sum(float(s.get("average_focus_score", 0) or 0) for s in week_sessions) / len(week_sessions)
            most_productive_day = self._get_most_productive_day(week_sessions)

            stats = {
                "week": datetime.now().strftime("%Y-W%W"),
                "total_hours": round(total_hours, 2),
                "sessions_count": len(week_sessions),
                "avg_daily_focus": round(avg_focus, 2),
                "most_productive_day": most_productive_day,
                "total_distractions": sum(int(s.get("phone_detections", 0) or 0) for s in week_sessions),
            }

            # Get Gemini analysis
            gemini_report = self.gemini.generate_weekly_report(stats)

            final_report = {
                **stats,
                "summary": gemini_report.get("week_summary", ""),
                "productivity_trend": gemini_report.get("productivity_trend", "Stable"),
                "key_insights": gemini_report.get("key_insights", []),
                "top_distractions": gemini_report.get("top_distractions", []),
                "recommendations": gemini_report.get("recommendations", []),
            }

            logger.info("Weekly report generated")
            return final_report
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return {}

    def _get_most_productive_day(self, sessions: List[Dict[str, Any]]) -> str:
        """Get most productive day from sessions."""
        if not sessions:
            return "N/A"

        day_totals = {}
        for session in sessions:
            start_time = datetime.fromisoformat(session.get("start_time", ""))
            day = start_time.strftime("%A")
            duration = int(session.get("study_duration", 0) or 0)
            day_totals[day] = day_totals.get(day, 0) + duration

        if day_totals:
            return max(day_totals, key=day_totals.get)
        return "N/A"

    def get_focus_distribution(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of focus levels."""
        distribution = {
            "high": 0,  # >= 80
            "medium": 0,  # 50-79
            "low": 0,  # < 50
        }

        for session in sessions:
            avg_focus = float(session.get("average_focus_score", 0) or 0)
            if avg_focus >= 80:
                distribution["high"] += 1
            elif avg_focus >= 50:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1

        return distribution

    def get_distraction_patterns(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distraction patterns."""
        patterns = {}
        for session in sessions:
            phone_detections = int(session.get("phone_detections", 0) or 0)
            if phone_detections > 0:
                patterns["phone"] = patterns.get("phone", 0) + phone_detections

        return patterns

    def export_report(self, report: Report) -> str:
        """Export report as formatted text."""
        text = f"""
╔════════════════════════════════════════╗
║        FOCUSLENS SESSION REPORT        ║
╚════════════════════════════════════════╝

📊 Session Details
─────────────────
Study Duration: {report.study_duration_str}
Focus Score: {report.average_focus_score}/100
Peak Focus: {report.peak_focus_score}/100
Low Focus: {report.low_focus_score}/100

📈 Session Analytics
────────────────────
Distractions: {report.distractions_count}
Phone Detections: {report.phone_detections}
Breaks Taken: {report.break_count}
Overall Rating: {report.overall_rating}/10

✨ Summary
─────────
{report.summary}

🎯 Achievements
───────────────
"""
        for achievement in report.achievements:
            text += f"  ✓ {achievement}\n"

        text += """
🔧 Areas for Improvement
────────────────────────
"""
        for area in report.areas_for_improvement:
            text += f"  • {area}\n"

        text += """
💡 Suggestions
──────────────
"""
        for suggestion in report.suggestions:
            text += f"  → {suggestion}\n"

        return text

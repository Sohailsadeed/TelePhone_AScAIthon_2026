"""
Session service for managing study sessions.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import uuid4
from database.database import Database
from models.session import Session, Event, FocusScore, Distraction, Report
from services.logger_service import LoggerService
from utils.helpers import generate_session_id
from config import Config

logger = LoggerService.get_logger(__name__)


class SessionService:
    """Manages study sessions."""

    def __init__(self, db: Database):
        """Initialize session service."""
        self.db = db
        self.current_session: Optional[Session] = None
        self.pause_time: Optional[datetime] = None

    def start_session(self, notes: str = "") -> Optional[Session]:
        """Start a new study session."""
        try:
            session_id = generate_session_id()
            start_time = datetime.now()
            db_start_time = start_time
            if isinstance(db_start_time, datetime):
                db_start_time = db_start_time.isoformat()

            # Create in database
            self.db.create_session(session_id, db_start_time, notes)

            # Create session object
            self.current_session = Session(
                session_id=session_id,
                start_time=start_time,
                notes=notes,
            )

            logger.info(f"Session started: {session_id}")
            return self.current_session
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return None

    def end_session(self) -> Optional[Session]:
        """End current session."""
        if self.current_session is None:
            logger.warning("No active session to end")
            return None

        try:
            end_time = datetime.now()
            self.current_session.end_time = end_time
            db_end_time = end_time
            if isinstance(db_end_time, datetime):
                db_end_time = db_end_time.isoformat()

            # Update in database
            self.db.end_session(self.current_session.session_id, db_end_time)

            # Calculate final stats
            self.current_session.study_duration = self._calculate_study_duration(
                self.current_session
            )
            if self.current_session.focus_scores:
                self.current_session.average_focus_score = (
                    sum(fs.score for fs in self.current_session.focus_scores)
                    / len(self.current_session.focus_scores)
                )

            # Update in database
            self.db.update_session(
                self.current_session.session_id,
                study_duration=self.current_session.study_duration,
                average_focus_score=self.current_session.average_focus_score,
            )

            logger.info(f"Session ended: {self.current_session.session_id}")
            return self.current_session
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return None

    def pause_session(self) -> bool:
        """Pause current session."""
        if self.current_session is None:
            logger.warning("No active session to pause")
            return False

        try:
            self.pause_time = datetime.now()
            logger.info(f"Session paused: {self.current_session.session_id}")
            return True
        except Exception as e:
            logger.error(f"Error pausing session: {e}")
            return False

    def resume_session(self) -> bool:
        """Resume paused session."""
        if self.current_session is None or self.pause_time is None:
            logger.warning("No paused session to resume")
            return False

        try:
            # Add pause duration to break time
            pause_duration = (datetime.now() - self.pause_time).total_seconds()
            self.current_session.break_duration += int(pause_duration)
            self.pause_time = None

            logger.info(
                f"Session resumed: {self.current_session.session_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Error resuming session: {e}")
            return False

    def add_event(
        self,
        event_type: str,
        study_state: str,
        focus_score: int,
        detected_objects: List[str],
        voice_message: str,
        dashboard_message: str,
        metadata: Dict[str, Any] = None,
    ) -> Optional[Event]:
        """Add event to current session."""
        if self.current_session is None:
            logger.warning("No active session")
            return None

        try:
            event_id = str(uuid4())[:8]
            timestamp = datetime.now()
            db_timestamp = timestamp
            if isinstance(db_timestamp, datetime):
                db_timestamp = db_timestamp.isoformat()

            event = Event(
                event_id=event_id,
                session_id=self.current_session.session_id,
                event_type=event_type,
                timestamp=timestamp,
                study_state=study_state,
                focus_score=focus_score,
                detected_objects=detected_objects,
                voice_message=voice_message,
                dashboard_message=dashboard_message,
                metadata=metadata or {},
            )

            # Save to database
            self.db.create_event(
                event_id=event_id,
                session_id=self.current_session.session_id,
                event_type=event_type,
                timestamp=db_timestamp,
                study_state=study_state,
                focus_score=focus_score,
                detected_objects=detected_objects,
                voice_message=voice_message,
                dashboard_message=dashboard_message,
                metadata=metadata,
            )

            self.current_session.events.append(event)
            logger.debug(f"Event added: {event_type}")
            return event
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            return None

    def add_focus_score(
        self,
        score: int,
        study_state: str,
        detected_objects: List[str],
    ) -> Optional[FocusScore]:
        """Add focus score to current session."""
        if self.current_session is None:
            logger.warning("No active session")
            return None

        try:
            timestamp = datetime.now()
            db_timestamp = timestamp
            if isinstance(db_timestamp, datetime):
                db_timestamp = db_timestamp.isoformat()

            fs = FocusScore(
                session_id=self.current_session.session_id,
                timestamp=timestamp,
                score=score,
                study_state=study_state,
                detected_objects=detected_objects,
            )

            # Save to database
            self.db.create_focus_score(
                session_id=self.current_session.session_id,
                timestamp=db_timestamp,
                score=score,
                study_state=study_state,
                detected_objects=detected_objects,
            )

            self.current_session.focus_scores.append(fs)
            return fs
        except Exception as e:
            logger.error(f"Error adding focus score: {e}")
            return None

    def add_distraction(
        self,
        object_type: str,
        duration_seconds: int,
        response_message: str,
    ) -> Optional[Distraction]:
        """Add distraction record."""
        if self.current_session is None:
            logger.warning("No active session")
            return None

        try:
            distraction_id = str(uuid4())[:8]
            timestamp = datetime.now()
            db_timestamp = timestamp
            if isinstance(db_timestamp, datetime):
                db_timestamp = db_timestamp.isoformat()

            distraction = Distraction(
                distraction_id=distraction_id,
                session_id=self.current_session.session_id,
                timestamp=timestamp,
                object_type=object_type,
                duration_seconds=duration_seconds,
                response_message=response_message,
            )

            # Save to database
            self.db.create_distraction(
                distraction_id=distraction_id,
                session_id=self.current_session.session_id,
                timestamp=db_timestamp,
                object_type=object_type,
                duration_seconds=duration_seconds,
                response_message=response_message,
            )

            self.current_session.distractions.append(distraction)

            # Track phone detection
            if object_type.lower() == "phone":
                self.current_session.phone_detections += 1

            logger.debug(f"Distraction recorded: {object_type}")
            return distraction
        except Exception as e:
            logger.error(f"Error adding distraction: {e}")
            return None

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current session."""
        if self.current_session is None:
            return {}

        try:
            study_duration = self._calculate_study_duration(self.current_session)
            focus_scores = [fs.score for fs in self.current_session.focus_scores]
            avg_focus = sum(focus_scores) / len(focus_scores) if focus_scores else 0

            return {
                "session_id": self.current_session.session_id,
                "elapsed_time": self.current_session.elapsed_time,
                "study_duration": study_duration,
                "break_duration": self.current_session.break_duration,
                "average_focus_score": round(avg_focus, 2),
                "max_focus_score": max(focus_scores) if focus_scores else 0,
                "min_focus_score": min(focus_scores) if focus_scores else 0,
                "events_count": len(self.current_session.events),
                "distractions_count": len(self.current_session.distractions),
                "phone_detections": self.current_session.phone_detections,
            }
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {}

    def _calculate_study_duration(self, session: Session) -> int:
        """Calculate study duration (excluding breaks)."""
        total = session.elapsed_time
        return max(0, total - session.break_duration)

    def get_current_session(self) -> Optional[Session]:
        """Get current session."""
        return self.current_session

    def is_session_active(self) -> bool:
        """Check if session is currently active."""
        return self.current_session is not None and self.current_session.is_active

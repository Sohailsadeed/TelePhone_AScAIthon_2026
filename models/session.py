"""
Data models for FocusLens.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class StudyState(Enum):
    """Study state enumeration."""
    FOCUSED = "Focused"
    DISTRACTED = "Distracted"
    BREAK = "Break"
    FATIGUED = "Fatigued"
    IDLE = "Idle"


@dataclass
class Detection:
    """Object detection result."""
    object_type: str
    confidence: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "object_type": self.object_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HeadPose:
    """Head pose data."""
    is_looking: bool
    pose_angle: float
    fatigue_level: str
    confidence: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_looking": self.is_looking,
            "pose_angle": self.pose_angle,
            "fatigue_level": self.fatigue_level,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Event:
    """Study session event."""
    event_id: str
    session_id: str
    event_type: str
    timestamp: datetime
    study_state: str
    focus_score: int
    detected_objects: List[str]
    voice_message: str
    dashboard_message: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "study_state": self.study_state,
            "focus_score": self.focus_score,
            "detected_objects": self.detected_objects,
            "voice_message": self.voice_message,
            "dashboard_message": self.dashboard_message,
            "metadata": self.metadata,
        }


@dataclass
class FocusScore:
    """Focus score data point."""
    session_id: str
    timestamp: datetime
    score: int
    study_state: str
    detected_objects: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "study_state": self.study_state,
            "detected_objects": self.detected_objects,
        }


@dataclass
class Distraction:
    """Distraction record."""
    distraction_id: str
    session_id: str
    timestamp: datetime
    object_type: str
    duration_seconds: int
    response_message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "distraction_id": self.distraction_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "object_type": self.object_type,
            "duration_seconds": self.duration_seconds,
            "response_message": self.response_message,
        }


@dataclass
class Session:
    """Study session."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    study_duration: int = 0  # seconds
    break_duration: int = 0  # seconds
    total_focus_score: int = 0
    average_focus_score: float = 0.0
    events: List[Event] = None
    focus_scores: List[FocusScore] = None
    distractions: List[Distraction] = None
    phone_detections: int = 0
    notes: str = ""
    
    def __post_init__(self):
        """Initialize lists."""
        if self.events is None:
            self.events = []
        if self.focus_scores is None:
            self.focus_scores = []
        if self.distractions is None:
            self.distractions = []
    
    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.end_time is None
    
    @property
    def elapsed_time(self) -> int:
        """Get elapsed time in seconds."""
        end = self.end_time or datetime.now()
        return int((end - self.start_time).total_seconds())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "study_duration": self.study_duration,
            "break_duration": self.break_duration,
            "total_focus_score": self.total_focus_score,
            "average_focus_score": self.average_focus_score,
            "events_count": len(self.events),
            "phone_detections": self.phone_detections,
            "notes": self.notes,
        }


@dataclass
class Report:
    """Study report."""
    report_id: str
    session_id: str
    report_type: str  # daily, weekly, custom
    generated_at: datetime
    study_duration_str: str
    average_focus_score: float
    peak_focus_score: int
    low_focus_score: int
    distractions_count: int
    phone_detections: int
    break_count: int
    summary: str
    achievements: List[str]
    areas_for_improvement: List[str]
    suggestions: List[str]
    overall_rating: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "session_id": self.session_id,
            "report_type": self.report_type,
            "generated_at": self.generated_at.isoformat(),
            "study_duration_str": self.study_duration_str,
            "average_focus_score": self.average_focus_score,
            "peak_focus_score": self.peak_focus_score,
            "low_focus_score": self.low_focus_score,
            "distractions_count": self.distractions_count,
            "phone_detections": self.phone_detections,
            "break_count": self.break_count,
            "summary": self.summary,
            "achievements": self.achievements,
            "areas_for_improvement": self.areas_for_improvement,
            "suggestions": self.suggestions,
            "overall_rating": self.overall_rating,
        }

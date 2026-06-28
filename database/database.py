"""
Database management for FocusLens using SQLite.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str = "focuslens.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self._initialize()

    def _initialize(self):
        """Initialize database and create tables."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create all required tables."""
        cursor = self.conn.cursor()

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                study_duration INTEGER DEFAULT 0,
                break_duration INTEGER DEFAULT 0,
                total_focus_score INTEGER DEFAULT 0,
                average_focus_score REAL DEFAULT 0.0,
                phone_detections INTEGER DEFAULT 0,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                study_state TEXT,
                focus_score INTEGER,
                detected_objects TEXT,
                voice_message TEXT,
                dashboard_message TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Focus scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS focus_scores (
                score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                score INTEGER NOT NULL,
                study_state TEXT,
                detected_objects TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Distractions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS distractions (
                distraction_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                object_type TEXT NOT NULL,
                duration_seconds INTEGER,
                response_message TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                report_type TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                study_duration_str TEXT,
                average_focus_score REAL,
                peak_focus_score INTEGER,
                low_focus_score INTEGER,
                distractions_count INTEGER,
                phone_detections INTEGER,
                break_count INTEGER,
                summary TEXT,
                achievements TEXT,
                areas_for_improvement TEXT,
                suggestions TEXT,
                overall_rating INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                date TEXT NOT NULL,
                total_sessions INTEGER DEFAULT 0,
                total_study_time INTEGER DEFAULT 0,
                average_focus INTEGER DEFAULT 0,
                peak_focus INTEGER DEFAULT 0,
                distractions_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        self.conn.commit()
        logger.info("Database initialized successfully")

    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return []

    def execute_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return one result."""
        results = self.execute(query, params)
        return results[0] if results else None

    def insert(self, query: str, params: tuple = ()) -> bool:
        """Execute an INSERT query."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return False

    def update(self, query: str, params: tuple = ()) -> bool:
        """Execute an UPDATE query."""
        return self.insert(query, params)

    def delete(self, query: str, params: tuple = ()) -> bool:
        """Execute a DELETE query."""
        return self.insert(query, params)

    # Session methods
    def create_session(
        self,
        session_id: str,
        start_time: datetime,
        notes: str = "",
    ) -> bool:
        """Create a new session."""
        query = """
            INSERT INTO sessions (session_id, start_time, created_at, notes)
            VALUES (?, ?, ?, ?)
        """
        return self.insert(
            query,
            (
                session_id,
                start_time if isinstance(start_time, str) else start_time.isoformat(),
                datetime.now().isoformat(),
                notes,
            ),
        )

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        query = "SELECT * FROM sessions WHERE session_id = ?"
        return self.execute_one(query, (session_id,))

    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session."""
        updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        query = f"UPDATE sessions SET {updates} WHERE session_id = ?"
        params = (*kwargs.values(), session_id)
        return self.update(query, params)

    def end_session(self, session_id: str, end_time: datetime) -> bool:
        """End a session."""
        return self.update_session(
            session_id,
            end_time=end_time if isinstance(end_time, str) else end_time.isoformat(),
        )

    def get_all_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all sessions."""
        query = "SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?"
        return self.execute(query, (limit,))

    def get_today_sessions(self) -> List[Dict[str, Any]]:
        """Get today's sessions."""
        query = """
            SELECT * FROM sessions 
            WHERE DATE(start_time) = DATE('now', 'localtime')
            ORDER BY start_time DESC
        """
        return self.execute(query)

    # Event methods
    def create_event(
        self,
        event_id: str,
        session_id: str,
        event_type: str,
        timestamp: datetime,
        study_state: str,
        focus_score: int,
        detected_objects: List[str],
        voice_message: str,
        dashboard_message: str,
        metadata: Dict[str, Any] = None,
    ) -> bool:
        """Create a new event."""
        import json
        query = """
            INSERT INTO events 
            (event_id, session_id, event_type, timestamp, study_state, focus_score, 
             detected_objects, voice_message, dashboard_message, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            event_id,
            session_id,
            event_type,
            timestamp if isinstance(timestamp, str) else timestamp.isoformat(),
            study_state,
            focus_score,
            json.dumps(detected_objects),
            voice_message,
            dashboard_message,
            json.dumps(metadata or {}),
            datetime.now().isoformat(),
        )
        return self.insert(query, params)

    def get_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all events for a session."""
        query = "SELECT * FROM events WHERE session_id = ? ORDER BY timestamp"
        return self.execute(query, (session_id,))

    # Focus score methods
    def create_focus_score(
        self,
        session_id: str,
        timestamp: datetime,
        score: int,
        study_state: str,
        detected_objects: List[str],
    ) -> bool:
        """Create a focus score record."""
        import json
        query = """
            INSERT INTO focus_scores 
            (session_id, timestamp, score, study_state, detected_objects, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            session_id,
            timestamp if isinstance(timestamp, str) else timestamp.isoformat(),
            score,
            study_state,
            json.dumps(detected_objects),
            datetime.now().isoformat(),
        )
        return self.insert(query, params)

    def get_session_focus_scores(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all focus scores for a session."""
        query = "SELECT * FROM focus_scores WHERE session_id = ? ORDER BY timestamp"
        return self.execute(query, (session_id,))

    # Distraction methods
    def create_distraction(
        self,
        distraction_id: str,
        session_id: str,
        timestamp: datetime,
        object_type: str,
        duration_seconds: int,
        response_message: str,
    ) -> bool:
        """Create a distraction record."""
        query = """
            INSERT INTO distractions 
            (distraction_id, session_id, timestamp, object_type, duration_seconds, response_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            distraction_id,
            session_id,
            timestamp if isinstance(timestamp, str) else timestamp.isoformat(),
            object_type,
            duration_seconds,
            response_message,
            datetime.now().isoformat(),
        )
        return self.insert(query, params)

    def get_session_distractions(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all distractions for a session."""
        query = "SELECT * FROM distractions WHERE session_id = ? ORDER BY timestamp"
        return self.execute(query, (session_id,))

    # Report methods
    def create_report(
        self,
        report_id: str,
        session_id: str,
        report_type: str,
        summary: str,
        achievements: List[str],
        areas_for_improvement: List[str],
        suggestions: List[str],
        **kwargs,
    ) -> bool:
        """Create a report."""
        import json
        query = """
            INSERT INTO reports 
            (report_id, session_id, report_type, generated_at, study_duration_str, 
             average_focus_score, peak_focus_score, low_focus_score, distractions_count, 
             phone_detections, break_count, summary, achievements, areas_for_improvement, 
             suggestions, overall_rating, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            report_id,
            session_id,
            report_type,
            datetime.now().isoformat(),
            kwargs.get("study_duration_str", ""),
            kwargs.get("average_focus_score", 0),
            kwargs.get("peak_focus_score", 0),
            kwargs.get("low_focus_score", 0),
            kwargs.get("distractions_count", 0),
            kwargs.get("phone_detections", 0),
            kwargs.get("break_count", 0),
            summary,
            json.dumps(achievements),
            json.dumps(areas_for_improvement),
            json.dumps(suggestions),
            kwargs.get("overall_rating", 0),
            datetime.now().isoformat(),
        )
        return self.insert(query, params)

    def get_session_report(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get report for a session."""
        query = "SELECT * FROM reports WHERE session_id = ?"
        return self.execute_one(query, (session_id,))

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()

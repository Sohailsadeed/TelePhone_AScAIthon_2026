"""
Main dashboard component for Streamlit.
"""

import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import Config
from services.logger_service import LoggerService
from services.camera_service import CameraService
from services.vision_service import VisionService
from services.gemini_service import GeminiService
from services.voice_service import VoiceService
from services.session_service import SessionService
from services.focus_service import FocusService
from services.analytics_service import AnalyticsService
from database.database import Database
from utils.helpers import format_duration, get_time_of_day
from utils.styles import STATUS_INDICATORS
from ui.cards import metric_card, focus_score_card, status_card
from ui.charts import create_focus_trend_chart
from ui.camera_view import display_camera_feed

logger = LoggerService.get_logger(__name__)


class Dashboard:
    """Main dashboard controller."""

    def __init__(self):
        """Initialize dashboard."""
        self.db = Database(Config.DATABASE_PATH)
        self.camera = CameraService(Config.CAMERA_INDEX)
        self.vision = VisionService()
        self.gemini = GeminiService()
        self.voice = VoiceService()
        self.session_service = SessionService(self.db)
        self.focus_service = FocusService()
        self.analytics = AnalyticsService(self.db, self.gemini)

    def setup_page(self):
        """Setup page configuration."""
        st.set_page_config(
            page_title="FocusLens - AI Study Intelligence",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Apply custom styles
        st.markdown("""
            <style>
                .main {
                    background-color: #0e1419;
                }
                [data-testid="stSidebar"] {
                    background-color: #1a1f2e;
                }
            </style>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render sidebar."""
        with st.sidebar:
            st.markdown("# 🎯 FocusLens")
            st.markdown("### AI Study Intelligence System")

            st.divider()

            # Session Control
            st.subheader("Session Control")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶ Start Session", use_container_width=True):
                    session = self.session_service.start_session()
                    if session:
                        st.success("Session started!")
                        st.session_state.current_session = session.session_id

            with col2:
                if st.button("⏹ End Session", use_container_width=True):
                    session = self.session_service.end_session()
                    if session:
                        st.success("Session ended!")
                        st.session_state.current_session = None

            st.divider()

            # Configuration
            st.subheader("Settings")

            if st.checkbox("🔊 Voice Enabled", value=self.voice.enabled):
                self.voice.enabled = True
            else:
                self.voice.enabled = False

            if st.checkbox("📹 Show Camera Feed", value=True):
                st.session_state.show_camera = True
            else:
                st.session_state.show_camera = False

            st.divider()

            # Statistics
            st.subheader("Quick Stats")

            if self.session_service.is_session_active():
                stats = self.session_service.get_session_stats()
                st.metric(
                    "Study Time",
                    format_duration(stats.get("study_duration", 0)),
                    f"{stats.get('events_count', 0)} events",
                )
                st.metric(
                    "Focus Score",
                    f"{stats.get('average_focus_score', 0):.0f}/100",
                )

    def render_main_dashboard(self):
        """Render main dashboard."""
        st.markdown("# 🎯 FocusLens Dashboard")
        st.markdown(f"*AI Study Intelligence System • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        st.divider()

        # Check if session is active
        if not self.session_service.is_session_active():
            st.info("📌 Start a session to begin monitoring your focus!")
            return

        # Get current session stats
        stats = self.session_service.get_session_stats()

        # Top metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            metric_card(
                "Study Time",
                format_duration(stats.get("study_duration", 0)),
                icon="⏱️",
                color="#00D9FF",
            )

        with col2:
            metric_card(
                "Average Focus",
                f"{stats.get('average_focus_score', 0):.0f}",
                "/ 100",
                icon="🎯",
                color="#4CAF50",
            )

        with col3:
            metric_card(
                "Distractions",
                stats.get("distractions_count", 0),
                icon="⚠️",
                color="#FF9800",
            )

        with col4:
            metric_card(
                "Phone Detections",
                stats.get("phone_detections", 0),
                icon="📱",
                color="#F44336",
            )

        st.divider()

        # Camera and analysis row
        col_camera, col_analysis = st.columns([2, 1])

        with col_camera:
            st.subheader("📹 Live Camera Feed")
            if st.session_state.get("show_camera", True):
                frame = self.camera.get_frame_rgb()
                if frame is not None:
                    display_camera_feed(frame)
                else:
                    st.warning("Camera not available")
            else:
                st.info("Camera feed hidden")

        with col_analysis:
            st.subheader("📊 Current Analysis")
            if self.session_service.current_session and self.session_service.current_session.focus_scores:
                latest_score = self.session_service.current_session.focus_scores[-1].score
                latest_state = self.session_service.current_session.focus_scores[-1].study_state

                color_map = {
                    "Focused": "#4CAF50",
                    "Distracted": "#FF9800",
                    "Break": "#2196F3",
                    "Fatigued": "#F44336",
                    "Idle": "#9E9E9E",
                }

                focus_score_card(
                    latest_score,
                    latest_state,
                    color_map.get(latest_state, "#00D9FF"),
                )

        st.divider()

        # Charts row
        col_trend, col_detected = st.columns(2)

        with col_trend:
            st.subheader("📈 Focus Trend")
            if self.session_service.current_session and self.session_service.current_session.focus_scores:
                focus_scores = [fs.score for fs in self.session_service.current_session.focus_scores]
                st.plotly_chart(
                    create_focus_trend_chart(focus_scores),
                    use_container_width=True,
                )

        with col_detected:
            st.subheader("🔍 Detected Objects")
            if self.session_service.current_session and self.session_service.current_session.events:
                detected = set()
                for event in self.session_service.current_session.events:
                    detected.update(event.detected_objects)

                if detected:
                    for obj in sorted(detected):
                        st.write(f"• {obj.replace('_', ' ').title()}")
                else:
                    st.write("No objects detected yet")

        st.divider()

        # AI Advice row
        st.subheader("💡 AI Insights")
        if self.session_service.current_session and self.session_service.current_session.focus_scores:
            insights = self.focus_service.get_focus_insights(
                [fs.score for fs in self.session_service.current_session.focus_scores]
            )
            for insight in insights:
                st.info(insight)

    def run(self):
        """Run dashboard."""
        self.setup_page()

        # Initialize session state
        if "current_session" not in st.session_state:
            st.session_state.current_session = None
        if "show_camera" not in st.session_state:
            st.session_state.show_camera = True

        # Render sidebar
        self.render_sidebar()

        # Render main content
        self.render_main_dashboard()

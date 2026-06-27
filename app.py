"""
FocusLens - AI Study Intelligence System
Main Streamlit Application
"""

import streamlit as st
import time
import cv2
from datetime import datetime
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
from ui.dashboard import Dashboard
from utils.helpers import format_duration

# Configure logger
LoggerService.initialize()
logger = LoggerService.get_logger(__name__)


def initialize_services():
    """Initialize all services."""
    try:
        db = Database(Config.DATABASE_PATH)
        camera = CameraService(Config.CAMERA_INDEX)
        vision = VisionService()
        gemini = GeminiService()
        voice = VoiceService()
        session_service = SessionService(db)
        focus_service = FocusService()
        analytics = AnalyticsService(db, gemini)

        return {
            "db": db,
            "camera": camera,
            "vision": vision,
            "gemini": gemini,
            "voice": voice,
            "session_service": session_service,
            "focus_service": focus_service,
            "analytics": analytics,
        }
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        st.error("Failed to initialize services. Check logs for details.")
        return None


def run_analysis_loop(services: dict):
    """Run the main analysis loop."""
    session_service = services["session_service"]
    camera = services["camera"]
    vision = services["vision"]
    gemini = services["gemini"]
    voice = services["voice"]
    focus_service = services["focus_service"]
    analytics = services["analytics"]

    if not session_service.is_session_active():
        st.warning("No active session")
        return

    # Get frame
    frame = camera.get_frame()
    if frame is None:
        st.warning("Could not capture frame")
        return

    # Analyze vision
    vision_analysis = vision.analyze_frame(frame)

    if not vision_analysis.get("analysis_successful"):
        st.warning("Vision analysis failed")
        return

    detected_objects = vision_analysis.get("detected_objects", [])
    head_pose = vision_analysis.get("head_pose", {})

    # Get AI analysis
    ai_analysis = gemini.analyze_vision(detected_objects, head_pose)

    # Calculate focus score
    focus_score = focus_service.analyze_focus(
        detected_objects,
        head_pose.get("is_looking", True),
        head_pose.get("fatigue_level", "Normal"),
        ai_analysis.get("study_state", "Idle"),
    )

    # Add event to session
    session_service.add_event(
        event_type=ai_analysis.get("event", "ANALYSIS"),
        study_state=ai_analysis.get("study_state", "Idle"),
        focus_score=focus_score,
        detected_objects=detected_objects,
        voice_message=ai_analysis.get("voice_message", ""),
        dashboard_message=ai_analysis.get("dashboard_message", ""),
        metadata={
            "head_pose": head_pose,
            "recommended_action": ai_analysis.get("recommended_action", "Continue"),
        },
    )

    # Add focus score
    session_service.add_focus_score(
        score=focus_score,
        study_state=ai_analysis.get("study_state", "Idle"),
        detected_objects=detected_objects,
    )

    # Speak message if enabled
    if voice.should_speak() and ai_analysis.get("voice_message"):
        voice.speak_async(ai_analysis["voice_message"])

    logger.debug(
        f"Analysis: Focus={focus_score}, State={ai_analysis.get('study_state')}, Objects={detected_objects}"
    )

    return {
        "frame": frame,
        "detected_objects": detected_objects,
        "focus_score": focus_score,
        "study_state": ai_analysis.get("study_state"),
        "head_pose": head_pose,
        "ai_analysis": ai_analysis,
    }


def main():
    """Main application."""
    # Page config
    st.set_page_config(
        page_title="FocusLens - AI Study Intelligence",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Apply theme
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

    # Initialize services
    if "services" not in st.session_state:
        st.session_state.services = initialize_services()

    if st.session_state.services is None:
        st.error("Failed to initialize application")
        return

    services = st.session_state.services

    # Sidebar
    with st.sidebar:
        st.markdown("# 🎯 FocusLens")
        st.markdown("### AI Study Intelligence")

        st.divider()

        # Configuration validation
        st.subheader("🔐 Configuration")

        if Config.GEMINI_API_KEY:
            st.success("✓ Gemini API configured")
        else:
            st.error("✗ Gemini API key missing")

        if Config.AFFERENS_API_KEY:
            st.success("✓ Afferens API configured")
        else:
            st.warning("⚠ Afferens API key missing (using mock)")

        st.divider()

        # Quick controls
        st.subheader("⚡ Quick Control")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("▶ Start", use_container_width=True, key="start_btn"):
                session = services["session_service"].start_session()
                if session:
                    st.session_state.active_session = session.session_id
                    st.success("Session started!")
                    st.rerun()

        with col2:
            if st.button("⏹ Stop", use_container_width=True, key="stop_btn"):
                session = services["session_service"].end_session()
                if session:
                    services["camera"].release()
                    st.session_state.active_session = None
                    st.success("Session ended!")
                    st.rerun()

        st.divider()

        # Settings
        st.subheader("⚙️ Settings")

        voice_toggle = st.checkbox(
            "🔊 Voice",
            value=services["voice"].enabled,
        )
        services["voice"].enabled = voice_toggle

        show_camera = st.checkbox(
            "📹 Show Camera",
            value=True,
        )

        st.divider()

        # Session info
        if services["session_service"].is_session_active():
            st.subheader("📊 Session Stats")

            stats = services["session_service"].get_session_stats()

            st.metric(
                "⏱️ Study Time",
                format_duration(stats.get("study_duration", 0)),
            )

            st.metric(
                "🎯 Avg Focus",
                f"{stats.get('average_focus_score', 0):.0f}/100",
            )

            st.metric(
                "⚠️ Distractions",
                stats.get("distractions_count", 0),
            )

        else:
            st.info("📌 No active session")

    # Main content
    st.markdown("# 🎯 FocusLens Dashboard")
    st.markdown(f"*AI Study Intelligence • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    st.divider()

    if not services["session_service"].is_session_active():
        st.info("👈 Start a session from the sidebar to begin!")

        # Show info
        with st.expander("📖 How to Use FocusLens"):
            st.markdown("""
            ### Getting Started
            
            1. **Start a Session**: Click the ▶ Start button
            2. **Position Camera**: Ensure your workspace is visible
            3. **Begin Studying**: The AI will monitor your focus in real-time
            4. **Get Guidance**: Receive voice tips and on-screen suggestions
            5. **End Session**: Click ⏹ Stop to finalize the session
            
            ### Features
            
            - 🎯 **Focus Tracking**: Real-time focus score assessment
            - 📱 **Distraction Detection**: Phone and other distraction alerts
            - 🧠 **AI Reasoning**: Gemini-powered insights and recommendations
            - 🔊 **Voice Guidance**: Natural language AI assistant
            - 📊 **Analytics**: Comprehensive reports and trends
            - ☕ **Break Recommendations**: Smart break suggestions
            
            ### Navigation
            
            - **📊 Analytics**: View detailed productivity patterns
            - **📄 Reports**: Generate comprehensive study reports
            - **⚙️ Settings**: Configure preferences
            """)

        return

    # Active session content
    col_main, col_sidebar = st.columns([3, 1])

    with col_main:
        st.subheader("📹 Live Analysis")

        # Placeholder for analysis
        placeholder_frame = st.empty()
        placeholder_analysis = st.empty()
        placeholder_chart = st.empty()

        # Run analysis
        analysis_result = run_analysis_loop(services)

        if analysis_result:
            # Display frame
            with placeholder_frame:
                # Convert to RGB for display
                display_frame = cv2.cvtColor(analysis_result["frame"], cv2.COLOR_BGR2RGB)
                st.image(display_frame, use_column_width=True)

            # Display analysis
            with placeholder_analysis:
                col1, col2, col3 = st.columns(3)

                with col1:
                    score = analysis_result["focus_score"]
                    color = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
                    st.metric(f"{color} Focus Score", f"{score}/100")

                with col2:
                    state = analysis_result["study_state"]
                    st.metric("📊 State", state)

                with col3:
                    objects = len(analysis_result["detected_objects"])
                    st.metric("🔍 Objects", objects)

            # Display chart
            with placeholder_chart:
                if services["session_service"].current_session:
                    scores = [fs.score for fs in services["session_service"].current_session.focus_scores]
                    if scores:
                        from ui.charts import create_focus_trend_chart
                        st.plotly_chart(
                            create_focus_trend_chart(scores),
                            use_container_width=True,
                        )

    with col_sidebar:
        st.subheader("💬 AI Insight")
        if analysis_result:
            st.info(analysis_result["ai_analysis"].get("voice_message", "Analyzing..."))

    st.divider()

    # Additional info
    st.subheader("📌 Current Session Details")

    if services["session_service"].is_session_active():
        stats = services["session_service"].get_session_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Study Time", format_duration(stats.get("study_duration", 0)))

        with col2:
            st.metric("Peak Focus", f"{stats.get('max_focus_score', 0)}/100")

        with col3:
            st.metric("Distractions", stats.get("distractions_count", 0))

        with col4:
            st.metric("Events", stats.get("events_count", 0))


if __name__ == "__main__":
    main()

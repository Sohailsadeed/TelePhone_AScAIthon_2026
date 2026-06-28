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


def run_analysis_loop(services: dict, frame_placeholder, analysis_placeholder, chart_placeholder, sidebar_placeholder, metrics_placeholders):
    """Run the main analysis loop components continuously."""
    session_service = services["session_service"]
    camera = services["camera"]
    vision = services["vision"]
    gemini = services["gemini"]
    voice = services["voice"]
    focus_service = services["focus_service"]
    analytics = services["analytics"]

    if not session_service.is_session_active():
        return False

    # Get frame
    frame = camera.get_frame()
    if frame is None:
        frame_placeholder.warning("Could not capture frame")
        return True

    # Analyze vision
    vision_analysis = vision.analyze_frame(frame)

    if not vision_analysis.get("analysis_successful"):
        analysis_placeholder.warning("Vision analysis failed")
        return True

    detected_objects = vision_analysis.get("detected_objects", [])
    head_pose = vision_analysis.get("head_pose", {})
    if "timestamp" in head_pose:
        head_pose["timestamp"] = (
            head_pose["timestamp"].isoformat()
            if isinstance(head_pose["timestamp"], datetime)
            else head_pose["timestamp"]
        )

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

    # --- Live Rendering Updates ---
    
    # 1. Update Video Frame Display
    display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_placeholder.image(display_frame, use_container_width=True)

    # 2. Update Live Analysis Sub-metrics
    with analysis_placeholder:
        col1, col2, col3 = st.columns(3)
        with col1:
            color = "🟢" if focus_score >= 80 else "🟡" if focus_score >= 50 else "🔴"
            st.metric(f"{color} Focus Score", f"{focus_score}/100")
        with col2:
            st.metric("📊 State", ai_analysis.get("study_state", "Idle"))
        with col3:
            st.metric("🔍 Objects", len(detected_objects))

    # 3. Update Chart
    if session_service.current_session:
        scores = [fs.score for fs in session_service.current_session.focus_scores]
        if scores:
            with chart_placeholder:
                from ui.charts import create_focus_trend_chart
                st.plotly_chart(
                    create_focus_trend_chart(scores),
                    use_container_width=True,
                )

    # 4. Update Sidebar AI Insights Container
    sidebar_placeholder.info(ai_analysis.get("voice_message", "Analyzing..."))

    # 5. Update Bottom Session Analytics Layout
    stats = session_service.get_session_stats()
    m_col1, m_col2, m_col3, m_col4 = metrics_placeholders
    m_col1.metric("Study Time", format_duration(stats.get("study_duration", 0)))
    m_col2.metric("Peak Focus", f"{stats.get('max_focus_score', 0)}/100")
    m_col3.metric("Distractions", stats.get("distractions_count", 0))
    m_col4.metric("Events", stats.get("events_count", 0))

    logger.debug(
        f"Analysis: Focus={focus_score}, State={ai_analysis.get('study_state')}, Objects={detected_objects}"
    )
    return True


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

    # Sidebar UI Layout
    with st.sidebar:
        st.markdown("# 🎯 FocusLens")
        st.markdown("### AI Study Intelligence")
        st.divider()

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

        st.subheader("⚙️ Settings")
        voice_toggle = st.checkbox("🔊 Voice", value=services["voice"].enabled)
        services["voice"].enabled = voice_toggle

        show_camera = st.checkbox("📹 Show Camera", value=True)
        st.divider()

        # Context-dependent Sidebar Stats Container
        sidebar_stats_container = st.container()

    # Main Dashboard Header Layout
    st.markdown("# 🎯 FocusLens Dashboard")
    st.markdown(f"*AI Study Intelligence • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    st.divider()

    # Handling Non-Active Session State View
    if not services["session_service"].is_session_active():
        with sidebar_stats_container:
            st.info("📌 No active session")
            
        st.info("👈 Start a session from the sidebar to begin!")
        with st.expander("📖 How to Use FocusLens"):
            st.markdown("""
            ### Getting Started
            1. **Start a Session**: Click the ▶ Start button
            2. **Position Camera**: Ensure your workspace is visible
            3. **Begin Studying**: The AI will monitor your focus in real-time
            4. **Get Guidance**: Receive voice tips and on-screen suggestions
            5. **End Session**: Click ⏹ Stop to finalize the session
            """)
        return

    # --- Setup Structural Placeholders for Streaming Loop ---
    col_main, col_sidebar = st.columns([3, 1])

    with col_main:
        st.subheader("📹 Live Analysis")
        placeholder_frame = st.empty()
        placeholder_analysis = st.empty()
        placeholder_chart = st.empty()

    with col_sidebar:
        st.subheader("💬 AI Insight")
        placeholder_ai_insight = st.empty()

    st.divider()
    st.subheader("📌 Current Session Details")
    
    # Initialize Persistent Bottom Metrics Layout Block
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    metrics_elements = (m_col1.empty(), m_col2.empty(), m_col3.empty(), m_col4.empty())

    # --- Live Running Driver Core Loop ---
    while services["session_service"].is_session_active():
        # Update Sidebar Live Session Metrics Counter UI Panel
        with sidebar_stats_container:
            stats = services["session_service"].get_session_stats()
            st.metric("⏱️ Study Time", format_duration(stats.get("study_duration", 0)))
            st.metric("🎯 Avg Focus", f"{stats.get('average_focus_score', 0):.0f}/100")
            st.metric("⚠️ Distractions", stats.get("distractions_count", 0))

        # Check if the user turned off the camera view feature via toggle
        if not show_camera:
            placeholder_frame.info("Camera view visibility disabled by preference.")

        # Run one tick of downstream operations and data analysis pipeline
        keep_looping = run_analysis_loop(
            services,
            frame_placeholder=placeholder_frame if show_camera else st.empty(),
            analysis_placeholder=placeholder_analysis,
            chart_placeholder=placeholder_chart,
            sidebar_placeholder=placeholder_ai_insight,
            metrics_placeholders=metrics_elements
        )
        
        if not keep_looping:
            break
            
        # Match loop intervals to hardware configuration values (~30 FPS or custom interval sleep)
        time.sleep(0.1)


if __name__ == "__main__":
    main()

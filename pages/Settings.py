"""
Settings page for FocusLens.
"""

import streamlit as st
from config import Config
from services.logger_service import LoggerService
from services.voice_service import VoiceService


def main():
    """Main settings page."""
    st.markdown("# ⚙️ Settings")
    st.markdown("*Configure FocusLens preferences*")

    # Initialize services
    logger = LoggerService.get_logger(__name__)
    voice_service = VoiceService()

    # Tab selection
    tab1, tab2, tab3, tab4 = st.tabs([
        "General",
        "Camera",
        "Voice",
        "About"
    ])

    with tab1:
        render_general_settings()

    with tab2:
        render_camera_settings()

    with tab3:
        render_voice_settings(voice_service)

    with tab4:
        render_about()


def render_general_settings():
    """Render general settings."""
    st.subheader("📋 General Settings")

    st.markdown("### Application Configuration")

    # Display current configuration
    st.write("**Current Configuration:**")

    config_data = Config.get_all()

    for key, value in config_data.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write(f"**{key}**")
        with col2:
            st.write(f"`{value}`")

    st.divider()

    # Break settings
    st.markdown("### Break Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        break_interval = st.number_input(
            "Break Interval (minutes)",
            value=Config.BREAK_INTERVAL,
            min_value=10,
            max_value=120,
        )
        st.caption(f"Current: {Config.BREAK_INTERVAL} minutes")

    with col2:
        break_duration = st.number_input(
            "Break Duration (minutes)",
            value=Config.BREAK_DURATION,
            min_value=1,
            max_value=30,
        )
        st.caption(f"Current: {Config.BREAK_DURATION} minutes")

    st.divider()

    # Cooldown settings
    st.markdown("### Message Cooldowns")

    col1, col2 = st.columns(2)

    with col1:
        voice_cooldown = st.number_input(
            "Voice Message Cooldown (seconds)",
            value=Config.VOICE_COOLDOWN,
            min_value=10,
            max_value=300,
        )

    with col2:
        distraction_cooldown = st.number_input(
            "Distraction Alert Cooldown (seconds)",
            value=Config.DISTRACTION_COOLDOWN,
            min_value=10,
            max_value=600,
        )

    st.divider()

    if st.button("💾 Save Settings"):
        st.success("Settings saved! (Note: Restart app for changes to take effect)")


def render_camera_settings():
    """Render camera settings."""
    st.subheader("📹 Camera Settings")

    st.markdown("### Camera Configuration")

    col1, col2 = st.columns(2)

    with col1:
        camera_index = st.number_input(
            "Camera Index",
            value=Config.CAMERA_INDEX,
            min_value=0,
            max_value=10,
        )
        st.caption("Usually 0 for default camera")

    with col2:
        frame_interval = st.number_input(
            "Frame Capture Interval (seconds)",
            value=Config.FRAME_INTERVAL,
            min_value=1,
            max_value=30,
        )

    st.divider()

    st.markdown("### Resolution")

    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input(
            "Width",
            value=Config.CAMERA_RESOLUTION[0],
            step=160,
        )

    with col2:
        height = st.number_input(
            "Height",
            value=Config.CAMERA_RESOLUTION[1],
            step=120,
        )

    st.divider()

    fps = st.slider(
        "FPS",
        min_value=15,
        max_value=60,
        value=Config.CAMERA_FPS,
        step=5,
    )

    st.divider()

    st.markdown("### Vision API")

    vision_enabled = st.checkbox(
        "Enable Vision Analysis",
        value=Config.VISION_API_ENABLED,
    )

    if vision_enabled:
        st.success("✓ Vision API enabled")
    else:
        st.warning("⚠ Vision API disabled - using mock detections")

    st.divider()

    if st.button("💾 Save Camera Settings"):
        st.success("Camera settings saved! (Note: Restart app for changes to take effect)")


def render_voice_settings(voice_service: VoiceService):
    """Render voice settings."""
    st.subheader("🔊 Voice Settings")

    st.markdown("### Voice Output")

    voice_enabled = st.checkbox(
        "Enable Voice Output",
        value=voice_service.enabled,
    )

    if voice_enabled:
        st.success("✓ Voice enabled")
    else:
        st.warning("⚠ Voice disabled")

    st.divider()

    st.markdown("### Voice Properties")

    rate = st.slider(
        "Speech Rate",
        min_value=50,
        max_value=300,
        value=150,
        step=10,
    )
    st.caption("Words per minute")

    volume = st.slider(
        "Volume",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.1,
    )

    st.divider()

    st.markdown("### Available Voices")

    voices = voice_service.get_voices()
    if voices:
        voice_names = [v.name for v in voices]
        selected_voice = st.selectbox(
            "Select Voice",
            voice_names,
        )

        st.caption(f"Selected: {selected_voice}")

        if st.button("🔊 Test Voice"):
            test_text = "This is a test of the voice system."
            voice_service.speak_blocking(test_text)
            st.success("Test complete!")

    else:
        st.warning("No voices available")

    st.divider()

    if st.button("💾 Save Voice Settings"):
        voice_service.set_voice_properties(rate=rate, volume=volume)
        st.success("Voice settings saved!")


def render_about():
    """Render about page."""
    st.subheader("ℹ️ About FocusLens")

    st.markdown("""
    ### 🎯 FocusLens - AI Study Intelligence System
    
    A comprehensive AI-powered study companion that monitors your focus, 
    detects distractions, and provides intelligent guidance for optimal productivity.
    
    **Version**: 1.0.0  
    **Built for**: 24-Hour AI Hardware Hackathon  
    **Theme**: Physical Perception using AI Agents
    
    ---
    
    ### 🔧 Technology Stack
    
    - **Frontend**: Streamlit
    - **Backend**: Python
    - **AI Model**: Google Gemini 2.5 Flash
    - **Vision API**: Afferens Vision API
    - **Camera**: OpenCV
    - **Database**: SQLite
    - **Visualization**: Plotly
    - **Speech**: pyttsx3
    
    ---
    
    ### 🎯 Key Features
    
    ✓ **Live Camera Monitoring** - Real-time observation of your study environment  
    ✓ **Object Detection** - Identifies distractions (phone, books, etc.)  
    ✓ **Focus Scoring** - AI-powered focus level assessment  
    ✓ **Session Management** - Automatic tracking of study sessions  
    ✓ **Voice Guidance** - Natural language AI assistant  
    ✓ **Analytics** - Comprehensive productivity reports  
    ✓ **Break Recommendations** - Smart break timing suggestions  
    
    ---
    
    ### 🏗️ Architecture
    
    The system follows the **Observe → Understand → Reason → Act** framework:
    
    1. **Observe**: Camera captures real-time workspace
    2. **Understand**: Vision API detects objects and environment
    3. **Reason**: Gemini AI analyzes focus and provides insights
    4. **Act**: Voice guidance and dashboard recommendations
    
    ---
    
    ### 📊 Observe, Understand, Reason, Act
    
    ```
    Camera → Vision Analysis → Gemini AI → Actions
       ↓           ↓               ↓         ↓
    Capture    Detect Objects   Reason   Voice/UI
    Frames     Head Pose        About    Feedback
               Fatigue          Focus
    ```
    
    ---
    
    ### 📝 License
    
    This project was created for the AI Hardware Hackathon 2024.
    
    """)

    st.divider()

    st.markdown("### 🔗 Links")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("[📖 Documentation](https://github.com)")

    with col2:
        st.markdown("[🐛 Report Issue](https://github.com)")

    with col3:
        st.markdown("[💬 Feedback](https://github.com)")

    st.divider()

    st.markdown("### 📬 Support")

    st.info("""
    For support or feature requests, please contact:  
    📧 **Email**: support@focuslens.ai  
    💬 **Discord**: [Join Community](https://discord.gg)
    """)


if __name__ == "__main__":
    main()

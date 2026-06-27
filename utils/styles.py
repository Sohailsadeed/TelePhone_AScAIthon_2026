"""
UI Styles and CSS for Streamlit dashboard.
"""

STREAMLIT_CONFIG = """
[theme]
primaryColor = "#00D9FF"
backgroundColor = "#0e1419"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
font = "sans serif"

[client]
showErrorDetails = false
"""

CUSTOM_CSS = """
<style>
    /* Main Container */
    .main {
        background-color: #0e1419;
        color: #fafafa;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #262730 100%);
        border-radius: 10px;
        padding: 20px;
        border-left: 4px solid #00D9FF;
        box-shadow: 0 4px 15px rgba(0, 217, 255, 0.1);
    }
    
    .focused-card {
        border-left-color: #4CAF50;
    }
    
    .distracted-card {
        border-left-color: #FF9800;
    }
    
    .break-card {
        border-left-color: #2196F3;
    }
    
    .fatigued-card {
        border-left-color: #F44336;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00D9FF;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00D9FF 0%, #0099cc 100%);
        color: #0e1419;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    .sidebar {
        background-color: #1a1f2e;
    }
    
    /* Progress Bar */
    .progress-bar {
        background: linear-gradient(90deg, #00D9FF 0%, #0099cc 100%);
        border-radius: 5px;
    }
    
    /* Metric Values */
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #00D9FF;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #b0bec5;
    }
</style>
"""

# Color Palette
COLOR_PALETTE = {
    "primary": "#00D9FF",
    "secondary": "#0099cc",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "danger": "#F44336",
    "info": "#2196F3",
    "dark": "#0e1419",
    "light": "#fafafa",
    "background": "#262730",
}

# Grade Colors
GRADE_COLORS = {
    "A": "#4CAF50",  # Green
    "B": "#8BC34A",  # Light Green
    "C": "#FFC107",  # Yellow
    "D": "#FF9800",  # Orange
    "F": "#F44336",  # Red
}

# Status Indicators
STATUS_INDICATORS = {
    "FOCUSED": "🟢 Focused",
    "DISTRACTED": "🟠 Distracted",
    "BREAK": "🔵 Break",
    "FATIGUED": "🔴 Fatigued",
    "IDLE": "⚪ Idle",
}

# Emotion Icons
EMOTION_ICONS = {
    "focused": "🎯",
    "distracted": "😕",
    "break": "☕",
    "fatigued": "😴",
    "idle": "😐",
    "celebrating": "🎉",
}

# 🎯 FocusLens – AI Study Intelligence System

**Built for the 24-Hour AI Hardware Hackathon**

A comprehensive AI-powered study assistant that continuously observes your workspace through a webcam, understands the environment using computer vision, reasons about your focus state using AI, and provides intelligent guidance for optimal productivity.

```
Observe → Understand → Reason → Act
   ↓          ↓          ↓        ↓
Camera    Vision API  Gemini  Voice/UI
```

---

## 🌟 Features

### 📹 Live Camera Monitoring
- Real-time workspace observation
- Continuous frame capture and analysis
- Customizable camera resolution and FPS

### 🔍 Object Detection
Detects and tracks:
- Person
- Phone
- Books & Notebooks
- Coffee Cup
- Backpack
- Keyboard & Mouse
- Empty Chair
- Head pose & Eye gaze
- Fatigue levels

### 🧠 AI-Powered Analysis
- **Gemini 2.5 Flash** reasoning about focus state
- Real-time study state classification:
  - Focused ✓
  - Distracted ⚠️
  - On Break ☕
  - Fatigued 😴
  - Idle 🔴

### 📊 Focus Tracking
- Real-time focus score (0-100)
- Focus trends and patterns
- Historical analysis
- Performance insights

### 🔊 Voice Guidance
- Natural language AI responses
- Smart cooldown to prevent spam
- Context-aware recommendations
- Motivational messages

### 📱 Distraction Detection
- Phone distraction alerts
- Distraction logging and analysis
- Patterns identification
- Targeted interventions

### ⏰ Session Management
- Automatic session tracking
- Pause/resume functionality
- Break recommendations
- Session statistics

### 📈 Analytics & Reports
- Daily reports
- Weekly summaries
- Focus distribution analysis
- Distraction patterns
- Productivity trends

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────┐
│           Streamlit Dashboard               │
├─────────────────────────────────────────────┤
│  Dashboard │ Analytics │ Reports │ Settings  │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Camera │ │ Vision │ │ Gemini │
    │Service │ │Service │ │Service │
    └────────┘ └────────┘ └────────┘
        ↓          ↓          ↓
        └──────────┼──────────┘
                   ↓
         ┌─────────────────────┐
         │  Session Service    │
         │  Focus Service      │
         │  Voice Service      │
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │   SQLite Database   │
         └─────────────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit 1.28+ |
| **Backend** | Python 3.8+ |
| **AI/ML** | Google Gemini 2.5 Flash |
| **Vision** | Afferens Vision API + OpenCV |
| **Database** | SQLite3 |
| **Charts** | Plotly |
| **Voice** | pyttsx3 |
| **HTTP** | Requests |

---

## 📋 Project Structure

```
FocusLens/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env.example             # Environment variables template
│
├── database/
│   └── database.py          # SQLite database management
│
├── services/
│   ├── logger_service.py    # Logging service
│   ├── camera_service.py    # Camera capture & management
│   ├── vision_service.py    # Afferens Vision API integration
│   ├── gemini_service.py    # Google Gemini AI integration
│   ├── voice_service.py     # Text-to-speech service
│   ├── session_service.py   # Study session management
│   ├── focus_service.py     # Focus analysis service
│   └── analytics_service.py # Report generation service
│
├── ui/
│   ├── dashboard.py         # Main dashboard controller
│   ├── cards.py             # UI card components
│   ├── charts.py            # Plotly chart components
│   └── camera_view.py       # Camera display component
│
├── pages/
│   ├── Analytics.py         # Analytics page
│   ├── Reports.py           # Reports page
│   └── Settings.py          # Settings page
│
├── models/
│   └── session.py           # Data models
│
├── utils/
│   ├── constants.py         # Application constants
│   ├── helpers.py           # Helper functions
│   ├── prompts.py           # Gemini prompts
│   └── styles.py            # UI styles
│
├── logs/                    # Application logs
│   └── focuslens.log       # Log file (generated)
│
└── reports/                 # Generated reports
    └── (generated reports)
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Webcam
- GPU recommended (for faster processing)

### Setup Steps

1. **Clone or extract the repository**
   ```bash
   cd focuslensai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - Navigate to `http://localhost:8501`

---

## 🔐 Environment Setup

### Required API Keys

#### Google Gemini API
1. Visit https://ai.google.dev/
2. Create a new API key
3. Add to `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

#### Afferens Vision API (Optional)
1. Visit https://www.afferens.ai/
2. Sign up and get API key
3. Add to `.env`:
   ```
   AFFERENS_API_KEY=your_key_here
   ```

### Configuration File

Create a `.env` file in the project root:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
AFFERENS_API_KEY=your_afferens_api_key

# Database
DATABASE_PATH=focuslens.db

# Camera (defaults to 1280x720 @ 30fps)
CAMERA_INDEX=0
FRAME_INTERVAL=5
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FPS=30

# Features
VOICE_ENABLED=true
VISION_API_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=focuslens.log

# Break & Focus Settings
BREAK_INTERVAL=40
BREAK_DURATION=5
VOICE_COOLDOWN=30
```

---

## 📖 Usage

### Starting a Session

1. **Click "▶ Start Session"** in the sidebar
2. **Position your camera** to see your workspace
3. **Begin studying** - the AI automatically monitors you

### During a Session

- 📊 **Dashboard**: Real-time focus score and status
- 📹 **Camera Feed**: Live workspace monitoring with annotations
- 💬 **AI Insights**: Voice guidance and recommendations
- ⚠️ **Alerts**: Distraction notifications

### Ending a Session

1. **Click "⏹ End Session"** when finished
2. **AI generates report** with:
   - Study duration
   - Focus statistics
   - Achievements
   - Improvement areas
   - Personalized suggestions

### Analyzing Results

- **📊 Analytics Tab**: Trends, patterns, distribution
- **📄 Reports Tab**: Daily/weekly/session reports
- **⚙️ Settings Tab**: Configuration & preferences

---

## 💡 How It Works

### The Observe-Understand-Reason-Act Framework

#### 1. **Observe** 📹
- Camera captures frames at configured interval
- Preprocesses images for analysis
- Maintains frame buffer for processing

#### 2. **Understand** 🔍
- **Vision API** detects:
  - Objects in the scene
  - Head pose and eye gaze
  - Fatigue indicators
- Extracts environmental context
- Analyzes visual features

#### 3. **Reason** 🧠
- **Gemini AI** analyzes:
  - Current focus state
  - Presence of distractions
  - Motivation level
  - Break recommendations
- Returns JSON with insights
- Determines recommended action

#### 4. **Act** 🔊
- **Voice feedback**: Natural language response
- **Dashboard update**: Real-time metrics
- **Database logging**: Event recording
- **Session tracking**: Continuous monitoring

### Focus Scoring Algorithm

```
Base Score: 100

Adjustments:
- Distracting object detected:        -15 per object
- Not looking at screen:              -20
- High fatigue:                        -25
- Study materials present:              +5
- Input devices visible:                +3

Final Score: MAX(0, MIN(100, adjusted))
```

---

## 📊 Data Models

### Session
```python
{
    "session_id": "unique_id",
    "start_time": "ISO timestamp",
    "end_time": "ISO timestamp",
    "study_duration": 1800,  # seconds
    "average_focus_score": 85.5,
    "events": [...],
    "focus_scores": [...],
    "distractions": [...]
}
```

### Event
```python
{
    "event_id": "unique_id",
    "session_id": "session_id",
    "event_type": "FOCUS|DISTRACTION|BREAK",
    "timestamp": "ISO timestamp",
    "study_state": "Focused|Distracted|Break|Fatigued",
    "focus_score": 85,
    "detected_objects": ["phone", "keyboard"],
    "voice_message": "Great focus!",
    "metadata": {...}
}
```

### Report
```python
{
    "report_id": "unique_id",
    "session_id": "session_id",
    "study_duration_str": "30m",
    "average_focus_score": 82.3,
    "distractions_count": 3,
    "summary": "AI generated summary",
    "achievements": ["Maintained 80+ focus", ...],
    "suggestions": ["Take more breaks", ...]
}
```

---

## 🎯 Gemini Prompts

The system uses specialized prompts for different scenarios:

### Vision Analysis Prompt
```
Analyze detected objects and head pose.
Return: study_state, focus_score, voice_message, recommended_action
```

### Session Summary Prompt
```
Summarize study session performance.
Return: achievements, improvements, suggestions, rating
```

### Break Recommendation Prompt
```
Should user take a break?
Return: should_break, break_reason, break_duration, activity
```

---

## 📊 Database Schema

### Tables

**sessions**
- session_id (PK)
- start_time, end_time
- study_duration, break_duration
- average_focus_score
- phone_detections

**events**
- event_id (PK)
- session_id (FK)
- event_type, timestamp
- study_state, focus_score
- detected_objects, voice_message

**focus_scores**
- score_id (PK)
- session_id (FK), timestamp
- score, study_state
- detected_objects

**distractions**
- distraction_id (PK)
- session_id (FK), timestamp
- object_type, duration_seconds

**reports**
- report_id (PK)
- session_id (FK)
- summary, achievements
- suggestions, overall_rating

---

## 🔧 Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `CAMERA_INDEX` | 0 | Webcam index |
| `FRAME_INTERVAL` | 5 | Seconds between frame analysis |
| `VOICE_ENABLED` | true | Enable text-to-speech |
| `VOICE_COOLDOWN` | 30 | Seconds between voice messages |
| `BREAK_INTERVAL` | 40 | Minutes before break recommendation |
| `FOCUS_SCORE_THRESHOLD` | 80 | High focus score threshold |
| `TEMPERATURE` | 0.7 | Gemini temperature (creativity) |
| `MAX_TOKENS` | 500 | Gemini max response tokens |

---

## 🚨 Troubleshooting

### Camera Not Working
- Check camera permissions
- Verify `CAMERA_INDEX` (try 0, 1, 2...)
- Test with `python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`

### Gemini API Errors
- Verify API key in `.env`
- Check internet connection
- Ensure API quotas not exceeded

### Voice Not Working
- Check `VOICE_ENABLED=true` in `.env`
- Verify speaker volume
- On Linux, may need: `sudo apt-get install espeak`

### Database Issues
- Delete `focuslens.db` to reset
- Check write permissions in directory

---

## 📈 Performance Tips

1. **Adjust Frame Interval**: Higher = faster, lower accuracy
2. **Reduce Camera Resolution**: Speeds up processing
3. **Use GPU**: Install CUDA for faster inference
4. **Close Background Apps**: Reduces system load
5. **Good Lighting**: Improves detection accuracy

---

## 🔮 Future Enhancements

- [ ] Multiple camera support
- [ ] Emotion recognition
- [ ] Pose estimation
- [ ] Hand gesture detection
- [ ] Multi-user support
- [ ] Cloud synchronization
- [ ] Mobile app companion
- [ ] Advanced calendar integration
- [ ] Team productivity analytics
- [ ] Custom AI model training
- [ ] Eye-tracking integration
- [ ] Biometric sensors

---

## 📄 License

This project was created for the AI Hardware Hackathon 2024.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

## 📞 Support

For issues, questions, or suggestions:
- 📧 Email: support@focuslens.ai
- 💬 Discord: [Join Community](#)
- 🐛 GitHub Issues: [Report Bug](#)

---

## 🙏 Acknowledgments

- **Google Gemini** for AI reasoning
- **Afferens Vision** for object detection
- **OpenCV** for computer vision
- **Streamlit** for rapid UI development
- **Plotly** for interactive visualizations

---

## 📊 Architecture Diagram

```
┌───────────────────────────────────────────────────────┐
│          FocusLens - AI Study Intelligence            │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Observe          Understand         Reason    Act   │
│  ┌────────┐       ┌──────────┐      ┌─────────┐     │
│  │ Camera │  -->  │ Afferens │ -->  │ Gemini  │     │
│  │OpenCV  │       │Vision API│      │2.5Flash │     │
│  └────────┘       └──────────┘      └────┬────┘     │
│                                           │          │
│                                           v          │
│                                    ┌──────────────┐  │
│                                    │Voice Output  │  │
│                                    │Dashboard UI  │  │
│                                    │Logging/Store │  │
│                                    └──────────────┘  │
│                                           │          │
│                                           v          │
│                                    ┌──────────────┐  │
│                                    │  SQLite DB   │  │
│                                    │Analytics    │  │
│                                    │Reports      │  │
│                                    └──────────────┘  │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

**Happy Studying! 🎓**

Built with ❤️ for the 24-Hour AI Hardware Hackathon

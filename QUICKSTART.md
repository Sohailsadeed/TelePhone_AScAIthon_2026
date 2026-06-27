# 🚀 FocusLens - Quick Start Guide

Get FocusLens running in 5 minutes!

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Gemini API key
```

**Need a Gemini API Key?**
1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Copy the key to `.env`

### 3. Run the App
```bash
streamlit run app.py
```

### 4. Open Browser
```
http://localhost:8501
```

## 🎯 First Session

1. Click **▶ Start Session** in the sidebar
2. Position your camera to see your desk
3. Start studying!
4. Watch the dashboard update in real-time
5. Click **⏹ End Session** when done

## 📊 View Results

- **📊 Analytics**: See focus trends
- **📄 Reports**: Get detailed session reports
- **⚙️ Settings**: Adjust preferences

## 🎮 Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Start Session | Click button |
| End Session | Click button |
| Toggle Camera | Checkbox |
| Toggle Voice | Checkbox |

## 🔊 Voice Features

The AI speaks when:
- Session starts/ends
- Distractions detected
- Time to take break
- Focus improves

## 📸 Camera Tips

- **Position**: Angle to see desk and face
- **Lighting**: Good natural or room lighting
- **Distance**: 2-3 feet from camera
- **Clean**: Wipe camera lens

## 🐛 Troubleshooting

### Camera Not Working?
```python
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'Failed')"
```

### API Key Error?
- Verify key in `.env`
- Check internet connection
- Restart app

### No Voice?
- Check `VOICE_ENABLED=true` in `.env`
- Check speaker volume
- Try test in Settings page

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

## 🆘 Need Help?

1. Check `.env` configuration
2. Run `python verify.py`
3. Check logs in `logs/focuslens.log`
4. Review README.md

---

**Happy Studying! 🎓**

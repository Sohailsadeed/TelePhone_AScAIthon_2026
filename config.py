"""
Configuration management for FocusLens.
Loads environment variables and provides configuration access.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file
ROOT = Path(__file__).parent
ENV_PATH = ROOT / ".env"
ENV_EXAMPLE_PATH = ROOT / ".env.example"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
elif ENV_EXAMPLE_PATH.exists():
    load_dotenv(ENV_EXAMPLE_PATH)


class Config:
    """Central configuration management."""

    # API Keys
    AFFERENS_API_KEY: str = os.getenv("AFFERENS_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "focuslens.db")

    # Camera Settings
    CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
    FRAME_INTERVAL: int = int(os.getenv("FRAME_INTERVAL", "5"))
    CAMERA_RESOLUTION: tuple = (int(os.getenv("CAMERA_WIDTH", "1280")), int(os.getenv("CAMERA_HEIGHT", "720")))
    CAMERA_FPS: int = int(os.getenv("CAMERA_FPS", "30"))

    # Features
    VOICE_ENABLED: bool = os.getenv("VOICE_ENABLED", "true").lower() == "true"
    VISION_API_ENABLED: bool = os.getenv("VISION_API_ENABLED", "true").lower() == "true"
    ANALYTICS_ENABLED: bool = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "focuslens.log")

    # Streamlit
    STREAMLIT_THEME: str = os.getenv("STREAMLIT_THEME", "dark")

    # Cooldown periods (seconds)
    VOICE_COOLDOWN: int = int(os.getenv("VOICE_COOLDOWN", "30"))
    DISTRACTION_COOLDOWN: int = int(os.getenv("DISTRACTION_COOLDOWN", "60"))

    # Break recommendations
    BREAK_INTERVAL: int = int(os.getenv("BREAK_INTERVAL", "40"))  # minutes
    BREAK_DURATION: int = int(os.getenv("BREAK_DURATION", "5"))  # minutes

    # Voice Settings
    DEFAULT_VOICE_SPEED: int = int(os.getenv("VOICE_SPEED", "150"))
    DEFAULT_VOICE_VOLUME: float = float(os.getenv("VOICE_VOLUME", "1.0"))
    DEFAULT_VOICE: str = os.getenv("VOICE_NAME", "default")

    # Focus thresholds
    FOCUS_SCORE_THRESHOLD: int = int(os.getenv("FOCUS_SCORE_THRESHOLD", "80"))

    # Model
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "500"))

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.GEMINI_API_KEY:
            print("WARNING: GEMINI_API_KEY not set in .env")
            return False
        return True

    @classmethod
    def get_all(cls) -> dict:
        """Get all configuration as dictionary."""
        return {
            "afferens_api_key": "***" if cls.AFFERENS_API_KEY else "NOT SET",
            "gemini_api_key": "***" if cls.GEMINI_API_KEY else "NOT SET",
            "database_path": cls.DATABASE_PATH,
            "camera_index": cls.CAMERA_INDEX,
            "frame_interval": cls.FRAME_INTERVAL,
            "camera_resolution": cls.CAMERA_RESOLUTION,
            "voice_enabled": cls.VOICE_ENABLED,
            "vision_api_enabled": cls.VISION_API_ENABLED,
            "analytics_enabled": cls.ANALYTICS_ENABLED,
            "log_level": cls.LOG_LEVEL,
            "gemini_model": cls.GEMINI_MODEL,
            "break_interval": cls.BREAK_INTERVAL,
        }

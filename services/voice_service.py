"""
Voice service for text-to-speech functionality.
"""

import pyttsx3
from typing import Optional
from datetime import datetime, timedelta
from config import Config
from services.logger_service import LoggerService

logger = LoggerService.get_logger(__name__)


class VoiceService:
    """Handles voice output using pyttsx3."""

    def __init__(self):
        """Initialize voice service."""
        self.enabled = Config.VOICE_ENABLED
        self.engine = None
        self.last_voice_time = None
        self.cooldown_seconds = Config.VOICE_COOLDOWN
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize text-to-speech engine."""
        if not self.enabled:
            logger.info("Voice service disabled")
            return

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", int(Config.DEFAULT_VOICE_SPEED))
            self.engine.setProperty("volume", 0.9)
            logger.info("Voice service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize voice service: {e}")
            self.enabled = False

    def speak(self, text: str, wait: bool = False) -> bool:
        """Speak text."""
        if not self.enabled or self.engine is None:
            return False

        try:
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
            else:
                # Non-blocking with async processing
                self.engine.startLoop(False)
                self.engine.iterate()
                self.engine.endLoop()

            self.last_voice_time = datetime.now()
            logger.debug(f"Voice: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Voice speaking error: {e}")
            return False

    def speak_async(self, text: str) -> bool:
        """Speak text asynchronously."""
        return self.speak(text, wait=False)

    def speak_blocking(self, text: str) -> bool:
        """Speak text and wait for completion."""
        return self.speak(text, wait=True)

    def should_speak(self) -> bool:
        """Check if enough time has passed since last voice message."""
        if self.last_voice_time is None:
            return True

        elapsed = (datetime.now() - self.last_voice_time).total_seconds()
        return elapsed >= self.cooldown_seconds

    def speak_if_ready(self, text: str) -> bool:
        """Speak only if cooldown has passed."""
        if not self.should_speak():
            logger.debug("Voice cooldown active")
            return False

        return self.speak_async(text)

    def set_voice_properties(
        self,
        rate: int = 150,
        volume: float = 0.9,
    ):
        """Set voice properties."""
        if self.engine is None:
            return

        try:
            self.engine.setProperty("rate", rate)
            self.engine.setProperty("volume", volume)
            logger.info(f"Voice properties updated: rate={rate}, volume={volume}")
        except Exception as e:
            logger.error(f"Error setting voice properties: {e}")

    def get_voices(self) -> list:
        """Get available voices."""
        if self.engine is None:
            return []

        try:
            return self.engine.getProperty("voices")
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []

    def set_voice(self, voice_id: int = 0):
        """Set active voice."""
        if self.engine is None:
            return

        try:
            voices = self.get_voices()
            if voice_id < len(voices):
                self.engine.setProperty("voice", voices[voice_id].id)
                logger.info(f"Voice set to: {voices[voice_id].name}")
        except Exception as e:
            logger.error(f"Error setting voice: {e}")

    def reset_cooldown(self):
        """Reset voice cooldown."""
        self.last_voice_time = None

    def pause(self):
        """Pause voice output."""
        if self.engine is not None:
            try:
                self.engine.pause()
            except Exception as e:
                logger.error(f"Error pausing voice: {e}")

    def resume(self):
        """Resume voice output."""
        if self.engine is not None:
            try:
                self.engine.resume()
            except Exception as e:
                logger.error(f"Error resuming voice: {e}")

    def stop(self):
        """Stop voice output."""
        if self.engine is not None:
            try:
                self.engine.stop()
                logger.info("Voice stopped")
            except Exception as e:
                logger.error(f"Error stopping voice: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.stop()

"""
Camera service for capturing video frames.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from datetime import datetime
from config import Config
from services.logger_service import LoggerService

logger = LoggerService.get_logger(__name__)


class CameraService:
    """Manages camera operations."""

    def __init__(self, camera_index: int = 0):
        """Initialize camera."""
        self.camera_index = camera_index
        self.cap = None
        self.last_frame = None
        self.is_initialized = False
        self._initialize_camera()

    def _initialize_camera(self):
        """Initialize camera capture."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_RESOLUTION[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_RESOLUTION[1])
            self.cap.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
            self.is_initialized = True
            logger.info(f"Camera initialized: {self.camera_index}")
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            self.is_initialized = False

    def get_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from camera."""
        if not self.is_initialized or self.cap is None:
            return None

        try:
            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame
                return frame
            else:
                logger.warning("Failed to read frame from camera")
                return None
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None

    def get_frame_rgb(self) -> Optional[np.ndarray]:
        """Get frame in RGB format."""
        frame = self.get_frame()
        if frame is not None:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the latest captured frame."""
        return self.last_frame

    def save_frame(self, filename: str) -> bool:
        """Save current frame to file."""
        if self.last_frame is None:
            return False

        try:
            cv2.imwrite(filename, self.last_frame)
            logger.info(f"Frame saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save frame: {e}")
            return False

    def get_frame_with_timestamp(self) -> Optional[Tuple[np.ndarray, str]]:
        """Get frame with timestamp."""
        frame = self.get_frame()
        if frame is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Add timestamp to frame
            cv2.putText(
                frame,
                timestamp,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            return frame, timestamp
        return None

    def get_frame_size(self) -> Tuple[int, int]:
        """Get frame dimensions."""
        if self.cap is None:
            return (0, 0)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def is_opened(self) -> bool:
        """Check if camera is opened."""
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        """Release camera."""
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
            logger.info("Camera released")

    def __del__(self):
        """Cleanup on deletion."""
        self.release()

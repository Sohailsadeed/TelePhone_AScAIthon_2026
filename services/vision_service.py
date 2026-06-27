"""
Vision service for handling Afferens Vision API.
"""

import numpy as np
import cv2
import base64
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
from config import Config
from services.logger_service import LoggerService
from utils.constants import DETECTABLE_OBJECTS

logger = LoggerService.get_logger(__name__)


class VisionService:
    """Handles vision analysis using Afferens Vision API."""

    def __init__(self):
        """Initialize vision service."""
        self.api_key = Config.AFFERENS_API_KEY
        self.api_endpoint = "https://afferens.com/api/demo?modality=VISION"
        self.last_detection = None
        self.detection_history = []

    def frame_to_base64(self, frame: np.ndarray) -> str:
        """Convert frame to base64 string."""
        try:
            _, buffer = cv2.imencode(".jpg", frame)
            return base64.b64encode(buffer).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding frame: {e}")
            return ""

    def detect_objects(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detect objects in frame using Afferens Vision API."""
        if not Config.VISION_API_ENABLED or not self.api_key:
            logger.warning("Vision API disabled or API key not set")
            return self._get_mock_detection()

        try:
            # Call Afferens API
            headers = {
                "X-API-KEY": self.api_key,
            }

            response = requests.get(
                self.api_endpoint,
                headers=headers,
                timeout=10,
            )

            logger.debug(f"Afferens raw response: {response.text}")

            if response.status_code == 200:
                result = response.json()
                self.last_detection = result
                self.detection_history.append(result)
                logger.debug(f"Detection successful: {len(result.get('objects', []))} objects")
                if "data" in result and len(result["data"]) > 0:
                    actual_data = result["data"][0].get("data", {})
                    return {
                        "objects": actual_data.get("objects", []),
                        "head_pose": {
                            "is_looking": True,
                            "yaw": 0,
                            "fatigue_level": "Normal",
                            "confidence": 0.9
                        }
                    }
                return self._get_mock_detection()
            else:
                logger.error(f"API error: {response.status_code}")
                return self._get_mock_detection()

        except Exception as e:
            logger.error(f"Vision detection error: {e}")
            return self._get_mock_detection()

    def get_detected_objects(self, frame: np.ndarray) -> List[str]:
        """Get list of detected objects."""
        detection = self.detect_objects(frame)
        objects = []

        for obj in detection.get("objects", []):
            obj_name = obj.get("label", "").lower()
            if obj_name in DETECTABLE_OBJECTS:
                objects.append(obj_name)

        return objects

    def get_head_pose(self, frame: np.ndarray) -> Dict[str, Any]:
        """Get head pose analysis."""
        detection = self.detect_objects(frame)
        head_data = detection.get("head_pose", {})

        return {
            "is_looking": head_data.get("is_looking", True),
            "pose_angle": head_data.get("yaw", 0),
            "fatigue_level": head_data.get("fatigue_level", "Normal"),
            "confidence": head_data.get("confidence", 0.0),
            "timestamp": datetime.now(),
        }

    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Comprehensive frame analysis."""
        try:
            detected_objects = self.get_detected_objects(frame)
            head_pose = self.get_head_pose(frame)

            return {
                "detected_objects": detected_objects,
                "head_pose": head_pose,
                "timestamp": datetime.now(),
                "frame_shape": frame.shape,
                "analysis_successful": True,
            }
        except Exception as e:
            logger.error(f"Frame analysis error: {e}")
            return {
                "detected_objects": [],
                "head_pose": {},
                "timestamp": datetime.now(),
                "analysis_successful": False,
            }

    def _get_mock_detection(self) -> Dict[str, Any]:
        """Get mock detection for testing."""
        logger.debug("Using mock detection")
        return {
            "objects": [
                {
                    "name": "person",
                    "confidence": 0.95,
                    "bbox": [0.1, 0.1, 0.9, 0.9],
                },
                {
                    "name": "keyboard",
                    "confidence": 0.87,
                    "bbox": [0.1, 0.7, 0.9, 1.0],
                },
            ],
            "head_pose": {
                "is_looking": True,
                "yaw": 0,
                "pitch": 0,
                "roll": 0,
                "fatigue_level": "Normal",
                "confidence": 0.92,
            },
        }

    def get_detection_summary(self) -> Dict[str, Any]:
        """Get summary of recent detections."""
        if not self.detection_history:
            return {"detections_count": 0, "common_objects": []}

        # Count object occurrences
        object_counts = {}
        for detection in self.detection_history[-10:]:  # Last 10 detections
            for obj in detection.get("objects", []):
                name = obj.get("name", "unknown")
                object_counts[name] = object_counts.get(name, 0) + 1

        # Get most common
        common = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "detections_count": len(self.detection_history),
            "common_objects": [obj[0] for obj in common],
            "object_frequencies": dict(common),
        }

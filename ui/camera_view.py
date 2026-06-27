"""
Camera view component for Streamlit dashboard.
"""

import streamlit as st
import cv2
import numpy as np
from typing import Optional, List, Tuple


def display_camera_feed(frame: np.ndarray, annotations: Optional[dict] = None):
    """Display camera feed with optional annotations."""
    # Make a copy to avoid modifying original
    display_frame = frame.copy()

    # Add annotations if provided
    if annotations:
        display_frame = add_annotations(display_frame, annotations)

    # Convert BGR to RGB for display
    rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

    # Display in Streamlit
    st.image(rgb_frame, channels="RGB", use_column_width=True)

    return rgb_frame


def add_annotations(frame: np.ndarray, annotations: dict) -> np.ndarray:
    """Add annotations to frame."""
    h, w = frame.shape[:2]

    # Add detected objects
    if annotations.get('detected_objects'):
        objects_text = "Objects: " + ", ".join(annotations['detected_objects'])
        cv2.putText(
            frame,
            objects_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 217, 255),
            2,
        )

    # Add focus score
    if annotations.get('focus_score') is not None:
        score = annotations['focus_score']
        color = get_score_color(score)
        score_text = f"Focus: {score}/100"
        cv2.putText(
            frame,
            score_text,
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    # Add study state
    if annotations.get('study_state'):
        state_text = f"State: {annotations['study_state']}"
        cv2.putText(
            frame,
            state_text,
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (76, 175, 80),
            2,
        )

    # Add timer
    if annotations.get('timer'):
        timer_text = f"Time: {annotations['timer']}"
        text_size = cv2.getTextSize(timer_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        x = w - text_size[0] - 10
        cv2.putText(
            frame,
            timer_text,
            (x, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 217, 255),
            2,
        )

    # Add fatigue indicator
    if annotations.get('fatigue_level'):
        fatigue = annotations['fatigue_level']
        fatigue_color = (76, 175, 80) if fatigue == "Low" else (255, 152, 0) if fatigue == "Medium" else (244, 67, 54)
        cv2.putText(
            frame,
            f"Fatigue: {fatigue}",
            (10, h - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            fatigue_color,
            2,
        )

    return frame


def get_score_color(score: int) -> Tuple[int, int, int]:
    """Get BGR color based on score."""
    if score >= 80:
        return (76, 175, 80)  # Green
    elif score >= 60:
        return (0, 217, 255)  # Cyan
    elif score >= 40:
        return (255, 152, 0)  # Orange
    else:
        return (244, 67, 54)  # Red


def draw_detection_boxes(
    frame: np.ndarray,
    detections: List[dict],
) -> np.ndarray:
    """Draw bounding boxes for detections."""
    h, w = frame.shape[:2]

    for detection in detections:
        bbox = detection.get('bbox')
        label = detection.get('label')
        confidence = detection.get('confidence', 0.0)

        if bbox:
            # Convert normalized bbox to pixel coordinates
            x1, y1, x2, y2 = bbox
            x1, x2 = int(x1 * w), int(x2 * w)
            y1, y2 = int(y1 * h), int(y2 * h)

            # Draw rectangle
            color = (0, 217, 255) if confidence > 0.8 else (255, 152, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label_text = f"{label} ({confidence:.2f})"
            cv2.putText(
                frame,
                label_text,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

    return frame


def create_placeholder_frame(width: int = 1280, height: int = 720) -> np.ndarray:
    """Create a placeholder frame."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Fill with gradient
    for i in range(height):
        intensity = int((i / height) * 100)
        frame[i, :] = [intensity, intensity, intensity]

    # Add text
    text = "Camera Feed Loading..."
    cv2.putText(
        frame,
        text,
        (width // 2 - 200, height // 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 217, 255),
        3,
    )

    return frame

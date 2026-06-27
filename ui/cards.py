"""
UI Card components for Streamlit dashboard.
"""

import streamlit as st
from typing import Dict, Any, Optional


def metric_card(
    title: str,
    value: Any,
    unit: str = "",
    icon: str = "📊",
    color: str = "#00D9FF",
    status: Optional[str] = None,
):
    """Display a metric card."""
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown(f"<h1 style='text-align: center; color: {color};'>{icon}</h1>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<h3 style='color: {color}; margin: 0;'>{title}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: white; margin: 0;'>{value} {unit}</h2>", unsafe_allow_html=True)
        if status:
            st.markdown(f"<p style='color: #b0bec5; margin: 0;'>{status}</p>", unsafe_allow_html=True)


def status_card(
    status: str,
    color: str,
    message: str,
    details: Dict[str, Any] = None,
):
    """Display a status card."""
    st.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(0, 153, 204, 0.1));
            border-left: 4px solid {color};
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        '>
            <h3 style='color: {color}; margin: 0;'>{status}</h3>
            <p style='color: white; margin: 10px 0;'>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if details:
        for key, value in details.items():
            st.markdown(f"  • **{key}**: {value}")


def focus_score_card(score: int, level: str, color: str):
    """Display focus score card."""
    progress = score / 100

    st.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, #1a1f2e 0%, #262730 100%);
            border-left: 4px solid {color};
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        '>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h3 style='color: #00D9FF; margin: 0;'>Focus Score</h3>
                    <h1 style='color: {color}; margin: 10px 0;'>{score}/100</h1>
                    <p style='color: white; margin: 0;'>Level: <span style='color: {color};'>{level}</span></p>
                </div>
                <div style='text-align: right;'>
                    <p style='font-size: 3em; margin: 0;'>{get_focus_emoji(score)}</p>
                </div>
            </div>
            <div style='background: #0e1419; height: 10px; border-radius: 5px; margin-top: 10px; overflow: hidden;'>
                <div style='background: linear-gradient(90deg, {color} 0%, transparent 100%); height: 100%; width: {progress*100}%;'></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_focus_emoji(score: int) -> str:
    """Get emoji based on focus score."""
    if score >= 80:
        return "🔥"
    elif score >= 60:
        return "💪"
    elif score >= 40:
        return "😐"
    else:
        return "😴"


def object_badge(obj_name: str, confidence: float = 1.0):
    """Display object detection badge."""
    bg_color = "#2196F3" if confidence > 0.8 else "#FF9800"
    st.markdown(
        f"""
        <span style='
            display: inline-block;
            background-color: {bg_color};
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            margin: 5px;
            font-size: 0.9em;
        '>
            {obj_name} ({confidence:.0%})
        </span>
        """,
        unsafe_allow_html=True,
    )


def progress_ring(percentage: float, label: str, color: str):
    """Display a progress ring."""
    st.markdown(
        f"""
        <div style='
            text-align: center;
            margin: 20px;
        '>
            <div style='
                width: 100px;
                height: 100px;
                border-radius: 50%;
                background: conic-gradient(
                    {color} 0deg {percentage * 3.6}deg,
                    #262730 {percentage * 3.6}deg 360deg
                );
                margin: 0 auto;
                display: flex;
                align-items: center;
                justify-content: center;
            '>
                <div style='
                    width: 90px;
                    height: 90px;
                    border-radius: 50%;
                    background: #0e1419;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                '>
                    <h2 style='color: {color}; margin: 0;'>{int(percentage)}%</h2>
                    <p style='color: #b0bec5; margin: 0; font-size: 0.8em;'>{label}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

"""
UI Charts using Plotly for Streamlit dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import pandas as pd
import streamlit as st


def create_focus_trend_chart(focus_scores: List[int]) -> go.Figure:
    """Create focus score trend chart."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=focus_scores,
        mode='lines+markers',
        name='Focus Score',
        line=dict(color='#00D9FF', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(0, 217, 255, 0.2)',
    ))

    fig.update_layout(
        title='Focus Score Trend',
        xaxis_title='Time (minutes)',
        yaxis_title='Focus Score',
        template='plotly_dark',
        hovermode='x unified',
        paper_bgcolor='#0e1419',
        plot_bgcolor='#262730',
    )

    return fig


def create_daily_stats_chart(data: Dict[str, Any]) -> go.Figure:
    """Create daily statistics chart."""
    categories = ['Study Time', 'Break Time', 'Focus Score', 'Distractions']
    values = [
        data.get('study_hours', 0),
        data.get('break_hours', 0),
        data.get('avg_focus', 0),
        data.get('distractions', 0),
    ]

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker=dict(
                color=['#4CAF50', '#2196F3', '#00D9FF', '#FF9800'],
            ),
            text=values,
            textposition='auto',
        )
    ])

    fig.update_layout(
        title='Daily Statistics',
        template='plotly_dark',
        paper_bgcolor='#0e1419',
        plot_bgcolor='#262730',
        showlegend=False,
    )

    return fig


def create_pie_chart_distractions(distractions: Dict[str, int]) -> go.Figure:
    """Create distraction pie chart."""
    fig = go.Figure(data=[go.Pie(
        labels=list(distractions.keys()),
        values=list(distractions.values()),
        marker=dict(
            colors=['#FF9800', '#F44336', '#E91E63', '#9C27B0', '#673AB7'],
        ),
    )])

    fig.update_layout(
        title='Distraction Breakdown',
        template='plotly_dark',
        paper_bgcolor='#0e1419',
    )

    return fig


def create_weekly_comparison_chart(weekly_data: List[Dict[str, Any]]) -> go.Figure:
    """Create weekly comparison chart."""
    days = [d.get('day', f'Day {i+1}') for i, d in enumerate(weekly_data)]
    focus_scores = [d.get('focus_score', 0) for d in weekly_data]
    study_hours = [d.get('study_hours', 0) for d in weekly_data]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=days,
        y=focus_scores,
        name='Focus Score',
        marker=dict(color='#00D9FF'),
        yaxis='y',
    ))

    fig.add_trace(go.Bar(
        x=days,
        y=study_hours,
        name='Study Hours',
        marker=dict(color='#4CAF50'),
        yaxis='y2',
    ))

    fig.update_layout(
        title='Weekly Comparison',
        yaxis=dict(title='Focus Score', color='#00D9FF'),
        yaxis2=dict(title='Study Hours', color='#4CAF50', overlaying='y', side='right'),
        template='plotly_dark',
        paper_bgcolor='#0e1419',
        plot_bgcolor='#262730',
        hovermode='x unified',
    )

    return fig


def create_focus_distribution_chart(distribution: Dict[str, int]) -> go.Figure:
    """Create focus level distribution chart."""
    colors = {
        'high': '#4CAF50',
        'medium': '#FFC107',
        'low': '#F44336',
    }

    fig = go.Figure(data=[
        go.Bar(
            x=list(distribution.keys()),
            y=list(distribution.values()),
            marker=dict(
                color=[colors.get(k, '#00D9FF') for k in distribution.keys()]
            ),
            text=list(distribution.values()),
            textposition='auto',
        )
    ])

    fig.update_layout(
        title='Focus Level Distribution',
        xaxis_title='Focus Level',
        yaxis_title='Sessions',
        template='plotly_dark',
        paper_bgcolor='#0e1419',
        plot_bgcolor='#262730',
    )

    return fig


def create_hourly_heatmap(hourly_data: Dict[int, float]) -> go.Figure:
    """Create hourly productivity heatmap."""
    hours = list(range(24))
    values = [hourly_data.get(h, 0) for h in hours]

    fig = go.Figure(data=go.Heatmap(
        z=[values],
        x=[f'{h:02d}:00' for h in hours],
        y=['Productivity'],
        colorscale='Viridis',
        colorbar=dict(title='Score'),
    ))

    fig.update_layout(
        title='Hourly Productivity Heatmap',
        template='plotly_dark',
        paper_bgcolor='#0e1419',
    )

    return fig


def create_timeline_chart(events: List[Dict[str, Any]]) -> go.Figure:
    """Create session timeline chart."""
    if not events:
        # Return empty chart
        fig = go.Figure()
        fig.update_layout(
            title='Session Timeline',
            template='plotly_dark',
            paper_bgcolor='#0e1419',
        )
        return fig

    df = pd.DataFrame(events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    fig = px.scatter(
        df,
        x='timestamp',
        y='focus_score',
        color='study_state',
        title='Session Timeline',
        labels={'focus_score': 'Focus Score', 'timestamp': 'Time'},
        template='plotly_dark',
    )

    fig.update_traces(marker=dict(size=8))
    fig.update_layout(
        paper_bgcolor='#0e1419',
        plot_bgcolor='#262730',
    )

    return fig


def create_gauge_chart(value: int, max_value: int = 100, title: str = "Metric") -> go.Figure:
    """Create gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        delta={'reference': max_value * 0.8},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': '#00D9FF'},
            'steps': [
                {'range': [0, max_value * 0.5], 'color': 'rgba(255, 152, 0, 0.3)'},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': 'rgba(0, 217, 255, 0.3)'},
                {'range': [max_value * 0.8, max_value], 'color': 'rgba(76, 175, 80, 0.3)'},
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9,
            },
        },
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0e1419',
    )

    return fig

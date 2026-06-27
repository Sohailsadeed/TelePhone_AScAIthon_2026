"""
Analytics page for FocusLens.
"""

import streamlit as st
from config import Config
from database.database import Database
from services.analytics_service import AnalyticsService
from services.gemini_service import GeminiService
from services.focus_service import FocusService
from ui.charts import (
    create_daily_stats_chart,
    create_pie_chart_distractions,
    create_weekly_comparison_chart,
    create_focus_distribution_chart,
    create_timeline_chart,
)
from utils.helpers import format_duration


def main():
    """Main analytics page."""
    st.markdown("# 📊 Analytics")
    st.markdown("*Analyze your study patterns and productivity*")

    # Initialize services
    db = Database(Config.DATABASE_PATH)
    gemini = GeminiService()
    analytics = AnalyticsService(db, gemini)
    focus_service = FocusService()

    # Tab selection
    tab1, tab2, tab3, tab4 = st.tabs([
        "Today",
        "Weekly",
        "Focus Patterns",
        "Distractions"
    ])

    with tab1:
        st.subheader("Today's Analytics")

        daily_report = analytics.generate_daily_report()

        if daily_report.get("sessions", 0) > 0:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Sessions", daily_report["sessions"])

            with col2:
                st.metric("Study Time", daily_report["total_study_time"])

            with col3:
                st.metric("Break Time", daily_report["total_break_time"])

            with col4:
                st.metric("Avg Focus", f"{daily_report['average_focus_score']:.1f}/100")

            st.divider()

            # Sessions list
            st.subheader("Sessions Today")
            sessions = db.get_today_sessions()

            for session in sessions:
                with st.expander(f"Session: {session['start_time'][:19]}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Duration", format_duration(session.get('study_duration', 0)))

                    with col2:
                        st.metric("Avg Focus", f"{session.get('average_focus_score', 0):.1f}")

                    with col3:
                        st.metric("Phone Detections", session.get('phone_detections', 0))

        else:
            st.info("No sessions recorded today")

    with tab2:
        st.subheader("Weekly Analytics")

        weekly_report = analytics.generate_weekly_report()

        if weekly_report.get("sessions_count", 0) > 0:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Sessions", weekly_report["sessions_count"])

            with col2:
                st.metric("Total Hours", f"{weekly_report['total_hours']:.1f}h")

            with col3:
                st.metric("Avg Focus", f"{weekly_report['avg_daily_focus']:.1f}")

            with col4:
                st.metric("Productivity", weekly_report.get("productivity_trend", "Stable"))

            st.divider()

            # Key insights
            st.subheader("Key Insights")
            for insight in weekly_report.get("key_insights", []):
                st.info(f"• {insight}")

            st.divider()

            # Recommendations
            st.subheader("Recommendations")
            for rec in weekly_report.get("recommendations", []):
                st.success(f"→ {rec}")

        else:
            st.info("No weekly data available")

    with tab3:
        st.subheader("Focus Patterns")

        all_sessions = db.get_all_sessions(limit=100)

        if all_sessions:
            # Focus distribution
            distribution = analytics.get_focus_distribution(all_sessions)
            st.plotly_chart(
                create_focus_distribution_chart(distribution),
                use_container_width=True,
            )

            # Focus insights
            focus_scores = []
            for session in all_sessions:
                if session.get('average_focus_score'):
                    focus_scores.append(int(session.get('average_focus_score')))

            if focus_scores:
                insights = focus_service.get_focus_insights(focus_scores)
                st.subheader("Pattern Insights")
                for insight in insights:
                    st.write(insight)

        else:
            st.info("No focus data available")

    with tab4:
        st.subheader("Distraction Analysis")

        all_sessions = db.get_all_sessions(limit=50)

        if all_sessions:
            patterns = analytics.get_distraction_patterns(all_sessions)

            if patterns:
                st.plotly_chart(
                    create_pie_chart_distractions(patterns),
                    use_container_width=True,
                )

                st.subheader("Distraction Breakdown")
                for distraction_type, count in patterns.items():
                    st.write(f"• **{distraction_type}**: {count} detections")

            else:
                st.info("No distractions recorded")

        else:
            st.info("No distraction data available")


if __name__ == "__main__":
    main()

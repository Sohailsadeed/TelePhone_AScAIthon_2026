"""
Reports page for FocusLens.
"""

import streamlit as st
from datetime import datetime, timedelta
from config import Config
from database.database import Database
from services.analytics_service import AnalyticsService
from services.gemini_service import GeminiService
from utils.helpers import format_duration


def main():
    """Main reports page."""
    st.markdown("# 📄 Reports")
    st.markdown("*Generate and view comprehensive study reports*")

    # Initialize services
    db = Database(Config.DATABASE_PATH)
    gemini = GeminiService()
    analytics = AnalyticsService(db, gemini)

    # Report type selection
    report_type = st.radio(
        "Select Report Type",
        ["Daily Report", "Weekly Report", "Session Report"],
        horizontal=True,
    )

    st.divider()

    if report_type == "Daily Report":
        render_daily_report(db, analytics)

    elif report_type == "Weekly Report":
        render_weekly_report(db, analytics)

    elif report_type == "Session Report":
        render_session_report(db, analytics)


def render_daily_report(db: Database, analytics: AnalyticsService):
    """Render daily report."""
    st.subheader("📅 Daily Report")

    # Date selection
    selected_date = st.date_input("Select Date", datetime.now().date())

    st.divider()

    # Get sessions for date
    all_sessions = db.get_all_sessions(limit=100)
    date_sessions = [
        s for s in all_sessions
        if datetime.fromisoformat(s.get("start_time", "")).date() == selected_date
    ]

    if not date_sessions:
        st.info(f"No sessions recorded for {selected_date}")
        return

    # Calculate stats
    total_study_time = sum(int(s.get("study_duration", 0) or 0) for s in date_sessions)
    total_break_time = sum(int(s.get("break_duration", 0) or 0) for s in date_sessions)
    avg_focus = sum(float(s.get("average_focus_score", 0) or 0) for s in date_sessions) / len(date_sessions)
    total_distractions = sum(int(s.get("phone_detections", 0) or 0) for s in date_sessions)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Study Time", format_duration(total_study_time))

    with col2:
        st.metric("Break Time", format_duration(total_break_time))

    with col3:
        st.metric("Avg Focus", f"{avg_focus:.1f}/100")

    with col4:
        st.metric("Distractions", total_distractions)

    st.divider()

    # Sessions breakdown
    st.subheader("Sessions Breakdown")

    for session in date_sessions:
        with st.expander(
            f"Session: {session['start_time'][11:19]} | Focus: {session.get('average_focus_score', 0):.0f}",
            expanded=False
        ):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Duration",
                    format_duration(session.get('study_duration', 0))
                )

            with col2:
                st.metric(
                    "Average Focus",
                    f"{session.get('average_focus_score', 0):.1f}"
                )

            with col3:
                st.metric(
                    "Phone Detections",
                    session.get('phone_detections', 0)
                )

            # Get session report if available
            report = db.get_session_report(session['session_id'])
            if report:
                st.subheader("AI Summary")
                st.write(report.get('summary', ''))

                st.subheader("Achievements")
                import json
                achievements = json.loads(report.get('achievements', '[]'))
                for achievement in achievements:
                    st.success(f"✓ {achievement}")

                st.subheader("Areas for Improvement")
                improvements = json.loads(report.get('areas_for_improvement', '[]'))
                for improvement in improvements:
                    st.warning(f"• {improvement}")

                st.subheader("Suggestions")
                suggestions = json.loads(report.get('suggestions', '[]'))
                for suggestion in suggestions:
                    st.info(f"→ {suggestion}")


def render_weekly_report(db: Database, analytics: AnalyticsService):
    """Render weekly report."""
    st.subheader("📊 Weekly Report")

    weekly_report = analytics.generate_weekly_report()

    if not weekly_report.get("sessions_count", 0):
        st.info("No data available for weekly report")
        return

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Sessions", weekly_report["sessions_count"])

    with col2:
        st.metric("Total Hours", f"{weekly_report['total_hours']:.1f}")

    with col3:
        st.metric("Avg Daily Focus", f"{weekly_report['avg_daily_focus']:.1f}")

    with col4:
        st.metric("Productivity", weekly_report.get("productivity_trend", "Stable"))

    st.divider()

    # AI Summary
    st.subheader("📝 Weekly Summary")
    st.write(weekly_report.get("week_summary", "No summary available"))

    st.divider()

    # Key Insights
    st.subheader("💡 Key Insights")
    for insight in weekly_report.get("key_insights", []):
        st.info(f"• {insight}")

    st.divider()

    # Top Distractions
    st.subheader("⚠️ Top Distractions")
    for distraction in weekly_report.get("top_distractions", []):
        st.warning(f"• {distraction}")

    st.divider()

    # Recommendations
    st.subheader("✨ Recommendations")
    for rec in weekly_report.get("recommendations", []):
        st.success(f"→ {rec}")


def render_session_report(db: Database, analytics: AnalyticsService):
    """Render session report."""
    st.subheader("📋 Session Report")

    # Get recent sessions
    sessions = db.get_all_sessions(limit=20)

    if not sessions:
        st.info("No sessions available")
        return

    session_options = {
        f"{s['start_time'][:19]} (Focus: {s.get('average_focus_score', 0):.0f})": s['session_id']
        for s in sessions
    }

    selected_session_label = st.selectbox(
        "Select Session",
        list(session_options.keys())
    )

    selected_session_id = session_options[selected_session_label]
    session = db.get_session(selected_session_id)

    if not session:
        st.error("Session not found")
        return

    # Display session metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Study Duration",
            format_duration(session.get('study_duration', 0))
        )

    with col2:
        st.metric(
            "Break Duration",
            format_duration(session.get('break_duration', 0))
        )

    with col3:
        st.metric(
            "Average Focus",
            f"{session.get('average_focus_score', 0):.1f}/100"
        )

    with col4:
        st.metric(
            "Phone Detections",
            session.get('phone_detections', 0)
        )

    st.divider()

    # Get session report
    report = db.get_session_report(selected_session_id)

    if report:
        st.subheader("📄 Report Summary")
        st.write(report.get('summary', 'No summary available'))

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✅ Achievements")
            import json
            achievements = json.loads(report.get('achievements', '[]'))
            if achievements:
                for achievement in achievements:
                    st.success(f"✓ {achievement}")
            else:
                st.write("None recorded")

        with col2:
            st.subheader("🎯 Areas for Improvement")
            improvements = json.loads(report.get('areas_for_improvement', '[]'))
            if improvements:
                for improvement in improvements:
                    st.warning(f"• {improvement}")
            else:
                st.write("None identified")

        st.divider()

        st.subheader("💡 Suggestions")
        suggestions = json.loads(report.get('suggestions', '[]'))
        if suggestions:
            for suggestion in suggestions:
                st.info(f"→ {suggestion}")
        else:
            st.write("No suggestions available")

        st.divider()

        st.metric("Overall Rating", f"{report.get('overall_rating', 0)}/10")

    else:
        st.info("No report generated for this session yet")

    # Get events
    st.divider()
    st.subheader("📍 Session Events")

    events = db.get_session_events(selected_session_id)
    if events:
        for event in events[:10]:  # Show last 10 events
            st.write(f"**{event['event_type']}** - {event['timestamp'][11:19]}")
            st.caption(event.get('dashboard_message', ''))
    else:
        st.write("No events recorded")


if __name__ == "__main__":
    main()

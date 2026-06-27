import datetime
import os

from database.logger import get_all_events


def _parse_duration_to_minutes(duration_value):
    try:
        if duration_value is None:
            return 0.0

        if isinstance(duration_value, (int, float)):
            return float(duration_value)

        duration_text = str(duration_value).strip().lower()
        if not duration_text:
            return 0.0

        if ":" in duration_text:
            parts = duration_text.split(":")
            if len(parts) == 2:
                minutes = float(parts[0])
                seconds = float(parts[1])
                return minutes + (seconds / 60.0)

        if duration_text.endswith("min"):
            return float(duration_text.replace("min", "").strip())

        return float(duration_text)
    except Exception:
        return 0.0


def generate_report():
    try:
        events = get_all_events()
        total_events = len(events)
        total_locks = 0
        total_alerts = 0
        study_time_minutes = 0.0

        for event in events:
            if len(event) < 5:
                continue

            event_type = str(event[2]).strip().lower()
            duration = event[4]

            if "lock" in event_type:
                total_locks += 1

            if "alert" in event_type:
                total_alerts += 1

            study_time_minutes += _parse_duration_to_minutes(duration)

        return {
            "total_events": total_events,
            "total_locks": total_locks,
            "total_alerts": total_alerts,
            "study_time_minutes": round(study_time_minutes, 2),
            "generated_at": datetime.datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"Error generating report: {e}")
        return {
            "total_events": 0,
            "total_locks": 0,
            "total_alerts": 0,
            "study_time_minutes": 0.0,
            "generated_at": datetime.datetime.now().isoformat(),
        }


def print_report():
    try:
        report = generate_report()
        print("FocusLens Report")
        print(f"Total events: {report['total_events']}")
        print(f"Total locks: {report['total_locks']}")
        print(f"Total alerts: {report['total_alerts']}")
        print(f"Study time (minutes): {report['study_time_minutes']}")
        print(f"Generated at: {report['generated_at']}")
        return report
    except Exception as e:
        print(f"Error printing report: {e}")
        return None

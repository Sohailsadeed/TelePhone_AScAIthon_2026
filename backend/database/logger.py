import sqlite3
import os
from datetime import datetime


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(LOGS_DIR, "focuslens.db")


os.makedirs(LOGS_DIR, exist_ok=True)


def _initialize_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                action_taken TEXT,
                duration TEXT
            )
            """
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized")
    except Exception as e:
        print(f"Database initialization failed: {e}")


def save_event(event_type, action_taken, duration):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (timestamp, event_type, action_taken, duration)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), event_type, action_taken, duration),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Failed to save event: {e}")


def get_all_events():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Failed to fetch events: {e}")
        return []


_initialize_database()

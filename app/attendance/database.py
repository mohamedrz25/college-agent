import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE = BASE_DIR / "college_agent.db"


def get_db():
    connection = sqlite3.connect(
        DATABASE,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    db = get_db()

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            active INTEGER DEFAULT 1
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            class_date TEXT NOT NULL,
            status TEXT NOT NULL,
            marked_at TEXT NOT NULL,

            UNIQUE(class_id, class_date),

            FOREIGN KEY(class_id)
            REFERENCES timetable(id)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_date TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    db.commit()
    db.close()

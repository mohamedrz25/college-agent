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

def add_class(subject, day_of_week, start_time, end_time=None):
    db = get_db()

    db.execute(
        """
        INSERT INTO timetable
        (subject, day_of_week, start_time, end_time)
        VALUES (?, ?, ?, ?)
        """,
        (subject, day_of_week, start_time, end_time)
    )

    db.commit()
    db.close()


def get_classes():
    db = get_db()

    rows = db.execute(
        """
        SELECT *
        FROM timetable
        WHERE active = 1
        ORDER BY day_of_week, start_time
        """
    ).fetchall()

    db.close()

    return rows


def get_today_classes(day):
    db = get_db()

    rows = db.execute(
        """
        SELECT *
        FROM timetable
        WHERE day_of_week = ?
        AND active = 1
        ORDER BY start_time
        """,
        (day,)
    ).fetchall()

    db.close()

    return rows


def mark_attendance(class_id, class_date, status, marked_at):
    db = get_db()

    db.execute(
        """
        INSERT INTO attendance
        (class_id, class_date, status, marked_at)
        VALUES (?, ?, ?, ?)

        ON CONFLICT(class_id, class_date)
        DO UPDATE SET
            status = excluded.status,
            marked_at = excluded.marked_at
        """,
        (
            class_id,
            class_date,
            status,
            marked_at
        )
    )

    db.commit()
    db.close()


def get_attendance():
    db = get_db()

    rows = db.execute(
        """
        SELECT
            attendance.*,
            timetable.subject,
            timetable.day_of_week,
            timetable.start_time
        FROM attendance
        JOIN timetable
        ON attendance.class_id = timetable.id
        ORDER BY class_date DESC
        """
    ).fetchall()

    db.close()

    return rows


def get_subject_statistics():
    db = get_db()

    rows = db.execute(
        """
        SELECT
            timetable.subject,
            COUNT(attendance.id) AS total_classes,
            SUM(
                CASE
                    WHEN attendance.status = 'present'
                    THEN 1
                    ELSE 0
                END
            ) AS present_classes
        FROM attendance
        JOIN timetable
        ON attendance.class_id = timetable.id
        GROUP BY timetable.subject
        """
    ).fetchall()

    db.close()

    results = []

    for row in rows:
        total = row["total_classes"]
        present = row["present_classes"] or 0

        percentage = (
            (present / total) * 100
            if total > 0
            else 0
        )

        results.append({
            "subject": row["subject"],
            "total": total,
            "present": present,
            "percentage": round(percentage, 2)
        })

    return results
    

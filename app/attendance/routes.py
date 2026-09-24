from flask import request, jsonify
from datetime import datetime, date

from . import attendance_bp
from .database import (
    init_db,
    add_class,
    get_classes,
    get_today_classes,
    mark_attendance,
    get_attendance,
    get_subject_statistics
)


# Initialize the database
init_db()


@attendance_bp.route("/add-class", methods=["POST"])
def create_class():
    data = request.get_json(silent=True) or {}

    subject = data.get("subject", "").strip()
    day_of_week = data.get("day_of_week", "").strip()
    start_time = data.get("start_time", "").strip()
    end_time = data.get("end_time", "").strip() or None

    if not subject or not day_of_week or not start_time:
        return jsonify({
            "error": "Subject, day and start time are required"
        }), 400

    add_class(
        subject,
        day_of_week,
        start_time,
        end_time
    )

    return jsonify({
        "message": "Class added successfully"
    }), 201


@attendance_bp.route("/classes", methods=["GET"])
def classes():
    rows = get_classes()

    return jsonify([
        dict(row)
        for row in rows
    ])


@attendance_bp.route("/today", methods=["GET"])
def today_classes():
    today = date.today().strftime("%A")

    rows = get_today_classes(today)

    return jsonify([
        dict(row)
        for row in rows
    ])


@attendance_bp.route("/mark", methods=["POST"])
def mark_class_attendance():
    data = request.get_json(silent=True) or {}

    class_id = data.get("class_id")
    status = data.get("status", "").strip().lower()

    if not class_id:
        return jsonify({
            "error": "class_id is required"
        }), 400

    if status not in ["present", "absent"]:
        return jsonify({
            "error": "Status must be present or absent"
        }), 400

    mark_attendance(
        class_id=class_id,
        class_date=date.today().isoformat(),
        status=status,
        marked_at=datetime.now().isoformat()
    )

    return jsonify({
        "message": f"Attendance marked as {status}"
    })


@attendance_bp.route("/attendance", methods=["GET"])
def attendance_history():
    rows = get_attendance()

    return jsonify([
        dict(row)
        for row in rows
    ])


@attendance_bp.route("/statistics", methods=["GET"])
def statistics():
    return jsonify(
        get_subject_statistics()
    )

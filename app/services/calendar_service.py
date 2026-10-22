from datetime import date, timedelta, datetime
from app.database.db import get_connection


def _week_bounds(ref: date) -> tuple[str, str]:
    start = ref - timedelta(days=ref.weekday())
    end   = start + timedelta(days=6)
    return start.isoformat(), end.isoformat()


def _month_bounds(ref: date) -> tuple[str, str]:
    start = ref.replace(day=1)
    if ref.month == 12:
        end = ref.replace(year=ref.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end = ref.replace(month=ref.month + 1, day=1) - timedelta(days=1)
    return start.isoformat(), end.isoformat()


def _fetch_appointments(date_from: str, date_to: str) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT a.*, p.name AS patient_name, d.name AS doctor_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors  d ON a.doctor_id  = d.id
               WHERE a.appointment_date BETWEEN ? AND ?
               ORDER BY a.appointment_date, a.appointment_time""",
            (date_from, date_to),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_daily_view(target_date: str = None) -> dict:
    ref = date.fromisoformat(target_date) if target_date else date.today()
    appointments = _fetch_appointments(ref.isoformat(), ref.isoformat())
    return {
        "view":         "daily",
        "date":         ref.isoformat(),
        "appointments": appointments,
        "total":        len(appointments),
    }


def get_weekly_view(target_date: str = None) -> dict:
    ref = date.fromisoformat(target_date) if target_date else date.today()
    start, end = _week_bounds(ref)
    appointments = _fetch_appointments(start, end)
    by_day = {}
    for apt in appointments:
        by_day.setdefault(apt["appointment_date"], []).append(apt)
    return {
        "view":         "weekly",
        "week_start":   start,
        "week_end":     end,
        "appointments": appointments,
        "by_day":       by_day,
        "total":        len(appointments),
    }


def get_monthly_view(target_date: str = None) -> dict:
    ref = date.fromisoformat(target_date) if target_date else date.today()
    start, end = _month_bounds(ref)
    appointments = _fetch_appointments(start, end)
    by_day = {}
    for apt in appointments:
        by_day.setdefault(apt["appointment_date"], []).append(apt)
    return {
        "view":         "monthly",
        "month_start":  start,
        "month_end":    end,
        "appointments": appointments,
        "by_day":       by_day,
        "total":        len(appointments),
    }


def check_slot_conflict(doctor_id: int, appointment_date: str,
                        appointment_time: str,
                        exclude_id: int = None) -> bool:
    conn = get_connection()
    try:
        query  = """SELECT id FROM appointments
                    WHERE doctor_id=? AND appointment_date=? AND appointment_time=?"""
        params = [doctor_id, appointment_date, appointment_time]
        if exclude_id:
            query  += " AND id != ?"
            params.append(exclude_id)
        row = conn.execute(query, params).fetchone()
        return row is not None
    finally:
        conn.close()


def get_doctor_schedule(doctor_id: int, target_date: str = None) -> list[dict]:
    ref = date.fromisoformat(target_date) if target_date else date.today()
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT a.*, p.name AS patient_name, d.name AS doctor_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors  d ON a.doctor_id  = d.id
               WHERE a.doctor_id=? AND a.appointment_date=?
               ORDER BY a.appointment_time""",
            (doctor_id, ref.isoformat()),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

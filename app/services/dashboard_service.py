from datetime import date
from app.database.db import get_connection


def get_dashboard_stats() -> dict:
    conn = get_connection()
    today = date.today().isoformat()
    try:
        total_patients = conn.execute(
            "SELECT COUNT(*) FROM patients"
        ).fetchone()[0]

        total_doctors = conn.execute(
            "SELECT COUNT(*) FROM doctors"
        ).fetchone()[0]

        todays_appointments = conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE appointment_date=?",
            (today,),
        ).fetchone()[0]

        scheduled_today = conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE appointment_date=? AND status='Scheduled'",
            (today,),
        ).fetchone()[0]

        pending_bills = conn.execute(
            "SELECT COUNT(*) FROM bills WHERE payment_status='Pending'"
        ).fetchone()[0]

        paid_bills = conn.execute(
            "SELECT COUNT(*) FROM bills WHERE payment_status='Paid'"
        ).fetchone()[0]

        pending_amount = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM bills WHERE payment_status='Pending'"
        ).fetchone()[0]

        paid_amount = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM bills WHERE payment_status='Paid'"
        ).fetchone()[0]

        total_appointments = conn.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]

        recent_patients = conn.execute(
            """SELECT id, patient_code, name, age, gender, blood_group
               FROM patients ORDER BY id DESC LIMIT 5"""
        ).fetchall()

        upcoming_appointments = conn.execute(
            """SELECT a.appointment_date, a.appointment_time, a.status,
                      p.name AS patient_name, d.name AS doctor_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors  d ON a.doctor_id  = d.id
               WHERE a.appointment_date >= ? AND a.status = 'Scheduled'
               ORDER BY a.appointment_date, a.appointment_time
               LIMIT 5""",
            (today,),
        ).fetchall()

        return {
            "total_patients":        total_patients,
            "total_doctors":         total_doctors,
            "todays_appointments":   todays_appointments,
            "scheduled_today":       scheduled_today,
            "total_appointments":    total_appointments,
            "pending_bills":         pending_bills,
            "paid_bills":            paid_bills,
            "pending_amount":        round(pending_amount, 2),
            "paid_amount":           round(paid_amount, 2),
            "recent_patients":       [dict(r) for r in recent_patients],
            "upcoming_appointments": [dict(r) for r in upcoming_appointments],
        }
    finally:
        conn.close()

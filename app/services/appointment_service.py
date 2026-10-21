from app.database.db import get_connection

VALID_STATUSES = ("Scheduled", "Completed", "Cancelled")


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def create_appointment(patient_id: int, doctor_id: int,
                       appointment_date: str, appointment_time: str,
                       status: str = "Scheduled", notes: str = None) -> dict:
    if not all([patient_id, doctor_id, appointment_date, appointment_time]):
        raise ValueError("patient_id, doctor_id, date, and time are required.")
    if status not in VALID_STATUSES:
        raise ValueError(f"Status must be one of {VALID_STATUSES}.")

    conn = get_connection()
    try:
        conflict = conn.execute(
            """SELECT id FROM appointments
               WHERE doctor_id=? AND appointment_date=? AND appointment_time=?""",
            (doctor_id, appointment_date, appointment_time),
        ).fetchone()
        if conflict:
            raise ValueError(
                f"Doctor is already booked on {appointment_date} at {appointment_time}."
            )

        cur = conn.execute(
            """INSERT INTO appointments
               (patient_id, doctor_id, appointment_date, appointment_time, status, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (patient_id, doctor_id, appointment_date, appointment_time, status, notes),
        )
        conn.commit()
        return get_appointment_by_id(cur.lastrowid)
    finally:
        conn.close()


def get_all_appointments() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT a.*, p.name AS patient_name, d.name AS doctor_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors  d ON a.doctor_id  = d.id
               ORDER BY a.appointment_date, a.appointment_time"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_appointment_by_id(appointment_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT a.*, p.name AS patient_name, d.name AS doctor_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors  d ON a.doctor_id  = d.id
               WHERE a.id=?""",
            (appointment_id,),
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def get_appointments_by_patient(patient_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT a.*, p.name AS patient_name, d.name AS doctor_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors  d ON a.doctor_id  = d.id
               WHERE a.patient_id=?
               ORDER BY a.appointment_date, a.appointment_time""",
            (patient_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_appointments_by_doctor(doctor_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT a.*, p.name AS patient_name, d.name AS doctor_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors  d ON a.doctor_id  = d.id
               WHERE a.doctor_id=?
               ORDER BY a.appointment_date, a.appointment_time""",
            (doctor_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_appointment(appointment_id: int, appointment_date: str = None,
                       appointment_time: str = None, status: str = None,
                       notes: str = None) -> dict:
    existing = get_appointment_by_id(appointment_id)
    if not existing:
        raise ValueError(f"Appointment id={appointment_id} not found.")

    new_date   = appointment_date or existing["appointment_date"]
    new_time   = appointment_time or existing["appointment_time"]
    new_status = status           or existing["status"]
    new_notes  = notes if notes is not None else existing["notes"]

    if new_status not in VALID_STATUSES:
        raise ValueError(f"Status must be one of {VALID_STATUSES}.")

    conn = get_connection()
    try:
        if appointment_date or appointment_time:
            conflict = conn.execute(
                """SELECT id FROM appointments
                   WHERE doctor_id=? AND appointment_date=? AND appointment_time=?
                   AND id != ?""",
                (existing["doctor_id"], new_date, new_time, appointment_id),
            ).fetchone()
            if conflict:
                raise ValueError(
                    f"Doctor is already booked on {new_date} at {new_time}."
                )

        conn.execute(
            """UPDATE appointments
               SET appointment_date=?, appointment_time=?, status=?, notes=?
               WHERE id=?""",
            (new_date, new_time, new_status, new_notes, appointment_id),
        )
        conn.commit()
        return get_appointment_by_id(appointment_id)
    finally:
        conn.close()


def delete_appointment(appointment_id: int) -> bool:
    if not get_appointment_by_id(appointment_id):
        raise ValueError(f"Appointment id={appointment_id} not found.")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
        conn.commit()
        return True
    finally:
        conn.close()

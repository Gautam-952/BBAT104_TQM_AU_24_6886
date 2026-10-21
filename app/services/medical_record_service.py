from app.database.db import get_connection


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def create_medical_record(patient_id: int, doctor_id: int,
                          diagnosis: str, prescription: str,
                          record_date: str) -> dict:
    if not all([patient_id, doctor_id, diagnosis, prescription, record_date]):
        raise ValueError("All medical record fields are required.")

    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO medical_records
               (patient_id, doctor_id, diagnosis, prescription, record_date)
               VALUES (?, ?, ?, ?, ?)""",
            (patient_id, doctor_id, diagnosis, prescription, record_date),
        )
        conn.commit()
        return get_medical_record_by_id(cur.lastrowid)
    finally:
        conn.close()


def get_all_medical_records() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT mr.*, p.name AS patient_name, d.name AS doctor_name
               FROM medical_records mr
               JOIN patients p ON mr.patient_id = p.id
               JOIN doctors  d ON mr.doctor_id  = d.id
               ORDER BY mr.record_date DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_medical_record_by_id(record_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT mr.*, p.name AS patient_name, d.name AS doctor_name
               FROM medical_records mr
               JOIN patients p ON mr.patient_id = p.id
               JOIN doctors  d ON mr.doctor_id  = d.id
               WHERE mr.id=?""",
            (record_id,),
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def get_records_by_patient(patient_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT mr.*, p.name AS patient_name, d.name AS doctor_name
               FROM medical_records mr
               JOIN patients p ON mr.patient_id = p.id
               JOIN doctors  d ON mr.doctor_id  = d.id
               WHERE mr.patient_id=?
               ORDER BY mr.record_date DESC""",
            (patient_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_medical_record(record_id: int, diagnosis: str = None,
                          prescription: str = None,
                          record_date: str = None) -> dict:
    existing = get_medical_record_by_id(record_id)
    if not existing:
        raise ValueError(f"Medical record id={record_id} not found.")

    new_diagnosis    = diagnosis    or existing["diagnosis"]
    new_prescription = prescription or existing["prescription"]
    new_date         = record_date  or existing["record_date"]

    conn = get_connection()
    try:
        conn.execute(
            """UPDATE medical_records
               SET diagnosis=?, prescription=?, record_date=?
               WHERE id=?""",
            (new_diagnosis, new_prescription, new_date, record_id),
        )
        conn.commit()
        return get_medical_record_by_id(record_id)
    finally:
        conn.close()


def delete_medical_record(record_id: int) -> bool:
    if not get_medical_record_by_id(record_id):
        raise ValueError(f"Medical record id={record_id} not found.")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM medical_records WHERE id=?", (record_id,))
        conn.commit()
        return True
    finally:
        conn.close()

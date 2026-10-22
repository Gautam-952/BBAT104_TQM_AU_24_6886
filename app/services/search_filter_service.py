from app.database.db import get_connection


def filter_patients(name: str = None, patient_code: str = None,
                    blood_group: str = None, age_min: int = None,
                    age_max: int = None) -> list[dict]:
    query  = "SELECT * FROM patients WHERE 1=1"
    params = []

    if name:
        query += " AND LOWER(name) LIKE ?"
        params.append(f"%{name.lower()}%")
    if patient_code:
        query += " AND LOWER(patient_code) LIKE ?"
        params.append(f"%{patient_code.lower()}%")
    if blood_group:
        query += " AND blood_group = ?"
        params.append(blood_group)
    if age_min is not None:
        query += " AND age >= ?"
        params.append(int(age_min))
    if age_max is not None:
        query += " AND age <= ?"
        params.append(int(age_max))

    query += " ORDER BY id"
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(query, params).fetchall()]
    finally:
        conn.close()


def filter_doctors(name: str = None, department: str = None,
                   specialization: str = None) -> list[dict]:
    query  = "SELECT * FROM doctors WHERE 1=1"
    params = []

    if name:
        query += " AND LOWER(name) LIKE ?"
        params.append(f"%{name.lower()}%")
    if department:
        query += " AND LOWER(department) LIKE ?"
        params.append(f"%{department.lower()}%")
    if specialization:
        query += " AND LOWER(specialization) LIKE ?"
        params.append(f"%{specialization.lower()}%")

    query += " ORDER BY id"
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(query, params).fetchall()]
    finally:
        conn.close()


def filter_appointments(status: str = None, date_from: str = None,
                        date_to: str = None, doctor_id: int = None,
                        patient_id: int = None) -> list[dict]:
    query = """
        SELECT a.*, p.name AS patient_name, d.name AS doctor_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND a.status = ?"
        params.append(status)
    if date_from:
        query += " AND a.appointment_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND a.appointment_date <= ?"
        params.append(date_to)
    if doctor_id:
        query += " AND a.doctor_id = ?"
        params.append(int(doctor_id))
    if patient_id:
        query += " AND a.patient_id = ?"
        params.append(int(patient_id))

    query += " ORDER BY a.appointment_date, a.appointment_time"
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(query, params).fetchall()]
    finally:
        conn.close()


def filter_bills(payment_status: str = None, date_from: str = None,
                 date_to: str = None, patient_id: int = None,
                 amount_min: float = None, amount_max: float = None) -> list[dict]:
    query = """
        SELECT b.*, p.name AS patient_name
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE 1=1
    """
    params = []

    if payment_status:
        query += " AND b.payment_status = ?"
        params.append(payment_status)
    if date_from:
        query += " AND b.bill_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND b.bill_date <= ?"
        params.append(date_to)
    if patient_id:
        query += " AND b.patient_id = ?"
        params.append(int(patient_id))
    if amount_min is not None:
        query += " AND b.amount >= ?"
        params.append(float(amount_min))
    if amount_max is not None:
        query += " AND b.amount <= ?"
        params.append(float(amount_max))

    query += " ORDER BY b.bill_date DESC"
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(query, params).fetchall()]
    finally:
        conn.close()

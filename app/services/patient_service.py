from app.database.db import get_connection


def _next_patient_code(conn) -> str:
    row = conn.execute("SELECT MAX(id) AS max_id FROM patients").fetchone()
    next_id = (row["max_id"] or 0) + 1
    return f"PAT-{next_id:04d}"


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def create_patient(name: str, age: int, gender: str, blood_group: str,
                   phone: str, address: str, emergency_contact: str) -> dict:
    if not all([name, age, gender, blood_group, phone, address, emergency_contact]):
        raise ValueError("All patient fields are required.")

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM patients WHERE phone = ?", (phone,)
        ).fetchone()
        if existing:
            raise ValueError(f"Phone number '{phone}' is already registered.")

        code = _next_patient_code(conn)
        conn.execute(
            """INSERT INTO patients
               (patient_code, name, age, gender, blood_group, phone, address, emergency_contact)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (code, name, int(age), gender, blood_group, phone, address, emergency_contact),
        )
        conn.commit()
        return get_patient_by_code(code)
    finally:
        conn.close()


def get_all_patients() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM patients ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_patient_by_id(patient_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM patients WHERE id = ?", (patient_id,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def get_patient_by_code(code: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM patients WHERE patient_code = ?", (code,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def update_patient(patient_id: int, name: str = None, age: int = None,
                   gender: str = None, blood_group: str = None,
                   phone: str = None, address: str = None,
                   emergency_contact: str = None) -> dict:
    existing = get_patient_by_id(patient_id)
    if not existing:
        raise ValueError(f"Patient with id={patient_id} not found.")

    updated = {
        "name":              name              or existing["name"],
        "age":               int(age)          if age is not None else existing["age"],
        "gender":            gender            or existing["gender"],
        "blood_group":       blood_group       or existing["blood_group"],
        "phone":             phone             or existing["phone"],
        "address":           address           or existing["address"],
        "emergency_contact": emergency_contact or existing["emergency_contact"],
    }

    if phone and phone != existing["phone"]:
        conn = get_connection()
        try:
            dup = conn.execute(
                "SELECT id FROM patients WHERE phone = ? AND id != ?",
                (phone, patient_id),
            ).fetchone()
            if dup:
                raise ValueError(f"Phone number '{phone}' is already registered.")
        finally:
            conn.close()

    conn = get_connection()
    try:
        conn.execute(
            """UPDATE patients
               SET name=?, age=?, gender=?, blood_group=?, phone=?,
                   address=?, emergency_contact=?
               WHERE id=?""",
            (updated["name"], updated["age"], updated["gender"],
             updated["blood_group"], updated["phone"],
             updated["address"], updated["emergency_contact"], patient_id),
        )
        conn.commit()
        return get_patient_by_id(patient_id)
    finally:
        conn.close()


def delete_patient(patient_id: int) -> bool:
    if not get_patient_by_id(patient_id):
        raise ValueError(f"Patient with id={patient_id} not found.")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        return True
    finally:
        conn.close()

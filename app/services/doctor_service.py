from app.database.db import get_connection


def _next_doctor_code(conn) -> str:
    row = conn.execute("SELECT MAX(id) AS max_id FROM doctors").fetchone()
    next_id = (row["max_id"] or 0) + 1
    return f"DOC-{next_id:04d}"


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def create_doctor(name: str, specialization: str, department: str,
                  phone: str, email: str) -> dict:
    if not all([name, specialization, department, phone, email]):
        raise ValueError("All doctor fields are required.")

    conn = get_connection()
    try:
        if conn.execute("SELECT id FROM doctors WHERE phone = ?", (phone,)).fetchone():
            raise ValueError(f"Phone number '{phone}' already registered.")
        if conn.execute("SELECT id FROM doctors WHERE email = ?", (email,)).fetchone():
            raise ValueError(f"Email '{email}' already registered.")

        code = _next_doctor_code(conn)
        conn.execute(
            """INSERT INTO doctors
               (doctor_code, name, specialization, department, phone, email)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (code, name, specialization, department, phone, email),
        )
        conn.commit()
        return get_doctor_by_code(code)
    finally:
        conn.close()


def get_all_doctors() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM doctors ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_doctor_by_id(doctor_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def get_doctor_by_code(code: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM doctors WHERE doctor_code = ?", (code,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def get_doctors_by_department(department: str) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM doctors WHERE LOWER(department) = LOWER(?)",
            (department,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_doctor(doctor_id: int, name: str = None, specialization: str = None,
                  department: str = None, phone: str = None,
                  email: str = None) -> dict:
    existing = get_doctor_by_id(doctor_id)
    if not existing:
        raise ValueError(f"Doctor with id={doctor_id} not found.")

    updated = {
        "name":           name           or existing["name"],
        "specialization": specialization or existing["specialization"],
        "department":     department     or existing["department"],
        "phone":          phone          or existing["phone"],
        "email":          email          or existing["email"],
    }

    conn = get_connection()
    try:
        if phone and phone != existing["phone"]:
            if conn.execute(
                "SELECT id FROM doctors WHERE phone = ? AND id != ?", (phone, doctor_id)
            ).fetchone():
                raise ValueError(f"Phone number '{phone}' already registered.")

        if email and email != existing["email"]:
            if conn.execute(
                "SELECT id FROM doctors WHERE email = ? AND id != ?", (email, doctor_id)
            ).fetchone():
                raise ValueError(f"Email '{email}' already registered.")

        conn.execute(
            """UPDATE doctors
               SET name=?, specialization=?, department=?, phone=?, email=?
               WHERE id=?""",
            (updated["name"], updated["specialization"], updated["department"],
             updated["phone"], updated["email"], doctor_id),
        )
        conn.commit()
        return get_doctor_by_id(doctor_id)
    finally:
        conn.close()


def delete_doctor(doctor_id: int) -> bool:
    if not get_doctor_by_id(doctor_id):
        raise ValueError(f"Doctor with id={doctor_id} not found.")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        conn.commit()
        return True
    finally:
        conn.close()

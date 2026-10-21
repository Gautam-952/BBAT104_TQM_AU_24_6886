from app.database.db import get_connection

VALID_STATUSES = ("Pending", "Paid", "Cancelled")


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def create_bill(patient_id: int, amount: float,
                bill_date: str, payment_status: str = "Pending") -> dict:
    if not all([patient_id, amount, bill_date]):
        raise ValueError("patient_id, amount, and bill_date are required.")
    if payment_status not in VALID_STATUSES:
        raise ValueError(f"payment_status must be one of {VALID_STATUSES}.")
    if float(amount) <= 0:
        raise ValueError("Amount must be greater than zero.")

    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO bills (patient_id, amount, payment_status, bill_date)
               VALUES (?, ?, ?, ?)""",
            (patient_id, float(amount), payment_status, bill_date),
        )
        conn.commit()
        return get_bill_by_id(cur.lastrowid)
    finally:
        conn.close()


def get_all_bills() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.*, p.name AS patient_name
               FROM bills b
               JOIN patients p ON b.patient_id = p.id
               ORDER BY b.bill_date DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_bill_by_id(bill_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT b.*, p.name AS patient_name
               FROM bills b
               JOIN patients p ON b.patient_id = p.id
               WHERE b.id=?""",
            (bill_id,),
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def get_bills_by_patient(patient_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT b.*, p.name AS patient_name
               FROM bills b
               JOIN patients p ON b.patient_id = p.id
               WHERE b.patient_id=?
               ORDER BY b.bill_date DESC""",
            (patient_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_bill(bill_id: int, amount: float = None,
                payment_status: str = None, bill_date: str = None) -> dict:
    existing = get_bill_by_id(bill_id)
    if not existing:
        raise ValueError(f"Bill id={bill_id} not found.")

    new_amount  = float(amount)  if amount         is not None else existing["amount"]
    new_status  = payment_status if payment_status is not None else existing["payment_status"]
    new_date    = bill_date      if bill_date       is not None else existing["bill_date"]

    if new_status not in VALID_STATUSES:
        raise ValueError(f"payment_status must be one of {VALID_STATUSES}.")
    if new_amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE bills SET amount=?, payment_status=?, bill_date=? WHERE id=?",
            (new_amount, new_status, new_date, bill_id),
        )
        conn.commit()
        return get_bill_by_id(bill_id)
    finally:
        conn.close()


def delete_bill(bill_id: int) -> bool:
    if not get_bill_by_id(bill_id):
        raise ValueError(f"Bill id={bill_id} not found.")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM bills WHERE id=?", (bill_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def get_billing_summary() -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT
                 COUNT(*) AS total,
                 SUM(CASE WHEN payment_status='Paid'      THEN 1 ELSE 0 END) AS paid_count,
                 SUM(CASE WHEN payment_status='Pending'   THEN 1 ELSE 0 END) AS pending_count,
                 SUM(CASE WHEN payment_status='Cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
                 SUM(CASE WHEN payment_status='Paid'      THEN amount ELSE 0 END) AS paid_total,
                 SUM(CASE WHEN payment_status='Pending'   THEN amount ELSE 0 END) AS pending_total
               FROM bills"""
        ).fetchone()
        return dict(row)
    finally:
        conn.close()

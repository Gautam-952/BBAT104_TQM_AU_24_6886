"""
app/database/db.py
==================
Hospital Management System â€“ Database Layer
BBAT104 TQM Project | Q03 â€“ Improve Usability
Student: Gautam Bisht | Roll: 21 (2410301021) | CSE-A

Responsibilities:
  - Provide get_connection() for all service modules.
  - Initialize all 7 SQLite tables with PRAGMA foreign_keys = ON.
  - Seed realistic hospital sample data on first run.
"""

import sqlite3
import hashlib
import os
from datetime import date, timedelta

# â”€â”€ Path to the database file â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH  = os.path.join(BASE_DIR, "database", "hospital.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite3 connection with foreign key enforcement enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row          # access columns by name
    return conn


# â”€â”€ Schema DDL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_DDL = """
-- Table 1: users
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK(role IN ('Admin', 'Doctor', 'Staff'))
);

-- Table 2: user_preferences  (1:1 with users)
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id            INTEGER PRIMARY KEY,
    dark_mode          INTEGER NOT NULL DEFAULT 0,
    theme_name         TEXT    NOT NULL DEFAULT 'Clinical Blue',
    custom_colors_json TEXT    DEFAULT NULL,
    updated_at         TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table 3: patients
CREATE TABLE IF NOT EXISTS patients (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_code      TEXT    NOT NULL UNIQUE,
    name              TEXT    NOT NULL,
    age               INTEGER NOT NULL,
    gender            TEXT    NOT NULL,
    blood_group       TEXT    NOT NULL,
    phone             TEXT    NOT NULL UNIQUE,
    address           TEXT    NOT NULL,
    emergency_contact TEXT    NOT NULL
);

-- Table 4: doctors
CREATE TABLE IF NOT EXISTS doctors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_code    TEXT    NOT NULL UNIQUE,
    name           TEXT    NOT NULL,
    specialization TEXT    NOT NULL,
    department     TEXT    NOT NULL,
    phone          TEXT    NOT NULL UNIQUE,
    email          TEXT    NOT NULL UNIQUE
);

-- Table 5: appointments
CREATE TABLE IF NOT EXISTS appointments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL,
    doctor_id        INTEGER NOT NULL,
    appointment_date TEXT    NOT NULL,
    appointment_time TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'Scheduled'
                     CHECK(status IN ('Scheduled', 'Completed', 'Cancelled')),
    notes            TEXT    DEFAULT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(id)  ON DELETE CASCADE,
    UNIQUE (doctor_id, appointment_date, appointment_time)
);

-- Table 6: medical_records
CREATE TABLE IF NOT EXISTS medical_records (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id   INTEGER NOT NULL,
    doctor_id    INTEGER NOT NULL,
    diagnosis    TEXT    NOT NULL,
    prescription TEXT    NOT NULL,
    record_date  TEXT    NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(id)  ON DELETE RESTRICT
);

-- Table 7: bills
CREATE TABLE IF NOT EXISTS bills (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL,
    amount         REAL    NOT NULL,
    payment_status TEXT    NOT NULL DEFAULT 'Pending'
                   CHECK(payment_status IN ('Pending', 'Paid', 'Cancelled')),
    bill_date      TEXT    NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- Indexes for Q03 search filters and calendar queries
CREATE INDEX IF NOT EXISTS idx_patients_phone           ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_blood_group     ON patients(blood_group);
CREATE INDEX IF NOT EXISTS idx_appointments_date        ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_bills_status             ON bills(payment_status);
"""


def _hash(password: str) -> str:
    """Return SHA-256 hex digest of the given password string."""
    return hashlib.sha256(password.encode()).hexdigest()


def _seed(conn: sqlite3.Connection) -> None:
    """Insert realistic hospital sample data (idempotent â€“ skips if data exists)."""
    cur = conn.cursor()

    today       = date.today()
    yesterday   = (today - timedelta(days=1)).isoformat()
    today_str   = today.isoformat()
    tomorrow    = (today + timedelta(days=1)).isoformat()
    two_days    = (today + timedelta(days=2)).isoformat()
    week_later  = (today + timedelta(days=7)).isoformat()
    ts_now      = today_str + " 00:00:00"

    # â”€â”€ Users â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    users = [
        ("admin",     _hash("Admin@123"),  "Admin"),
        ("dr_sharma", _hash("Doctor@456"), "Doctor"),
        ("staff01",   _hash("Staff@789"),  "Staff"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?,?,?)",
        users,
    )

    # â”€â”€ User Preferences â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    prefs = [
        (1, 0, "Clinical Blue", None, ts_now),
        (2, 0, "Emerald Care",  None, ts_now),
        (3, 1, "Clinical Blue", None, ts_now),   # staff01 prefers dark mode
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO user_preferences
           (user_id, dark_mode, theme_name, custom_colors_json, updated_at)
           VALUES (?,?,?,?,?)""",
        prefs,
    )

    # â”€â”€ Patients â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    patients = [
        ("PAT-0001", "Arjun Mehta",    34, "Male",   "B+",  "9876543210",
         "12, Rose Garden, Delhi",         "Priya Mehta â€“ 9876543211"),
        ("PAT-0002", "Sunita Rawat",   52, "Female", "A-",  "9823456781",
         "45, Sector 7, Noida",            "Ramesh Rawat â€“ 9823456782"),
        ("PAT-0003", "Karan Singh",    28, "Male",   "O+",  "9712345678",
         "78, MG Road, Bangalore",         "Neeta Singh â€“ 9712345679"),
        ("PAT-0004", "Meena Patel",    65, "Female", "AB+", "9645321870",
         "22, Navarangpura, Ahmedabad",    "Suresh Patel â€“ 9645321871"),
        ("PAT-0005", "Rohit Verma",    19, "Male",   "B-",  "9534218760",
         "5, Civil Lines, Jaipur",         "Kavita Verma â€“ 9534218761"),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO patients
           (patient_code, name, age, gender, blood_group, phone, address, emergency_contact)
           VALUES (?,?,?,?,?,?,?,?)""",
        patients,
    )

    # â”€â”€ Doctors â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    doctors = [
        ("DOC-0001", "Dr. Ramesh Sharma",  "Cardiology",    "Cardiology",    "9811223344", "r.sharma@hospital.in"),
        ("DOC-0002", "Dr. Anjali Nair",    "Neurology",     "Neurology",     "9822334455", "a.nair@hospital.in"),
        ("DOC-0003", "Dr. Vikram Joshi",   "Orthopedics",   "Orthopedics",   "9833445566", "v.joshi@hospital.in"),
        ("DOC-0004", "Dr. Pooja Gupta",    "General Medicine","General",     "9844556677", "p.gupta@hospital.in"),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO doctors
           (doctor_code, name, specialization, department, phone, email)
           VALUES (?,?,?,?,?,?)""",
        doctors,
    )

    # â”€â”€ Appointments â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    appointments = [
        (1, 1, yesterday,   "09:00", "Completed", "Routine cardiac check-up"),
        (2, 2, yesterday,   "11:00", "Completed", "Post-surgery neurology follow-up"),
        (3, 3, today_str,   "10:00", "Scheduled", "Knee pain evaluation"),
        (4, 1, today_str,   "14:00", "Scheduled", "ECG and consultation"),
        (5, 4, tomorrow,    "09:30", "Scheduled", "Fever and general weakness"),
        (5, 2, two_days,    "10:00", "Scheduled", "Migraine management"),
        (2, 4, week_later,  "11:00", "Scheduled", "Diabetes follow-up"),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO appointments
           (patient_id, doctor_id, appointment_date, appointment_time, status, notes)
           VALUES (?,?,?,?,?,?)""",
        appointments,
    )

    # â”€â”€ Medical Records â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    records = [
        (1, 1, "Hypertension Stage 1",
         "Amlodipine 5mg OD, Salt-restricted diet, 30 min daily walk", yesterday),
        (2, 2, "Lumbar disc herniation",
         "Pregabalin 75mg BD, Physiotherapy sessions x 10, Ice pack", yesterday),
        (3, 3, "Medial meniscus tear â€“ Grade 2",
         "Diclofenac 50mg BD, Knee brace, Avoid weight-bearing for 2 weeks", yesterday),
        (4, 4, "Type 2 Diabetes Mellitus",
         "Metformin 500mg BD, HbA1c test in 3 months, Diabetic diet chart", yesterday),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO medical_records
           (patient_id, doctor_id, diagnosis, prescription, record_date)
           VALUES (?,?,?,?,?)""",
        records,
    )

    # â”€â”€ Bills â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    bills = [
        (1,  1500.00, "Paid",    yesterday),
        (2,  2200.00, "Paid",    yesterday),
        (3,   800.00, "Pending", today_str),
        (4,  3500.00, "Pending", today_str),
        (5,   450.00, "Pending", tomorrow),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO bills
           (patient_id, amount, payment_status, bill_date)
           VALUES (?,?,?,?)""",
        bills,
    )

    conn.commit()


def init_db() -> None:
    """
    Initialize the database:
      1. Ensure the database/ directory exists.
      2. Create all 7 tables (idempotent via IF NOT EXISTS).
      3. Seed realistic sample data (idempotent via INSERT OR IGNORE).
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Step A: create schema (executescript auto-commits)
    conn = get_connection()
    try:
        conn.executescript(_DDL)
    finally:
        conn.close()

    # Step B: seed data in a fresh connection (tables now guaranteed to exist)
    conn = get_connection()
    try:
        _seed(conn)
        print(f"[DB] Initialized â†’ {DB_PATH}")
    finally:
        conn.close()


# â”€â”€ Allow direct execution for testing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if __name__ == "__main__":
    init_db()
    conn = get_connection()
    tables = ["users", "user_preferences", "patients", "doctors",
              "appointments", "medical_records", "bills"]
    print("\nâ”€â”€ Seed Data Counts â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
    for t in tables:
        row = conn.execute(f"SELECT COUNT(*) AS cnt FROM {t}").fetchone()
        print(f"  {t:<20} : {row['cnt']} row(s)")
    conn.close()


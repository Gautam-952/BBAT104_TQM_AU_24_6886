# Database Design Document
## BBAT104 – Hospital Management System | Q03 – Improve Usability

---

| Field              | Details                         |
| :----------------- | :------------------------------ |
| **Student Name**   | Gautam Bisht                    |
| **Roll Number**    | 21 (2410301021)                 |
| **Branch/Section** | CSE – A                         |
| **Database**       | SQLite3 (`database/hospital.db`)|
| **Version**        | 1.0 — Review 1                  |
| **Date**           | October 2026                    |

---

## 1. Database Configuration

- **Engine:** SQLite3 (Python stdlib `sqlite3` module)
- **File Path:** `database/hospital.db`
- **Foreign Keys:** `PRAGMA foreign_keys = ON` (enforced on every connection)
- **Encoding:** UTF-8
- **Total Tables:** 7

---

## 2. Entity-Relationship Overview

```
users (1) ────────── (1) user_preferences
  │
  └── (role-based access to all modules)

patients (1) ──────── (M) appointments
patients (1) ──────── (M) medical_records
patients (1) ──────── (M) bills

doctors  (1) ──────── (M) appointments
doctors  (1) ──────── (M) medical_records
```

---

## 3. Table Schemas

---

### Table 1: `users`
Stores system login credentials and roles.

| Column          | Type     | Constraints                              | Description                      |
| :-------------- | :------- | :--------------------------------------- | :------------------------------- |
| `id`            | INTEGER  | PRIMARY KEY AUTOINCREMENT                | Unique user identifier           |
| `username`      | TEXT     | NOT NULL, UNIQUE                         | Login username                   |
| `password_hash` | TEXT     | NOT NULL                                 | SHA-256 hashed password          |
| `role`          | TEXT     | NOT NULL, CHECK(role IN ('Admin','Doctor','Staff')) | User access role    |

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK(role IN ('Admin', 'Doctor', 'Staff'))
);
```

---

### Table 2: `user_preferences`
Stores per-user UI preferences (Dark Mode, Theme). 1:1 with `users`.

| Column              | Type     | Constraints                        | Description                         |
| :------------------ | :------- | :--------------------------------- | :---------------------------------- |
| `user_id`           | INTEGER  | PRIMARY KEY, FK → users(id)        | Links to users table                |
| `dark_mode`         | INTEGER  | NOT NULL, DEFAULT 0                | 0 = Light, 1 = Dark                 |
| `theme_name`        | TEXT     | NOT NULL, DEFAULT 'Clinical Blue'  | Active theme name                   |
| `custom_colors_json`| TEXT     | DEFAULT NULL                       | JSON string for custom hex colors   |
| `updated_at`        | TEXT     | NOT NULL                           | ISO8601 timestamp of last update    |

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id            INTEGER PRIMARY KEY,
    dark_mode          INTEGER NOT NULL DEFAULT 0,
    theme_name         TEXT    NOT NULL DEFAULT 'Clinical Blue',
    custom_colors_json TEXT    DEFAULT NULL,
    updated_at         TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

### Table 3: `patients`
Core patient registration data.

| Column             | Type     | Constraints               | Description                        |
| :----------------- | :------- | :------------------------ | :--------------------------------- |
| `id`               | INTEGER  | PRIMARY KEY AUTOINCREMENT | Unique patient identifier          |
| `patient_code`     | TEXT     | NOT NULL, UNIQUE          | Auto-generated code: `PAT-0001`    |
| `name`             | TEXT     | NOT NULL                  | Full name                          |
| `age`              | INTEGER  | NOT NULL                  | Age in years                       |
| `gender`           | TEXT     | NOT NULL                  | Male / Female / Other              |
| `blood_group`      | TEXT     | NOT NULL                  | e.g., A+, B-, O+                   |
| `phone`            | TEXT     | NOT NULL, UNIQUE          | Contact number                     |
| `address`          | TEXT     | NOT NULL                  | Residential address                |
| `emergency_contact`| TEXT     | NOT NULL                  | Emergency contact number/name      |

**SQL:**
```sql
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
```

---

### Table 4: `doctors`
Doctor profiles and departmental information.

| Column           | Type     | Constraints               | Description                        |
| :--------------- | :------- | :------------------------ | :--------------------------------- |
| `id`             | INTEGER  | PRIMARY KEY AUTOINCREMENT | Unique doctor identifier           |
| `doctor_code`    | TEXT     | NOT NULL, UNIQUE          | Auto-generated code: `DOC-0001`    |
| `name`           | TEXT     | NOT NULL                  | Full name                          |
| `specialization` | TEXT     | NOT NULL                  | Medical specialization             |
| `department`     | TEXT     | NOT NULL                  | Hospital department                |
| `phone`          | TEXT     | NOT NULL, UNIQUE          | Contact number                     |
| `email`          | TEXT     | NOT NULL, UNIQUE          | Email address                      |

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS doctors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_code    TEXT    NOT NULL UNIQUE,
    name           TEXT    NOT NULL,
    specialization TEXT    NOT NULL,
    department     TEXT    NOT NULL,
    phone          TEXT    NOT NULL UNIQUE,
    email          TEXT    NOT NULL UNIQUE
);
```

---

### Table 5: `appointments`
Patient-doctor appointment scheduling.

| Column             | Type     | Constraints                                              | Description                    |
| :----------------- | :------- | :------------------------------------------------------- | :----------------------------- |
| `id`               | INTEGER  | PRIMARY KEY AUTOINCREMENT                                | Unique appointment identifier  |
| `patient_id`       | INTEGER  | NOT NULL, FK → patients(id)                              | Linked patient                 |
| `doctor_id`        | INTEGER  | NOT NULL, FK → doctors(id)                               | Linked doctor                  |
| `appointment_date` | TEXT     | NOT NULL                                                 | Date in `YYYY-MM-DD` format    |
| `appointment_time` | TEXT     | NOT NULL                                                 | Time in `HH:MM` format         |
| `status`           | TEXT     | NOT NULL, DEFAULT 'Scheduled', CHECK(status IN (...))    | Scheduled/Completed/Cancelled  |
| `notes`            | TEXT     | DEFAULT NULL                                             | Optional clinical notes        |

**Unique Constraint:** `(doctor_id, appointment_date, appointment_time)` — prevents double-booking.

**SQL:**
```sql
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
```

---

### Table 6: `medical_records`
Clinical records linking patients and doctors.

| Column        | Type     | Constraints               | Description                        |
| :------------ | :------- | :------------------------ | :--------------------------------- |
| `id`          | INTEGER  | PRIMARY KEY AUTOINCREMENT | Unique record identifier           |
| `patient_id`  | INTEGER  | NOT NULL, FK → patients(id)| Linked patient                    |
| `doctor_id`   | INTEGER  | NOT NULL, FK → doctors(id) | Treating doctor                   |
| `diagnosis`   | TEXT     | NOT NULL                  | Clinical diagnosis text            |
| `prescription`| TEXT     | NOT NULL                  | Prescribed medications/treatments  |
| `record_date` | TEXT     | NOT NULL                  | Date in `YYYY-MM-DD` format        |

**SQL:**
```sql
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
```

---

### Table 7: `bills`
Patient billing and payment tracking.

| Column           | Type     | Constraints                                             | Description                    |
| :--------------- | :------- | :------------------------------------------------------ | :----------------------------- |
| `id`             | INTEGER  | PRIMARY KEY AUTOINCREMENT                               | Unique bill identifier         |
| `patient_id`     | INTEGER  | NOT NULL, FK → patients(id)                             | Linked patient                 |
| `amount`         | REAL     | NOT NULL                                                | Bill amount in currency units  |
| `payment_status` | TEXT     | NOT NULL, DEFAULT 'Pending', CHECK(status IN (...))     | Pending / Paid / Cancelled     |
| `bill_date`      | TEXT     | NOT NULL                                                | Date in `YYYY-MM-DD` format    |

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS bills (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL,
    amount         REAL    NOT NULL,
    payment_status TEXT    NOT NULL DEFAULT 'Pending'
                   CHECK(payment_status IN ('Pending', 'Paid', 'Cancelled')),
    bill_date      TEXT    NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
```

---

## 4. Relationships Summary

| Relationship                         | Type   | FK Column                     | On Delete   |
| :----------------------------------- | :----- | :---------------------------- | :---------- |
| `user_preferences` → `users`         | 1:1    | `user_preferences.user_id`    | CASCADE     |
| `appointments` → `patients`          | M:1    | `appointments.patient_id`     | CASCADE     |
| `appointments` → `doctors`           | M:1    | `appointments.doctor_id`      | CASCADE     |
| `medical_records` → `patients`       | M:1    | `medical_records.patient_id`  | CASCADE     |
| `medical_records` → `doctors`        | M:1    | `medical_records.doctor_id`   | RESTRICT    |
| `bills` → `patients`                 | M:1    | `bills.patient_id`            | CASCADE     |

---

## 5. Indexing Strategy

| Index Name                             | Table           | Columns                                     | Purpose                         |
| :------------------------------------- | :-------------- | :------------------------------------------ | :------------------------------ |
| `idx_patients_phone`                   | patients        | `phone`                                     | Fast duplicate check            |
| `idx_patients_blood_group`             | patients        | `blood_group`                               | Q03 Search Filter               |
| `idx_appointments_date`                | appointments    | `appointment_date`                          | Calendar queries                |
| `idx_appointments_doctor_date_time`    | appointments    | `doctor_id, appointment_date, appointment_time` | Conflict detection (UNIQUE) |
| `idx_bills_status`                     | bills           | `payment_status`                            | Q03 Search Filter               |

---

## 6. Sample Seed Data Overview

The `db.py` module seeds the following realistic demo records on first run:

| Table             | Sample Records  |
| :---------------- | :-------------- |
| `users`           | 3 (Admin, Doctor, Staff) |
| `user_preferences`| 3 (one per user, Light mode, Clinical Blue) |
| `patients`        | 5 patients (mixed demographics, blood groups) |
| `doctors`         | 4 doctors (Cardiology, Neurology, Orthopedics, General) |
| `appointments`    | 6 appointments (mixed dates, statuses) |
| `medical_records` | 4 records                              |
| `bills`           | 5 bills (mixed Paid/Pending)           |

---

# System Architecture Document
## BBAT104 – Hospital Management System | Q03 – Improve Usability

---

| Field              | Details                         |
| :----------------- | :------------------------------ |
| **Student Name**   | Gautam Bisht                    |
| **Roll Number**    | 21 (2410301021)                 |
| **Branch/Section** | CSE – A                         |
| **Version**        | 1.0 — Review 1                  |
| **Date**           | October 2026                    |

---

## 1. Architectural Overview

The Hospital Management System follows a **Layered / Modular Architecture** with a clear separation of concerns across four layers. This design ensures maintainability, testability, and extensibility.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 4: USABILITY UI LAYER                      │
│              (app/ui/app_ui.py  +  main.py)                         │
│   Tkinter GUI — Tabs, KPI Cards, Dark Mode Toggle, Theme Selector,  │
│   Calendar View, Live Search Bars, CRUD Forms                       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │  calls
┌───────────────────────────▼─────────────────────────────────────────┐
│                    LAYER 3: Q03 USABILITY LAYER                     │
│              (app/services/usability_service.py — Facade)           │
│   theme_service.py         → Dark Mode + Custom Themes              │
│   dashboard_service.py     → Real-time KPI Aggregation              │
│   search_filter_service.py → Multi-criteria Search & Filtering      │
│   calendar_service.py      → Appointment Views + Conflict Detection │
└───────────────────────────┬─────────────────────────────────────────┘
                            │  calls
┌───────────────────────────▼─────────────────────────────────────────┐
│                  LAYER 2: CORE CRUD SERVICE LAYER                   │
│              (app/services/)                                        │
│   patient_service.py        → Patient CRUD                          │
│   doctor_service.py         → Doctor CRUD                           │
│   appointment_service.py    → Appointment CRUD                      │
│   medical_record_service.py → Medical Record CRUD                   │
│   bill_service.py           → Billing CRUD                          │
│   user_service.py           → User CRUD + Password Hashing          │
└───────────────────────────┬─────────────────────────────────────────┘
                            │  calls
┌───────────────────────────▼─────────────────────────────────────────┐
│                  LAYER 1: SQLITE3 DATABASE LAYER                    │
│              (app/database/db.py  +  database/hospital.db)          │
│   SQLite3 with PRAGMA foreign_keys = ON                             │
│   7 Tables: users, user_preferences, patients, doctors,             │
│             appointments, medical_records, bills                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer Descriptions

### Layer 1 — SQLite3 Database Layer
- **Files:** `app/database/db.py`, `database/hospital.db`
- **Responsibility:** Schema initialization, connection management, seed data insertion.
- **Key Design Decisions:**
  - `PRAGMA foreign_keys = ON` to enforce referential integrity.
  - All tables use auto-increment integer primary keys.
  - `user_preferences` has a 1:1 relationship with `users`.
  - `appointments`, `medical_records`, and `bills` link to `patients` and `doctors` via foreign keys.

### Layer 2 — Core CRUD Service Layer
- **Files:** `app/services/{patient,doctor,appointment,medical_record,bill,user}_service.py`
- **Responsibility:** All Create / Read / Update / Delete operations for the six core entities.
- **Key Design Decisions:**
  - Each service is a standalone module with no cross-module imports (except `db.py`).
  - `user_service.py` uses `hashlib.sha256` for password hashing.
  - Auto-code generation: `PAT-0001`, `DOC-0001` format using `PRINTF` or Python `zfill`.

### Layer 3 — Q03 Usability Layer
- **Files:** `app/services/{theme,dashboard,search_filter,calendar,usability}_service.py`
- **Responsibility:** The five TQM Q03 usability features.
- **Key Design Decisions:**
  - `usability_service.py` acts as a **Facade** — the UI interacts with one central object.
  - `theme_service.py` handles both Dark Mode and Custom Themes (two Q03 features in one file).
  - `calendar_service.py` uses Python's `datetime` for week/month calculations.
  - `search_filter_service.py` uses parameterized SQL queries (prevents SQL injection).

### Layer 4 — Usability UI Layer
- **Files:** `app/ui/app_ui.py`, `main.py`
- **Responsibility:** Tkinter-based desktop GUI; entry point for the live demo.
- **Key Design Decisions:**
  - Single-window tabbed layout using `ttk.Notebook`.
  - Top bar with persistent Dark Mode toggle and Theme dropdown.
  - Each tab corresponds to one CRUD module or Q03 feature.

---

## 3. Main System Workflow Diagram

```
User launches: python main.py
        │
        ▼
main.py ──► db.py: Initialize DB + Seed Data
        │
        ▼
main.py ──► app_ui.py: Launch Tkinter Window
        │
        ├──► Top Bar:
        │       ├── [Dark Mode Toggle] ──► theme_service.toggle_dark_mode()
        │       └── [Theme Dropdown]   ──► theme_service.apply_theme()
        │
        ├──► Tab: Dashboard
        │       └── [Load KPIs] ──► dashboard_service.get_dashboard_stats()
        │
        ├──► Tab: Patients
        │       ├── [Add/Edit/Delete] ──► patient_service.create/update/delete_patient()
        │       └── [Search]         ──► search_filter_service.filter_patients()
        │
        ├──► Tab: Doctors
        │       ├── [Add/Edit/Delete] ──► doctor_service.create/update/delete_doctor()
        │       └── [Search]         ──► search_filter_service.filter_doctors()
        │
        ├──► Tab: Appointments
        │       ├── [Schedule]       ──► appointment_service.create_appointment()
        │       │                         └── calendar_service.check_conflict()
        │       └── [Filter]         ──► search_filter_service.filter_appointments()
        │
        ├──► Tab: Medical Records
        │       └── [Add/Edit/Delete] ──► medical_record_service.*
        │
        ├──► Tab: Billing
        │       ├── [Generate Bill]  ──► bill_service.create_bill()
        │       └── [Filter]         ──► search_filter_service.filter_bills()
        │
        └──► Tab: Calendar
                └── [View Day/Week/Month] ──► calendar_service.get_daily/weekly/monthly_view()
```

---

## 4. Module Dependency Map

```
main.py
 └── app/ui/app_ui.py
      └── app/services/usability_service.py  (Facade)
           ├── app/services/theme_service.py
           ├── app/services/dashboard_service.py
           ├── app/services/search_filter_service.py
           └── app/services/calendar_service.py
      └── app/services/patient_service.py
      └── app/services/doctor_service.py
      └── app/services/appointment_service.py
      └── app/services/medical_record_service.py
      └── app/services/bill_service.py
      └── app/services/user_service.py
           └── app/database/db.py  (all services depend on this)
                └── database/hospital.db
```

---

## 5. Technology & Design Patterns

| Pattern / Technology    | Usage                                                    |
| :---------------------- | :------------------------------------------------------- |
| **Layered Architecture**| 4 layers: DB → CRUD → Q03 → UI                          |
| **Facade Pattern**      | `usability_service.py` wraps all 5 Q03 services          |
| **Repository Pattern**  | Each service acts as a repository for its entity         |
| **MVC Influence**       | Services = Model+Controller; `app_ui.py` = View          |
| **SQLite3 + Parameterized Queries** | Prevents SQL injection; enforces FK integrity |
| **SHA-256 Hashing**     | Secure password storage in `user_service.py`             |

---

## 6. File Structure Reference

```text
Hospital-TQM-Project/
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py
│   ├── models/
│   │   └── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── patient_service.py
│   │   ├── doctor_service.py
│   │   ├── appointment_service.py
│   │   ├── medical_record_service.py
│   │   ├── bill_service.py
│   │   ├── user_service.py
│   │   ├── theme_service.py          # Q03.1 Dark Mode & Q03.2 Custom Themes
│   │   ├── dashboard_service.py      # Q03.3 Dashboard Overview
│   │   ├── search_filter_service.py  # Q03.4 Search Filters
│   │   ├── calendar_service.py       # Q03.5 Calendar
│   │   └── usability_service.py      # Q03 Integration Facade
│   └── ui/
│       ├── __init__.py
│       └── app_ui.py
├── database/
│   └── hospital.db
├── docs/
│   ├── SRS.md
│   ├── ARCHITECTURE.md
│   └── DATABASE_DESIGN.md
├── tests/
│   ├── test_crud.py
│   └── test_q03_usability.py
├── main.py
├── README.md
└── .gitignore
```

---

# Hospital Management System — BBAT104 TQM Project
## Assigned Quality Goal: Q03 — Improve Usability

---

## 1. Student & Project Information

| Field | Details |
| :--- | :--- |
| **Course** | BBAT104 – Fundamentals of Total Quality Management |
| **Academic Session** | 2026–27 |
| **Student Name** | Gautam Bisht |
| **Roll Number** | 21 (2410301021) |
| **Branch & Section** | Computer Science & Engineering (CSE) – Section A |
| **Baseline System** | Hospital Management System |
| **Assigned Quality Goal** | **Q03 – Improve Usability** |
| **5 Mandatory Q03 Features** | 1. Dark Mode, 2. Custom Themes, 3. Dashboard Overview, 4. Search Filters, 5. Calendar |
| **Core TQM Objective** | Reduce patient wait times, prevent record duplication, and improve staff navigation efficiency |
| **Technology Stack** | Python 3.x, SQLite3 (`database/hospital.db`), Pytest, Tkinter GUI (`main.py`) |

---

## 2. Project Overview & TQM Quality Goal (Q03)

Hospital receptionists, ward nurses, and doctors operate in demanding clinical environments under tight time constraints. Legacy hospital software typically suffers from high cognitive friction, visual fatigue, disjointed screens, duplicate patient entry, and accidental appointment double-booking.

This project implements **Quality Goal Q03 (Improve Usability)** by transforming the baseline Hospital Management System into an ergonomic, streamlined clinical workstation:
* **Visual Ergonomics:** Reducing optical strain during prolonged shifts via synchronized Dark Mode and accessible theme palettes.
* **Navigation Efficiency:** Providing an instant real-time KPI overview and aggregated feeds so operators immediately understand hospital load.
* **Search Speed & Error Reduction:** Eliminating duplicate patient registrations and lost records with multi-criteria real-time filtering.
* **Scheduling Integrity:** Preventing doctor slot clashes and double-booking using automated calendar slot conflict checks.

---

## 3. Five Mandatory Q03 Usability Features

### Q03.1 — Dark Mode Toggle & Persistence
* **Implementation:** `app/services/theme_service.py` & `app/ui/app_ui.py`
* **Behavior:** Seamless one-click toggle in the top navigation bar between Light (`#f8fafc`) and Dark (`#0f172a`) modes. Preferences are persisted in SQLite `user_preferences` table across restarts.

### Q03.2 — Custom Themes & Color Validation
* **Implementation:** `app/services/theme_service.py`
* **Behavior:** Offers 4 pre-engineered medical color themes:
  1. **Clinical Blue** (`#0f172a` base, `#3b82f6` accent)
  2. **Emerald Care** (`#022c22` base, `#10b981` accent)
  3. **High Contrast** (`#000000` base, `#facc15` accent)
  4. **Warm Neutral** (`#1c1917` base, `#f97316` accent)
* Includes hex regex validation (`#RGB` or `#RRGGBB`) ensuring accessibility and rejecting invalid color codes.

### Q03.3 — Dashboard Overview & Real-Time KPIs
* **Implementation:** `app/services/dashboard_service.py` & `app/ui/app_ui.py`
* **Behavior:** Live KPI cards displaying:
  * Total Patients registered
  * Active Doctors on duty
  * Today's Appointments & Scheduled count
  * Pending Bills count & Total Outstanding Revenue (Rs.)
  * Live feeds of Recent Patient Registrations and Upcoming Appointments.

### Q03.4 — Advanced Multi-Criteria Search Filters
* **Implementation:** `app/services/search_filter_service.py`
* **Behavior:** Real-time parameterized search inputs eliminating manual browsing:
  * **Patients:** Name substring, Patient Code (`PAT-XXXX`), Blood Group, Age Range (`age_min` - `age_max`).
  * **Doctors:** Name, Department, Specialization.
  * **Appointments:** Status (`Scheduled`, `Completed`, `Cancelled`), Date Ranges.
  * **Billing:** Payment Status (`Pending`, `Paid`), Minimum/Maximum Amount.

### Q03.5 — Appointment Calendar & Slot Conflict Protection
* **Implementation:** `app/services/calendar_service.py`
* **Behavior:** Comprehensive schedule management:
  * **Daily, Weekly, and Monthly Agenda Views:** Displays doctor bookings chronologically.
  * **Double-Booking Prevention:** SQLite unique constraints and service validation reject overlapping bookings for the same doctor at the same date and time slot.

---

## 4. System Architecture

The project follows a clean 4-tier layered architecture:

```text
┌─────────────────────────────────────────────────────────────────┐
│                    GUI Presentation Layer                       │
│                     (app/ui/app_ui.py)                          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                   Q03 Usability Facade Layer                    │
│                 (app/services/usability_service.py)             │
├────────────────────────────────┬────────────────────────────────┤
│ • theme_service.py             │ • dashboard_service.py         │
│ • search_filter_service.py     │ • calendar_service.py          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                     Core CRUD Service Layer                     │
│ • patient_service.py           │ • doctor_service.py            │
│ • appointment_service.py       │ • medical_record_service.py    │
│ • bill_service.py              │ • user_service.py              │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                      SQLite3 Database Layer                     │
│                    (app/database/db.py)                         │
│                    database/hospital.db                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Database Design (7 Tables)

1. **`users`**: User authentication with SHA-256 password hashing and role enforcement (`Admin`, `Doctor`, `Staff`).
2. **`user_preferences`**: Q03 usability preferences (`dark_mode`, `theme_name`, `custom_colors_json`, `updated_at`).
3. **`patients`**: Patient demographics, unique code (`PAT-XXXX`), phone, blood group, emergency contact.
4. **`doctors`**: Doctor roster, unique code (`DOC-XXXX`), specialization, department, contact info.
5. **`appointments`**: Doctor-patient bookings with date, time, status, notes, and slot conflict unique index.
6. **`medical_records`**: Clinical history, diagnoses, prescriptions, and visit dates.
7. **`bills`**: Patient invoices, amount (Rs.), payment status (`Pending`, `Paid`, `Cancelled`), and date.

Foreign keys (`PRAGMA foreign_keys = ON;`) are strictly enforced with cascade deletions.

---

## 6. Directory Structure

```text
Hospital-TQM-Project/
│
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                     # SQLite engine, schema DDL & realistic seed data
│   │
│   ├── models/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── patient_service.py        # Patient CRUD
│   │   ├── doctor_service.py         # Doctor CRUD
│   │   ├── appointment_service.py    # Appointment scheduling & conflict checks
│   │   ├── medical_record_service.py # Medical history & prescriptions
│   │   ├── bill_service.py           # Billing, invoicing & revenue calculation
│   │   ├── user_service.py           # User management & SHA-256 auth
│   │   ├── theme_service.py          # Q03.1 Dark Mode & Q03.2 Custom Themes
│   │   ├── dashboard_service.py      # Q03.3 Dashboard Overview KPIs
│   │   ├── search_filter_service.py  # Q03.4 Multi-criteria Search Filters
│   │   ├── calendar_service.py       # Q03.5 Calendar & Conflict Engine
│   │   └── usability_service.py      # Q03 Unified Integration Facade
│   │
│   └── ui/
│       ├── __init__.py
│       └── app_ui.py                 # Full 7-tab Tkinter Graphical User Interface
│
├── database/
│   └── hospital.db                   # SQLite3 database file
│
├── docs/
│   ├── SRS.md                        # Software Requirements Specification (Q03)
│   ├── ARCHITECTURE.md               # Layered architectural workflows & diagrams
│   └── DATABASE_DESIGN.md            # Schema definitions, indices & relationships
│
├── tests/
│   ├── test_crud.py                  # Pytest suite for 6 core CRUD modules
│   └── test_q03_usability.py         # Pytest suite for 5 Q03 Usability features
│
├── main.py                           # Main application entry point (seeds DB & opens UI)
├── README.md                         # Project documentation
└── .gitignore                        # Git exclusion rules
```

---

## 7. How to Run the Application & Tests

### Prerequisites
* Python 3.10+
* SQLite3 (bundled with standard Python)
* Tkinter (bundled with standard Python)
* Pytest (`pip install pytest`)

### 1. Launch the Desktop Application
Run either from the project root:
```bash
python main.py
```
Or directly launch the UI module:
```bash
python app/ui/app_ui.py
```

### 2. Run the Automated Pytest Suite
Run the full test suite with verbose output:
```bash
pytest -v
```

---

## 8. Review 1 & Review 2 Deliverables Status

| Deliverable | Requirement | Status |
| :--- | :--- | :---: |
| **Review 1: SRS** | `docs/SRS.md` covering Q03 objectives, scope, roles, modules | ✅ Complete |
| **Review 1: Architecture** | `docs/ARCHITECTURE.md` with layered design & workflows | ✅ Complete |
| **Review 1: DB Design** | `docs/DATABASE_DESIGN.md` detailing 7 tables & FK constraints | ✅ Complete |
| **Review 2: Database Layer** | `app/database/db.py` with foreign keys & realistic seed data | ✅ Complete |
| **Review 2: 6 CRUD Modules** | Patients, Doctors, Users, Appointments, Records, Bills | ✅ Complete |
| **Review 2: Q03.1 Dark Mode** | Toggle and persistence in `user_preferences` | ✅ Complete |
| **Review 2: Q03.2 Themes** | 4 preset themes + custom hex color validation | ✅ Complete |
| **Review 2: Q03.3 Dashboard** | Real-time KPI counts, financial totals & active feeds | ✅ Complete |
| **Review 2: Q03.4 Filters** | Multi-criteria parameterized search across all entities | ✅ Complete |
| **Review 2: Q03.5 Calendar** | Daily/Weekly/Monthly calendar & slot conflict prevention | ✅ Complete |
| **Review 2: Working GUI** | Full 7-tab Tkinter interface with live theme switching | ✅ Complete |
| **Review 2: Test Suite** | 25+ automated pytest tests in `tests/` with 0 failures | ✅ Complete |

---

*Academic Session 2026–27 | Gautam Bisht | Roll No: 21 (2410301021) | CSE-A | BBAT104 Fundamentals of TQM*

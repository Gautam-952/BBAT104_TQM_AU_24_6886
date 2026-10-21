# Software Requirements Specification (SRS)
## BBAT104 – Fundamentals of Total Quality Management
### Hospital Management System | Q03 – Improve Usability

---

| Field              | Details                                    |
| :----------------- | :----------------------------------------- |
| **Student Name**   | Gautam Bisht                               |
| **Roll Number**    | 21 (2410301021)                            |
| **Branch/Section** | CSE – A                                    |
| **Course**         | BBAT104 – Fundamentals of TQM              |
| **Session**        | 2026–27                                    |
| **Quality Goal**   | Q03 – Improve Usability                    |
| **Version**        | 1.0                                        |
| **Date**           | October 2026                               |

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for a **Hospital Management System (HMS)** developed as part of the BBAT104 TQM course project. The system is designed to demonstrate TQM Quality Goal **Q03 – Improve Usability** by addressing real-world inefficiencies in hospital operations.

### 1.2 Scope
The HMS covers six core operational modules (Patient, Doctor, Appointment, Medical Record, Billing, and User management) enhanced with five **Q03 Usability features** (Dark Mode, Custom Themes, Dashboard Overview, Search Filters, and Calendar). The system is a desktop application built with Python 3.x, SQLite3, and Tkinter.

### 1.3 Definitions & Acronyms

| Term   | Definition                                   |
| :----- | :------------------------------------------- |
| HMS    | Hospital Management System                   |
| TQM    | Total Quality Management                     |
| Q03    | Assigned quality goal: Improve Usability     |
| CRUD   | Create, Read, Update, Delete                 |
| SRS    | Software Requirements Specification          |
| UI     | User Interface                               |
| KPI    | Key Performance Indicator                    |
| DB     | Database (SQLite3)                           |

---

## 2. Problem Statement

Poorly structured hospital management software causes the following measurable quality problems:

| Problem                        | Impact                                          |
| :----------------------------- | :---------------------------------------------- |
| Long patient wait times        | Reduced patient satisfaction and care quality   |
| Duplicate patient records      | Incorrect diagnosis and billing errors          |
| Doctor scheduling clashes      | Missed appointments and resource conflicts      |
| No centralized dashboard       | Operators cannot assess hospital status quickly |
| Absence of search/filter tools | Staff waste time manually scrolling records     |
| No dark mode / theme support   | Eye fatigue during night shifts                 |
| No calendar view               | Difficulty visualizing upcoming appointments    |

**Core TQM Goal:** Reduce patient wait times, prevent record duplication, and improve staff navigation efficiency through a usability-focused HMS.

---

## 3. Quality Objective — Q03: Improve Usability

The five mandatory Q03 usability features implemented in this project are:

| #   | Feature              | Description                                                                 |
| :-- | :------------------- | :-------------------------------------------------------------------------- |
| 1   | **Dark Mode**        | Toggle between light and dark color schemes; persists per user preference   |
| 2   | **Custom Themes**    | Preset themes (Clinical Blue, Emerald Care, High Contrast, Warm Neutral) + custom hex color support |
| 3   | **Dashboard Overview** | Real-time KPI cards: Total Patients, Total Doctors, Today's Appointments, Bills summary |
| 4   | **Search Filters**   | Multi-criteria live search for Patients, Doctors, Appointments, and Bills   |
| 5   | **Calendar**         | Daily/weekly/monthly appointment views with doctor slot conflict detection  |

---

## 4. Scope & User Roles

### 4.1 User Roles

| Role      | Permissions                                                                   |
| :-------- | :---------------------------------------------------------------------------- |
| **Admin** | Full access: manage users, all CRUD operations, view all reports              |
| **Doctor**| View/update own appointments and medical records; read patient data           |
| **Staff** | Manage patient registration, billing, and appointment scheduling              |

### 4.2 System Boundaries
- **In Scope:** Patient, Doctor, Appointment, Medical Record, Billing, User CRUD; 5 Q03 features; Pytest suite.
- **Out of Scope:** Network/multi-user concurrency, external integrations (HL7, DICOM), Review 3/4 artefacts (FMEA, SIPOC, Pareto, Fishbone).

---

## 5. Modules & Features

### 5.1 Core CRUD Modules (6)

| Module              | Key Operations                                                             |
| :------------------ | :------------------------------------------------------------------------- |
| **Patient**         | Register, view, update, delete patient; unique `patient_code` generation   |
| **Doctor**          | Add, view, update, delete doctor; unique `doctor_code` generation          |
| **Appointment**     | Schedule, view, update, cancel appointments; conflict detection            |
| **Medical Record**  | Create, view, update, delete medical records linked to patient & doctor    |
| **Billing**         | Generate, view, update bills; track Paid / Pending / Cancelled status      |
| **User**            | Register, authenticate, update, delete users with hashed passwords (SHA-256)|

### 5.2 Q03 Usability Modules (5)

| Module                   | Service File                  | Key Operations                                              |
| :----------------------- | :---------------------------- | :---------------------------------------------------------- |
| **Dark Mode**            | `theme_service.py`            | Toggle dark/light; persist preference; return color tokens  |
| **Custom Themes**        | `theme_service.py`            | Apply preset/custom themes; hex color validation            |
| **Dashboard Overview**   | `dashboard_service.py`        | Fetch real-time KPI counts; recent admissions               |
| **Search Filters**       | `search_filter_service.py`    | Filter patients, doctors, appointments, bills               |
| **Calendar**             | `calendar_service.py`         | Generate daily/weekly/monthly views; prevent double-booking |

---

## 6. Functional Requirements

### FR-01: Patient Management
- FR-01.1: System shall allow staff to register a new patient with mandatory fields: name, age, gender, blood group, phone, address, emergency contact.
- FR-01.2: System shall auto-generate a unique `patient_code` (e.g., `PAT-0001`).
- FR-01.3: System shall prevent duplicate phone numbers during registration.
- FR-01.4: System shall allow update and soft-delete of patient records.

### FR-02: Doctor Management
- FR-02.1: System shall allow admin to add doctors with specialization and department.
- FR-02.2: System shall auto-generate a unique `doctor_code` (e.g., `DOC-0001`).

### FR-03: Appointment Management
- FR-03.1: System shall allow scheduling appointments linking a patient and doctor.
- FR-03.2: System shall enforce slot conflict detection (no two appointments for same doctor at same date/time).
- FR-03.3: Appointment status shall be one of: `Scheduled`, `Completed`, `Cancelled`.

### FR-04: Medical Records
- FR-04.1: System shall link medical records to a patient and a doctor.
- FR-04.2: Records shall include diagnosis, prescription, and record date.

### FR-05: Billing
- FR-05.1: System shall generate bills linked to a patient.
- FR-05.2: Payment status shall be one of: `Pending`, `Paid`, `Cancelled`.

### FR-06: User Management
- FR-06.1: Passwords shall be hashed using SHA-256 before storage.
- FR-06.2: Roles shall be restricted to: `Admin`, `Doctor`, `Staff`.

### FR-Q03.1: Dark Mode
- The system shall persist dark/light mode preference per user in `user_preferences`.
- Toggling mode shall immediately update all UI color tokens.

### FR-Q03.2: Custom Themes
- System shall offer 4 preset themes and support custom hex color input.
- Invalid hex codes shall be rejected with a descriptive error.

### FR-Q03.3: Dashboard Overview
- Dashboard shall display real-time counts: Total Patients, Total Doctors, Today's Appointments, Pending Bills, Paid Bills, Recent Admissions (last 5).

### FR-Q03.4: Search Filters
- Patients: filter by name, code, blood group, age range.
- Doctors: filter by department, specialization.
- Appointments: filter by status, date.
- Bills: filter by payment status.

### FR-Q03.5: Calendar
- System shall generate appointment lists for a given day, week, or month.
- System shall detect and block double-booking of a doctor at the same date/time slot.

---

## 7. Non-Functional Requirements

| Category          | Requirement                                                              |
| :---------------- | :----------------------------------------------------------------------- |
| **Performance**   | Dashboard KPI fetch in < 500 ms on local SQLite                          |
| **Reliability**   | Foreign key constraints enforced via `PRAGMA foreign_keys = ON`          |
| **Usability**     | UI must support Dark Mode, themes, and be navigable via tabs             |
| **Testability**   | Minimum 12 automated Pytest tests covering CRUD and Q03 features         |
| **Portability**   | Runs on Python 3.x on Windows/Linux/macOS without additional dependencies beyond stdlib |
| **Security**      | Passwords stored as SHA-256 hashes; no plaintext storage                 |

---

## 8. Technology Stack

| Component    | Technology                          |
| :----------- | :---------------------------------- |
| Language     | Python 3.x                          |
| Database     | SQLite3 (`database/hospital.db`)    |
| UI Framework | Tkinter (stdlib)                    |
| Testing      | Pytest                              |
| Password     | `hashlib.sha256` (stdlib)           |

---

*End of SRS — Review 1 Deliverable*

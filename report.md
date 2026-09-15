# 🏥 PulseCare HMS — Comprehensive Technical Project Report

**Project Title**: PulseCare Hospital Management System (HMS v2.0)  
**Academic Program**: IIT Madras BS Degree in Data Science & Applications  
**Course Milestone**: Modernization & Architecture Upgrade (MAD-1 Project)  
**Author**: Ramrup Satpati (Student ID: 24f3004027)  
**Date**: September 15, 2026  
**License**: GNU General Public License v3.0 (GNU GPLv3)  
**Live Showcase URL**: [https://24f3004027.github.io/HMS-MAD-Projectv1/](https://24f3004027.github.io/HMS-MAD-Projectv1/)  
**GitHub Repository**: [https://github.com/24f3004027/HMS-MAD-Projectv1](https://github.com/24f3004027/HMS-MAD-Projectv1)  

---

## 1. Executive Summary

**PulseCare HMS** is a modernized, full-stack multi-role hospital management web application built using Python, Flask, SQLAlchemy, Flask-Login, and an HTML5 3D Canvas visual engine. Designed as a real-world healthcare administration platform, PulseCare HMS connects Administrators, Specialist Doctors, and Patients into a unified digital ecosystem.

Key achievements of this modernization milestone include:
- **3D Perspective Canvas Engine**: Real-time rendering of floating, rotating 3D Medical Plus (`+`) crosses with depth perspective scaling and an animated EKG heartbeat pulse wave scanner (`canvas-bg.js`).
- **Multi-Role Portal Access Control**: Role-based access control (RBAC) separating Admin governance, Doctor clinical management, and Patient appointment scheduling.
- **Doctor Profile Avatar System**: Dynamic photo avatar engine with `@property def avatar_url` on `Doctor` models and automatic `onerror` fallback handling for broken image URLs.
- **Automated Database Seeding**: Integrated SQLite auto-seeding engine (`perform_seeding()`) and standalone seeder script (`create_db.py`).
- **100% Automated Test Pass Rate**: Verified via `test_app.py` test suite.
- **GNU GPLv3 Re-Licensing**: Fully compliant with the GNU General Public License v3.0.

---

## 2. System Architecture & Tech Stack

PulseCare HMS follows the Model-View-Controller (MVC) architectural pattern with a modular blueprint structure:

```
HMS-MAD-Projectv1/
├── app/
│   ├── __init__.py           # Flask App Factory, LoginManager & Auto-Seeder
│   ├── models.py             # SQLAlchemy Database Schemas & Avatar Engine
│   ├── routes.py             # Multi-Role Routing & Controllers
│   ├── static/
│   │   └── js/canvas-bg.js   # 3D Medical Cross & EKG Heartbeat Visual Engine
│   └── templates/            # Glassmorphism 2.0 Jinja2 Templates
├── docs/
│   └── index.html            # GitHub Pages Interactive Showcase Page
├── instance/                 # SQLite Database (hms.db)
├── create_db.py              # Database Initialization Script
├── run.py                    # Application Entry Point (Port 5002)
├── test_app.py               # Automated Unit Test Suite
├── report.md                 # Markdown Technical Report
└── LICENSE                   # GNU General Public License v3.0 (GNU GPLv3)
```

### Technology Stack Table

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.14 / Flask 3.x | Routing, Session Management, Blueprint Architecture |
| **ORM / Database** | SQLAlchemy / SQLite | Object-Relational Mapping & Persistence |
| **Authentication** | Flask-Login & Werkzeug | Password Hashing (`scrypt`/`pbkdf2`) & Multi-Model `load_user` |
| **Frontend Styling** | Bootstrap 5.3 + Glassmorphism 2.0 | Dark/Light Mode Theme Switcher with `localStorage` |
| **Visual Animation** | HTML5 Canvas (JavaScript ES6) | 3D Medical Plus Rotation & Heartbeat EKG Pulse Wave |
| **Unit Testing** | Python `unittest` | Automated Verification Suite |
| **License** | GNU GPLv3 | Open Source Copyleft Licensing |

---

## 3. Database Schema & Entity Relationships

The relational database schema models complex medical workflows between hospital departments, doctors, patients, appointments, treatments, and availabilities.

```
       ┌──────────────┐
       │  Department  │
       └──────┬───────┘
              │ 1
              │
              │ N
       ┌──────┴───────┐             ┌──────────────┐
       │    Doctor    ├────────────►│ Availability │
       └──────┬───────┘ 1         N └──────────────┘
              │ 1
              │
              │ N
       ┌──────┴───────┐ 1         1 ┌──────────────┐
       │ Appointment  ├────────────►│  Treatment   │
       └──────▲───────┘           N └──────────────┘
              │ N
              │
              │ 1
       ┌──────┴───────┐
       │   Patient    │
       └──────────────┘
```

### Key Models Breakdown

1. **`Admin`**: System governance credentials (`username`, `email`, `password_hash`).
2. **`Department`**: Medical specialties (Cardiology, Neurology, Pediatrics, Orthopedics, General Medicine).
3. **`Doctor`**: Specialist details (`name`, `email`, `specialization`, `experience_years`, `consultation_fee`, `profile_image`, `is_active`). Includes `@property def avatar_url` for high-resolution doctor portrait photos with fallback handling.
4. **`Patient`**: Registered patient details (`name`, `age`, `gender`, `contact`, `email`, `password_hash`).
5. **`Appointment`**: Scheduled visits (`date`, `time`, `doctor_id`, `patient_id`, `status`, `diagnosis`, `treatment_notes`, `prescription`).
6. **`Treatment`**: Medical charges (`description`, `medicine`, `cost`, `appointment_id`).
7. **`Availability`**: 7-day recurring doctor schedule slots (`doctor_id`, `date`, `slot_time`, `is_available`).

---

## 4. Portal Capabilities & User Experience

### 4.1 Administrator Portal
- **Doctor Onboarding**: Add new specialist doctors with department mapping and initial consultation fees.
- **Roster Governance**: Toggle doctor active/inactive status and view hospital metrics.
- **Department Management**: Add new medical departments and monitor patient booking volume.

### 4.2 Specialist Doctor Portal
- **Clinical Queue**: View today's, upcoming, and completed patient appointments.
- **Medical Records**: Update appointment status (Booked, Confirmed, Completed, Cancelled), record clinical diagnoses, write prescriptions, and log treatment costs.
- **Modal Window Management**: Modals feature enhanced close (`X`) cross buttons with SVG filter inversion in dark mode and fail-proof JavaScript event delegation.

### 4.3 Patient Portal
- **Doctor Discovery**: Search specialist doctors by name, department, or medical specialty.
- **Appointment Booking**: Select available time slots, view doctor consultation fees, and track appointment statuses.
- **Medical History**: Access past treatment notes, prescriptions, and financial summaries.

---

## 5. Visual Engine & UI Innovations

- **3D Medical Plus (`+`) Canvas**: The background canvas (`canvas-bg.js`) projects 3D rotating medical cross particles with perspective depth scaling:
  $$\text{scale} = \frac{f}{f + z}$$
  where $f = 450$ is the focal length and $z$ represents particle depth. Particles rotate smoothly around X, Y, and Z axes while drifting toward the viewer.
- **Heartbeat EKG Waveform**: An animated electrocardiogram (P-Q-R-S-T) pulse wave scanner continuously sweeps across the canvas with a glowing cyan trailing lead.
- **Dark & Light Mode Switcher**: Seamless theme switching with persistent state saved to `localStorage`.

---

## 6. Verification & Automated Testing

The application includes an automated unit test suite in `test_app.py` verifying authentication and appointment booking logic:

```bash
$ python -m unittest test_app.py
..
----------------------------------------------------------------------
Ran 2 tests in 0.476s

OK
```

---

## 7. Conclusion & Licensing

PulseCare HMS represents a complete modernization of academic hospital management applications. By combining robust backend Flask architecture with modern 3D HTML5 visual design and professional doctor profile avatars, the platform delivers an intuitive experience for healthcare professionals and patients alike.

**License**: Distributed under the **GNU General Public License v3.0 (GNU GPLv3)**.

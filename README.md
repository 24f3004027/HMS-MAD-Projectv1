# 🏥 PulseCare HMS — 3D Healthcare Management Platform

> **IIT Madras BS Degree — Modernization Milestone Showcase**  
> *A full-stack, multi-role hospital management web application engineered with Python, Flask, SQLAlchemy, Glassmorphism UI 2.0, 3D rotating Medical Plus (`+`) canvas visual effects, and animated heartbeat EKG pulse waves.*

---

## 🌐 Live Interactive GitHub Pages Landing Site
👉 **[PulseCare HMS Showcase Site](https://24f3004027.github.io/HMS-MAD-Projectv1/)**

---

## ⚡ Key Highlights & Architecture

- **3D Floating Medical Cross Canvas**: HTML5 perspective projection engine rendering floating 3D rotating Medical Plus (`+`) crosses, mouse parallax tilt, and smooth animated EKG heartbeat pulse waves (`canvas-bg.js`).
- **Multi-Role Portal Access**: Dedicated authorization workflows for **Admins**, **Doctors**, and **Patients**.
- **Modern Glassmorphism 2.0**: Dark & Light mode switcher with persistent `localStorage`, custom glassmorphism cards, and medical color accents.
- **Automated Database Engine**: SQLite with automatic initial data seeding (`perform_seeding()`) and standalone seeder script (`create_db.py`).
- **Robust Verification**: 100% test pass rate using automated unit test suite (`test_app.py`).

---

## 🔑 Default Seeded Credentials

| Role | Login Identifier | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | System setup, Doctor onboarding, Patient status overview |
| **Doctor** | `sarah@hms.org` | `doctor123` | Patient queue, Diagnosis, Prescriptions, Availability |
| **Patient** | `ramrup` or `ramrup@hms.org` | `user123` | Doctor search, Appointment booking, Rescheduling |

---

## 💻 Quickstart & Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/24f3004027/HMS-MAD-Projectv1.git
cd HMS-MAD-Projectv1

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed database (Optional, auto-seeds on first run)
python create_db.py

# 5. Run application (Port 5002)
python run.py
```

Open your browser at `http://localhost:5002`.

---

## 🧪 Automated Testing

Run unit tests cleanly using Python `unittest`:

```bash
python -m unittest test_app.py
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

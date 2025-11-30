📘 Hospital Management System (HMS)
Modern, Responsive Full-Stack Healthcare Appointment Platform

A fully functional hospital management system built with Flask + SQLAlchemy, featuring a complete glassmorphism UI, separate portals for Admin, Doctor, and Patient, and full appointment + availability workflows.

This project is designed as a real-world mini HMS for academic or practical use.

🚀 Features
👤 Patient Portal

Register, login & manage profile

Search doctors by name/department

Book appointments with validation

Reschedule or cancel appointments

View past & upcoming appointments

Auto-generated treatment history chart

🩺 Doctor Portal

Login & view dashboard

Set availability for next 7 days

View today's, upcoming & past appointments

Update appointment diagnosis and treatment

Prescription entry

Appointment status analytics chart

🛠 Admin Portal

Secure admin login

Add doctors with department mapping

View/search doctors & patients

Blacklist patient or doctor

View system-wide appointments

View doctor login credentials (email only)

🎨 UI / UX

Built using Bootstrap 5 + custom Glassmorphism CSS, including:

Fully responsive design

Smooth gradients

Blurred card effects

Clean form styling

Unified theme across all portals

🏗 Tech Stack
Category	Technology
Backend	Flask, Python, Jinja2
Database	SQLAlchemy (SQLite / MySQL compatible)
Frontend	HTML5, Bootstrap 5, Glassmorphism CSS
Auth	Secure hashed passwords using Werkzeug
Charts	Chart.js

📂 Project Structure

HMS-MAD-Projectv1/
│── run.py
│── requirements.txt
│── instance/                
│   └── hms.db
│── venv/                    
│── app/
│   ├── __init__.py
│   ├── api.py
│   ├── models.py
│   ├── routes.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── patient_login.html
│   │   ├── patient_register.html
│   │   ├── patient_dashboard.html
│   │   ├── patient_profile.html
│   │   ├── patient_book.html
│   │   ├── patient_reschedule.html
│   │   ├── doctor_login.html
│   │   ├── doctor_dashboard.html
│   │   ├── doctor_appointment_view.html
│   │   ├── doctor_availability.html
│   │   ├── admin_login.html
│   │   ├── admin_dashboard.html
│   │   ├── add_doctor.html
│   │   ├── update_doctor.html
│   │   ├── search_doctors.html
│   │   ├── search_patients.html
│   │   ├── view_doctors.html
│   │   ├── view_appointments.html
│   │   ├── doctor_credentials.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
└── README.md


⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/<your-username>/HMS.git
cd HMS

2️⃣ Create virtual environment
python3 -m venv venv
source venv/bin/activate    # Linux / Mac
venv\Scripts\activate       # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Initialize the database
python
>>> from app import db
>>> db.create_all()
>>> exit()

5️⃣ Run the server
flask run


Visit: http://127.0.0.1:5000

📸 Screenshots (Add yours)

You can add images like:

/screenshots/home.png
/screenshots/patient_dashboard.png
/screenshots/doctor_availability.png
/screenshots/admin_dashboard.png

🔑 Default Credentials (Optional)
Role	Username	Password
Admin	admin	admin123 (example)
🧪 API Endpoints (Short)
Method	Endpoint	Description
GET	/api/doctors	List all doctors
GET	/api/patients	List all patients
POST	/api/appointments	Create appointment
PUT	/api/appointments/<id>	Update appointment
DELETE	/api/appointments/<id>	Delete appointment

Add more as needed.

🤝 Contributing

Pull requests are welcome!
If adding significant changes, create a feature branch:

git checkout -b feature-new-module

📜 License

MIT License – free to use, modify, and distribute.

⭐ Support

If you liked the project, consider giving the repo a star ⭐ on GitHub!

import os
import sys
import importlib.util
from datetime import datetime, date, time, timezone
from flask import Flask
from flask_login import LoginManager
def _load_submodule(name):
    full_name = f"app.{name}"
    if full_name in sys.modules:
        return sys.modules[full_name]
    file_path = os.path.join(os.path.dirname(__file__), f"{name}.py")
    spec = importlib.util.spec_from_file_location(full_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module

_models = _load_submodule('models')
db = _models.db
Admin = _models.Admin
Department = _models.Department
Doctor = _models.Doctor
Patient = _models.Patient
Appointment = _models.Appointment
Treatment = _models.Treatment
Availability = _models.Availability

login_manager = LoginManager()
login_manager.login_view = "routes.login"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    if not user_id or "-" not in user_id:
        return None
    role, id_str = user_id.split("-", 1)
    try:
        pk = int(id_str)
    except ValueError:
        return None

    if role == "admin":
        return db.session.get(Admin, pk)
    elif role == "doctor":
        return db.session.get(Doctor, pk)
    elif role == "patient":
        return db.session.get(Patient, pk)
    return None

def perform_seeding():
    print("Auto-seeding initial HMS database...")
    # Admin
    admin = Admin(username="admin", email="admin@hms.org")
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()

    # Departments
    deps = [
        Department(name="Cardiology", description="Heart & Vascular Care"),
        Department(name="Neurology", description="Brain & Nervous System"),
        Department(name="Pediatrics", description="Child & Adolescent Care"),
        Department(name="Orthopedics", description="Bone & Joint Surgery"),
        Department(name="General Medicine", description="Primary Healthcare")
    ]
    db.session.add_all(deps)
    db.session.commit()

    # Doctors
    doc1 = Doctor(name="Dr. Sarah Jenkins", email="sarah@hms.org", department_id=deps[0].id, specialization="Cardiology & Electrophysiology", experience_years=12, consultation_fee=800.0)
    doc1.set_password("doctor123")

    doc2 = Doctor(name="Dr. Alex Rivera", email="alex@hms.org", department_id=deps[1].id, specialization="Neuro-Oncology", experience_years=10, consultation_fee=900.0)
    doc2.set_password("doctor123")

    doc3 = Doctor(name="Dr. Priya Sharma", email="priya@hms.org", department_id=deps[2].id, specialization="Pediatric Healthcare", experience_years=8, consultation_fee=600.0)
    doc3.set_password("doctor123")

    db.session.add_all([doc1, doc2, doc3])
    db.session.commit()

    # Patients
    pat1 = Patient(name="Ramrup Satpati", age=22, gender="Male", contact="+91 9876543210", email="ramrup", password_hash="")
    pat1.set_password("user123")

    pat2 = Patient(name="John Doe", age=32, gender="Male", contact="+91 9123456789", email="johndoe@example.com", password_hash="")
    pat2.set_password("user123")

    db.session.add_all([pat1, pat2])
    db.session.commit()

    # Sample Appointments
    app1 = Appointment(
        date=date.today(),
        time=time(10, 0),
        doctor_id=doc1.id,
        patient_id=pat1.id,
        status="Completed",
        diagnosis="Mild Hypertension",
        treatment_notes="Patient presented with elevated BP. Advised diet and regular exercise.",
        prescription="Amlodipine 5mg once daily"
    )

    app2 = Appointment(
        date=date.today(),
        time=time(14, 30),
        doctor_id=doc2.id,
        patient_id=pat1.id,
        status="Booked"
    )

    db.session.add_all([app1, app2])
    db.session.commit()

    # Treatments
    t1 = Treatment(description="ECG & Lipid Profile", medicine="Amlodipine 5mg", cost=1200.0, appointment_id=app1.id)
    db.session.add(t1)
    db.session.commit()

    print("HMS Database successfully seeded!")
    print("---------------------------------------------------------")
    print("Admin Login:     username: admin      | password: admin123")
    print("Doctor Login:    email: sarah@hms.org | password: doctor123")
    print("Patient Login:   username: ramrup     | password: user123")
    print("---------------------------------------------------------")

def create_app(test_config=None):
    from .models import db, Admin
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-hms-modern-2026"

    if test_config:
        app.config.update(test_config)
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hms.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    routes_module = _load_submodule('routes')
    app.register_blueprint(routes_module.routes_bp)

    @app.before_request
    def ensure_db_ready():
        if not getattr(app, "_db_initialized", False):
            db.create_all()
            try:
                if Admin.query.count() == 0:
                    perform_seeding()
            except Exception:
                db.session.rollback()
                db.create_all()
                if Admin.query.count() == 0:
                    perform_seeding()
            app._db_initialized = True

    return app

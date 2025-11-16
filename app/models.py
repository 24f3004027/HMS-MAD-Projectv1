from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -----------------------------
# 1. ADMIN (Predefined)
# -----------------------------
class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# -----------------------------
# 2. DEPARTMENT / SPECIALIZATION
# -----------------------------
class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    doctors = db.relationship("Doctor", backref="department", lazy=True)

# -----------------------------
# 3. DOCTOR
# -----------------------------
class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)

    appointments = db.relationship("Appointment", backref="doctor", lazy=True)

# -----------------------------
# 4. PATIENT
# -----------------------------
class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    appointments = db.relationship("Appointment", backref="patient", lazy=True)

# -----------------------------
# 5. APPOINTMENT
# Doctor–Patient many-to-many relationship
# -----------------------------
class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    treatments = db.relationship("Treatment", backref="appointment", lazy=True)

# -----------------------------
# 6. TREATMENT
# Linked to Appointment
# -----------------------------
class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    medicine = db.Column(db.String(255))
    cost = db.Column(db.Float)

    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)

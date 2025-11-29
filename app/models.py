from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db
from datetime import datetime

# -----------------------------
# 1. ADMIN (Predefined)
# -----------------------------
class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Unique login ID
    def get_id(self):
        return f"admin-{self.id}"


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
class Doctor(UserMixin, db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    appointments = db.relationship("Appointment", backref="doctor", lazy=True)

    def get_id(self):
        return f"doctor-{self.id}"


# -----------------------------
# 4. PATIENT
# -----------------------------
class Patient(UserMixin, db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20), nullable=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    appointments = db.relationship("Appointment", backref="patient", lazy=True)

    def get_id(self):
        return f"patient-{self.id}"


# -----------------------------
# 5. APPOINTMENT
# -----------------------------
class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    status = db.Column(db.String(20), default="Booked") 
    diagnosis = db.Column(db.Text, nullable=True)
    treatment_notes = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    treatments = db.relationship("Treatment", backref="appointment", lazy=True)


# -----------------------------
# 6. TREATMENT 
# -----------------------------
class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    medicine = db.Column(db.String(255))
    cost = db.Column(db.Float)

    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)


# -----------------------------
# 7. AVAILABILITY 
# -----------------------------
class Availability(db.Model):
    __tablename__ = "availability"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    doctor = db.relationship("Doctor", backref="availability")
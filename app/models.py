from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# -----------------------------------------------------------------------------
# 1. Admin Model
# -----------------------------------------------------------------------------
class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, default="admin@hms.org")
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"admin-{self.id}"

    @property
    def display_name(self):
        return self.username

# -----------------------------------------------------------------------------
# 2. Department Model
# -----------------------------------------------------------------------------
class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    doctors = db.relationship("Doctor", backref="department", lazy=True, cascade="all, delete-orphan")

# -----------------------------------------------------------------------------
# 3. Doctor Model
# -----------------------------------------------------------------------------
class Doctor(UserMixin, db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    specialization = db.Column(db.String(100), nullable=True)
    experience_years = db.Column(db.Integer, default=5)
    consultation_fee = db.Column(db.Float, default=500.0)
    profile_image = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    appointments = db.relationship("Appointment", backref="doctor", lazy=True)
    availabilities = db.relationship("Availability", backref="doctor", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"doctor-{self.id}"

    @property
    def display_name(self):
        return self.name

    @property
    def avatar_url(self):
        if self.profile_image:
            return self.profile_image
        default_avatars = [
            "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=400&auto=format&fit=crop&q=80"
        ]
        idx = ((self.id or 1) - 1) % len(default_avatars)
        return default_avatars[idx]

# -----------------------------------------------------------------------------
# 4. Patient Model
# -----------------------------------------------------------------------------
class Patient(UserMixin, db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    appointments = db.relationship("Appointment", backref="patient", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"patient-{self.id}"

    @property
    def display_name(self):
        return self.name

# -----------------------------------------------------------------------------
# 5. Appointment Model
# -----------------------------------------------------------------------------
class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    status = db.Column(db.String(20), default="Booked")  # Booked, Confirmed, Completed, Cancelled
    diagnosis = db.Column(db.Text, nullable=True)
    treatment_notes = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    treatments = db.relationship("Treatment", backref="appointment", lazy=True, cascade="all, delete-orphan")

# -----------------------------------------------------------------------------
# 6. Treatment Model
# -----------------------------------------------------------------------------
class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=False)
    medicine = db.Column(db.String(255), nullable=True)
    cost = db.Column(db.Float, default=0.0)

    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)

# -----------------------------------------------------------------------------
# 7. Availability Model
# -----------------------------------------------------------------------------
class Availability(db.Model):
    __tablename__ = "availability"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    slot_time = db.Column(db.String(20), nullable=True, default="09:00 AM")
    is_available = db.Column(db.Boolean, default=True)
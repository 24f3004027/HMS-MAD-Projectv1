from datetime import datetime, date, time, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, Admin, Department, Doctor, Patient, Appointment, Treatment, Availability

routes_bp = Blueprint("routes", __name__)

# -----------------------------------------------------------------------------
# General & Auth Routes
# -----------------------------------------------------------------------------

@routes_bp.route("/favicon.ico")
def favicon():
    return "", 204

@routes_bp.route("/")
def index():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("routes.admin_dashboard"))
        elif isinstance(current_user, Doctor):
            return redirect(url_for("routes.doctor_dashboard"))
        elif isinstance(current_user, Patient):
            return redirect(url_for("routes.patient_dashboard"))
    
    doctors = Doctor.query.filter_by(is_active=True).limit(6).all()
    departments = Department.query.all()
    return render_template("index.html", doctors=doctors, departments=departments)

@routes_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "patient")

        if role == "admin":
            user = Admin.query.filter((Admin.username == identifier) | (Admin.email == identifier)).first()
            if user and user.check_password(password):
                login_user(user)
                flash(f"Welcome back, Admin {user.username}!", "success")
                return redirect(url_for("routes.admin_dashboard"))

        elif role == "doctor":
            user = Doctor.query.filter((Doctor.email == identifier) | (Doctor.name.ilike(f"%{identifier}%"))).first()
            if user and user.check_password(password):
                if not user.is_active:
                    flash("Account is deactivated. Please contact administrator.", "danger")
                    return render_template("login.html")
                login_user(user)
                flash(f"Welcome back, {user.name}!", "success")
                return redirect(url_for("routes.doctor_dashboard"))

        elif role == "patient":
            user = Patient.query.filter((Patient.name.ilike(f"%{identifier}%")) | (Patient.email == identifier)).first()
            if user and user.check_password(password):
                if not user.is_active:
                    flash("Account is deactivated.", "danger")
                    return render_template("login.html")
                login_user(user)
                flash(f"Welcome back, {user.name}!", "success")
                return redirect(url_for("routes.patient_dashboard"))

        flash("Invalid login credentials or selected role.", "danger")

    return render_template("login.html")

@routes_bp.route("/patient/register", methods=["GET", "POST"])
def patient_register():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        age = request.form.get("age", 25)
        gender = request.form.get("gender", "Male")
        contact = request.form.get("contact", "").strip()

        if not name or not email or not password:
            flash("Name, Email, and Password are required.", "warning")
            return render_template("patient_register.html")

        if Patient.query.filter_by(email=email).first():
            flash("Email address is already registered.", "danger")
            return render_template("patient_register.html")

        patient = Patient(name=name, email=email, age=int(age), gender=gender, contact=contact)
        patient.set_password(password)
        db.session.add(patient)
        db.session.commit()

        login_user(patient)
        flash("Registration successful! Welcome to PulseCare HMS.", "success")
        return redirect(url_for("routes.patient_dashboard"))

    return render_template("patient_register.html")

@routes_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("routes.login"))

# -----------------------------------------------------------------------------
# Admin Routes
# -----------------------------------------------------------------------------

@routes_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        flash("Admin access required.", "danger")
        return redirect(url_for("routes.index"))

    doctors = Doctor.query.all()
    patients = Patient.query.all()
    departments = Department.query.all()
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()

    total_patients = len(patients)
    total_doctors = len(doctors)
    total_appointments = Appointment.query.count()
    total_revenue = db.session.query(db.func.sum(Treatment.cost)).scalar() or 0.0

    return render_template("admin_dashboard.html",
                           doctors=doctors,
                           patients=patients,
                           departments=departments,
                           appointments=appointments,
                           total_patients=total_patients,
                           total_doctors=total_doctors,
                           total_appointments=total_appointments,
                           total_revenue=total_revenue)

@routes_bp.route("/admin/doctor/add", methods=["GET", "POST"])
@login_required
def add_doctor():
    if not isinstance(current_user, Admin):
        flash("Admin access required.", "danger")
        return redirect(url_for("routes.index"))

    departments = Department.query.all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        department_id = request.form.get("department_id")
        specialization = request.form.get("specialization", "").strip()
        try:
            exp = int(request.form.get("experience_years", 5))
            fee = float(request.form.get("consultation_fee", 500.0))
        except ValueError:
            exp, fee = 5, 500.0

        if not name or not email or not password or not department_id:
            flash("All required fields must be filled.", "warning")
            return render_template("add_doctor.html", departments=departments)

        if Doctor.query.filter_by(email=email).first():
            flash("Doctor with this email already exists.", "danger")
            return render_template("add_doctor.html", departments=departments)

        doc = Doctor(name=name, email=email, department_id=int(department_id),
                     specialization=specialization, experience_years=exp, consultation_fee=fee)
        doc.set_password(password)
        db.session.add(doc)
        db.session.commit()

        flash(f"{name} registered successfully!", "success")
        return redirect(url_for("routes.admin_dashboard"))

    return render_template("add_doctor.html", departments=departments)

@routes_bp.route("/admin/doctor/<int:doctor_id>/toggle", methods=["POST"])
@login_required
def toggle_doctor(doctor_id):
    if not isinstance(current_user, Admin):
        flash("Admin access required.", "danger")
        return redirect(url_for("routes.index"))

    doctor = db.session.get(Doctor, doctor_id)
    if doctor:
        doctor.is_active = not doctor.is_active
        db.session.commit()
        status_text = "activated" if doctor.is_active else "deactivated"
        flash(f"Doctor {doctor.name} {status_text}.", "info")

    return redirect(url_for("routes.admin_dashboard"))

@routes_bp.route("/admin/department/add", methods=["POST"])
@login_required
def add_department():
    if not isinstance(current_user, Admin):
        flash("Admin access required.", "danger")
        return redirect(url_for("routes.index"))

    name = request.form.get("name", "").strip()
    desc = request.form.get("description", "").strip()

    if name:
        existing = Department.query.filter_by(name=name).first()
        if not existing:
            dept = Department(name=name, description=desc)
            db.session.add(dept)
            db.session.commit()
            flash(f"Department '{name}' created!", "success")
        else:
            flash("Department name already exists.", "warning")

    return redirect(url_for("routes.admin_dashboard"))

# -----------------------------------------------------------------------------
# Doctor Routes
# -----------------------------------------------------------------------------

@routes_bp.route("/doctor/dashboard")
@login_required
def doctor_dashboard():
    if not isinstance(current_user, Doctor):
        flash("Doctor access required.", "danger")
        return redirect(url_for("routes.index"))

    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.date.desc(), Appointment.time.asc()).all()
    availabilities = Availability.query.filter_by(doctor_id=current_user.id).all()

    return render_template("doctor_dashboard.html",
                           doctor=current_user,
                           appointments=appointments,
                           availabilities=availabilities)

@routes_bp.route("/doctor/appointment/<int:appointment_id>/update", methods=["POST"])
@login_required
def update_appointment(appointment_id):
    if not isinstance(current_user, Doctor):
        flash("Doctor access required.", "danger")
        return redirect(url_for("routes.index"))

    appointment = db.session.get(Appointment, appointment_id)
    if not appointment or appointment.doctor_id != current_user.id:
        flash("Appointment not found or unauthorized.", "danger")
        return redirect(url_for("routes.doctor_dashboard"))

    status = request.form.get("status", appointment.status)
    diagnosis = request.form.get("diagnosis", "").strip()
    notes = request.form.get("treatment_notes", "").strip()
    prescription = request.form.get("prescription", "").strip()
    try:
        treatment_cost = float(request.form.get("treatment_cost", 0.0))
    except ValueError:
        treatment_cost = 0.0

    appointment.status = status
    if diagnosis: appointment.diagnosis = diagnosis
    if notes: appointment.treatment_notes = notes
    if prescription: appointment.prescription = prescription

    if treatment_cost > 0:
        treatment = Treatment(description=diagnosis or "General Consultation", medicine=prescription, cost=treatment_cost, appointment_id=appointment.id)
        db.session.add(treatment)

    db.session.commit()
    flash(f"Appointment #{appointment.id} updated successfully.", "success")
    return redirect(url_for("routes.doctor_dashboard"))

# -----------------------------------------------------------------------------
# Patient Routes
# -----------------------------------------------------------------------------

@routes_bp.route("/patient/dashboard")
@login_required
def patient_dashboard():
    if not isinstance(current_user, Patient):
        flash("Patient access required.", "danger")
        return redirect(url_for("routes.index"))

    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.date.desc()).all()
    departments = Department.query.all()
    doctors = Doctor.query.filter_by(is_active=True).all()

    return render_template("patient_dashboard.html",
                           patient=current_user,
                           appointments=appointments,
                           departments=departments,
                           doctors=doctors)

@routes_bp.route("/patient/search_doctors")
@login_required
def search_doctors():
    query = request.args.get("q", "").strip()
    dept_id = request.args.get("department_id")

    doctors_query = Doctor.query.filter_by(is_active=True)
    if query:
        doctors_query = doctors_query.filter(
            (Doctor.name.ilike(f"%{query}%")) |
            (Doctor.specialization.ilike(f"%{query}%"))
        )
    if dept_id:
        doctors_query = doctors_query.filter_by(department_id=int(dept_id))

    doctors = doctors_query.all()
    departments = Department.query.all()

    return render_template("search_doctors.html", doctors=doctors, departments=departments, query=query, selected_dept=int(dept_id) if dept_id else None)

@routes_bp.route("/patient/book/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def book_appointment(doctor_id):
    if not isinstance(current_user, Patient):
        flash("Patient access required.", "danger")
        return redirect(url_for("routes.index"))

    doctor = db.session.get(Doctor, doctor_id)
    if not doctor or not doctor.is_active:
        flash("Doctor unavailable.", "danger")
        return redirect(url_for("routes.patient_dashboard"))

    if request.method == "POST":
        app_date_str = request.form.get("date")
        app_time_str = request.form.get("time", "09:00")

        if not app_date_str:
            flash("Please select an appointment date.", "warning")
            return render_template("book_appointment.html", doctor=doctor)

        try:
            app_date = datetime.strptime(app_date_str, "%Y-%m-%d").date()
            app_time = datetime.strptime(app_time_str, "%H:%M").time()
        except ValueError:
            flash("Invalid date or time format.", "danger")
            return render_template("book_appointment.html", doctor=doctor)

        new_app = Appointment(
            date=app_date,
            time=app_time,
            doctor_id=doctor.id,
            patient_id=current_user.id,
            status="Booked"
        )
        db.session.add(new_app)
        db.session.commit()

        flash(f"Appointment booked with {doctor.name} for {app_date_str} at {app_time_str}!", "success")
        return redirect(url_for("routes.patient_dashboard"))

    return render_template("book_appointment.html", doctor=doctor)

@routes_bp.route("/patient/appointment/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment or (appointment.patient_id != current_user.id and not isinstance(current_user, Admin)):
        flash("Unauthorized or appointment not found.", "danger")
        return redirect(url_for("routes.patient_dashboard"))

    appointment.status = "Cancelled"
    db.session.commit()
    flash(f"Appointment #{appointment.id} cancelled.", "info")
    return redirect(url_for("routes.patient_dashboard"))
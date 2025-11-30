from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Doctor, Patient, Appointment, Department, Admin, Availability, db
from datetime import date, datetime, timedelta
import re

routes = Blueprint("routes", __name__)

# -------------------------
# Basic Pages
# -------------------------

@routes.route("/")
def index():
    return render_template("index.html")


# -------------------------
# Patient Pages
# -------------------------

@routes.route("/patient/register", methods=["GET", "POST"])
def patient_register():
    if request.method == "POST":
        name = request.form["name"].strip()
        age = request.form["age"]
        gender = request.form["gender"]
        contact = request.form["contact"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        # --- Backend validation ---
        if len(name) < 3:
            return "Name must be at least 3 characters."

        if not age.isdigit() or int(age) < 1 or int(age) > 120:
            return "Invalid age."

        if gender not in ["Male", "Female", "Other"]:
            return "Invalid gender."

        if not contact.isdigit() or len(contact) != 10:
            return "Contact must be a 10-digit number."

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            return "Invalid email format."

        if len(password) < 6:
            return "Password must be at least 6 characters."

        # Check duplicate email
        if Patient.query.filter_by(email=email).first():
            return "Email already exists."

        hashed_password = generate_password_hash(password)

        new_patient = Patient(
            name=name,
            age=age,
            gender=gender,
            contact=contact,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_patient)
        db.session.commit()

        return redirect("/patient/login")

    return render_template("patient_register.html")


@routes.route("/patient/login", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        if not email or not password:
            return "Both fields required."

        patient = Patient.query.filter_by(email=email, is_active=True).first()

        if not patient:
            return "Invalid email."

        if not check_password_hash(patient.password_hash, password):
            return "Incorrect password."

        session["patient_id"] = patient.id
        session["role"] = "patient"
        return redirect("/patient/dashboard")

    return render_template("patient_login.html")


@routes.route("/patient/dashboard")
def patient_dashboard():
    if "patient_id" not in session:
        return redirect("/patient/login")

    patient = Patient.query.get(session["patient_id"])
    today = date.today()

    upcoming = Appointment.query.filter_by(patient_id=patient.id).filter(
        Appointment.date >= today
    ).all()

    past = Appointment.query.filter_by(patient_id=patient.id).filter(
        Appointment.date < today
    ).all()

    dates = [str(a.date) for a in past] if past else []
    statuses = [a.status for a in past] if past else []
    diagnoses = [a.diagnosis or "None" for a in past] if past else []

    return render_template(
        "patient_dashboard.html",
        patient=patient,
        upcoming=upcoming,
        past=past,
        dates=dates,
        statuses=statuses,
        diagnoses=diagnoses
    )

# -------------------------
# Doctor Pages
# -------------------------

@routes.route("/doctor/login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        if not email or not password:
            return "Email and password required."

        doctor = Doctor.query.filter_by(email=email, is_active=True).first()

        if not doctor:
            return "Doctor does not exist or is blacklisted."

        if not check_password_hash(doctor.password_hash, password):
            return "Incorrect password."

        session["doctor_id"] = doctor.id
        session["doctor_name"] = doctor.name
        session["role"] = "doctor"
        return redirect("/doctor/dashboard")

    return render_template("doctor_login.html")


@routes.route("/doctor/dashboard")
def doctor_dashboard():
    if "doctor_id" not in session:
        return redirect("/doctor/login")

    doctor_id = session["doctor_id"]
    today = date.today()

    todays = Appointment.query.filter_by(doctor_id=doctor_id).filter(
        Appointment.date == today
    ).all()

    upcoming = Appointment.query.filter_by(doctor_id=doctor_id).filter(
        Appointment.date > today
    ).all()

    past = Appointment.query.filter_by(doctor_id=doctor_id).filter(
        Appointment.date < today
    ).all()

    booked = Appointment.query.filter_by(doctor_id=doctor_id, status="Booked").count()
    completed = Appointment.query.filter_by(doctor_id=doctor_id, status="Completed").count()
    cancelled = Appointment.query.filter_by(doctor_id=doctor_id, status="Cancelled").count()

    return render_template(
        "doctor_dashboard.html",
        todays=todays,
        upcoming=upcoming,
        past=past,
        booked=booked,
        completed=completed,
        cancelled=cancelled
    )

@routes.route("/doctor/appointment/<int:appt_id>", methods=["GET", "POST"])
def doctor_view_appointment(appt_id):
    if "doctor_id" not in session:
        return redirect("/doctor/login")

    appt = Appointment.query.get_or_404(appt_id)

    if appt.doctor_id != session["doctor_id"]:
        return "Unauthorized access.", 403

    if request.method == "POST":
        appt.diagnosis = request.form["diagnosis"]
        appt.treatment_notes = request.form["treatment_notes"]
        appt.prescription = request.form["prescription"]
        appt.status = request.form["status"]

        db.session.commit()
        return redirect(f"/doctor/appointment/{appt_id}")

    history = Appointment.query.filter(
        Appointment.patient_id == appt.patient_id,
        Appointment.id != appt.id
    ).order_by(Appointment.date.desc()).all()

    return render_template(
        "doctor_appointment_view.html",
        appt=appt,
        history=history
    )

@routes.route("/doctor/appointment/update/<int:appt_id>", methods=["POST"])
def doctor_update_appointment(appt_id):
    if "doctor_id" not in session:
        return redirect("/doctor/login")

    appt = Appointment.query.get_or_404(appt_id)

    if appt.doctor_id != session["doctor_id"]:
        return "Unauthorized access."

    appt.diagnosis = request.form["diagnosis"]
    appt.treatment_notes = request.form["treatment_notes"]
    appt.prescription = request.form["prescription"]
    appt.status = request.form["status"]

    db.session.commit()
    return redirect(f"/doctor/appointment/{appt_id}")


# -------------------------
# Admin Pages
# -------------------------

@routes.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            session["admin_id"] = admin.id
            session["role"] = "admin"
            return redirect("/admin/dashboard")

        return "Invalid admin credentials."

    return render_template("admin_login.html")


@routes.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect("/admin/login")

    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()

    return render_template(
        "admin_dashboard.html",
        doctors=total_doctors,
        patients=total_patients,
        appointments=total_appointments
    )

@routes.route("/admin/add_doctor", methods=["GET", "POST"])
def add_doctor():
    if "admin_id" not in session:
        return redirect("/admin/login")

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        dept_id = request.form["department_id"]

        # Backend validation
        if len(name) < 3:
            return "Doctor name must be at least 3 characters."

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            return "Invalid email format."

        if len(password) < 6:
            return "Password must be at least 6 characters."

        # Check valid department
        if not Department.query.get(dept_id):
            return "Invalid department."

        # Check duplicate email
        if Doctor.query.filter_by(email=email).first():
            return "Email already exists for another doctor."

        hashed_pass = generate_password_hash(password)

        new_doc = Doctor(
            name=name,
            email=email,
            password_hash=hashed_pass,
            department_id=dept_id
        )

        db.session.add(new_doc)
        db.session.commit()

        return redirect("/admin/dashboard")

    # FIX: Load departments for dropdown
    departments = Department.query.all()
    return render_template("add_doctor.html", departments=departments)

@routes.route("/admin/update_doctor/<int:doctor_id>", methods=["GET", "POST"])
def update_doctor(doctor_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        dept_id = request.form["department_id"]

        if len(name) < 3:
            return "Name must be at least 3 characters."

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            return "Invalid email format."

        if not Department.query.get(dept_id):
            return "Invalid department."

        existing = Doctor.query.filter_by(email=email).first()
        if existing and existing.id != doctor.id:
            return "Email already assigned to another doctor."

        doctor.name = name
        doctor.email = email
        doctor.department_id = dept_id

        db.session.commit()
        return redirect("/admin/doctors")

    return render_template("update_doctor.html", doctor=doctor)

@routes.route("/admin/doctors")
def view_doctors():
    if "admin_id" not in session:
        return redirect("/admin/login")

    doctors = Doctor.query.filter_by(is_active=True).all()
    return render_template("view_doctors.html", doctors=doctors)


@routes.route("/admin/search_doctors", methods=["GET", "POST"])
def search_doctors():
    if "admin_id" not in session:
        return redirect("/admin/login")

    results = []

    if request.method == "POST":
        query = request.form["query"]

        results = Doctor.query.join(Department).filter(
            (Doctor.name.ilike(f"%{query}%")) |
            (Department.name.ilike(f"%{query}%"))
        ).all()

    return render_template("search_doctors.html", doctors=results)


@routes.route("/admin/search_patients", methods=["GET", "POST"])
def search_patients():
    if "admin_id" not in session:
        return redirect("/admin/login")

    results = []

    if request.method == "POST":
        query = request.form["query"]

        results = Patient.query.filter(
            Patient.is_active == True,
        ).filter(
            (Patient.name.ilike(f"%{query}%")) |
            (Patient.gender.ilike(f"%{query}%")) |
            (Patient.contact.ilike(f"%{query}%")) |
            (Patient.id.like(f"%{query}%"))
        ).all()

    return render_template("search_patients.html", patients=results)


@routes.route("/admin/appointments")
def view_appointments():
    if "admin_id" not in session:
        return redirect("/admin/login")

    today = date.today()

    upcoming = Appointment.query.filter(Appointment.date >= today).all()
    past = Appointment.query.filter(Appointment.date < today).all()

    return render_template(
        "view_appointments.html",
        upcoming=upcoming,
        past=past
    )


@routes.route("/admin/blacklist_doctor/<int:doctor_id>")
def blacklist_doctor(doctor_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_active = False
    db.session.commit()
    return redirect("/admin/doctors")


@routes.route("/admin/blacklist_patient/<int:patient_id>")
def blacklist_patient(patient_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    patient = Patient.query.get_or_404(patient_id)
    patient.is_active = False
    db.session.commit()
    return redirect("/admin/search_patients")


@routes.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------------
# Booking + Reschedule (with Validation)
# -------------------------

@routes.route("/patient/search_doctors", methods=["GET", "POST"])
def patient_search_doctors():
    if "patient_id" not in session:
        return redirect("/patient/login")

    results = []
    if request.method == "POST":
        query = request.form["query"]

        results = Doctor.query.join(Department).filter(
            Doctor.is_active == True,
            (
                Doctor.name.ilike(f"%{query}%") |
                Department.name.ilike(f"%{query}%")
            )
        ).all()

    return render_template("patient_search_doctors.html", doctors=results)


@routes.route("/patient/book/<int:doctor_id>", methods=["GET", "POST"])
def patient_book(doctor_id):
    if "patient_id" not in session:
        return redirect("/patient/login")

    doctor = Doctor.query.get_or_404(doctor_id)

    today = date.today()
    days = [today + timedelta(days=i) for i in range(1, 8)]

    avail_data = []
    for d in days:
        slot = Availability.query.filter_by(doctor_id=doctor_id, date=d).first()

        if not slot:
            slot = Availability(
                doctor_id=doctor_id,
                date=d,
                is_available=True
            )
            db.session.add(slot)
            db.session.commit()

        avail_data.append({
            "date": d,
            "available": slot.is_available
        })

    if request.method == "POST":
        try:
            selected_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
            selected_time = datetime.strptime(request.form["time"], "%H:%M:%S").time()
        except:
            return "Invalid date or time format."

        if selected_date < date.today():
            return "You cannot book past dates."

        avail = Availability.query.filter_by(doctor_id=doctor_id, date=selected_date).first()
        if not avail or not avail.is_available:
            return "Doctor is not available on this day."

        duplicate = Appointment.query.filter_by(
            patient_id=session["patient_id"],
            date=selected_date,
            time=selected_time
        ).first()
        if duplicate:
            return "You already have an appointment at this time."

        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=selected_date,
            time=selected_time
        ).first()
        if existing:
            return "This time slot is already booked."

        appt = Appointment(
            doctor_id=doctor_id,
            patient_id=session["patient_id"],
            date=selected_date,
            time=selected_time,
            status="Booked"
        )

        db.session.add(appt)
        db.session.commit()
        return redirect("/patient/dashboard")

    return render_template(
        "patient_book.html",
        doctor=doctor,
        avail_data=avail_data
    )

@routes.route("/patient/cancel/<int:appt_id>")
def patient_cancel(appt_id):
    if "patient_id" not in session:
        return redirect("/patient/login")

    appt = Appointment.query.get_or_404(appt_id)

    if appt.patient_id != session["patient_id"]:
        return "Unauthorized action."

    if appt.date < date.today():
        return "You cannot cancel past appointments."

    appt.status = "Cancelled"
    db.session.commit()
    return redirect("/patient/dashboard")


@routes.route("/patient/reschedule/<int:appt_id>", methods=["GET", "POST"])
def patient_reschedule(appt_id):
    if "patient_id" not in session:
        return redirect("/patient/login")

    appt = Appointment.query.get_or_404(appt_id)

    if appt.date < date.today():
        return "You cannot reschedule past appointments."

    doctor_id = appt.doctor_id
    today = date.today()

    days = [today + timedelta(days=i) for i in range(1, 8)]

    avail_data = []
    for d in days:
        slot = Availability.query.filter_by(doctor_id=doctor_id, date=d).first()
        avail_data.append({
            "date": d,
            "available": slot.is_available if slot else False
        })

    if request.method == "POST":
        try:
            selected_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
            selected_time = datetime.strptime(request.form["time"], "%H:%M:%S").time()
        except:
            return "Invalid date or time format."

        if selected_date < date.today():
            return "Cannot reschedule to a past date."

        avail = Availability.query.filter_by(doctor_id=doctor_id, date=selected_date).first()
        if not avail or not avail.is_available:
            return "Doctor unavailable on selected day."

        # Prevent same patient duplicate
        duplicate = Appointment.query.filter_by(
            patient_id=session["patient_id"],
            date=selected_date,
            time=selected_time
        ).first()
        if duplicate:
            return "You already have an appointment at this time."

        # Prevent doctor double booking
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=selected_date,
            time=selected_time
        ).first()
        if existing:
            return "This slot is already booked."

        appt.date = selected_date
        appt.time = selected_time
        appt.status = "Rescheduled"

        db.session.commit()
        return redirect("/patient/dashboard")

    return render_template(
        "patient_reschedule.html",
        appt=appt,
        avail_data=avail_data
    )

@routes.route("/patient/profile", methods=["GET", "POST"])
def patient_profile():
    if "patient_id" not in session:
        return redirect("/patient/login")

    patient = Patient.query.get_or_404(session["patient_id"])

    if request.method == "POST":
        name = request.form["name"].strip()
        age = request.form["age"]
        gender = request.form["gender"].strip()
        contact = request.form["contact"].strip()

        # Simple backend validation
        if len(name) < 3:
            return "Name must be at least 3 characters."

        if not age.isdigit() or int(age) < 1 or int(age) > 120:
            return "Invalid age."

        if gender not in ["Male", "Female", "Other"]:
            return "Invalid gender."

        if not contact.isdigit() or len(contact) != 10:
            return "Contact must be a 10-digit number."

        # Save updated data
        patient.name = name
        patient.age = int(age)
        patient.gender = gender
        patient.contact = contact

        db.session.commit()
        return redirect("/patient/dashboard")

    return render_template("patient_profile.html", patient=patient)

@routes.route("/doctor/availability", methods=["GET", "POST"])
def doctor_availability():
    if "doctor_id" not in session:
        return redirect("/doctor/login")

    doctor_id = session["doctor_id"]

    # next 7 days
    today = date.today()
    days = [today + timedelta(days=i) for i in range(1, 8)]

    if request.method == "POST":
        # Loop through all 7 day checkboxes
        for d in days:
            key = f"day_{d}"
            checked = request.form.get(key) == "on"

            slot = Availability.query.filter_by(doctor_id=doctor_id, date=d).first()
            if not slot:
                slot = Availability(doctor_id=doctor_id, date=d)

            slot.is_available = checked
            db.session.add(slot)

        db.session.commit()
        return redirect("/doctor/availability")

    # GET request → load all availability
    availability = []
    for d in days:
        slot = Availability.query.filter_by(doctor_id=doctor_id, date=d).first()
        availability.append({
            "id": d,                         # id replaced with date since you loop day_{{date}}
            "date": d.strftime("%Y-%m-%d"),
            "is_available": slot.is_available if slot else False
        })

    return render_template("doctor_availability.html", availability=availability)

@routes.route("/admin/doctor_credentials/<int:doctor_id>")
def doctor_credentials(doctor_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    doctor = Doctor.query.get_or_404(doctor_id)

    return render_template("doctor_credentials.html", doctor=doctor)

@routes.route("/admin/patients")
def admin_view_patients():
    if "admin_id" not in session:
        return redirect("/admin/login")

    patients = Patient.query.filter_by(is_active=True).all()
    return render_template("view_patients.html", patients=patients)


@routes.route("/admin/patient_credentials/<int:patient_id>")
def admin_patient_credentials(patient_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    patient = Patient.query.get_or_404(patient_id)

    return render_template("patient_credentials.html", patient=patient)
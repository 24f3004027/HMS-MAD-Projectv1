from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from .models import Doctor, Patient, Appointment, Department, db
from datetime import date

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

@routes.route("/patient/register")
def patient_register():
    return render_template("patient_register.html")

@routes.route("/patient/login")
def patient_login():
    return render_template("patient_login.html")

@routes.route("/patient/dashboard")
def patient_dashboard():
    return render_template("patient_dashboard.html")


# -------------------------
# Doctor Pages
# -------------------------

@routes.route("/doctor/login")
def doctor_login():
    return render_template("doctor_login.html")

@routes.route("/doctor/dashboard")
def doctor_dashboard():
    return render_template("doctor_dashboard.html")


# -------------------------
# Admin Pages
# -------------------------

@routes.route("/admin/login")
def admin_login():
    return render_template("admin_login.html")


@routes.route("/admin/dashboard")
def admin_dashboard():
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
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        dept_id = request.form["department_id"]

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

    return render_template("add_doctor.html")

@routes.route("/admin/doctors")
def view_doctors():
    doctors = Doctor.query.filter_by(is_active=True).all()
    return render_template("view_doctors.html", doctors=doctors)

@routes.route("/admin/update_doctor/<int:doctor_id>", methods=["GET", "POST"])
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == "POST":
        doctor.name = request.form["name"]
        doctor.email = request.form["email"]
        doctor.department_id = request.form["department_id"]

        db.session.commit()
        return redirect("/admin/doctors")

    return render_template("update_doctor.html", doctor=doctor)

@routes.route("/admin/search_doctors", methods=["GET", "POST"])
def search_doctors():
    results = []

    if request.method == "POST":
        query = request.form["query"]

        # Search by doctor name OR department name
        results = Doctor.query.join(Department).filter(
            (Doctor.name.ilike(f"%{query}%")) |
            (Department.name.ilike(f"%{query}%"))
        ).all()

    return render_template("search_doctors.html", doctors=results)

@routes.route("/admin/search_patients", methods=["GET", "POST"])
def search_patients():
    results = []

    if request.method == "POST":
        query = request.form["query"]

        results = Patient.query.filter(
            Patient.is_active == True,   # <-- Only active patients
        ).filter(
            (Patient.name.ilike(f"%{query}%")) |
            (Patient.gender.ilike(f"%{query}%")) |
            (Patient.contact.ilike(f"%{query}%")) |
            (Patient.id.like(f"%{query}%"))
        ).all()

    return render_template("search_patients.html", patients=results)

@routes.route("/admin/appointments")
def view_appointments():
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
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_active = False
    db.session.commit()
    return redirect("/admin/doctors")

@routes.route("/admin/blacklist_patient/<int:patient_id>")
def blacklist_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.is_active = False
    db.session.commit()
    return redirect("/admin/search_patients")

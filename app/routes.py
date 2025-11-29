from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Doctor, Patient, Appointment, Department, Admin, Availability, db
from datetime import date, datetime, timedelta

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
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        contact = request.form["contact"]
        email = request.form["email"]
        password = request.form["password"]

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
        email = request.form["email"]
        password = request.form["password"]

        patient = Patient.query.filter_by(email=email, is_active=True).first()

        if patient and check_password_hash(patient.password_hash, password):
            session["patient_id"] = patient.id
            session["role"] = "patient"
            return redirect("/patient/dashboard")

        return "Invalid email or password. Try again."

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
        email = request.form["email"]
        password = request.form["password"]

        doctor = Doctor.query.filter_by(email=email, is_active=True).first()

        if doctor and check_password_hash(doctor.password_hash, password):
            session["doctor_id"] = doctor.id
            session["doctor_name"] = doctor.name
            session["role"] = "doctor"
            return redirect("/doctor/dashboard")

        return "Invalid doctor credentials or blacklisted."

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

    # ---- Count statuses ----
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

    # Prevent unauthorized access
    if appt.doctor_id != session["doctor_id"]:
        return "Unauthorized access.", 403

    # Handle update
    if request.method == "POST":
        appt.diagnosis = request.form["diagnosis"]
        appt.treatment_notes = request.form["treatment_notes"]
        appt.prescription = request.form["prescription"]
        appt.status = request.form["status"]

        db.session.commit()

        return redirect(f"/doctor/appointment/{appt_id}")

    # Fetch patient history EXCEPT current appointment
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
    if "admin_id" not in session:
        return redirect("/admin/login")

    doctors = Doctor.query.filter_by(is_active=True).all()
    return render_template("view_doctors.html", doctors=doctors)


@routes.route("/admin/update_doctor/<int:doctor_id>", methods=["GET", "POST"])
def update_doctor(doctor_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

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

@routes.route("/doctor/availability", methods=["GET", "POST"])
def doctor_availability():
    if "doctor_id" not in session:
        return redirect("/doctor/login")

    doctor_id = session["doctor_id"]
    today = date.today()

    # Get or create availability for next 7 days
    availability_list = []

    for i in range(7):
        d = today + timedelta(days=i)
        avail = Availability.query.filter_by(doctor_id=doctor_id, date=d).first()
        if not avail:
            avail = Availability(doctor_id=doctor_id, date=d, is_available=True)
            db.session.add(avail)
        availability_list.append(avail)

    db.session.commit()

    # If doctor updates the form
    if request.method == "POST":
        for a in availability_list:
            checkbox_name = f"day_{a.id}"
            a.is_available = checkbox_name in request.form
        db.session.commit()

        return redirect("/doctor/availability")

    return render_template("doctor_availability.html", availability=availability_list)

@routes.route("/admin/doctor_credentials/<int:doctor_id>")
def doctor_credentials(doctor_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template("doctor_credentials.html", doctor=doctor)

@routes.route("/patient/profile", methods=["GET", "POST"])
def patient_profile():
    if "patient_id" not in session:
        return redirect("/patient/login")

    patient = Patient.query.get(session["patient_id"])

    if request.method == "POST":
        patient.name = request.form["name"]
        patient.age = request.form["age"]
        patient.gender = request.form["gender"]
        patient.contact = request.form["contact"]

        # Email cannot change (optional rule, safer)
        # patient.email = request.form["email"]

        db.session.commit()
        return redirect("/patient/dashboard")

    return render_template("patient_profile.html", patient=patient)

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

    # next 7 days
    today = date.today()
    days = [today + timedelta(days=i) for i in range(1, 8)]

    # load availability for each day
    avail_data = []
    for d in days:
        slot = Availability.query.filter_by(doctor_id=doctor_id, date=d).first()
        avail_data.append({
            "date": d,
            "available": slot.is_available if slot else False
        })
    
    if request.method == "POST":
        selected_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        selected_time = datetime.strptime(request.form["time"], "%H:%M:%S").time()

        # prevent double booking
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=selected_date,
            time=selected_time
        ).first()

        if existing:
            return "This slot is already booked."

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

    # Prevent canceling others’ appointments
    if appt.patient_id != session["patient_id"]:
        return "Unauthorized action."

    # Prevent canceling past appointments
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

    # cannot reschedule past appointments
    if appt.date < date.today():
        return "You cannot reschedule past appointments."

    doctor_id = appt.doctor_id
    today = date.today()

    # next 7 days
    days = [today + timedelta(days=i) for i in range(1, 8)]

    # load doctor availability
    avail_data = []
    for d in days:
        slot = Availability.query.filter_by(doctor_id=doctor_id, date=d).first()
        avail_data.append({
            "date": d,
            "available": slot.is_available if slot else False
        })

    if request.method == "POST":
        selected_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        selected_time = datetime.strptime(request.form["time"], "%H:%M:%S").time()

        # check double booking
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=selected_date,
            time=selected_time
        ).first()

        if existing:
            return "This slot is already taken."

        # update appointment
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
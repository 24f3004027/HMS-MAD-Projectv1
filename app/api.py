from flask import Blueprint, jsonify, request
from .models import Doctor, Patient, Appointment, db
from datetime import datetime, date

api = Blueprint("api", __name__, url_prefix="/api")

# ----------------------------------------
# 1. UPDATE APPOINTMENT (PUT)
# ----------------------------------------
@api.route("/appointments/<int:appt_id>", methods=["PUT"])
def update_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    data = request.json or {}

    if "date" in data:
        try:
            appt.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except:
            return jsonify({"error": "Invalid date format"}), 400

    if "time" in data:
        try:
            appt.time = datetime.strptime(data["time"], "%H:%M:%S").time()
        except:
            return jsonify({"error": "Invalid time format"}), 400

    if "status" in data:
        appt.status = data["status"]

    db.session.commit()
    return jsonify({"message": "Appointment updated successfully"}), 200


# ----------------------------------------
# 2. DELETE APPOINTMENT (DELETE)
# ----------------------------------------
@api.route("/appointments/<int:appt_id>", methods=["DELETE"])
def delete_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)

    if appt.date < date.today():
        return jsonify({"error": "Cannot delete past appointments"}), 403

    db.session.delete(appt)
    db.session.commit()

    return jsonify({"message": "Appointment deleted successfully"}), 200


# ----------------------------------------
# 3. GET ALL DOCTORS
# ----------------------------------------
@api.route("/doctors", methods=["GET"])
def get_doctors():
    doctors = Doctor.query.filter_by(is_active=True).all()
    data = [
        {
            "id": d.id,
            "name": d.name,
            "email": d.email,
            "department": d.department.name
        }
        for d in doctors
    ]
    return jsonify({"doctors": data})


# ----------------------------------------
# 4. GET SINGLE DOCTOR
# ----------------------------------------
@api.route("/doctors/<int:id>", methods=["GET"])
def get_single_doctor(id):
    d = Doctor.query.get_or_404(id)
    return jsonify({
        "id": d.id,
        "name": d.name,
        "email": d.email,
        "department": d.department.name
    })


# ----------------------------------------
# 5. GET PATIENT LIST
# ----------------------------------------
@api.route("/patients", methods=["GET"])
def get_patients():
    patients = Patient.query.filter_by(is_active=True).all()
    data = [
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "contact": p.contact
        }
        for p in patients
    ]
    return jsonify({"patients": data})


# ----------------------------------------
# 6. GET ALL APPOINTMENTS
# ----------------------------------------
@api.route("/appointments", methods=["GET"])
def get_appointments():
    appts = Appointment.query.all()
    data = [
        {
            "id": a.id,
            "date": str(a.date),
            "time": str(a.time),
            "doctor_id": a.doctor_id,
            "patient_id": a.patient_id,
            "status": a.status
        }
        for a in appts
    ]
    return jsonify({"appointments": data})


# ----------------------------------------
# 7. CREATE APPOINTMENT (POST) - FINAL VERSION
# ----------------------------------------
@api.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.json or {}

    required = ["date", "time", "doctor_id", "patient_id"]
    for key in required:
        if key not in data:
            return jsonify({"error": f"Missing field: {key}"}), 400

    # validate date/time
    try:
        date_obj = datetime.strptime(data["date"], "%Y-%m-%d").date()
        time_obj = datetime.strptime(data["time"], "%H:%M:%S").time()
    except:
        return jsonify({"error": "Invalid date/time format"}), 400

    if date_obj < date.today():
        return jsonify({"error": "Cannot create past appointment"}), 400

    # doctor existence
    if not Doctor.query.get(data["doctor_id"]):
        return jsonify({"error": "Invalid doctor ID"}), 404

    # patient existence
    if not Patient.query.get(data["patient_id"]):
        return jsonify({"error": "Invalid patient ID"}), 404

    # double booking
    exists = Appointment.query.filter_by(
        doctor_id=data["doctor_id"],
        date=date_obj,
        time=time_obj
    ).first()

    if exists:
        return jsonify({"error": "Slot already booked"}), 409

    # create appointment
    appt = Appointment(
        date=date_obj,
        time=time_obj,
        doctor_id=data["doctor_id"],
        patient_id=data["patient_id"],
        status="Booked"
    )

    db.session.add(appt)
    db.session.commit()

    return jsonify({"message": "Appointment created"}), 201


# ------------ ADMIN STATS ------------
@api.route("/admin/stats", methods=["GET"])
def admin_stats():
    return jsonify({
        "doctors": Doctor.query.count(),
        "patients": Patient.query.count(),
        "appointments": Appointment.query.count()
    })


# ------------ PATIENT APPOINTMENT STATS ------------
@api.route("/patient/<int:patient_id>/stats", methods=["GET"])
def patient_stats(patient_id):
    completed = Appointment.query.filter_by(patient_id=patient_id, status="Completed").count()
    cancelled = Appointment.query.filter_by(patient_id=patient_id, status="Cancelled").count()
    upcoming = Appointment.query.filter(Appointment.patient_id == patient_id, Appointment.date >= date.today()).count()

    return jsonify({
        "completed": completed,
        "cancelled": cancelled,
        "upcoming": upcoming
    })
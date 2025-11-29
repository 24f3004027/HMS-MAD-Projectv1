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
    data = request.json

    if "date" in data:
        appt.date = datetime.strptime(data["date"], "%Y-%m-%d").date()

    if "time" in data:
        appt.time = datetime.strptime(data["time"], "%H:%M:%S").time()

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

    # Optional rule: block deletion of past appointments
    if appt.date < date.today():
        return jsonify({"error": "Cannot delete past appointments"}), 403

    db.session.delete(appt)
    db.session.commit()

    return jsonify({"message": "Appointment deleted successfully"}), 200


# ----------------------------------------
# 3. GET ALL DOCTORS (GET)
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
# 7. CREATE APPOINTMENT (POST)
# ----------------------------------------
@api.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.json

    date_obj = datetime.strptime(data["date"], "%Y-%m-%d").date()
    time_obj = datetime.strptime(data["time"], "%H:%M:%S").time()

    # Prevent double booking
    exists = Appointment.query.filter_by(
        doctor_id=data["doctor_id"],
        date=date_obj,
        time=time_obj
    ).first()

    if exists:
        return jsonify({"error": "Doctor is already booked for this slot"}), 409

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

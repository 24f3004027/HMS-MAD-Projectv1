import unittest
from datetime import date, time
from app import create_app, db, Admin, Department, Doctor, Patient, Appointment, Treatment

class HMSTestCase(unittest.TestCase):
    def setUp(self):
        test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Create Admin
            admin = Admin(username="admin", email="admin@hms.org")
            admin.set_password("admin123")
            db.session.add(admin)

            # Create Department & Doctor
            dept = Department(name="Cardiology", description="Heart Care")
            db.session.add(dept)
            db.session.commit()

            doc = Doctor(name="Dr. Sarah Jenkins", email="sarah@hms.org", department_id=dept.id, consultation_fee=800.0, profile_image="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&auto=format&fit=crop&q=80")
            doc.set_password("doctor123")
            db.session.add(doc)

            # Create Patient
            patient = Patient(name="Ramrup Satpati", email="ramrup@hms.org", age=22, gender="Male")
            patient.set_password("user123")
            db.session.add(patient)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_admin_login_and_dashboard(self):
        res = self.client.post("/login", data={"identifier": "admin", "password": "admin123", "role": "admin"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Admin Dashboard", res.data)

    def test_patient_login_and_appointment_booking(self):
        # Patient Login
        login_res = self.client.post("/login", data={"identifier": "ramrup@hms.org", "password": "user123", "role": "patient"}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Welcome, Ramrup Satpati", login_res.data)

        # Book Appointment with Dr. Sarah Jenkins (ID 1)
        book_res = self.client.post("/patient/book/1", data={"date": str(date.today()), "time": "10:00"}, follow_redirects=True)
        self.assertEqual(book_res.status_code, 200)
        self.assertIn(b"Appointment booked with Dr. Sarah Jenkins", book_res.data)

if __name__ == "__main__":
    unittest.main()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import re

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secretkey123"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hms.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # If a user tries to access a protected page, redirect here
    login_manager.login_view = "routes.index"

    from .models import Admin, Doctor, Patient

    @login_manager.user_loader
    def load_user(user_id):
        #Source GeeksForGeeks.com

        if "-" not in user_id:
            return None

        role, real_id = user_id.split("-", 1)

        if not real_id.isdigit():
            return None

        real_id = int(real_id)

        if role == "admin":
            return Admin.query.get(real_id)
        elif role == "doctor":
            return Doctor.query.get(real_id)
        elif role == "patient":
            return Patient.query.get(real_id)

        return None

    # Register blueprints
    from .routes import routes
    from .api import api

    app.register_blueprint(routes)
    app.register_blueprint(api)

    return app

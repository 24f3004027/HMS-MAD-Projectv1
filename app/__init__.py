from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()   # <-- db is created here

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secretkey123"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hms.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # import blueprints AFTER db is created
    from .routes import routes
    from .api import api

    app.register_blueprint(routes)
    app.register_blueprint(api)

    return app

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()


def init_database(app):
    with app.app_context():
        from models import analysis, resume, user  # noqa: F401

        db.create_all()
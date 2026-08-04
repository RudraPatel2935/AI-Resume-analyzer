from flask import Flask
import os

from config import Config
from database.db import db, login_manager, init_database
from routes.auth import auth_bp
from routes.resume import resume_bp
from routes.analysis import analysis_bp
from models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    init_database(app)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(analysis_bp)

    @app.route("/")
    def index():
        from flask import render_template

        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=not Config.is_production)
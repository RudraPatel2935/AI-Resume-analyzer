import os
from urllib.parse import quote_plus


def _is_production_environment():
    return bool(os.environ.get("K_SERVICE") or os.environ.get("GOOGLE_CLOUD_PROJECT"))


def _build_database_uri(base_dir):
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url

    cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    if cloud_sql_connection_name and db_user and db_password and db_name:
        return (
            "postgresql+psycopg2://"
            f"{quote_plus(db_user)}:{quote_plus(db_password)}"
            f"@/{db_name}?host=/cloudsql/{cloud_sql_connection_name}"
        )

    if _is_production_environment():
        raise RuntimeError(
            "Production requires DATABASE_URL or Cloud SQL env vars: CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_PASSWORD, DB_NAME."
        )

    return f"sqlite:///{os.path.join(base_dir, 'database', 'app.db')}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
    basedir = os.path.abspath(os.path.dirname(__file__))
    is_production = _is_production_environment()

    SQLALCHEMY_DATABASE_URI = _build_database_uri(basedir)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join("/tmp", "uploads") if is_production else os.path.join(basedir, "uploads"),
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    MODEL_DIR = os.environ.get(
        "MODEL_DIR", os.path.join(basedir, "ml_models", "resume_classifier")
    )
    SKILLS_FILE = os.environ.get("SKILLS_FILE", os.path.join(basedir, "datasets", "skills.json"))
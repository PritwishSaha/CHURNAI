import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# SQLite cannot create its own folder, so make sure it exists before the app starts.
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

_HOST = os.environ.get("HOST", "127.0.0.1")


def _debug_default():
    """Debug mode is on by default only when the app is bound to localhost."""
    explicit = os.environ.get("FLASK_DEBUG")
    if explicit is not None:
        return explicit.strip().lower() in {"1", "true", "yes", "on"}
    return _HOST in {"127.0.0.1", "localhost"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "customer-churn-development-key")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        f"sqlite:///{(DATABASE_DIR / 'churn_history.db').as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MODEL_PATH = Path(
        os.environ.get("MODEL_PATH")
        or BASE_DIR / "models" / "churn_deployment_bundle.pkl"
    )

    TEMPLATES_AUTO_RELOAD = True

    HOST = _HOST
    PORT = int(os.environ.get("PORT", "5000"))
    DEBUG = _debug_default()

import os

from dotenv import load_dotenv

load_dotenv()


def database_url():
    """Return a SQLAlchemy URL compatible with Neon and local SQLite."""
    url = os.getenv("DATABASE_URL", "sqlite:///trippilot.db")
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Config:
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me-before-production")
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7
    MAX_CONTENT_LENGTH = 32 * 1024
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 4

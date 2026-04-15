import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-cambiar-en-produccion")

    # ── Base de datos ─────────────────────────────────────────────────────────
    @staticmethod
    def _build_db_url():
        url = os.getenv("DATABASE_URL")
        if url:
            return url
        user     = os.getenv("DB_USER",     "root")
        password = os.getenv("DB_PASSWORD", "")
        host     = os.getenv("DB_HOST",     "localhost")
        port     = os.getenv("DB_PORT",     "3306")
        name     = os.getenv("DB_NAME",     "empresa_activos")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

    SQLALCHEMY_DATABASE_URI        = _build_db_url.__func__()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle":  280,
        "pool_pre_ping": True,
        "pool_size":     5,
        "max_overflow":  10,
    }

    # ── SMTP (smtplib) — leído directamente desde .env ────────────────────────
    MAIL_SERVER         = os.getenv("MAIL_SERVER",  "sandbox.smtp.mailtrap.io")
    MAIL_PORT           = int(os.getenv("MAIL_PORT", 2525))
    MAIL_USE_TLS        = True    # ← agregar
    MAIL_USE_SSL        = False  
    MAIL_USERNAME       = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD       = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "no-reply@activosapp.mx")
    
    # ── App host (para links en correos) ──────────────────────────────────────
    APP_HOST = os.getenv("APP_HOST", "localhost")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}
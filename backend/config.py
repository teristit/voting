import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # Конфигурация базы данных
    # Приоритет: PostgreSQL (продакшн) -> SQLite (разработка/тесты)
    POSTGRES_URL = os.getenv("DATABASE_URL")
    if POSTGRES_URL:
        SQLALCHEMY_DATABASE_URI = POSTGRES_URL
        DATABASE_TYPE = "postgresql"
    else:
        DB_FILE = os.getenv("DB_FILE", "smart_bonus.db")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_FILE}"
        DATABASE_TYPE = "sqlite"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # JWT конфигурация
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_HOURS", "1")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "7")))

    # CORS конфигурация
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Telegram Bot конфигурация
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8266839851:AAHKbgpKR_EtDgVqPC2ww2V_tXkI-KsHfl4")
    TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")

    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "smart_bonus.log")

    # Резервное копирование
    BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_SCHEDULE = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    BACKUP_PATH = os.getenv("BACKUP_PATH", "./backups")

    # Системные настройки по умолчанию
    DEFAULT_SYSTEM_SETTINGS = {
        "vote_scale_min": int(os.getenv("VOTE_SCALE_MIN", "0")),
        "vote_scale_max": int(os.getenv("VOTE_SCALE_MAX", "10")),
        "self_vote_weight": float(os.getenv("SELF_VOTE_WEIGHT", "0.8")),
        "min_votes_required": int(os.getenv("MIN_VOTES_REQUIRED", "3")),
        "session_duration_days": int(os.getenv("SESSION_DURATION_DAYS", "7")),
        "auto_create_sessions": os.getenv("AUTO_CREATE_SESSIONS", "true").lower() == "true",
        "session_start_day": os.getenv("SESSION_START_DAY", "monday"),
        "advance_creation_days": int(os.getenv("ADVANCE_CREATION_DAYS", "1")),
        "auto_add_participants": os.getenv("AUTO_ADD_PARTICIPANTS", "true").lower() == "true",
        "reopen_window_hours": int(os.getenv("REOPEN_WINDOW_HOURS", "72")),
        "notifications_enabled": os.getenv("NOTIFICATIONS_ENABLED", "true").lower() == "true"
    }

    # Экспорт данных
    EXPORT_FORMATS = ["xlsx", "csv"]
    EXPORT_PATH = os.getenv("EXPORT_PATH", "./exports")

    # Размеры страниц для пагинации
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

    # Безопасность
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOGIN_ATTEMPT_TIMEOUT = int(os.getenv("LOGIN_ATTEMPT_TIMEOUT", "300"))  # в секундах

    # Уведомления
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM = os.getenv("EMAIL_FROM")

    # Celery (для фоновых задач)
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key"
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
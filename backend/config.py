import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # SQLite файл базы данных
    DB_FILE = os.getenv("DB_FILE", "smart_bonus.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_FILE}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8266839851:AAHKbgpKR_EtDgVqPC2ww2V_tXkI-KsHfl4")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_SCHEDULE = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

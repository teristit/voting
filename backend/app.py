# backend/app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from extensions import db, migrate, jwt
from config import Config
from routes import (
    auth_bp, users_bp, sessions_bp,
    participants_bp, votes_bp, results_bp,
    settings_bp, audit_bp
)

def create_app(test_config=None):
    """Фабрика Flask-приложения с поддержкой тестового конфига."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 🟢 тестовая конфигурация подменяет PostgreSQL ДО инициализации db
    if test_config:
        app.config.update(test_config)

    # Инициализация расширений
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Создание базы SQLite, если файла нет
    db_file = app.config.get("DB_FILE")
    if db_file and not os.path.exists(db_file):
        with app.app_context():
            db.create_all()
            print(f"[INFO] Создана база данных SQLite: {db_file}")

    # Регистрация blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")
    app.register_blueprint(sessions_bp, url_prefix="/api/v1/sessions")
    app.register_blueprint(participants_bp, url_prefix="/api/v1/participants")
    app.register_blueprint(votes_bp, url_prefix="/api/v1/votes")
    app.register_blueprint(results_bp, url_prefix="/api/v1/results")
    app.register_blueprint(settings_bp, url_prefix="/api/v1/settings")
    app.register_blueprint(audit_bp, url_prefix="/api/v1/audit")

    @app.route("/")
    def index():
        return jsonify({
            "status": "ok",
            "service": "Smart Bonus API",
            "version": "1.0.0"
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

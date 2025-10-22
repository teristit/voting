from extensions import db
from datetime import datetime


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    setting_key = db.Column(db.String(100), primary_key=True)
    setting_value = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

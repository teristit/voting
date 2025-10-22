from extensions import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = "audit_log"

    log_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id", ondelete="SET NULL"))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON)
    session_id = db.Column(db.BigInteger, db.ForeignKey("sessions.session_id", ondelete="SET NULL"))
    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "action": self.action,
            "details": self.details,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": None if not self.timestamp else self.timestamp.isoformat()
        }

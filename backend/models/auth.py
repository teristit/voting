from extensions import db
from datetime import datetime
import uuid

class AuthSession(db.Model):
    __tablename__ = "auth_sessions"

    session_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = db.Column(db.String(255), nullable=False, index=True)
    device_info = db.Column(db.JSON)
    ip_address = db.Column(db.String(64))
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RevokedToken(db.Model):
    __tablename__ = "revoked_tokens"

    token_hash = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(100))

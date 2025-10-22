from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    telegram_id = db.Column(db.BigInteger, unique=True, index=True)
    telegram_username = db.Column(db.String(255))
    role = db.Column(db.String(20), default="user", nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    permissions = db.Column(db.JSON, default=list)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    votes_given = db.relationship("Vote", foreign_keys="Vote.voter_id", back_populates="voter")
    votes_received = db.relationship("Vote", foreign_keys="Vote.target_id", back_populates="target")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "telegram_id": self.telegram_id,
            "telegram_username": self.telegram_username,
            "role": self.role,
            "active": self.active
        }

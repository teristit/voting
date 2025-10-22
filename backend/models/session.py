from extensions import db
from datetime import datetime

class Session(db.Model):
    __tablename__ = "sessions"

    session_id = db.Column(db.BigInteger, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True)
    auto_participants = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)

    participants = db.relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    votes = db.relationship("Vote", back_populates="session", cascade="all, delete-orphan")
    bonus_parameters = db.relationship("BonusParameters", back_populates="session", cascade="all, delete-orphan")
    results = db.relationship("Result", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "start_date": None if not self.start_date else self.start_date.isoformat(),
            "end_date": None if not self.end_date else self.end_date.isoformat(),
            "active": self.active,
            "auto_participants": self.auto_participants,
            "created_at": None if not self.created_at else self.created_at.isoformat(),
            "closed_at": None if not self.closed_at else None
        }

class SessionParticipant(db.Model):
    __tablename__ = "session_participants"

    participant_id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(db.BigInteger, db.ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    can_vote = db.Column(db.Boolean, default=True)
    can_receive_votes = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default="active", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = db.relationship("Session", back_populates="participants")

    __table_args__ = (db.UniqueConstraint("session_id", "user_id", name="uq_session_user"),)

    def to_dict(self):
        return {
            "participant_id": self.participant_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "can_vote": self.can_vote,
            "can_receive_votes": self.can_receive_votes,
            "status": self.status
        }

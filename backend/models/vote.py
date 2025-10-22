from extensions import db
from datetime import datetime

class Vote(db.Model):
    __tablename__ = "votes"

    vote_id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(db.BigInteger, db.ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    voter_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    score = db.Column(db.SmallInteger, nullable=False)
    modified_by_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = db.relationship("Session", back_populates="votes")
    voter = db.relationship("User", foreign_keys=[voter_id], back_populates="votes_given")
    target = db.relationship("User", foreign_keys=[target_id], back_populates="votes_received")

    __table_args__ = (db.UniqueConstraint("session_id", "voter_id", "target_id", name="uq_vote_unique"),)

    def to_dict(self):
        return {
            "vote_id": self.vote_id,
            "session_id": self.session_id,
            "voter_id": self.voter_id,
            "target_id": self.target_id,
            "score": self.score
        }

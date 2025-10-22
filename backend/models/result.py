from extensions import db
from datetime import datetime

class Result(db.Model):
    __tablename__ = "results"

    result_id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(db.BigInteger, db.ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    average_score = db.Column(db.Numeric(5,2))
    rank = db.Column(db.Integer)
    total_bonus = db.Column(db.Numeric(15,2))
    votes_received = db.Column(db.Integer)
    calculation_details = db.Column(db.JSON)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("Session", back_populates="results")

    def to_dict(self):
        return {
            "result_id": self.result_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "average_score": float(self.average_score) if self.average_score is not None else None,
            "rank": self.rank,
            "total_bonus": float(self.total_bonus) if self.total_bonus is not None else None,
            "votes_received": self.votes_received,
            "calculated_at": None if not self.calculated_at else self.calculated_at.isoformat(),
            "calculation_details": self.calculation_details
        }

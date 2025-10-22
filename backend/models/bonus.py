from extensions import db
from datetime import datetime

class BonusParameters(db.Model):
    __tablename__ = "bonus_parameters"

    param_id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(db.BigInteger, db.ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    average_weekly_revenue = db.Column(db.Numeric(15,2))
    participation_multiplier = db.Column(db.Numeric(5,4))
    total_weekly_bonus = db.Column(db.Numeric(15,2))
    participants_info = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("Session", back_populates="bonus_parameters")

    def to_dict(self):
        return {
            "param_id": self.param_id,
            "session_id": self.session_id,
            "average_weekly_revenue": float(self.average_weekly_revenue) if self.average_weekly_revenue is not None else None,
            "participation_multiplier": float(self.participation_multiplier) if self.participation_multiplier is not None else None,
            "total_weekly_bonus": float(self.total_weekly_bonus) if self.total_weekly_bonus is not None else None,
            "participants_info": self.participants_info
        }

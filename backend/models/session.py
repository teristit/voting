from datetime import datetime
from extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class Session(db.Model):
    __tablename__ = 'sessions'
    
    session_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True, server_default='true')
    auto_participants = db.Column(db.Boolean, nullable=False, default=True, server_default='true')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp())
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    participants = db.relationship('SessionParticipant', back_populates='session', cascade='all, delete-orphan')
    votes = db.relationship('Vote', back_populates='session', cascade='all, delete-orphan')
    bonus_parameters = db.relationship('BonusParameters', back_populates='session', cascade='all, delete-orphan')
    results = db.relationship('Result', back_populates='session', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='session')
    
    def is_active(self):
        """Check if session is currently active."""
        return self.active and self.closed_at is None
    
    def get_participants(self, status=None, can_vote=None, can_receive_votes=None):
        """Get participants with optional filtering."""
        query = self.participants
        
        if status:
            query = query.filter(SessionParticipant.status == status)
        if can_vote is not None:
            query = query.filter(SessionParticipant.can_vote == can_vote)
        if can_receive_votes is not None:
            query = query.filter(SessionParticipant.can_receive_votes == can_receive_votes)
            
        return query.all()
    
    def get_active_participants(self):
        """Get all active participants."""
        return self.get_participants(status='active')
    
    def get_voters(self):
        """Get participants who can vote."""
        return self.get_participants(status='active', can_vote=True)
    
    def get_vote_recipients(self):
        """Get participants who can receive votes."""
        return self.get_participants(status='active', can_receive_votes=True)
    
    def to_dict(self, include_stats=False):
        """Convert session to dictionary representation."""
        result = {
            'session_id': self.session_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'active': self.active,
            'auto_participants': self.auto_participants,
            'created_at': self.created_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }
        
        if include_stats:
            result.update({
                'participants_count': len(self.participants),
                'active_participants_count': len(self.get_active_participants()),
                'votes_count': len(self.votes)
            })
            
        return result
    
    def __repr__(self):
        return f'<Session {self.session_id}: {self.start_date} - {self.end_date} ({"active" if self.active else "inactive"})>'


class SessionParticipant(db.Model):
    __tablename__ = 'session_participants'
    
    participant_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(
        db.BigInteger, 
        db.ForeignKey('sessions.session_id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    user_id = db.Column(
        db.BigInteger, 
        db.ForeignKey('users.user_id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    can_vote = db.Column(db.Boolean, nullable=False, default=True, server_default='true')
    can_receive_votes = db.Column(db.Boolean, nullable=False, default=True, server_default='true')
    status = db.Column(
        db.String(20), 
        nullable=False, 
        default='active', 
        server_default='active'
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp(), onupdate=datetime.utcnow)
    
    # Relationships
    session = db.relationship('Session', back_populates='participants')
    user = db.relationship('User', back_populates='session_participations')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('session_id', 'user_id', name='uq_session_user'),
        db.CheckConstraint(
            "status IN ('active', 'excluded', 'vacation', 'sick_leave')",
            name='check_participant_status'
        ),
    )
    
    def is_active(self):
        """Check if participant is active."""
        return self.status == 'active'
    
    def can_participate_in_voting(self):
        """Check if participant can vote."""
        return self.is_active() and self.can_vote
    
    def can_receive_votes_from_others(self):
        """Check if participant can receive votes."""
        return self.is_active() and self.can_receive_votes
    
    def to_dict(self, include_user=False):
        """Convert participant to dictionary representation."""
        result = {
            'participant_id': self.participant_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'can_vote': self.can_vote,
            'can_receive_votes': self.can_receive_votes,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_user and self.user:
            result['user'] = self.user.to_dict()
            
        return result
    
    def __repr__(self):
        return f'<SessionParticipant {self.participant_id}: User {self.user_id} in Session {self.session_id} ({self.status})>'


class BonusParameters(db.Model):
    __tablename__ = 'bonus_parameters'
    
    param_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(
        db.BigInteger, 
        db.ForeignKey('sessions.session_id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    average_weekly_revenue = db.Column(db.Numeric(15, 2), nullable=True)
    participation_multiplier = db.Column(db.Numeric(5, 4), nullable=True)
    total_weekly_bonus = db.Column(db.Numeric(15, 2), nullable=True)
    participants_info = db.Column(JSONB, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp())
    
    # Relationships
    session = db.relationship('Session', back_populates='bonus_parameters')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint(
            'participation_multiplier >= 0 AND participation_multiplier <= 1',
            name='check_participation_multiplier_range'
        ),
    )
    
    def to_dict(self):
        """Convert bonus parameters to dictionary representation."""
        return {
            'param_id': self.param_id,
            'session_id': self.session_id,
            'average_weekly_revenue': float(self.average_weekly_revenue) if self.average_weekly_revenue else None,
            'participation_multiplier': float(self.participation_multiplier) if self.participation_multiplier else None,
            'total_weekly_bonus': float(self.total_weekly_bonus) if self.total_weekly_bonus else None,
            'participants_info': self.participants_info,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<BonusParameters {self.param_id}: Session {self.session_id}, Bonus {self.total_weekly_bonus}>'

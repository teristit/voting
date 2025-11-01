from datetime import datetime
from extensions import db


class Vote(db.Model):
    __tablename__ = 'votes'
    
    vote_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(
        db.BigInteger, 
        db.ForeignKey('sessions.session_id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    voter_id = db.Column(
        db.BigInteger, 
        db.ForeignKey('users.user_id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    target_id = db.Column(
        db.BigInteger, 
        db.ForeignKey('users.user_id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    score = db.Column(db.SmallInteger, nullable=False)
    modified_by_admin = db.Column(db.Boolean, nullable=False, default=False, server_default='false')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp(), onupdate=datetime.utcnow)
    
    # Relationships
    session = db.relationship('Session', back_populates='votes')
    voter = db.relationship('User', foreign_keys=[voter_id], back_populates='votes_given')
    target = db.relationship('User', foreign_keys=[target_id], back_populates='votes_received')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('session_id', 'voter_id', 'target_id', name='uq_vote_unique'),
        db.CheckConstraint(
            'score >= 0 AND score <= 10',
            name='check_vote_score_range'
        ),
    )
    
    def is_self_vote(self):
        """Check if this is a self-vote (voter voting for themselves)."""
        return self.voter_id == self.target_id
    
    def is_valid_score(self):
        """Check if score is within valid range."""
        return 0 <= self.score <= 10
    
    def to_dict(self, include_names=False):
        """Convert vote to dictionary representation."""
        result = {
            'vote_id': self.vote_id,
            'session_id': self.session_id,
            'voter_id': self.voter_id,
            'target_id': self.target_id,
            'score': self.score,
            'modified_by_admin': self.modified_by_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_names:
            result.update({
                'voter_name': self.voter.name if self.voter else None,
                'target_name': self.target.name if self.target else None
            })
            
        return result
    
    def __repr__(self):
        return f'<Vote {self.vote_id}: User {self.voter_id} -> User {self.target_id} (Score: {self.score})>'

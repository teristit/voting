from datetime import datetime
from extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=True)
    telegram_username = db.Column(db.String(255), nullable=True)
    role = db.Column(
        db.String(20), 
        nullable=False, 
        default='user',
        server_default='user'
    )
    active = db.Column(db.Boolean, nullable=False, default=True, server_default='true')
    permissions = db.Column(JSONB, nullable=False, default=[], server_default='[]')
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp(), onupdate=datetime.utcnow)
    
    # Relationships
    session_participations = db.relationship('SessionParticipant', back_populates='user')
    votes_given = db.relationship('Vote', foreign_keys='Vote.voter_id', back_populates='voter')
    votes_received = db.relationship('Vote', foreign_keys='Vote.target_id', back_populates='target')
    results = db.relationship('Result', back_populates='user')
    auth_sessions = db.relationship('AuthSession', back_populates='user')
    audit_logs = db.relationship('AuditLog', back_populates='user')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint(
            "role IN ('user', 'manager', 'admin')",
            name='check_user_role'
        ),
    )
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role == 'admin':
            self.permissions = ['*']
        elif self.role == 'manager':
            self.permissions = ['users:read', 'sessions:read', 'results:read', 'exports:read']
        elif self.role == 'user':
            self.permissions = []
    
    def has_permission(self, permission):
        """Check if user has specific permission."""
        if '*' in self.permissions:
            return True
        return permission in self.permissions
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def is_manager(self):
        """Check if user is manager."""
        return self.role == 'manager'
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary representation."""
        result = {
            'user_id': self.user_id,
            'name': self.name, 
            'role': self.role,
            'active': self.active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            result.update({
                'email': self.email,
                'telegram_id': self.telegram_id,
                'telegram_username': self.telegram_username,
                'permissions': self.permissions
            })
            
        return result
    
    def __repr__(self):
        return f'<User {self.user_id}: {self.name} ({self.role})>'

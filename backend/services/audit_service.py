from datetime import datetime
from extensions import db
from models.audit import AuditLog

def log_action(user_id, action, details=None, session_id=None, ip_address=None, user_agent=None):
    try:
        log = AuditLog(user_id=user_id, action=action, details=details, session_id=session_id, ip_address=ip_address, user_agent=user_agent, timestamp=datetime.utcnow())
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("[audit_service] error:", e)

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models.audit import AuditLog

audit_bp = Blueprint("audit_bp", __name__)

@audit_bp.route("/", methods=["GET"])
@jwt_required()
def get_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    return jsonify([l.to_dict() for l in logs])

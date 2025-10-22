from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.session import Session
from services.audit_service import log_action
from services.notification_service import send_notification
from services.bonus_calc import calculate_bonus_for_session

sessions_bp = Blueprint("sessions_bp", __name__)

@sessions_bp.route("/", methods=["GET"])
@jwt_required()
def get_sessions():
    sessions = Session.query.order_by(Session.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sessions])

@sessions_bp.route("/", methods=["POST"])
@jwt_required()
def create_session():
    current_user = get_jwt_identity()
    data = request.get_json() or {}
    session = Session(start_date=data["start_date"], end_date=data["end_date"], active=data.get("active", True), auto_participants=data.get("auto_participants", True))
    db.session.add(session); db.session.commit()
    log_action(current_user, "session_created", {"session_id": session.session_id})
    send_notification(chat_id=current_user, message=f"🗳 Создана новая сессия #{session.session_id}")
    return jsonify({"status":"success","session": session.to_dict()}), 201

@sessions_bp.route("/<int:session_id>/close", methods=["POST"])
@jwt_required()
def close_session(session_id):
    current_user = get_jwt_identity()
    session = Session.query.get_or_404(session_id)
    session.active = False
    session.closed_at = db.func.now()
    db.session.commit()
    log_action(current_user, "session_closed", {"session_id": session_id})
    send_notification(chat_id=current_user, message=f"✅ Сессия #{session_id} закрыта.")
    calculate_bonus_for_session(session_id)
    return jsonify({"status":"success","message": f"Session {session_id} closed and results calculated."})

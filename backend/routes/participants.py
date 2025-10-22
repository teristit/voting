from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.session import SessionParticipant
from services.audit_service import log_action

participants_bp = Blueprint("participants_bp", __name__)

@participants_bp.route("/<int:session_id>", methods=["GET"])
@jwt_required()
def list_participants(session_id):
    participants = SessionParticipant.query.filter_by(session_id=session_id).all()
    return jsonify([p.to_dict() for p in participants])

@participants_bp.route("/<int:session_id>", methods=["POST"])
@jwt_required()
def add_participant(session_id):
    current_user = get_jwt_identity()
    data = request.get_json() or {}
    part = SessionParticipant(session_id=session_id, user_id=data["user_id"], can_vote=data.get("can_vote", True), can_receive_votes=data.get("can_receive_votes", True), status=data.get("status", "active"))
    db.session.add(part); db.session.commit()
    log_action(current_user, "participant_added", {"session_id": session_id, "user_id": data["user_id"]})
    return jsonify({"status":"success","participant": part.to_dict()})

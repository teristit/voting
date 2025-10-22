from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.vote import Vote
from services.audit_service import log_action

votes_bp = Blueprint("votes_bp", __name__)

@votes_bp.route("/", methods=["POST"])
@jwt_required()
def submit_votes():
    current_user = get_jwt_identity()
    data = request.get_json() or {}
    session_id = data.get("session_id")
    votes = data.get("votes", [])
    for v in votes:
        existing = Vote.query.filter_by(session_id=session_id, voter_id=current_user, target_id=v["target_id"]).first()
        if existing:
            existing.score = v["score"]
        else:
            db.session.add(Vote(session_id=session_id, voter_id=current_user, target_id=v["target_id"], score=v["score"]))
    db.session.commit()
    log_action(current_user, "votes_submitted", {"session_id": session_id, "count": len(votes)})
    return jsonify({"status":"success","message":"Votes saved"})

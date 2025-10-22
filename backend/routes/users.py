from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from services.audit_service import log_action

users_bp = Blueprint("users_bp", __name__)

@users_bp.route("/", methods=["GET"])
@jwt_required()
def list_users():
    users = User.query.order_by(User.name.asc()).all()
    return jsonify([u.to_dict() for u in users])

@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@users_bp.route("/<int:user_id>", methods=["PATCH"])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    data = request.get_json() or {}
    user = User.query.get_or_404(user_id)
    if "role" in data:
        user.role = data["role"]
    if "permissions" in data:
        user.permissions = data["permissions"]
    db.session.commit()
    log_action(current_user, "user_updated", {"target_id": user_id, **data})
    return jsonify({"status":"success","user": user.to_dict()})

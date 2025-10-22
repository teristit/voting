from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from extensions import db
from models.user import User
from models.auth import AuthSession, RevokedToken
from services.telegram_auth import verify_telegram_init_data
from services.audit_service import log_action
import hashlib

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/telegram", methods=["POST"])
def telegram_login():
    data = request.get_json() or {}
    init_data = data.get("init_data")
    user_info = verify_telegram_init_data(init_data)
    if not user_info:
        return jsonify({"status":"error","message":"Invalid Telegram data"}), 401

    telegram_id = user_info.get("id")
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(name=user_info.get("first_name","Unknown"), telegram_id=telegram_id, telegram_username=user_info.get("username"), role="user", active=True)
        db.session.add(user); db.session.commit()
        log_action(None, "user_created", {"telegram_id": telegram_id, "name": user.name})

    access_token = create_access_token(identity=user.user_id, expires_delta=timedelta(hours=1))
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()

    auth_session = AuthSession(user_id=user.user_id, token_hash=token_hash, expires_at=datetime.utcnow()+timedelta(hours=1))
    db.session.add(auth_session); db.session.commit()

    log_action(user.user_id, "login", {"telegram_id": telegram_id})
    return jsonify({"status":"success","token": access_token, "user": user.to_dict()})

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    token = request.headers.get("Authorization","").replace("Bearer ","")
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    revoked = RevokedToken(token_hash=token_hash, user_id=current_user, reason="logout")
    db.session.add(revoked); db.session.commit()
    log_action(current_user, "logout", {"token_hash": token_hash})
    return jsonify({"status":"success","message":"Logged out"})

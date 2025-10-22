from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.settings_service import get_setting, set_setting
from services.audit_service import log_action
from models.settings import SystemSetting

settings_bp = Blueprint("settings_bp", __name__)

@settings_bp.route("/", methods=["GET"])
@jwt_required()
def list_settings():
    settings = SystemSetting.query.all()
    return jsonify({s.setting_key: s.setting_value for s in settings})

@settings_bp.route("/<key>", methods=["PATCH"])
@jwt_required()
def update_setting(key):
    current_user = get_jwt_identity()
    data = request.get_json() or {}
    value = data.get("value")
    set_setting(key, value)
    log_action(current_user, "setting_updated", {"key": key, "value": value})
    return jsonify({"status":"success","key": key, "value": value})

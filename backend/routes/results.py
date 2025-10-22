from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from services.bonus_calc import calculate_bonus_for_session
from models.result import Result

results_bp = Blueprint("results_bp", __name__)

@results_bp.route("/<int:session_id>", methods=["GET"])
@jwt_required()
def get_results(session_id):
    results = Result.query.filter_by(session_id=session_id).order_by(Result.rank.asc()).all()
    return jsonify([r.to_dict() for r in results])

@results_bp.route("/<int:session_id>/recalculate", methods=["POST"])
@jwt_required()
def recalc_results(session_id):
    results = calculate_bonus_for_session(session_id)
    return jsonify({"status":"success","results": results})

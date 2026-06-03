from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from services import badge_service
from utils.api_response import fail, success


badge_bp = Blueprint("badge", __name__)


@badge_bp.route("/definitions", methods=["GET"])
def get_badge_definitions():
    payload = badge_service.list_definitions()
    return success(data=payload, message="success", code=200)


@badge_bp.route("/my", methods=["GET"])
@jwt_required()
def get_my_badges():
    user_id = get_jwt_identity()
    payload = badge_service.list_user_badges(user_id=user_id)
    return success(data=payload, message="success", code=200)


@badge_bp.route("/evaluate", methods=["POST"])
@jwt_required()
def evaluate_my_badges():
    user_id = get_jwt_identity()
    try:
        payload = badge_service.evaluate_user_badges(user_id=user_id)
    except ValueError as err:
        return fail(str(err), code=400)
    return success(data=payload, message="success", code=200)

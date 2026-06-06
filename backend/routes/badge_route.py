from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.exceptions import BadRequest

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


@badge_bp.route("/equipped", methods=["GET"])
@jwt_required()
def get_equipped_badges():
    user_id = get_jwt_identity()
    payload = badge_service.list_equipped_badges(user_id=user_id)
    return success(data=payload, message="success", code=200)


@badge_bp.route("/equipped", methods=["PUT"])
@jwt_required()
def update_equipped_badges():
    user_id = get_jwt_identity()
    try:
        data = _json_object_body()
        payload = badge_service.update_equipped_badges(
            user_id=user_id,
            badge_codes=data.get("badgeCodes"),
        )
    except ValueError as err:
        return fail(str(err), code=400)
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


@badge_bp.route("/changes", methods=["GET"])
@jwt_required()
def get_badge_changes():
    user_id = get_jwt_identity()
    payload = badge_service.list_unread_changes(user_id=user_id)
    return success(data=payload, message="success", code=200)


@badge_bp.route("/changes/read", methods=["POST"])
@jwt_required()
def mark_badge_changes_read():
    user_id = get_jwt_identity()
    raw_body = request.get_data(cache=True)
    if not raw_body:
        if request.is_json:
            return fail("请求体必须是有效的JSON对象", code=400)
        data = {}
    elif not request.is_json:
        return fail("请求体必须是有效的JSON对象", code=400)
    else:
        try:
            data = request.get_json()
        except BadRequest:
            return fail("请求体必须是有效的JSON对象", code=400)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON对象", code=400)
    try:
        payload = badge_service.mark_changes_read(
            user_id=user_id,
            change_ids=data.get("changeIds"),
        )
    except ValueError as err:
        return fail(str(err), code=400)
    return success(data=payload, message="success", code=200)


def _json_object_body():
    raw_body = request.get_data(cache=True)
    if not raw_body or not request.is_json:
        raise ValueError("请求体必须是有效的JSON对象")
    try:
        data = request.get_json()
    except BadRequest as exc:
        raise ValueError("请求体必须是有效的JSON对象") from exc
    if not isinstance(data, dict):
        raise ValueError("请求体必须是有效的JSON对象")
    return data

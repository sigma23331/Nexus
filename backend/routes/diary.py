import re
from datetime import datetime

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import diary_service
from services.user_profile_service import UserProfileService
from utils.api_response import success, fail
from utils.validators import parse_page_limit, validate_enum

diary_bp = Blueprint('diary', __name__)


@diary_bp.route('/entry', methods=['POST'])
@jwt_required()
def save_entry():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON", code=400)

    mood_tag = data.get('moodTag')
    content = data.get('content')
    is_public = data.get('isPublic', False)

    try:
        validate_enum(mood_tag, ("happy", "calm", "sad", "angry", "tired"), "moodTag")
    except ValueError as err:
        return fail(str(err), code=400)

    if not isinstance(content, str) or not content.strip():
        return fail("content 必须为非空字符串", code=400)

    user_id = get_jwt_identity()
    try:
        payload = diary_service.create_entry(
            user_id=user_id,
            mood_tag=mood_tag,
            content=content,
            is_public=is_public,
        )
    except ValueError as err:
        return fail(str(err), code=400)

    try:
        UserProfileService.update_profile_by_behavior(
            user_id=user_id, event_type="diary_created", event_time=datetime.utcnow()
        )
    except Exception:
        current_app.logger.warning("profile rule fields update failed", exc_info=True)

    return success(data=payload, message="success", code=200)


@diary_bp.route('/timeline', methods=['GET'])
@jwt_required()
def get_timeline():
    try:
        page, limit = parse_page_limit(request.args)
    except ValueError as err:
        return fail(str(err), code=400)

    year_month = request.args.get('yearMonth')
    if year_month and not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', year_month):
        return fail("yearMonth 必须为 YYYY-MM", code=400)

    user_id = get_jwt_identity()
    payload = diary_service.list_timeline(
        user_id=user_id,
        page=page,
        limit=limit,
        year_month=year_month,
    )
    return success(data=payload, message="success", code=200)


@diary_bp.route('/entry/<id>', methods=['GET'])
@jwt_required()
def get_entry(id):
    user_id = get_jwt_identity()
    try:
        payload = diary_service.get_entry(user_id=user_id, entry_id=id)
    except LookupError as err:
        return fail(str(err), code=404)
    except PermissionError as err:
        return fail(str(err), code=403)

    return success(data=payload, message="success", code=200)


@diary_bp.route('/entry/<id>', methods=['PUT'])
@jwt_required()
def update_entry(id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON", code=400)

    user_id = get_jwt_identity()
    try:
        payload = diary_service.update_entry(user_id=user_id, entry_id=id, payload=data)
    except ValueError as err:
        return fail(str(err), code=400)
    except LookupError as err:
        return fail(str(err), code=404)
    except PermissionError as err:
        return fail(str(err), code=403)

    return success(data=payload, message="success", code=200)


@diary_bp.route('/entry/<id>', methods=['DELETE'])
@jwt_required()
def delete_entry(id):
    user_id = get_jwt_identity()
    try:
        payload = diary_service.delete_entry(user_id=user_id, entry_id=id)
    except LookupError as err:
        return fail(str(err), code=404)
    except PermissionError as err:
        return fail(str(err), code=403)

    return success(data=payload, message="success", code=200)

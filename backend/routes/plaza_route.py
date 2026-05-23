from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import plaza_service
from services import plaza_comment_service
from utils.api_response import success, fail
from utils.validators import validate_enum
from .plaza_comment_helpers import REPORT_REASON_CODES

plaza_bp = Blueprint('plaza', __name__)


@plaza_bp.route('/cards', methods=['GET'])
@jwt_required()
def get_cards():
    tab = request.args.get('tab', 'latest')
    cursor = request.args.get('cursor')
    limit_raw = request.args.get('limit', '10')

    try:
        validate_enum(tab, ("hot", "latest"), "tab")
        limit = int(limit_raw)
    except ValueError as err:
        return fail(str(err), code=400)

    user_id = get_jwt_identity()
    try:
        payload = plaza_service.list_cards(
            user_id=user_id,
            tab=tab,
            cursor=cursor,
            limit=limit,
        )
    except ValueError as err:
        return fail(str(err), code=400)

    return success(data=payload, message="success", code=200)


@plaza_bp.route('/cards/<card_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(card_id):
    cursor = request.args.get('cursor')
    limit_raw = request.args.get('limit', '20')

    try:
        limit = int(limit_raw)
    except ValueError:
        return fail("limit 必须为整数", code=400)

    user_id = get_jwt_identity()
    try:
        payload = plaza_comment_service.list_comments(
            current_user_id=user_id,
            card_id=card_id,
            cursor=cursor,
            limit=limit,
        )
    except ValueError as err:
        return fail(str(err), code=400)
    except LookupError as err:
        return fail(str(err), code=404)

    return success(data=payload, message="success", code=200)


@plaza_bp.route('/cards/<card_id>/comments', methods=['POST'])
@jwt_required()
def post_comment(card_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON", code=400)

    content = data.get('content')
    parent_id = data.get('parentId')
    if not isinstance(content, str) or not content.strip():
        return fail("content 字段不能为空", code=400)
    if parent_id is not None and (not isinstance(parent_id, str) or not parent_id.strip()):
        return fail("parentId 必须为非空字符串", code=400)

    user_id = get_jwt_identity()
    try:
        payload = plaza_comment_service.create_comment(
            user_id=user_id,
            card_id=card_id,
            content=content,
            parent_id=parent_id.strip() if isinstance(parent_id, str) else None,
        )
    except ValueError as err:
        return fail(str(err), code=400)
    except LookupError as err:
        return fail(str(err), code=404)

    return success(data=payload, message="success", code=200)


@plaza_bp.route('/comments/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    user_id = get_jwt_identity()
    try:
        payload = plaza_comment_service.delete_comment(user_id=user_id, comment_id=comment_id)
    except LookupError as err:
        return fail(str(err), code=404)
    except PermissionError as err:
        return fail(str(err), code=403)

    return success(data=payload, message="success", code=200)


@plaza_bp.route('/comments/<comment_id>/reports', methods=['POST'])
@jwt_required()
def report_comment(comment_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON", code=400)

    reason_code = data.get('reasonCode')
    reason_text = data.get('reasonText')
    try:
        validate_enum(reason_code, REPORT_REASON_CODES, "reasonCode")
    except ValueError as err:
        return fail(str(err), code=400)
    if reason_text is not None and not isinstance(reason_text, str):
        return fail("reasonText 必须为字符串", code=400)

    user_id = get_jwt_identity()
    try:
        payload = plaza_comment_service.report_comment(
            user_id=user_id,
            comment_id=comment_id,
            reason_code=reason_code,
            reason_text=reason_text,
        )
    except ValueError as err:
        return fail(str(err), code=400)
    except LookupError as err:
        return fail(str(err), code=404)

    return success(data=payload, message="success", code=200)


@plaza_bp.route('/comments/<comment_id>/replies', methods=['GET'])
@jwt_required()
def get_replies(comment_id):
    cursor = request.args.get('cursor')
    limit_raw = request.args.get('limit', '20')

    try:
        limit = int(limit_raw)
    except ValueError:
        return fail("limit 必须为整数", code=400)

    user_id = get_jwt_identity()
    try:
        payload = plaza_comment_service.list_replies(
            current_user_id=user_id,
            comment_id=comment_id,
            cursor=cursor,
            limit=limit,
        )
    except ValueError as err:
        return fail(str(err), code=400)
    except LookupError as err:
        return fail(str(err), code=404)

    return success(data=payload, message="success", code=200)


@plaza_bp.route('/card', methods=['POST'])
@jwt_required()
def post_card():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON", code=400)

    user_id = get_jwt_identity()
    try:
        payload = plaza_service.create_card(user_id=user_id, payload=data)
    except ValueError as err:
        return fail(str(err), code=400)
    except LookupError as err:
        return fail(str(err), code=404)

    return success(data=payload, message="success", code=200)


@plaza_bp.route('/like', methods=['POST'])
@jwt_required()
def toggle_like():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON", code=400)

    card_id = data.get('cardId')
    action = data.get('action')

    if not isinstance(card_id, str) or not card_id.strip():
        return fail("cardId 字段不能为空", code=400)

    try:
        validate_enum(action, ("like", "unlike"), "action")
    except ValueError as err:
        return fail(str(err), code=400)

    user_id = get_jwt_identity()
    try:
        payload = plaza_service.toggle_like(user_id=user_id, card_id=card_id.strip(), action=action)
    except ValueError as err:
        return fail(str(err), code=400)
    except LookupError as err:
        return fail(str(err), code=404)

    return success(data=payload, message="success", code=200)


@plaza_bp.route('/card/<id>', methods=['DELETE'])
@jwt_required()
def delete_card(id):
    user_id = get_jwt_identity()
    try:
        payload = plaza_service.delete_card(user_id=user_id, card_id=id)
    except LookupError as err:
        return fail(str(err), code=404)
    except PermissionError as err:
        return fail(str(err), code=403)

    return success(data=payload, message="success", code=200)

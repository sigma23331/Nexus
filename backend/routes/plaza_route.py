from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import plaza_service
from utils.api_response import success, fail
from utils.validators import validate_enum

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

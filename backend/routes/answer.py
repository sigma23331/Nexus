from datetime import datetime

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import answer_service
from services.user_profile_service import UserProfileService
from utils.api_response import success, fail
from utils.validators import parse_page_limit, validate_enum

answer_bp = Blueprint('answer', __name__)


@answer_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_answer():
    data = request.get_json(silent=True)
    question = (data or {}).get('question')

    if not isinstance(question, str) or not question.strip():
        return fail("question 必须为非空字符串", code=400)
    if len(question.strip()) > 200:
        return fail("question 长度不能超过200", code=400)

    user_id = get_jwt_identity()
    payload = answer_service.ask_question(user_id=user_id, question=question)
    try:
        UserProfileService.update_profile_by_behavior(
            user_id=user_id, event_type="answer_created", event_time=datetime.utcnow()
        )
    except Exception:
        current_app.logger.warning("profile rule fields update failed", exc_info=True)
    return success(data=payload, message="success", code=200)


@answer_bp.route('/history', methods=['GET'])
@jwt_required()
def answer_history():
    try:
        page, limit = parse_page_limit(request.args)
    except ValueError as err:
        return fail(str(err), code=400)

    user_id = get_jwt_identity()
    payload = answer_service.list_history(user_id=user_id, page=page, limit=limit)
    return success(data=payload, message="success", code=200)


@answer_bp.route('/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON", code=400)

    answer_id = data.get('answerId')
    action = data.get('action')

    if not isinstance(answer_id, str) or not answer_id.strip():
        return fail("answerId 字段不能为空", code=400)

    try:
        validate_enum(action, ("favorite", "unfavorite"), "action")
    except ValueError as err:
        return fail(str(err), code=400)

    user_id = get_jwt_identity()
    try:
        payload = answer_service.toggle_favorite(
            user_id=user_id,
            answer_id=answer_id.strip(),
            action=action,
        )
    except LookupError as err:
        return fail(str(err), code=404)

    return success(data=payload, message="success", code=200)

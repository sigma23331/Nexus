from sqlalchemy.exc import SQLAlchemyError

from flask import Blueprint, g, jsonify, request

from middleware.auth import login_required
from services.user_profile_service import UserProfileService

user_bp = Blueprint('user', __name__)


@user_bp.route('/profiles', methods=['GET'])
@login_required
def get_my_profile():
    profile = UserProfileService.get_by_user_id(g.user_id)
    if not profile:
        return jsonify({
            'code': 404,
            'message': '用户画像不存在',
            'data': None,
        }), 404

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': UserProfileService.to_dict(profile),
    }), 200


@user_bp.route('/profiles/<user_id>', methods=['GET'])
@login_required
def get_profile_by_user_id(user_id):
    if user_id != g.user_id:
        return jsonify({
            'code': 403,
            'message': '无权限访问该资源',
            'data': None,
        }), 403

    profile = UserProfileService.get_by_user_id(user_id)
    if not profile:
        return jsonify({
            'code': 404,
            'message': '用户画像不存在',
            'data': None,
        }), 404

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': UserProfileService.to_dict(profile),
    }), 200


@user_bp.route('/profiles', methods=['PUT'])
@login_required
def update_my_profile():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            'code': 400,
            'message': '请求体必须为 JSON',
            'data': None,
        }), 400

    try:
        update_data = UserProfileService.parse_update_payload(payload)
    except ValueError as exc:
        return jsonify({
            'code': 400,
            'message': str(exc),
            'data': None,
        }), 400

    if not update_data:
        return jsonify({
            'code': 400,
            'message': '没有可更新的字段',
            'data': None,
        }), 400

    profile = UserProfileService.get_by_user_id(g.user_id)
    if not profile:
        return jsonify({
            'code': 404,
            'message': '用户画像不存在',
            'data': None,
        }), 404

    try:
        updated_profile = UserProfileService.update(g.user_id, **update_data)
    except SQLAlchemyError:
        return jsonify({
            'code': 500,
            'message': '更新失败，请稍后重试',
            'data': None,
        }), 500

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': UserProfileService.to_dict(updated_profile),
    }), 200

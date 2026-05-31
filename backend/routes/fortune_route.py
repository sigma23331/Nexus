from datetime import datetime

from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import fortune_service
from services import fortune_pk_service
from services.user_profile_service import UserProfileService
from utils.api_response import success, fail

fortune_bp = Blueprint('fortune', __name__)


@fortune_bp.route('/today', methods=['GET'])
@jwt_required()
def today_fortune():
    user_id = get_jwt_identity()
    payload = fortune_service.get_today_fortune(user_id=user_id)
    try:
        UserProfileService.update_profile_by_behavior(
            user_id=user_id, event_type="fortune_created", event_time=datetime.utcnow()
        )
    except Exception:
        current_app.logger.warning("profile rule fields update failed", exc_info=True)
    return success(data=payload, message="success", code=200)


@fortune_bp.route('/trend', methods=['GET'])
@jwt_required()
def fortune_trend():
    user_id = get_jwt_identity()
    payload = fortune_service.get_trend(user_id=user_id)
    return success(data=payload, message="success", code=200)


@fortune_bp.route('/stats/global', methods=['GET'])
@jwt_required()
def global_stats():
    payload = fortune_service.get_global_stats()
    return success(data=payload, message="success", code=200)


@fortune_bp.route('/pk', methods=['POST'])
@jwt_required()
def create_fortune_pk():
    user_id = get_jwt_identity()
    try:
        payload = fortune_pk_service.create_pk(user_id=user_id)
    except LookupError as err:
        return fail(str(err), code=404)
    except ValueError as err:
        return fail(str(err), code=400)

    return success(data=payload, message="success", code=200)


@fortune_bp.route('/pk', methods=['GET'])
@jwt_required(optional=True)
def get_or_join_fortune_pk():
    token = request.args.get('token')
    current_user_id = get_jwt_identity()
    try:
        payload = fortune_pk_service.get_or_join_pk(
            token=token,
            current_user_id=current_user_id,
        )
    except ValueError as err:
        return fail(str(err), code=400)
    except LookupError as err:
        return fail(str(err), code=404)
    except PermissionError as err:
        return fail(str(err), code=410)

    return success(data=payload, message="success", code=200)

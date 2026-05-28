# backend/routes/user.py
import re
from datetime import date

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.diary import DiaryEntry
from models.fortune import FortuneRecord
from models.user import Gender, User
from services.fortune_service import (
    _deserialize_content_pair,
    _normalize_history_lines,
    _normalize_lucky_hour,
)
from services.profile_analysis_service import ProfileAnalysisService
from services.user_profile_service import UserProfileService

user_bp = Blueprint('user', __name__)


def _serialize_user_info(user):
    gender = getattr(user, 'gender', None)
    if isinstance(gender, Gender):
        gender_value = gender.value
    elif isinstance(gender, str) and gender:
        gender_value = gender
    else:
        gender_value = Gender.SECRET.value

    return {
        "uid": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png",
        "birthday": user.birthday.isoformat() if getattr(user, 'birthday', None) else None,
        "latitude": getattr(user, 'latitude', None),
        "longitude": getattr(user, 'longitude', None),
        "locationAccuracy": getattr(user, 'location_accuracy', None),
        "locationUpdatedAt": (
            user.location_updated_at.isoformat() if getattr(user, 'location_updated_at', None) else None
        ),
        "gender": gender_value,
    }


def get_current_user():
    """从 JWT 获取当前用户对象，不存在时返回 None"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.filter_by(id=user_id).first()


# ==================== 6.1 个人中心概览 ====================

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user = get_current_user()
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    # 统计数据
    diary_count = DiaryEntry.query.filter_by(user_id=user.id).count()
    answer_collected = user.favorites.count()      # 收藏的答案数
    plaza_post_count = user.plaza_cards.count()    # 广场发布卡片数

    # AI 分析：冷却后自动更新 mood_tendency / topic_interests / self_context_tag
    try:
        ProfileAnalysisService.trigger_analysis_if_needed(user_id=user.id)
    except Exception:
        current_app.logger.warning("mood analysis failed for user %s", user.id, exc_info=True)

    profile = UserProfileService.get_by_user_id(user.id)
    profile_data = UserProfileService.to_dict(profile) if profile else None

    return jsonify(code=200, message="success", data={
        "userInfo": _serialize_user_info(user),
        "stats": {
            "diaryCount": diary_count,
            "answerCollected": answer_collected,
            "plazaPostCount": plaza_post_count
        },
        "profile": profile_data,
    }), 200


# ==================== 6.1.1 修改个人信息 ====================

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify(code=400, message="请求体必须是有效的JSON对象", data=None), 400

    allowed_fields = {
        'nickname',
        'avatar',
        'birthday',
        'gender',
        'latitude',
        'longitude',
        'locationAccuracy',
    }
    provided_fields = {k for k in payload.keys() if k in allowed_fields}
    if not provided_fields:
        return jsonify(
            code=400,
            message="仅支持更新 nickname、avatar、birthday、gender 或地理位置字段",
            data=None,
        ), 400

    # 昵称更新：非空、长度限制、唯一性
    if 'nickname' in provided_fields:
        nickname = payload.get('nickname')
        if not isinstance(nickname, str) or not nickname.strip():
            return jsonify(code=400, message="昵称不能为空", data=None), 400
        nickname = nickname.strip()
        if len(nickname) > 20:
            return jsonify(code=400, message="昵称长度不能超过20个字符", data=None), 400
        existing = User.query.filter(User.nickname == nickname, User.id != user.id).first()
        if existing:
            return jsonify(code=400, message="昵称已被占用", data=None), 400
        user.nickname = nickname

    # 头像更新：允许 URL 或 dataURL（前端上传图片时用 base64）
    if 'avatar' in provided_fields:
        avatar = payload.get('avatar')
        if avatar is None:
            avatar = ''
        if not isinstance(avatar, str):
            return jsonify(code=400, message="头像格式无效", data=None), 400
        avatar = avatar.strip()
        if len(avatar) > 2_000_000:
            return jsonify(code=400, message="头像数据过大，请压缩后重试", data=None), 400
        user.avatar = avatar

    if 'birthday' in provided_fields:
        birthday = payload.get('birthday')
        if birthday in (None, ''):
            user.birthday = None
        elif not isinstance(birthday, str):
            return jsonify(code=400, message="birthday 必须为 YYYY-MM-DD 格式", data=None), 400
        else:
            try:
                user.birthday = date.fromisoformat(birthday.strip())
            except ValueError:
                return jsonify(code=400, message="birthday 必须为 YYYY-MM-DD 格式", data=None), 400

    if 'gender' in provided_fields:
        gender = payload.get('gender')
        if not isinstance(gender, str):
            return jsonify(code=400, message="gender 必须为 male、female 或 secret", data=None), 400
        gender = gender.strip().lower()
        if gender not in {item.value for item in Gender}:
            return jsonify(code=400, message="gender 必须为 male、female 或 secret", data=None), 400
        user.gender = Gender(gender)

    if 'latitude' in provided_fields or 'longitude' in provided_fields or 'locationAccuracy' in provided_fields:
        latitude = payload.get('latitude')
        longitude = payload.get('longitude')
        accuracy = payload.get('locationAccuracy')

        if latitude is None or longitude is None:
            return jsonify(code=400, message="latitude 和 longitude 不能为空", data=None), 400

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            return jsonify(code=400, message="latitude/longitude 必须是数字", data=None), 400

        if not (-90 <= latitude <= 90):
            return jsonify(code=400, message="latitude 超出范围", data=None), 400
        if not (-180 <= longitude <= 180):
            return jsonify(code=400, message="longitude 超出范围", data=None), 400

        if accuracy is not None:
            try:
                accuracy = float(accuracy)
            except (TypeError, ValueError):
                return jsonify(code=400, message="locationAccuracy 必须是数字", data=None), 400
            if accuracy < 0:
                return jsonify(code=400, message="locationAccuracy 不能为负数", data=None), 400

        from datetime import datetime

        user.latitude = latitude
        user.longitude = longitude
        user.location_accuracy = accuracy
        user.location_updated_at = datetime.utcnow()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("更新用户资料失败")
        return jsonify(code=500, message="更新失败，请稍后重试", data=None), 500

    return jsonify(code=200, message="更新成功", data={
        "userInfo": _serialize_user_info(user)
    }), 200


# ==================== 6.2 历史运势记录 ====================

@user_bp.route('/history/fortune', methods=['GET'])
@jwt_required()
def get_fortune_history():
    user = get_current_user()
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    # 分页参数解析
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify(code=400, message="page 和 limit 必须为整数", data=None), 400

    if page < 1 or limit < 1 or limit > 50:
        return jsonify(code=400, message="page 不能小于1，limit 范围 1-50", data=None), 400

    # 查询当前用户的运势记录，按日期降序
    pagination = FortuneRecord.query.filter_by(user_id=user.id)\
        .order_by(FortuneRecord.date.desc())\
        .paginate(page=page, per_page=limit, error_out=False)

    fortune_list = []
    for rec in pagination.items:
        content_main, content_sub = _deserialize_content_pair(rec.content)
        lucky_hour = _normalize_lucky_hour(rec)
        fortune_list.append({
            "date": rec.date.isoformat() if rec.date else None,
            "score": rec.score,
            "title": rec.title,
            "content_main": content_main,
            "content_sub": content_sub,
            "love": getattr(rec, "love", None) or "平稳",
            "career": getattr(rec, "career", None) or "平稳",
            "health": getattr(rec, "health", None) or "稳定",
            "wealth": getattr(rec, "wealth", None) or "平稳",
            "yi": rec.yi or [],
            "ji": rec.ji or [],
            "gua_meaning_lines": _normalize_history_lines(rec),
            "lucky_hour_name": lucky_hour["name"],
            "lucky_hour_range": lucky_hour["range"],
        })

    return jsonify(code=200, message="success", data={
        "total": pagination.total,
        "page": page,
        "limit": limit,
        "list": fortune_list
    }), 200


# ==================== 6.3 历史收藏答案 ====================

@user_bp.route('/history/favorites', methods=['GET'])
@jwt_required()
def get_favorite_answers():
    user = get_current_user()
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify(code=400, message="page 和 limit 必须为整数", data=None), 400

    if page < 1 or limit < 1 or limit > 50:
        return jsonify(code=400, message="page 不能小于1，limit 范围 1-50", data=None), 400

    # 通过 favorites 关系获取收藏的答案记录（按收藏时间降序，收藏表继承了 BaseModel 有 created_at）
    # Favorite 模型关联了 answer，且 Favorite 本身有 created_at 字段表示收藏时间
    from models.association import Favorite

    fav_pagination = (
        Favorite.query.filter_by(user_id=user.id)
        .order_by(Favorite.created_at.desc())
        .paginate(page=page, per_page=limit, error_out=False)
    )

    answer_list = []
    for fav in fav_pagination.items:
        ans = fav.answer  # 通过关系获取 AnswerRecord
        if ans:
            answer_list.append({
                "id": ans.id,
                "question": ans.question,
                "answerText": ans.answer_text,
                "createdAt": ans.created_at.isoformat() + "Z" if ans.created_at else None
            })

    return jsonify(code=200, message="success", data={
        "total": fav_pagination.total,
        "page": page,
        "limit": limit,
        "list": answer_list
    }), 200


# ==================== 6.9 修改头像 ====================

@user_bp.route('/profile/avatar', methods=['PUT'])
@jwt_required()
def update_avatar():
    """
    修改用户头像
    Request JSON: { "avatar": "头像URL" }
    """
    user = get_current_user()
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    data = request.get_json(silent=True)
    if not data or 'avatar' not in data:
        return jsonify(code=400, message="缺少 avatar 参数", data=None), 400

    avatar_url = data['avatar'].strip() if isinstance(data['avatar'], str) else ''

    # 简单校验：非空时检查是否为合法 URL（支持 http/https/相对路径）
    if avatar_url:
        url_pattern = re.compile(
            r'^(https?://)?'  # http:// 或 https:// (可选)
            r'[\w\-]+(\.[\w\-]+)+'  # 域名
            r'([\w\-.,@?^=%&:/~+#]*)?$'  # 路径、查询等
        )
        if not url_pattern.match(avatar_url):
            return jsonify(code=400, message="头像 URL 格式不正确", data=None), 400

    user.avatar = avatar_url
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("更新头像失败: %s", exc, exc_info=True)
        return jsonify(code=500, message="更新失败，请稍后重试", data=None), 500

    return jsonify(code=200, message="头像更新成功", data={
        "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png"
    }), 200


# ==================== 6.10 修改昵称 ====================

@user_bp.route('/profile/nickname', methods=['PUT'])
@jwt_required()
def update_nickname():
    """
    修改用户昵称
    Request JSON: { "nickname": "新昵称" }
    """
    user = get_current_user()
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    data = request.get_json(silent=True)
    if not data or 'nickname' not in data:
        return jsonify(code=400, message="缺少 nickname 参数", data=None), 400

    new_nickname = data['nickname'].strip() if isinstance(data['nickname'], str) else ''

    # 长度校验（1-20 字符）
    if len(new_nickname) < 1 or len(new_nickname) > 20:
        return jsonify(code=400, message="昵称长度必须在1-20个字符之间", data=None), 400

    user.nickname = new_nickname
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(code=409, message="该昵称已被使用，请更换", data=None), 409
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("更新昵称失败: %s", exc, exc_info=True)
        return jsonify(code=500, message="更新失败，请稍后重试", data=None), 500

    return jsonify(code=200, message="昵称更新成功", data={
        "nickname": user.nickname
    }), 200


# ==================== 6.11 修改密码 ====================

@user_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def update_password():
    """
    修改用户密码（不验证旧密码，适用于验证码登录后首次设密或已登录重置密码）
    Request JSON: { "new_password": "新密码" }
    密码要求：长度 6-20 位
    """
    user = get_current_user()
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    data = request.get_json(silent=True)
    if not data or 'new_password' not in data:
        return jsonify(code=400, message="缺少 new_password 参数", data=None), 400

    new_password = data['new_password']
    if not isinstance(new_password, str):
        return jsonify(code=400, message="密码必须是字符串", data=None), 400

    if len(new_password) < 6 or len(new_password) > 20:
        return jsonify(code=400, message="密码长度需为 6-20 位", data=None), 400

    # 设置新密码（自动计算哈希）
    user.set_password(new_password)

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("修改密码失败: %s", exc, exc_info=True)
        return jsonify(code=500, message="修改失败，请稍后重试", data=None), 500

    return jsonify(code=200, message="密码修改成功", data={"success": True}), 200

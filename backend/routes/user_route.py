# backend/routes/user.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.fortune import FortuneRecord
from models.answer import AnswerRecord
from models.diary import DiaryEntry
from extensions import db
from services.profile_analysis_service import ProfileAnalysisService
from services.user_profile_service import UserProfileService

user_bp = Blueprint('user', __name__)


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
        current_app.logger.warning(f"mood analysis failed for user {user.id}", exc_info=True)

    profile = UserProfileService.get_by_user_id(user.id)
    profile_data = UserProfileService.to_dict(profile) if profile else None

    return jsonify(code=200, message="success", data={
        "userInfo": {
            "uid": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png"
        },
        "stats": {
            "diaryCount": diary_count,
            "answerCollected": answer_collected,
            "plazaPostCount": plaza_post_count
        },
        "profile": profile_data,
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

    fortune_list = [{
        "date": rec.date.isoformat() if rec.date else None,
        "score": rec.score,
        "title": rec.title,
    } for rec in pagination.items]

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
    fav_pagination = Favorite.query\
        .filter_by(user_id=user.id)\
        .order_by(Favorite.created_at.desc())\
        .paginate(page=page, per_page=limit, error_out=False)

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

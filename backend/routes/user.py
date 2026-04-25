from datetime import date, datetime

from sqlalchemy.exc import SQLAlchemyError

from flask import Blueprint, current_app, g, jsonify, request

from extensions import db
from middleware.auth import login_required
from models.answer import AnswerRecord
from models.diary import DiaryEntry, MoodType
from models.fortune import FortuneRecord
from services.user_profile_service import UserProfileService

user_bp = Blueprint('user', __name__)


def _trigger_profile_update_after_behavior(user_id: str, event_type: str, event_time: datetime, payload: dict):
    try:
        UserProfileService.update_profile_by_behavior(
            user_id=user_id,
            event_type=event_type,
            event_time=event_time,
            payload=payload,
            window_days=7,
        )
    except (SQLAlchemyError, ValueError) as exc:
        db.session.rollback()
        current_app.logger.warning(
            'Failed to update profile by behavior for user %s: %s',
            user_id,
            str(exc),
        )
        return 'failed'

    return 'success'


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


@user_bp.route('/diaries', methods=['POST'])
@login_required
def create_diary_entry():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            'code': 400,
            'message': '请求体必须为 JSON',
            'data': None,
        }), 400

    mood_tag_raw = payload.get('mood_tag')
    content = payload.get('content')
    is_public = payload.get('is_public', False)

    if not isinstance(mood_tag_raw, str):
        return jsonify({
            'code': 400,
            'message': 'mood_tag 必须为字符串',
            'data': None,
        }), 400

    try:
        mood_tag = MoodType(mood_tag_raw)
    except ValueError:
        return jsonify({
            'code': 400,
            'message': f'不支持的 mood_tag: {mood_tag_raw}',
            'data': None,
        }), 400

    if not isinstance(content, str) or not content.strip():
        return jsonify({
            'code': 400,
            'message': 'content 必须为非空字符串',
            'data': None,
        }), 400

    if not isinstance(is_public, bool):
        return jsonify({
            'code': 400,
            'message': 'is_public 必须为布尔值',
            'data': None,
        }), 400

    diary_entry = DiaryEntry(
        user_id=g.user_id,
        mood_tag=mood_tag,
        content=content.strip(),
        is_public=is_public,
        created_date=date.today(),
    )

    try:
        db.session.add(diary_entry)
        db.session.commit()
    except (SQLAlchemyError, ValueError) as exc:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'日记创建失败: {str(exc)}',
            'data': None,
        }), 500

    profile_update_status = _trigger_profile_update_after_behavior(
        user_id=g.user_id,
        event_type='diary_created',
        event_time=diary_entry.created_at or datetime.utcnow(),
        payload={'diary_entry_id': diary_entry.id},
    )

    return jsonify({
        'code': 201,
        'message': '日记创建成功',
        'data': {
            'id': diary_entry.id,
            'user_id': diary_entry.user_id,
            'mood_tag': diary_entry.mood_tag.value,
            'content': diary_entry.content,
            'is_public': diary_entry.is_public,
            'created_at': diary_entry.created_at.isoformat() if diary_entry.created_at else None,
            'created_date': diary_entry.created_date.isoformat() if diary_entry.created_date else None,
            'profile_update_status': profile_update_status,
        },
    }), 201


@user_bp.route('/fortunes', methods=['POST'])
@login_required
def create_fortune_record():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            'code': 400,
            'message': '请求体必须为 JSON',
            'data': None,
        }), 400

    fortune_date_raw = payload.get('date')
    score = payload.get('score')
    title = payload.get('title')
    content = payload.get('content')
    yi = payload.get('yi')
    ji = payload.get('ji')
    lucky_color = payload.get('lucky_color')
    lucky_direction = payload.get('lucky_direction')

    try:
        fortune_date = datetime.strptime(fortune_date_raw, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return jsonify({
            'code': 400,
            'message': 'date 必须为 YYYY-MM-DD',
            'data': None,
        }), 400

    if not isinstance(score, int):
        return jsonify({
            'code': 400,
            'message': 'score 必须为整数',
            'data': None,
        }), 400

    if not isinstance(title, str) or not title.strip():
        return jsonify({
            'code': 400,
            'message': 'title 必须为非空字符串',
            'data': None,
        }), 400

    if not isinstance(content, str) or not content.strip():
        return jsonify({
            'code': 400,
            'message': 'content 必须为非空字符串',
            'data': None,
        }), 400

    if not isinstance(yi, list) or not yi:
        return jsonify({
            'code': 400,
            'message': 'yi 必须为非空数组',
            'data': None,
        }), 400

    if not isinstance(ji, list) or not ji:
        return jsonify({
            'code': 400,
            'message': 'ji 必须为非空数组',
            'data': None,
        }), 400

    fortune_record = FortuneRecord(
        user_id=g.user_id,
        date=fortune_date,
        score=score,
        title=title.strip(),
        content=content.strip(),
        yi=yi,
        ji=ji,
        lucky_color=lucky_color,
        lucky_direction=lucky_direction,
    )

    try:
        db.session.add(fortune_record)
        db.session.commit()
    except (SQLAlchemyError, ValueError) as exc:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'运势记录创建失败: {str(exc)}',
            'data': None,
        }), 500

    profile_update_status = _trigger_profile_update_after_behavior(
        user_id=g.user_id,
        event_type='fortune_created',
        event_time=fortune_record.created_at or datetime.utcnow(),
        payload={'fortune_record_id': fortune_record.id},
    )

    return jsonify({
        'code': 201,
        'message': '运势记录创建成功',
        'data': {
            'id': fortune_record.id,
            'user_id': fortune_record.user_id,
            'date': fortune_record.date.isoformat(),
            'score': fortune_record.score,
            'title': fortune_record.title,
            'content': fortune_record.content,
            'yi': fortune_record.yi,
            'ji': fortune_record.ji,
            'lucky_color': fortune_record.lucky_color,
            'lucky_direction': fortune_record.lucky_direction,
            'created_at': fortune_record.created_at.isoformat() if fortune_record.created_at else None,
            'profile_update_status': profile_update_status,
        },
    }), 201


@user_bp.route('/answers', methods=['POST'])
@login_required
def create_answer_record():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            'code': 400,
            'message': '请求体必须为 JSON',
            'data': None,
        }), 400

    question = payload.get('question')
    answer_text = payload.get('answer_text')

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            'code': 400,
            'message': 'question 必须为非空字符串',
            'data': None,
        }), 400

    if not isinstance(answer_text, str) or not answer_text.strip():
        return jsonify({
            'code': 400,
            'message': 'answer_text 必须为非空字符串',
            'data': None,
        }), 400

    answer_record = AnswerRecord(
        user_id=g.user_id,
        question=question.strip(),
        answer_text=answer_text.strip(),
    )

    try:
        db.session.add(answer_record)
        db.session.commit()
    except (SQLAlchemyError, ValueError) as exc:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'答案记录创建失败: {str(exc)}',
            'data': None,
        }), 500

    profile_update_status = _trigger_profile_update_after_behavior(
        user_id=g.user_id,
        event_type='answer_created',
        event_time=answer_record.created_at or datetime.utcnow(),
        payload={'answer_record_id': answer_record.id},
    )

    return jsonify({
        'code': 201,
        'message': '答案记录创建成功',
        'data': {
            'id': answer_record.id,
            'user_id': answer_record.user_id,
            'question': answer_record.question,
            'answer_text': answer_record.answer_text,
            'created_at': answer_record.created_at.isoformat() if answer_record.created_at else None,
            'profile_update_status': profile_update_status,
        },
    }), 201

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from extensions import db
from datetime import datetime, timedelta
import random
import string

auth_bp = Blueprint('auth', __name__)

# 模拟短信验证码存储: { phone: { code, expires_at, sent_at, action } }
_sms_store = {}


def _generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def _check_sms_rate(phone):
    """返回 True 表示允许发送"""
    now = datetime.utcnow()
    record = _sms_store.get(phone)
    if record and (now - record['sent_at']).seconds < 60:
        return False
    return True


# -------------------- 2.2 手机号方式 --------------------

@auth_bp.route('/sms/send', methods=['POST'])
def send_sms():
    """发送短信验证码（登录用）"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    phone = data.get('phone')
    if not phone:
        return jsonify(code=400, message="phone 字段不能为空", data=None), 400

    if not _check_sms_rate(phone):
        return jsonify(code=429, message="发送频率过高，请60秒后再试", data=None), 429

    code = _generate_code()
    _sms_store[phone] = {
        'code': code,
        'expires_at': datetime.utcnow() + timedelta(seconds=300),
        'sent_at': datetime.utcnow(),
        'action': 'login'
    }
    current_app.logger.info(f"[模拟短信] 手机 {phone} 验证码: {code}")
    return jsonify(code=200, message="验证码已发送", data={"success": True, "expiresIn": 300}), 200


@auth_bp.route('/sms/login', methods=['POST'])
def sms_login():
    """手机号验证码登录/注册"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    phone = data.get('phone')
    code = data.get('code')
    if not phone or not code:
        return jsonify(code=400, message="phone 和 code 不能为空", data=None), 400

    record = _sms_store.get(phone)
    if not record or record.get('action') != 'login':
        return jsonify(code=400, message="未找到验证码，请先发送", data=None), 400
    if datetime.utcnow() > record['expires_at']:
        return jsonify(code=400, message="验证码已过期", data=None), 400
    if record['code'] != code:
        return jsonify(code=400, message="验证码错误", data=None), 400

    del _sms_store[phone]

    user = User.query.filter_by(phone=phone).first()
    is_new = False
    if not user:
        user = User(phone=phone, nickname=f"用户{phone[-4:]}")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        is_new = True

    token = create_access_token(identity=user.id)
    return jsonify(code=200, message="登录成功", data={
        "token": token,
        "userInfo": {
            "uid": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png"
        },
        "isNewUser": is_new
    }), 200


# -------------------- 2.2.3 / 2.2.4 绑定手机号 --------------------

@auth_bp.route('/sms/bind/send', methods=['POST'])
@jwt_required()
def send_bind_sms():
    """已登录用户请求绑定手机号前发送验证码"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    phone = data.get('phone')
    if not phone:
        return jsonify(code=400, message="phone 字段不能为空", data=None), 400

    # 检查新手机号是否已被其他用户绑定
    existing = User.query.filter_by(phone=phone).first()
    current_uid = get_jwt_identity()
    if existing and existing.id != current_uid:
        return jsonify(code=400, message="该手机号已被其他用户绑定", data=None), 400

    if not _check_sms_rate(phone):
        return jsonify(code=429, message="发送频率过高，请60秒后再试", data=None), 429

    code = _generate_code()
    _sms_store[phone] = {
        'code': code,
        'expires_at': datetime.utcnow() + timedelta(seconds=300),
        'sent_at': datetime.utcnow(),
        'action': 'bind'
    }
    current_app.logger.info(f"[模拟短信] 手机 {phone} 绑定验证码: {code}")
    return jsonify(code=200, message="验证码已发送", data={"success": True, "expiresIn": 300}), 200


@auth_bp.route('/sms/bind/confirm', methods=['POST'])
@jwt_required()
def confirm_bind_sms():
    """确认绑定手机号"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    phone = data.get('phone')
    code = data.get('code')
    if not phone or not code:
        return jsonify(code=400, message="phone 和 code 不能为空", data=None), 400

    record = _sms_store.get(phone)
    if not record or record.get('action') != 'bind':
        return jsonify(code=400, message="未找到验证码，请先发送", data=None), 400
    if datetime.utcnow() > record['expires_at']:
        return jsonify(code=400, message="验证码已过期", data=None), 400
    if record['code'] != code:
        return jsonify(code=400, message="验证码错误", data=None), 400

    # 再次检查手机号唯一性
    current_uid = get_jwt_identity()
    existing = User.query.filter_by(phone=phone).first()
    if existing and existing.id != current_uid:
        return jsonify(code=400, message="该手机号已被其他用户绑定", data=None), 400

    user = User.query.get(current_uid)
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    user.phone = phone
    db.session.commit()
    del _sms_store[phone]

    return jsonify(code=200, message="手机号绑定成功", data={"success": True}), 200


# -------------------- 2.4 通用接口 --------------------

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """验证 token 有效性"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(code=401, message="用户不存在", data=None), 401

    return jsonify(code=200, message="token有效", data={
        "valid": True,
        "userInfo": {
            "uid": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png",
            "phone": user.phone
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """登出（前端清除 token，后端可选黑名单）"""
    # 简单返回成功，实际可配合 token 黑名单
    return jsonify(code=200, message="登出成功", data={"success": True}), 200


# -------------------- 2.1 账密方式（暂缓实现）--------------------

@auth_bp.route('/password/register', methods=['POST'])
def password_register():
    return jsonify(code=501, message="账密注册暂未开放", data=None), 501


@auth_bp.route('/password/login', methods=['POST'])
def password_login():
    return jsonify(code=501, message="账密登录暂未开放", data=None), 501


# -------------------- 2.3 微信方式（预留）--------------------

@auth_bp.route('/wechat/login', methods=['POST'])
def wechat_login():
    return jsonify(code=501, message="微信登录暂未实现", data=None), 501
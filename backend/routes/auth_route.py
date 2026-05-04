import re
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

# 模拟短信验证码存储（生产环境请改用 Redis）
_sms_store = {}

# ---------- 工具函数 ----------
def _generate_code(length: int = 6) -> str:
    """生成指定长度的数字验证码"""
    return ''.join(__import__('random').choices(__import__('string').digits, k=length))

def _check_sms_rate(phone: str) -> bool:
    """同一手机号 60 秒内只允许发一次验证码"""
    now = datetime.utcnow()
    record = _sms_store.get(phone)
    if record and (now - record['sent_at']).seconds < 60:
        return False
    return True

def _make_unique_nickname(phone: str) -> str:
    """根据手机号后四位生成不重复的默认昵称（用于自动注册）"""
    base = f"用户{phone[-4:]}"
    nickname = base
    suffix = 1
    while User.query.filter_by(nickname=nickname).first():
        nickname = f"{base}_{suffix}"
        suffix += 1
        if len(nickname) > 20:
            # 超长保护，截断并保留唯一标识
            nickname = f"{base[:16]}_{suffix}"
    return nickname

# ---------- 短信验证码发送 ----------
@auth_bp.route('/sms/send', methods=['POST'])
def send_sms():
    """发送短信验证码（自动判断登录/注册场景）"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    phone = data.get('phone')
    if not phone:
        return jsonify(code=400, message="phone 字段不能为空", data=None), 400

    if not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify(code=400, message="无效的手机号格式", data=None), 400

    if not _check_sms_rate(phone):
        return jsonify(code=429, message="发送频率过高，请60秒后再试", data=None), 429

    existing = User.query.filter_by(phone=phone).first()
    action = 'login' if existing else 'register'

    code = _generate_code()
    _sms_store[phone] = {
        'code': code,
        'expires_at': datetime.utcnow() + timedelta(seconds=300),
        'sent_at': datetime.utcnow(),
        'action': action
    }
    current_app.logger.info(f"[模拟短信] 手机 {phone} 验证码: {code} (场景: {action})")
    return jsonify(code=200, message="验证码已发送", data={"success": True, "expiresIn": 300}), 200

# ---------- 短信验证码登录（自动注册） ----------
@auth_bp.route('/sms/login', methods=['POST'])
def sms_login():
    """手机号验证码登录/自动注册（无密码）"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    phone = data.get('phone')
    code = data.get('code')
    if not phone or not code:
        return jsonify(code=400, message="phone 和 code 不能为空", data=None), 400

    record = _sms_store.get(phone)
    if not record or record.get('action') not in ('login', 'register'):
        return jsonify(code=400, message="未找到验证码，请先发送", data=None), 400
    if datetime.utcnow() > record['expires_at']:
        return jsonify(code=400, message="验证码已过期", data=None), 400
    if record['code'] != code:
        return jsonify(code=400, message="验证码错误", data=None), 400

    del _sms_store[phone]

    user = User.query.filter_by(phone=phone).first()
    is_new = False
    if not user:
        # 昵称唯一性处理
        user = User(
            phone=phone,
            nickname=_make_unique_nickname(phone)
        )
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

# ---------- 注册（验证码 + 密码） ----------
@auth_bp.route('/register', methods=['POST'])
def register():
    """短信验证码 + 密码注册"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    phone = data.get('phone')
    code = data.get('code')
    password = data.get('password')

    if not phone or not code or not password:
        return jsonify(code=400, message="phone、code、password 不能为空", data=None), 400
    if not isinstance(phone, str) or not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify(code=400, message="无效的手机号格式", data=None), 400
    if not isinstance(password, str) or len(password) < 6 or len(password) > 20:
        return jsonify(code=400, message="密码长度需为6-20位", data=None), 400

    # 手机号唯一性检查
    if User.query.filter_by(phone=phone).first():
        return jsonify(code=400, message="该手机号已注册，请直接登录", data=None), 400

    # 验证验证码
    record = _sms_store.get(phone)
    if not record or record.get('action') not in ('login', 'register'):
        return jsonify(code=400, message="未找到验证码，请先发送", data=None), 400
    if datetime.utcnow() > record['expires_at']:
        return jsonify(code=400, message="验证码已过期", data=None), 400
    if record['code'] != code:
        return jsonify(code=400, message="验证码错误", data=None), 400

    try:
        user = User(
            phone=phone,
            nickname=_make_unique_nickname(phone)
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    except Exception as e:
        current_app.logger.error(f"注册用户失败: {str(e)}")
        db.session.rollback()
        return jsonify(code=500, message="注册失败，请稍后重试", data=None), 500

    del _sms_store[phone]

    token = create_access_token(identity=user.id)
    return jsonify(code=200, message="注册成功", data={
        "token": token,
        "userInfo": {
            "uid": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png"
        },
        "isNewUser": True
    }), 200

# ---------- 新增：昵称+密码注册（无验证码） ----------
@auth_bp.route('/register/nickname', methods=['POST'])
def register_nickname():
    """昵称 + 密码注册（无需手机号、无需验证码）"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    nickname = data.get('nickname')
    password = data.get('password')

    if not nickname or not password:
        return jsonify(code=400, message="nickname 和 password 不能为空", data=None), 400
    if not isinstance(nickname, str) or not (1 <= len(nickname.strip()) <= 20):
        return jsonify(code=400, message="昵称长度为1-20个字符", data=None), 400
    if not isinstance(password, str) or len(password) < 6 or len(password) > 20:
        return jsonify(code=400, message="密码长度需为6-20位", data=None), 400

    nickname = nickname.strip()

    # 检查昵称唯一性
    if User.query.filter_by(nickname=nickname).first():
        return jsonify(code=400, message="该昵称已被占用", data=None), 400

    try:
        user = User(nickname=nickname)  # phone 为 None
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    except Exception as e:
        current_app.logger.error(f"昵称注册失败: {str(e)}")
        db.session.rollback()
        return jsonify(code=500, message="注册失败，请稍后重试", data=None), 500

    token = create_access_token(identity=user.id)
    return jsonify(code=200, message="注册成功", data={
        "token": token,
        "userInfo": {
            "uid": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png"
        },
        "isNewUser": True
    }), 200

# ---------- 密码登录（支持手机号或昵称） ----------
@auth_bp.route('/password/login', methods=['POST'])
def password_login():
    """
    手机号/昵称 + 密码登录
    支持字段：
      - account: 手机号或昵称（推荐）
      - phone: 仅手机号（向后兼容，优先于 account 中的手机号）
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    password = data.get('password')
    if not password:
        return jsonify(code=400, message="password 不能为空", data=None), 400

    # 优先使用 account 字段，若没有则回退到 phone 字段
    account = data.get('account')
    phone = data.get('phone')

    user = None
    if account:
        # 判断输入是否手机号格式
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.query.filter_by(phone=account).first()
        else:
            user = User.query.filter_by(nickname=account).first()
    elif phone:
        if not isinstance(phone, str) or not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify(code=400, message="无效的手机号格式", data=None), 400
        user = User.query.filter_by(phone=phone).first()
    else:
        return jsonify(code=400, message="请提供 account（手机号/昵称）或 phone", data=None), 400

    if not user:
        return jsonify(code=400, message="账号或密码错误", data=None), 400
    if not user.password_hash:
        return jsonify(code=400, message="该账号未设置密码，请使用验证码登录", data=None), 400
    if not user.check_password(password):
        return jsonify(code=400, message="账号或密码错误", data=None), 400

    token = create_access_token(identity=user.id)
    return jsonify(code=200, message="登录成功", data={
        "token": token,
        "userInfo": {
            "uid": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png"
        },
        "isNewUser": False
    }), 200

# ---------- 绑定手机号（已登录） ----------
@auth_bp.route('/sms/bind/send', methods=['POST'])
@jwt_required()
def send_bind_sms():
    """已登录用户绑定手机号前发送验证码"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    phone = data.get('phone')
    if not phone:
        return jsonify(code=400, message="phone 字段不能为空", data=None), 400

    if not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify(code=400, message="无效的手机号格式", data=None), 400

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

# ---------- 通用认证接口 ----------
@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """校验 token 有效性"""
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
    """登出（前端清除 token，后端可扩展黑名单）"""
    return jsonify(code=200, message="登出成功", data={"success": True}), 200
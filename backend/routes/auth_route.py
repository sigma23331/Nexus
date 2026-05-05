import os
import re
import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from alibabacloud_credentials.credentials import AccessKeyCredential
from alibabacloud_dypnsapi20170525 import models as dypns_models
from alibabacloud_dypnsapi20170525.client import Client as DypnsClient
from alibabacloud_tea_openapi import models as open_api_models
from models.user import User
from extensions import db
from services import sms_service

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# 全局阿里云客户端缓存
_dypns_client = None

# ---------- 工具函数 ----------
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


def _get_dypns_client() -> DypnsClient:
    """获取或创建阿里云号码认证 DYPNS 客户端"""
    global _dypns_client
    if _dypns_client is None:
        try:
            access_key = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID', '')
            secret_key = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')
            if not access_key or not secret_key:
                raise ValueError("缺少阿里云AccessKey配置")

            credential = AccessKeyCredential(access_key, secret_key)
            config = open_api_models.Config(credential=credential)
            config.endpoint = current_app.config.get('DYPNS_API_ENDPOINT', 'dypnsapi.aliyuncs.com')
            config.region_id = os.environ.get('ALIBABA_CLOUD_REGION_ID', 'cn-hangzhou')
            _dypns_client = DypnsClient(config)
        except Exception as e:
            logger.error(f"创建DYPNS客户端失败: {e}")
            raise
    return _dypns_client


def _find_phone_value(payload):
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key and key.lower() in {'phonenumber', 'phone_number', 'phoneno', 'phone_no', 'mobile', 'phone'} and value:
                return value
            nested = _find_phone_value(value)
            if nested:
                return nested
    return None


def _extract_phone_number_from_response(response):
    """从阿里云号码认证返回结果中解析手机号"""
    if response is None:
        return None

    if isinstance(response, dict):
        body = response.get('body')
        if isinstance(body, dict):
            data = body.get('data')
            if isinstance(data, dict):
                return data.get('mobile') or data.get('phone')
        return _find_phone_value(response)

    body = getattr(response, 'body', None)
    if body:
        data = getattr(body, 'data', None)
        if data:
            return getattr(data, 'mobile', None) or getattr(data, 'phone', None)
        phone = getattr(body, 'mobile', None) or getattr(body, 'phone', None)
        if phone:
            return phone

    return _find_phone_value(response)

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

    if not sms_service.can_send(phone):
        return jsonify(code=429, message="发送频率过高，请60秒后再试", data=None), 429

    existing = User.query.filter_by(phone=phone).first()
    action = 'login' if existing else 'register'

    result = sms_service.send_verify_code(phone=phone, action=action)
    data = {
        "success": result.success,
        "provider": result.provider,
        "expiresIn": result.expires_in,
    }
    if result.error:
        data["error"] = result.error

    status_code = 200 if result.success else 500
    return jsonify(code=status_code, message=result.message, data=data), status_code

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

    verify_result = sms_service.verify_code(
        phone=phone,
        code=code,
        allowed_actions=('login', 'register'),
    )
    if not verify_result.success:
        return jsonify(code=400, message=verify_result.message, data=None), 400

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

    # 验证验证码（注册或登录场景均可，因为 /sms/send 已自动区分）
    verify_result = sms_service.verify_code(
        phone=phone,
        code=code,
        allowed_actions=('login', 'register'),
    )
    if not verify_result.success:
        return jsonify(code=400, message=verify_result.message, data=None), 400

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

    if not sms_service.can_send(phone):
        return jsonify(code=429, message="发送频率过高，请60秒后再试", data=None), 429

    result = sms_service.send_verify_code(phone=phone, action='bind')
    data = {
        "success": result.success,
        "provider": result.provider,
        "expiresIn": result.expires_in,
    }
    if result.error:
        data["error"] = result.error

    status_code = 200 if result.success else 500
    return jsonify(code=status_code, message=result.message, data=data), status_code

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

    verify_result = sms_service.verify_code(
        phone=phone,
        code=code,
        allowed_actions=('bind',),
    )
    if not verify_result.success:
        return jsonify(code=400, message=verify_result.message, data=None), 400

    current_uid = get_jwt_identity()
    existing = User.query.filter_by(phone=phone).first()
    if existing and existing.id != current_uid:
        return jsonify(code=400, message="该手机号已被其他用户绑定", data=None), 400

    user = User.query.get(current_uid)
    if not user:
        return jsonify(code=404, message="用户不存在", data=None), 404

    user.phone = phone
    db.session.commit()
    return jsonify(code=200, message="手机号绑定成功", data={"success": True}), 200


@auth_bp.route('/mobile/verify', methods=['POST'])
def verify_mobile():
    """号码认证回调：使用阿里云 DYPNS access_code 解析手机号并登录/注册用户"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify(code=400, message="请求体必须是有效的JSON", data=None), 400

    access_code = data.get('access_code') or data.get('accessCode')
    requested_phone = data.get('phone')
    if not access_code:
        return jsonify(code=400, message="access_code 不能为空", data=None), 400

    try:
        dypns_client = _get_dypns_client()
        request_model = dypns_models.GetPhoneWithTokenRequest(sp_token=access_code)
        response = dypns_client.get_phone_with_token(request_model)
        phone = _extract_phone_number_from_response(response)
    except Exception as e:
        current_app.logger.exception("号码认证失败")
        return jsonify(code=500, message=f"号码认证失败: {str(e)}", data=None), 500

    if not phone:
        return jsonify(code=500, message="未能解析到认证手机号", data=None), 500
    if requested_phone and requested_phone != phone:
        return jsonify(code=400, message="认证结果手机号与请求手机号不匹配", data=None), 400
    if not isinstance(phone, str) or not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify(code=400, message="认证结果手机号格式不正确", data=None), 400

    user = User.query.filter_by(phone=phone).first()
    is_new = False
    if not user:
        user = User(phone=phone, nickname=f"用户{phone[-4:]}")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        is_new = True

    token = create_access_token(identity=user.id)
    return jsonify(code=200, message="认证成功", data={
        "token": token,
        "userInfo": {
            "uid": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar or "https://api.xinyundao.com/default_avatar.png",
            "phone": user.phone
        },
        "isNewUser": is_new
    }), 200

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
import json
import random
import string
from dataclasses import dataclass
from datetime import datetime, timedelta

from flask import current_app


_sms_store = {}
_dypns_client = None


@dataclass
class SmsSendResult:
    success: bool
    provider: str
    message: str
    expires_in: int = 300
    error: str | None = None


@dataclass
class SmsVerifyResult:
    success: bool
    provider: str
    message: str


def _generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def can_send(phone: str, interval_seconds: int = 60) -> bool:
    record = _sms_store.get(phone)
    if not record:
        return True
    return (datetime.utcnow() - record['sent_at']).total_seconds() >= interval_seconds


def _use_real_provider() -> bool:
    return current_app.config.get('SMS_PROVIDER', 'mock') == 'aliyun'


def _get_dypns_client():
    global _dypns_client
    if _dypns_client is not None:
        return _dypns_client

    from alibabacloud_credentials.client import Client as CredentialClient
    from alibabacloud_dypnsapi20170525.client import Client as DypnsClient
    from alibabacloud_tea_openapi import models as open_api_models

    credential = CredentialClient()
    config = open_api_models.Config(credential=credential)
    config.endpoint = current_app.config.get('DYPNS_API_ENDPOINT', 'dypnsapi.aliyuncs.com')
    _dypns_client = DypnsClient(config)
    return _dypns_client


def _get_body_attr(response, name: str, default=None):
    def candidate_names(raw_name: str) -> list[str]:
        parts = [part for part in raw_name.split('_') if part]
        pascal = ''.join(part[:1].upper() + part[1:] for part in parts)
        camel = pascal[:1].lower() + pascal[1:] if pascal else raw_name
        return [raw_name, raw_name[:1].upper() + raw_name[1:], camel, pascal]

    def get_from_container(container, raw_name: str):
        if isinstance(container, dict):
            for candidate in candidate_names(raw_name):
                if candidate in container:
                    return container[candidate]
            return None
        for candidate in candidate_names(raw_name):
            value = getattr(container, candidate, None)
            if value is not None:
                return value
        return None

    body = getattr(response, 'body', None)
    if body is None and isinstance(response, dict):
        body = response.get('body')

    value = get_from_container(body, name)
    if value is not None:
        return value

    model = get_from_container(body, 'model')
    if model is not None:
        value = get_from_container(model, name)
        if value is not None:
            return value

    if isinstance(response, dict):
        for candidate in candidate_names(name):
            if candidate in response:
                return response[candidate]
    return default


def _mask_phone(phone: str) -> str:
    if not phone or len(phone) < 7:
        return phone or ''
    return f"{phone[:3]}****{phone[-4:]}"


def send_verify_code(phone: str, action: str, expires_in: int = 300) -> SmsSendResult:
    """Send an SMS verification code.

    In production, set SMS_PROVIDER=aliyun to let Alibaba Cloud generate and verify
    the code. In development/test, the mock provider keeps the code in memory.
    """
    if _use_real_provider():
        try:
            from alibabacloud_dypnsapi20170525 import models as dypns_models
            from alibabacloud_tea_util import models as util_models

            client = _get_dypns_client()
            request = dypns_models.SendSmsVerifyCodeRequest(
                sign_name=current_app.config['SMS_SIGN_NAME'],
                template_code=current_app.config['SMS_TEMPLATE_CODE'],
                phone_number=phone,
                template_param=json.dumps(
                    {
                        'code': '##code##',
                        'min': str(max(1, expires_in // 60)),
                    },
                    ensure_ascii=False,
                ),
                valid_time=expires_in,
                code_length=current_app.config.get('SMS_CODE_LENGTH', 6),
                code_type=1,
                interval=current_app.config.get('SMS_SEND_INTERVAL', 60),
            )
            response = client.send_sms_verify_code_with_options(
                request,
                util_models.RuntimeOptions(),
            )
            code = _get_body_attr(response, 'code')
            success = bool(_get_body_attr(response, 'success', False))
            request_id = _get_body_attr(response, 'request_id') or _get_body_attr(response, 'requestid')
            current_app.logger.info(
                '[Aliyun SMS] send result phone=%s action=%s success=%s code=%s request_id=%s',
                _mask_phone(phone), action, success, code, request_id,
            )
            if code == 'OK' and success:
                return SmsSendResult(
                    success=True,
                    provider='aliyun',
                    message='验证码已发送',
                    expires_in=expires_in,
                )
            return SmsSendResult(
                success=False,
                provider='aliyun',
                message='验证码发送失败',
                expires_in=expires_in,
                error=str(code or 'UNKNOWN_ERROR'),
            )
        except Exception as exc:
            current_app.logger.exception('[Aliyun SMS] send verify code failed')
            return SmsSendResult(
                success=False,
                provider='aliyun',
                message='验证码发送失败',
                expires_in=expires_in,
                error=str(exc),
            )

    code = _generate_code(current_app.config.get('SMS_CODE_LENGTH', 6))
    _sms_store[phone] = {
        'code': code,
        'expires_at': datetime.utcnow() + timedelta(seconds=expires_in),
        'sent_at': datetime.utcnow(),
        'action': action,
    }
    current_app.logger.info(f'[模拟短信] 手机 {phone} 验证码: {code} (场景: {action})')
    return SmsSendResult(
        success=True,
        provider='mock',
        message='验证码已发送',
        expires_in=expires_in,
    )


def verify_code(phone: str, code: str, allowed_actions: tuple[str, ...]) -> SmsVerifyResult:
    if _use_real_provider():
        try:
            from alibabacloud_dypnsapi20170525 import models as dypns_models
            from alibabacloud_tea_util import models as util_models

            client = _get_dypns_client()
            request = dypns_models.CheckSmsVerifyCodeRequest(
                phone_number=phone,
                verify_code=code,
            )
            response = client.check_sms_verify_code_with_options(
                request,
                util_models.RuntimeOptions(),
            )
            verify_result = _get_body_attr(response, 'verify_result')
            code = _get_body_attr(response, 'code')
            request_id = _get_body_attr(response, 'request_id') or _get_body_attr(response, 'requestid')
            current_app.logger.info(
                '[Aliyun SMS] verify result phone=%s verify_result=%s code=%s request_id=%s',
                _mask_phone(phone), verify_result, code, request_id,
            )
            if verify_result == 'PASS':
                return SmsVerifyResult(True, 'aliyun', '验证通过')
            return SmsVerifyResult(False, 'aliyun', '验证码错误')
        except Exception:
            current_app.logger.exception('[Aliyun SMS] verify code failed')
            return SmsVerifyResult(False, 'aliyun', '验证码校验失败')

    record = _sms_store.get(phone)
    if not record or record.get('action') not in allowed_actions:
        return SmsVerifyResult(False, 'mock', '未找到验证码，请先发送')
    if datetime.utcnow() > record['expires_at']:
        _sms_store.pop(phone, None)
        return SmsVerifyResult(False, 'mock', '验证码已过期')
    if record['code'] != code:
        return SmsVerifyResult(False, 'mock', '验证码错误')

    _sms_store.pop(phone, None)
    return SmsVerifyResult(True, 'mock', '验证通过')

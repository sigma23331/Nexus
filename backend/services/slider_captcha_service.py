import secrets
import time
from typing import Any

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


SLIDER_WIDTH = 280
HANDLE_SIZE = 44
MIN_TARGET_X = 72
MAX_TARGET_X = SLIDER_WIDTH - HANDLE_SIZE - 8
VERIFY_TOLERANCE = 8
CHALLENGE_MAX_AGE = 120
VERIFIED_MAX_AGE = 120
MIN_DRAG_DURATION_MS = 300
MAX_DRAG_DURATION_MS = 15000

_used_verified_nonces: dict[str, float] = {}


def _serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config.get("SECRET_KEY") or current_app.config.get("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY must be configured for slider captcha")

    return URLSafeTimedSerializer(
        secret_key,
        salt="slider-captcha",
    )


def _cleanup_used_nonces(now: float | None = None) -> None:
    current = now or time.time()
    expired = [
        nonce
        for nonce, used_at in _used_verified_nonces.items()
        if current - used_at > VERIFIED_MAX_AGE
    ]
    for nonce in expired:
        _used_verified_nonces.pop(nonce, None)


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def create_slider_challenge(phone: str) -> dict[str, Any]:
    target_x = secrets.randbelow(MAX_TARGET_X - MIN_TARGET_X + 1) + MIN_TARGET_X
    payload = {
        "kind": "slider_challenge",
        "nonce": secrets.token_urlsafe(16),
        "phone": phone,
        "targetX": target_x,
        "issuedAt": int(time.time()),
    }

    return {
        "challengeToken": _serializer().dumps(payload),
        "targetX": target_x,
        "sliderWidth": SLIDER_WIDTH,
        "handleSize": HANDLE_SIZE,
        "expiresIn": CHALLENGE_MAX_AGE,
    }


def verify_slider_challenge(
    challenge_token: str,
    phone: str,
    offset_x: Any,
    duration_ms: Any,
    track: list[Any] | None,
) -> tuple[bool, str, str | None]:
    if not challenge_token:
        return False, "滑块验证已失效，请重试", None

    try:
        payload = _serializer().loads(challenge_token, max_age=CHALLENGE_MAX_AGE)
    except SignatureExpired:
        return False, "滑块验证已过期，请重试", None
    except BadSignature:
        return False, "滑块验证无效，请重试", None

    if payload.get("kind") != "slider_challenge" or payload.get("phone") != phone:
        return False, "滑块验证无效，请重试", None

    final_x = _to_float(offset_x)
    target_x = _to_float(payload.get("targetX"))
    drag_duration = _to_float(duration_ms)
    if final_x is None or target_x is None or drag_duration is None:
        return False, "滑块验证数据异常，请重试", None

    if abs(final_x - target_x) > VERIFY_TOLERANCE:
        return False, "滑块位置不正确，请重试", None

    if drag_duration < MIN_DRAG_DURATION_MS or drag_duration > MAX_DRAG_DURATION_MS:
        return False, "请按正常速度拖动滑块", None

    if not track or len(track) < 3:
        return False, "滑块轨迹异常，请重试", None

    verified_payload = {
        "kind": "slider_verified",
        "nonce": secrets.token_urlsafe(16),
        "phone": phone,
        "issuedAt": int(time.time()),
    }
    return True, "验证成功", _serializer().dumps(verified_payload)


def verify_slider_captcha_token(token: str, phone: str) -> tuple[bool, str]:
    if not token:
        return False, "请先完成滑块验证"

    try:
        payload = _serializer().loads(token, max_age=VERIFIED_MAX_AGE)
    except SignatureExpired:
        return False, "滑块验证已过期，请重新验证"
    except BadSignature:
        return False, "滑块验证无效，请重新验证"

    nonce = payload.get("nonce")
    if payload.get("kind") != "slider_verified" or payload.get("phone") != phone or not nonce:
        return False, "滑块验证无效，请重新验证"

    _cleanup_used_nonces()
    if nonce in _used_verified_nonces:
        return False, "滑块验证已使用，请重新验证"

    _used_verified_nonces[nonce] = time.time()
    return True, "验证成功"

import os
import logging
import requests

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
TURNSTILE_SECRET_KEY = os.environ.get("CLOUDFLARE_TURNSTILE_SECRET_KEY")


def verify_turnstile_token(token: str, client_ip: str = None) -> tuple[bool, str]:
    """
    验证 Turnstile token
    
    Args:
        token: 前端传来的 Turnstile token
        client_ip: 客户端 IP（可选，增强安全性）
    
    Returns:
        tuple: (是否验证成功, 错误信息)
    """
    if not TURNSTILE_SECRET_KEY:
        logger.error("TURNSTILE_SECRET_KEY 未配置")
        return False, "Turnstile 配置错误，请联系管理员"

    if not token:
        return False, "人机验证失败，请重试"

    data = {
        "secret": TURNSTILE_SECRET_KEY,
        "response": token,
    }
    if client_ip:
        data["remoteip"] = client_ip

    try:
        response = requests.post(TURNSTILE_VERIFY_URL, data=data, timeout=10)
        result = response.json()
        logger.debug(f"Turnstile 验证结果: {result}")

        if result.get("success"):
            return True, "验证成功"
        else:
            error_codes = result.get("error-codes", [])
            error_msg = ", ".join(error_codes) if error_codes else "人机验证失败，请重试"
            return False, error_msg
    except requests.RequestException as e:
        logger.error(f"Turnstile 验证请求异常: {e}")
        return False, "验证服务异常，请稍后重试"
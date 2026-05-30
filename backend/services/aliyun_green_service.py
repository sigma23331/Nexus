import json
import os
import uuid

from flask import current_app


_green_client = None
_green_client_endpoint = None

DEFAULT_SERVICE_CODE = "comment_detection"
DEFAULT_REGION = "cn-shanghai"


def _green_enabled() -> bool:
    return bool(current_app.config.get("ALIYUN_GREEN_ENABLED", False))


def _import_green_modules():
    """内容安全 2.0（green20220302）SDK 模块，延迟导入避免无依赖环境报错。"""
    from alibabacloud_green20220302.client import Client
    from alibabacloud_green20220302 import models as green_models
    from alibabacloud_tea_openapi.models import Config
    from alibabacloud_tea_util import models as util_models

    return Client, green_models, Config, util_models


def _resolve_credentials():
    access_key = (
        current_app.config.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
        or current_app.config.get("ALIBABA_CLOUD_ACCESS_KEY")
        or os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "")
    )
    secret_key = (
        current_app.config.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        or current_app.config.get("ALIBABA_CLOUD_SECRET_KEY")
        or os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "")
    )
    if not access_key or not secret_key:
        raise ValueError("缺少阿里云 Green 审核凭据配置")
    return access_key, secret_key


def _resolve_region_endpoint():
    region = current_app.config.get("ALIYUN_GREEN_REGION") or DEFAULT_REGION
    endpoint = current_app.config.get("ALIYUN_GREEN_ENDPOINT") or f"green-cip.{region}.aliyuncs.com"
    return region, endpoint


def _service_code():
    return current_app.config.get("ALIYUN_GREEN_SERVICE_CODE") or DEFAULT_SERVICE_CODE


def _timeout_ms():
    seconds = current_app.config.get("ALIYUN_GREEN_TIMEOUT", 3)
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        seconds = 3
    return max(seconds, 1) * 1000


def get_green_client():
    """构建并缓存内容安全 2.0 客户端（按 endpoint 缓存，配置变更后自动重建）。"""
    global _green_client, _green_client_endpoint

    Client, _, Config, _ = _import_green_modules()
    access_key, secret_key = _resolve_credentials()
    region, endpoint = _resolve_region_endpoint()

    if _green_client is not None and _green_client_endpoint == endpoint:
        return _green_client

    connect_timeout = _timeout_ms()
    config = Config(
        access_key_id=access_key,
        access_key_secret=secret_key,
        region_id=region,
        endpoint=endpoint,
        connect_timeout=connect_timeout,
        read_timeout=connect_timeout * 2,
    )
    _green_client = Client(config)
    _green_client_endpoint = endpoint
    return _green_client


def _map_label_to_reason_code(label: str, details=None):
    label_text = str(label or "").lower()
    serialized_details = json.dumps(details or {}, ensure_ascii=False).lower()
    combined = f"{label_text} {serialized_details}"
    if "politic" in combined or "涉政" in combined:
        return "POLITICAL_SENSITIVE"
    if "ad" in combined or "spam" in combined or "广告" in combined:
        return "AD_SPAM"
    if "abuse" in combined or "辱骂" in combined:
        return "ABUSE_LANGUAGE"
    if "porn" in combined or "sex" in combined or "色情" in combined:
        return "SEXUAL_CONTENT"
    if "violen" in combined or "暴恐" in combined or "terror" in combined:
        return "VIOLENCE_RISK"
    if "illegal" in combined or "contraband" in combined or "违禁" in combined:
        return "ILLEGAL_CONTENT"
    return "ALIYUN_GREEN_REVIEW"


def _parse_reason(reason_raw):
    if not reason_raw:
        return {}
    if isinstance(reason_raw, (dict, list)):
        return reason_raw
    try:
        return json.loads(reason_raw)
    except (TypeError, ValueError):
        return {"raw": str(reason_raw)}


def _extract_risk_level(parsed_reason) -> str:
    if isinstance(parsed_reason, dict):
        return str(parsed_reason.get("riskLevel", "")).lower()
    if isinstance(parsed_reason, list):
        levels = [
            str(item.get("riskLevel", "")).lower()
            for item in parsed_reason
            if isinstance(item, dict)
        ]
        if "high" in levels:
            return "high"
        if "medium" in levels:
            return "medium"
        return levels[0] if levels else ""
    return ""


def _suggestion_from(labels, risk_level) -> str:
    """将 2.0 的 labels/riskLevel 归一为上层使用的 pass/review/block 语义。"""
    if not labels:
        return "pass"
    if risk_level == "high":
        return "block"
    return "review"


def normalize_text_moderation(response) -> dict:
    """归一化内容安全 2.0 TextModeration 响应为统一的审核结果结构。"""
    status_code = getattr(response, "status_code", None)
    body = getattr(response, "body", None)
    if status_code is not None and status_code != 200:
        raise RuntimeError(f"aliyun_green_http_status_{status_code}")
    if body is None:
        raise RuntimeError("aliyun_green_empty_body")

    code = getattr(body, "code", None)
    if code != 200:
        message = str(getattr(body, "message", "") or "").strip()
        raise RuntimeError(f"aliyun_green_response_code_{code}: {message}".strip())

    data = getattr(body, "data", None)
    labels_raw = (getattr(data, "labels", None) or "") if data is not None else ""
    reason_raw = getattr(data, "reason", None) if data is not None else None

    labels = [item.strip() for item in str(labels_raw).split(",") if item.strip()]
    parsed_reason = _parse_reason(reason_raw)
    risk_level = _extract_risk_level(parsed_reason)
    suggestion = _suggestion_from(labels, risk_level)

    return {
        "provider_name": "aliyun_green",
        "suggestion": suggestion,
        "label": labels[0] if labels else "",
        "reason_code": _map_label_to_reason_code(",".join(labels), parsed_reason) if labels else None,
        "filtered_text": None,
        "details": parsed_reason,
        "raw": {"code": code, "labels": labels_raw, "reason": reason_raw, "riskLevel": risk_level},
    }


def scan_text(text: str, data_id: str | None = None, scene: str | None = None) -> dict | None:
    """调用内容安全 2.0 文本审核增强版（TextModeration）。

    保留 `scene` 形参以兼容旧调用；2.0 通过 serviceCode 区分场景，
    serviceCode 由 ALIYUN_GREEN_SERVICE_CODE 配置（控制台「文本审核增强版」规则）。
    """
    if not _green_enabled():
        return None

    normalized_text = str(text or "").strip()
    if not normalized_text:
        return None

    _, green_models, _, util_models = _import_green_modules()
    client = get_green_client()

    service_parameters = {
        "content": normalized_text,
        "dataId": data_id or str(uuid.uuid4()),
    }
    request = green_models.TextModerationRequest(
        service=_service_code(),
        service_parameters=json.dumps(service_parameters, ensure_ascii=False),
    )
    runtime = util_models.RuntimeOptions()
    response = client.text_moderation_with_options(request, runtime)
    return normalize_text_moderation(response)

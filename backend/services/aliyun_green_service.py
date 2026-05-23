import json
import uuid

from flask import current_app


_green_client = None


def _green_enabled() -> bool:
    return bool(current_app.config.get("ALIYUN_GREEN_ENABLED", False))


def _import_green_modules():
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.profile import region_provider
    from aliyunsdkgreen.request.v20180509 import TextScanRequest

    return AcsClient, region_provider, TextScanRequest


def _resolve_request_class(text_scan_module):
    if hasattr(text_scan_module, "TextScanRequest"):
        return text_scan_module.TextScanRequest
    return text_scan_module


def get_green_client():
    global _green_client
    if _green_client is not None:
        return _green_client

    AcsClient, region_provider, _ = _import_green_modules()
    access_key = current_app.config.get("ALIBABA_CLOUD_ACCESS_KEY_ID") or current_app.config.get(
        "ALIBABA_CLOUD_ACCESS_KEY"
    )
    secret_key = current_app.config.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET") or current_app.config.get(
        "ALIBABA_CLOUD_SECRET_KEY"
    )
    if not access_key:
        access_key = __import__("os").environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "")
    if not secret_key:
        secret_key = __import__("os").environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "")
    if not access_key or not secret_key:
        raise ValueError("缺少阿里云 Green 审核凭据配置")

    region = current_app.config.get("ALIYUN_GREEN_REGION", "cn-shanghai")
    endpoint = current_app.config.get("ALIYUN_GREEN_ENDPOINT", "green.cn-shanghai.aliyuncs.com")
    region_provider.modify_point("Green", region, endpoint)
    _green_client = AcsClient(access_key, secret_key, region)
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
    if "violence" in combined or "暴恐" in combined:
        return "VIOLENCE_RISK"
    if "illegal" in combined or "违禁" in combined:
        return "ILLEGAL_CONTENT"
    return "ALIYUN_GREEN_REVIEW"


def normalize_green_result(raw: dict) -> dict:
    data = (raw or {}).get("data") or []
    task = data[0] if data else {}
    task_code = task.get("code", 200)
    if task_code != 200:
        raise RuntimeError(f"aliyun_green_task_code_{task_code}")

    results = task.get("results") or []
    result = results[0] if results else {}
    suggestion = str(result.get("suggestion") or "review").lower()
    label = result.get("label") or ""
    filtered_content = result.get("filteredContent")
    details = result.get("details") or []
    return {
        "provider_name": "aliyun_green",
        "suggestion": suggestion,
        "label": label,
        "reason_code": _map_label_to_reason_code(label, details),
        "filtered_text": filtered_content,
        "details": details,
        "raw": raw,
    }


def scan_text(text: str, data_id: str | None = None, scene: str = "antispam") -> dict | None:
    if not _green_enabled():
        return None

    client = get_green_client()
    _, _, text_scan_module = _import_green_modules()
    request_class = _resolve_request_class(text_scan_module)
    request = request_class()
    if hasattr(request, "set_accept_format"):
        request.set_accept_format("JSON")
    if hasattr(request, "set_method"):
        request.set_method("POST")

    payload = {
        "scenes": [scene],
        "tasks": [
            {
                "dataId": data_id or str(uuid.uuid4()),
                "content": text,
            }
        ],
    }
    request.set_content(json.dumps(payload).encode("utf-8"))
    response = client.do_action_with_exception(request)
    if isinstance(response, bytes):
        response = response.decode("utf-8")
    if isinstance(response, str):
        response = json.loads(response)
    return normalize_green_result(response if isinstance(response, dict) else {})

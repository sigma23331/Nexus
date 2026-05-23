import re
from dataclasses import asdict, dataclass, field
from typing import Any

from flask import current_app

from extensions import db
from models import ContentModerationLog
from services import aliyun_green_service


ACTION_PASS = "pass"
ACTION_REVIEW = "review"
ACTION_REJECT = "reject"
ACTION_FALLBACK = "fallback"

SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"

USER_PUBLIC_REVIEW_SCENES = {
    "plaza_card_content",
    "plaza_card_tags",
    "plaza_comment_content",
    "comment_report_reason",
}
USER_REVIEW_ALLOWED_SCENES = {"plaza_comment_content"}
FAIL_CLOSED_REVIEW_SCENES = {"plaza_comment_content"}

_RULES = [
    {
        "label": "abuse",
        "severity": SEVERITY_MEDIUM,
        "action": ACTION_REVIEW,
        "reason_code": "ABUSE_LANGUAGE",
        "patterns": [r"傻[逼比]", r"妈[的逼比]", r"滚出去", r"废物", r"脑残"],
    },
    {
        "label": "sexual",
        "severity": SEVERITY_HIGH,
        "action": ACTION_REJECT,
        "reason_code": "SEXUAL_CONTENT",
        "patterns": [r"色情网", r"约炮", r"裸聊", r"成人视频", r"援交"],
    },
    {
        "label": "violence",
        "severity": SEVERITY_HIGH,
        "action": ACTION_REJECT,
        "reason_code": "VIOLENCE_RISK",
        "patterns": [r"砍死", r"炸弹", r"杀了?你", r"屠杀", r"恐袭"],
    },
    {
        "label": "illegal",
        "severity": SEVERITY_HIGH,
        "action": ACTION_REJECT,
        "reason_code": "ILLEGAL_CONTENT",
        "patterns": [r"代开发票", r"办证", r"赌博", r"洗钱", r"毒品", r"走私"],
    },
    {
        "label": "ad",
        "severity": SEVERITY_HIGH,
        "action": ACTION_REJECT,
        "reason_code": "AD_SPAM",
        "patterns": [
            r"加[vV微薇威]",
            r"vx[:：]?\w+",
            r"qq群",
            r"私聊领",
            r"https?://",
            r"\b1[3-9]\d{9}\b",
        ],
    },
    {
        "label": "self_harm",
        "severity": SEVERITY_HIGH,
        "action": ACTION_REJECT,
        "reason_code": "SELF_HARM_RISK",
        "patterns": [r"自杀", r"轻生", r"割腕", r"结束生命", r"怎么死"],
    },
    {
        "label": "politics",
        "severity": SEVERITY_HIGH,
        "action": ACTION_REJECT,
        "reason_code": "POLITICAL_SENSITIVE",
        "patterns": [
            r"六四",
            r"法轮功",
            r"台独",
            r"疆独",
            r"港独",
            r"颠覆国家政权",
            r"中共[下倒]",
            r"习近平",
        ],
    },
]


@dataclass
class ReviewResult:
    action: str
    labels: list[str] = field(default_factory=list)
    reason_code: str | None = None
    severity: str = SEVERITY_LOW
    processed_text: str | None = None
    provider_name: str = "builtin"
    provider_result: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def _mask_text(text: str, rules: list[dict[str, Any]]) -> str:
    masked = text
    for rule in rules:
        for pattern in rule["hit_patterns"]:
            masked = re.sub(pattern, "***", masked, flags=re.IGNORECASE)
    return masked


def _clone_result(result: "ReviewResult", **overrides):
    payload = result.to_dict()
    payload.update(overrides)
    return ReviewResult(**payload)


def _merge_actions(results: list[dict[str, Any]], is_ai_output: bool, scene: str) -> str:
    if not results:
        return ACTION_PASS
    if any(item["action"] == ACTION_REJECT for item in results):
        return ACTION_REJECT if not is_ai_output else ACTION_FALLBACK
    if any(item["action"] == ACTION_REVIEW for item in results):
        if scene in USER_PUBLIC_REVIEW_SCENES and not is_ai_output:
            return ACTION_REVIEW
        return ACTION_REJECT if not is_ai_output else ACTION_FALLBACK
    return ACTION_PASS


def _merge_severity(results: list[dict[str, Any]]) -> str:
    if any(item["severity"] == SEVERITY_HIGH for item in results):
        return SEVERITY_HIGH
    if any(item["severity"] == SEVERITY_MEDIUM for item in results):
        return SEVERITY_MEDIUM
    return SEVERITY_LOW


def _evaluate_rules(text: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for rule in _RULES:
        hit_patterns = [pattern for pattern in rule["patterns"] if re.search(pattern, text, re.IGNORECASE)]
        if hit_patterns:
            matches.append(
                {
                    "label": rule["label"],
                    "severity": rule["severity"],
                    "action": rule["action"],
                    "reason_code": rule["reason_code"],
                    "hit_patterns": hit_patterns,
                }
            )
    return matches


def _persist_log(scene: str, text: str, result: ReviewResult, user_id=None, target_type=None, target_id=None):
    try:
        record = ContentModerationLog(
            scene=scene,
            target_type=target_type or "unknown",
            target_id=target_id,
            user_id=user_id,
            original_text=text,
            processed_text=result.processed_text,
            action=result.action,
            severity=result.severity,
            labels=result.labels,
            reason_code=result.reason_code,
            provider_name=result.provider_name,
            provider_result=result.provider_result,
        )
        db.session.add(record)
        db.session.flush()
        return record
    except Exception:
        return None


def _provider_enabled():
    try:
        return bool(current_app.config.get("ALIYUN_GREEN_ENABLED", False))
    except RuntimeError:
        return False


def _provider_fail_open():
    try:
        return bool(current_app.config.get("ALIYUN_GREEN_FAIL_OPEN", False))
    except RuntimeError:
        return False


def _build_local_result(scene: str, normalized: str, matches: list[dict[str, Any]], is_ai_output: bool):
    return ReviewResult(
        action=_merge_actions(matches, is_ai_output=is_ai_output, scene=scene),
        labels=[item["label"] for item in matches],
        reason_code=matches[0]["reason_code"] if matches else None,
        severity=_merge_severity(matches),
        processed_text=_mask_text(normalized, matches) if matches else normalized,
        provider_name="builtin",
        provider_result={"rule_hits": matches},
    )


def _provider_action_for_scene(suggestion: str, scene: str, is_ai_output: bool):
    suggestion = str(suggestion or "review").lower()
    if suggestion == ACTION_PASS:
        return ACTION_PASS
    if is_ai_output:
        return ACTION_FALLBACK
    if suggestion == ACTION_REVIEW and scene in USER_REVIEW_ALLOWED_SCENES:
        return ACTION_REVIEW
    return ACTION_REJECT


def _severity_for_provider_suggestion(suggestion: str):
    if suggestion == ACTION_PASS:
        return SEVERITY_LOW
    if suggestion == ACTION_REVIEW:
        return SEVERITY_MEDIUM
    return SEVERITY_HIGH


def _merge_results(local_result: ReviewResult, provider_result: dict | None, scene: str, is_ai_output: bool):
    if not provider_result:
        return local_result

    provider_action = _provider_action_for_scene(provider_result.get("suggestion"), scene, is_ai_output)
    labels = list(local_result.labels)
    provider_label = provider_result.get("label")
    if provider_label:
        labels = list(dict.fromkeys(labels + [provider_label]))
    reason_code = provider_result.get("reason_code") or local_result.reason_code
    severity = local_result.severity
    provider_severity = _severity_for_provider_suggestion(provider_result.get("suggestion"))
    if provider_severity == SEVERITY_HIGH or severity == SEVERITY_HIGH:
        severity = SEVERITY_HIGH
    elif provider_severity == SEVERITY_MEDIUM or severity == SEVERITY_MEDIUM:
        severity = SEVERITY_MEDIUM

    action_priority = {
        ACTION_PASS: 0,
        ACTION_REVIEW: 1,
        ACTION_REJECT: 2,
        ACTION_FALLBACK: 2,
    }
    final_action = local_result.action
    if action_priority.get(provider_action, 0) > action_priority.get(local_result.action, 0):
        final_action = provider_action
    if is_ai_output and final_action == ACTION_REJECT:
        final_action = ACTION_FALLBACK

    processed_text = provider_result.get("filtered_text") or local_result.processed_text
    merged_provider_result = dict(local_result.provider_result)
    merged_provider_result["aliyun_green"] = provider_result
    return ReviewResult(
        action=final_action,
        labels=labels,
        reason_code=reason_code,
        severity=severity,
        processed_text=processed_text,
        provider_name="aliyun_green",
        provider_result=merged_provider_result,
    )


def _failure_result(local_result: ReviewResult, scene: str, is_ai_output: bool, error_text: str):
    if _provider_fail_open():
        merged = dict(local_result.provider_result)
        merged["aliyun_green_error"] = error_text
        return _clone_result(local_result, provider_result=merged)

    fallback_action = ACTION_FALLBACK if is_ai_output else ACTION_REJECT
    if not is_ai_output and scene in FAIL_CLOSED_REVIEW_SCENES:
        fallback_action = ACTION_REVIEW

    merged = dict(local_result.provider_result)
    merged["aliyun_green_error"] = error_text
    return ReviewResult(
        action=fallback_action,
        labels=list(dict.fromkeys(local_result.labels + ["aliyun_green_error"])),
        reason_code=local_result.reason_code or "ALIYUN_GREEN_UNAVAILABLE",
        severity=max(local_result.severity, SEVERITY_MEDIUM, key={SEVERITY_LOW: 0, SEVERITY_MEDIUM: 1, SEVERITY_HIGH: 2}.get),
        processed_text=local_result.processed_text,
        provider_name="aliyun_green",
        provider_result=merged,
    )


def _review_text(scene: str, text: str, user_id=None, target_type=None, target_id=None, is_ai_output=False):
    normalized = str(text or "").strip()
    matches = _evaluate_rules(normalized)
    result = _build_local_result(scene=scene, normalized=normalized, matches=matches, is_ai_output=is_ai_output)
    if _provider_enabled() and normalized:
        try:
            provider_result = aliyun_green_service.scan_text(
                text=normalized,
                data_id=target_id or None,
                scene="antispam",
            )
            result = _merge_results(result, provider_result, scene=scene, is_ai_output=is_ai_output)
        except Exception as exc:
            result = _failure_result(result, scene=scene, is_ai_output=is_ai_output, error_text=str(exc))
    _persist_log(
        scene=scene,
        text=normalized,
        result=result,
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
    )
    return result


def review_user_generated_text(scene: str, text: str, user_id=None, target_type=None, target_id=None):
    return _review_text(
        scene=scene,
        text=text,
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        is_ai_output=False,
    )


def review_ai_generated_text(scene: str, text: str, user_id=None, target_type=None, target_id=None):
    return _review_text(
        scene=scene,
        text=text,
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        is_ai_output=True,
    )


def is_content_safe(text: str):
    result = review_user_generated_text(scene="legacy", text=text, target_type="legacy")
    return result.action == ACTION_PASS, result.processed_text or ""

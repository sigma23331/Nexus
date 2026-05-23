from services import content_review_service
from flask import Flask


def _build_app(**config):
    app = Flask(__name__)
    app.config.update(config)
    return app


def test_is_content_safe_returns_true_for_clean_text():
    passed, processed = content_review_service.is_content_safe("今天状态不错，继续加油")

    assert passed is True
    assert processed == "今天状态不错，继续加油"


def test_is_content_safe_masks_blocked_patterns_case_insensitive():
    passed, processed = content_review_service.is_content_safe("你这人真傻逼，别骂妈的")

    assert passed is False
    assert "傻逼" not in processed
    assert "妈的" not in processed
    assert processed.count("***") >= 2


def test_review_user_generated_text_uses_aliyun_pass(monkeypatch):
    app = _build_app(ALIYUN_GREEN_ENABLED=True, ALIYUN_GREEN_FAIL_OPEN=False)

    with app.app_context():
        monkeypatch.setattr(
            content_review_service.aliyun_green_service,
            "scan_text",
            lambda **_: {
                "provider_name": "aliyun_green",
                "suggestion": "pass",
                "label": "",
                "reason_code": None,
                "filtered_text": None,
                "details": [],
                "raw": {},
            },
        )
        result = content_review_service.review_user_generated_text("answer_question_input", "今天状态不错")

    assert result.action == content_review_service.ACTION_PASS
    assert result.provider_name == "aliyun_green"


def test_review_user_generated_text_maps_aliyun_politics_to_reject(monkeypatch):
    app = _build_app(ALIYUN_GREEN_ENABLED=True, ALIYUN_GREEN_FAIL_OPEN=False)

    with app.app_context():
        monkeypatch.setattr(
            content_review_service.aliyun_green_service,
            "scan_text",
            lambda **_: {
                "provider_name": "aliyun_green",
                "suggestion": "block",
                "label": "politics",
                "reason_code": "POLITICAL_SENSITIVE",
                "filtered_text": "***",
                "details": [],
                "raw": {},
            },
        )
        result = content_review_service.review_user_generated_text("answer_question_input", "某些敏感内容")

    assert result.action == content_review_service.ACTION_REJECT
    assert result.reason_code == "POLITICAL_SENSITIVE"


def test_review_comment_maps_aliyun_review_to_pending_review_action(monkeypatch):
    app = _build_app(ALIYUN_GREEN_ENABLED=True, ALIYUN_GREEN_FAIL_OPEN=False)

    with app.app_context():
        monkeypatch.setattr(
            content_review_service.aliyun_green_service,
            "scan_text",
            lambda **_: {
                "provider_name": "aliyun_green",
                "suggestion": "review",
                "label": "politics",
                "reason_code": "POLITICAL_SENSITIVE",
                "filtered_text": None,
                "details": [],
                "raw": {},
            },
        )
        result = content_review_service.review_user_generated_text("plaza_comment_content", "灰区评论")

    assert result.action == content_review_service.ACTION_REVIEW


def test_review_ai_generated_text_fails_closed_to_fallback(monkeypatch):
    app = _build_app(ALIYUN_GREEN_ENABLED=True, ALIYUN_GREEN_FAIL_OPEN=False)

    with app.app_context():
        monkeypatch.setattr(
            content_review_service.aliyun_green_service,
            "scan_text",
            lambda **_: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        result = content_review_service.review_ai_generated_text("answer_output", "AI 回复")

    assert result.action == content_review_service.ACTION_FALLBACK

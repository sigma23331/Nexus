import os
import types

from flask import Flask

from services import aliyun_green_service


def _build_app(**config):
    app = Flask(__name__)
    app.config.update(config)
    return app


def setup_function():
    aliyun_green_service._green_client = None
    aliyun_green_service._green_client_endpoint = None


class _FakeData:
    def __init__(self, labels, reason):
        self.labels = labels
        self.reason = reason


class _FakeBody:
    def __init__(self, code, message="", labels="", reason=None):
        self.code = code
        self.message = message
        self.data = _FakeData(labels, reason)


class _FakeResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body


def _install_fake_client(response):
    class _FakeClient:
        def text_moderation_with_options(self, request, runtime):
            self.last_request = request
            return response

    fake = _FakeClient()
    aliyun_green_service.get_green_client = lambda: fake
    return fake


def test_scan_text_pass_when_no_labels(monkeypatch):
    monkeypatch.setattr(aliyun_green_service, "get_green_client", lambda: None, raising=False)
    fake = _install_fake_client(_FakeResponse(200, _FakeBody(code=200, labels="", reason=None)))

    app = _build_app(ALIYUN_GREEN_ENABLED=True, ALIYUN_GREEN_SERVICE_CODE="comment_detection")
    with app.app_context():
        result = aliyun_green_service.scan_text("今天天气不错", data_id="d1")

    assert result["suggestion"] == "pass"
    assert result["reason_code"] is None
    assert fake.last_request.service == "comment_detection"


def test_scan_text_block_on_high_risk_label(monkeypatch):
    monkeypatch.setattr(aliyun_green_service, "get_green_client", lambda: None, raising=False)
    _install_fake_client(
        _FakeResponse(
            200,
            _FakeBody(
                code=200,
                labels="political_content",
                reason='{"riskLevel":"high","riskTips":"涉政"}',
            ),
        )
    )

    app = _build_app(ALIYUN_GREEN_ENABLED=True)
    with app.app_context():
        result = aliyun_green_service.scan_text("敏感内容", data_id="d2")

    assert result["suggestion"] == "block"
    assert result["reason_code"] == "POLITICAL_SENSITIVE"


def test_scan_text_review_on_low_risk_label(monkeypatch):
    monkeypatch.setattr(aliyun_green_service, "get_green_client", lambda: None, raising=False)
    _install_fake_client(
        _FakeResponse(
            200,
            _FakeBody(code=200, labels="ad", reason='{"riskLevel":"low"}'),
        )
    )

    app = _build_app(ALIYUN_GREEN_ENABLED=True)
    with app.app_context():
        result = aliyun_green_service.scan_text("加微信领福利", data_id="d3")

    assert result["suggestion"] == "review"
    assert result["reason_code"] == "AD_SPAM"


def test_scan_text_disabled_returns_none():
    app = _build_app(ALIYUN_GREEN_ENABLED=False)
    with app.app_context():
        assert aliyun_green_service.scan_text("任意内容") is None


def test_normalize_raises_on_non_200_body():
    body = _FakeBody(code=596, message="You have not opened ... service")
    response = _FakeResponse(200, body)
    try:
        aliyun_green_service.normalize_text_moderation(response)
        assert False, "should raise"
    except RuntimeError as err:
        assert "596" in str(err)

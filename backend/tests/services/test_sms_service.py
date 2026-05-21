from datetime import datetime, timedelta

from flask import Flask

from services import sms_service


def _build_app():
    app = Flask(__name__)
    app.config["SMS_PROVIDER"] = "mock"
    app.config["SMS_CODE_LENGTH"] = 6
    app.config["SMS_SEND_INTERVAL"] = 60
    return app


def setup_function():
    sms_service._sms_store.clear()


def test_mask_phone_hides_middle_digits():
    assert sms_service._mask_phone("13800138000") == "138****8000"


def test_can_send_respects_interval():
    phone = "13800138000"
    sms_service._sms_store[phone] = {
        "sent_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "code": "123456",
        "action": "login",
    }

    assert sms_service.can_send(phone, interval_seconds=60) is False


def test_send_verify_code_mock_provider_stores_code(monkeypatch):
    app = _build_app()
    monkeypatch.setattr(sms_service, "_generate_code", lambda *_: "654321")

    with app.app_context():
        result = sms_service.send_verify_code("13800138000", "login", expires_in=120)

    assert result.success is True
    assert result.provider == "mock"
    assert sms_service._sms_store["13800138000"]["code"] == "654321"


def test_verify_code_success_and_remove_record():
    app = _build_app()
    phone = "13800138000"
    sms_service._sms_store[phone] = {
        "code": "123456",
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "sent_at": datetime.utcnow(),
        "action": "login",
    }

    with app.app_context():
        result = sms_service.verify_code(phone, "123456", ("login",))

    assert result.success is True
    assert phone not in sms_service._sms_store


def test_verify_code_expired_returns_false_and_cleanup():
    app = _build_app()
    phone = "13800138000"
    sms_service._sms_store[phone] = {
        "code": "123456",
        "expires_at": datetime.utcnow() - timedelta(seconds=1),
        "sent_at": datetime.utcnow() - timedelta(minutes=2),
        "action": "login",
    }

    with app.app_context():
        result = sms_service.verify_code(phone, "123456", ("login",))

    assert result.success is False
    assert result.message == "验证码已过期"
    assert phone not in sms_service._sms_store

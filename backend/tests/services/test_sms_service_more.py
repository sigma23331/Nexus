import sys
import types
from datetime import datetime, timedelta

from flask import Flask

from services import sms_service


def _build_app(provider="mock"):
    app = Flask(__name__)
    app.config["SMS_PROVIDER"] = provider
    app.config["SMS_CODE_LENGTH"] = 6
    app.config["SMS_SEND_INTERVAL"] = 60
    app.config["SMS_SIGN_NAME"] = "test-sign"
    app.config["SMS_TEMPLATE_CODE"] = "SMS_001"
    app.config["DYPNS_API_ENDPOINT"] = "mock.endpoint"
    return app


def setup_function():
    sms_service._sms_store.clear()
    sms_service._dypns_client = None


def _install_fake_aliyun_modules():
    cred_client_mod = types.ModuleType("alibabacloud_credentials.client")

    class CredentialClient:
        pass

    cred_client_mod.Client = CredentialClient

    dypns_client_mod = types.ModuleType("alibabacloud_dypnsapi20170525.client")

    class DypnsClient:
        def __init__(self, config):
            self.config = config

    dypns_client_mod.Client = DypnsClient

    openapi_models_mod = types.ModuleType("alibabacloud_tea_openapi.models")

    class Config:
        def __init__(self, credential):
            self.credential = credential
            self.endpoint = None

    openapi_models_mod.Config = Config

    dypns_models_mod = types.ModuleType("alibabacloud_dypnsapi20170525.models")

    class SendSmsVerifyCodeRequest:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class CheckSmsVerifyCodeRequest:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    dypns_models_mod.SendSmsVerifyCodeRequest = SendSmsVerifyCodeRequest
    dypns_models_mod.CheckSmsVerifyCodeRequest = CheckSmsVerifyCodeRequest

    tea_util_models_mod = types.ModuleType("alibabacloud_tea_util.models")

    class RuntimeOptions:
        pass

    tea_util_models_mod.RuntimeOptions = RuntimeOptions

    dypns_pkg = types.ModuleType("alibabacloud_dypnsapi20170525")
    dypns_pkg.models = dypns_models_mod

    tea_util_pkg = types.ModuleType("alibabacloud_tea_util")
    tea_util_pkg.models = tea_util_models_mod

    sys.modules["alibabacloud_credentials.client"] = cred_client_mod
    sys.modules["alibabacloud_dypnsapi20170525.client"] = dypns_client_mod
    sys.modules["alibabacloud_tea_openapi.models"] = openapi_models_mod
    sys.modules["alibabacloud_dypnsapi20170525"] = dypns_pkg
    sys.modules["alibabacloud_dypnsapi20170525.models"] = dypns_models_mod
    sys.modules["alibabacloud_tea_util"] = tea_util_pkg
    sys.modules["alibabacloud_tea_util.models"] = tea_util_models_mod


def test_get_body_attr_supports_body_model_and_response_dict_fallback():
    model = types.SimpleNamespace(VerifyResult="PASS")
    response = types.SimpleNamespace(body={"model": model})

    assert sms_service._get_body_attr(response, "verify_result") == "PASS"
    assert sms_service._get_body_attr({"requestId": "r1"}, "request_id") == "r1"
    assert sms_service._get_body_attr({}, "missing", default="x") == "x"


def test_get_dypns_client_builds_and_caches_client():
    app = _build_app(provider="aliyun")
    _install_fake_aliyun_modules()

    with app.app_context():
        c1 = sms_service._get_dypns_client()
        c2 = sms_service._get_dypns_client()

    assert c1 is c2
    assert c1.config.endpoint == "mock.endpoint"


def test_send_verify_code_real_provider_success_and_failure(monkeypatch):
    app = _build_app(provider="aliyun")
    _install_fake_aliyun_modules()

    class FakeClient:
        def __init__(self, success=True):
            self.success = success

        def send_sms_verify_code_with_options(self, _req, _runtime):
            if self.success:
                return {"body": {"code": "OK", "success": True, "requestId": "rid-1"}}
            return {"body": {"code": "NO", "success": False, "requestId": "rid-2"}}

    with app.app_context():
        monkeypatch.setattr(sms_service, "_get_dypns_client", lambda: FakeClient(True))
        ok = sms_service.send_verify_code("13800138000", "login", expires_in=90)
        assert ok.success is True
        assert ok.provider == "aliyun"

        monkeypatch.setattr(sms_service, "_get_dypns_client", lambda: FakeClient(False))
        bad = sms_service.send_verify_code("13800138000", "login", expires_in=90)
        assert bad.success is False
        assert bad.error == "NO"


def test_send_verify_code_real_provider_exception(monkeypatch):
    app = _build_app(provider="aliyun")
    _install_fake_aliyun_modules()

    class FakeClient:
        def send_sms_verify_code_with_options(self, _req, _runtime):
            raise RuntimeError("network")

    with app.app_context():
        monkeypatch.setattr(sms_service, "_get_dypns_client", lambda: FakeClient())
        out = sms_service.send_verify_code("13800138000", "login")

    assert out.success is False
    assert out.provider == "aliyun"
    assert "network" in out.error


def test_verify_code_real_provider_pass_fail_and_exception(monkeypatch):
    app = _build_app(provider="aliyun")
    _install_fake_aliyun_modules()

    class FakeClient:
        def __init__(self, mode):
            self.mode = mode

        def check_sms_verify_code_with_options(self, _req, _runtime):
            if self.mode == "pass":
                return {"body": {"verifyResult": "PASS", "code": "OK"}}
            if self.mode == "fail":
                return {"body": {"verifyResult": "REJECT", "code": "NO"}}
            raise RuntimeError("boom")

    with app.app_context():
        monkeypatch.setattr(sms_service, "_get_dypns_client", lambda: FakeClient("pass"))
        assert sms_service.verify_code("13800138000", "123456", ("login",)).success is True

        monkeypatch.setattr(sms_service, "_get_dypns_client", lambda: FakeClient("fail"))
        assert sms_service.verify_code("13800138000", "123456", ("login",)).success is False

        monkeypatch.setattr(sms_service, "_get_dypns_client", lambda: FakeClient("err"))
        out = sms_service.verify_code("13800138000", "123456", ("login",))
        assert out.success is False
        assert out.message == "验证码校验失败"


def test_verify_code_mock_branch_not_found_and_wrong_code():
    app = _build_app(provider="mock")

    with app.app_context():
        missing = sms_service.verify_code("13800138000", "123456", ("login",))
        assert missing.success is False

    phone = "13800138000"
    sms_service._sms_store[phone] = {
        "code": "654321",
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "sent_at": datetime.utcnow(),
        "action": "bind",
    }

    with app.app_context():
        action_bad = sms_service.verify_code(phone, "654321", ("login",))
        assert action_bad.success is False

    sms_service._sms_store[phone] = {
        "code": "654321",
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "sent_at": datetime.utcnow(),
        "action": "login",
    }
    with app.app_context():
        code_bad = sms_service.verify_code(phone, "000000", ("login",))
        assert code_bad.success is False
        assert code_bad.message == "验证码错误"

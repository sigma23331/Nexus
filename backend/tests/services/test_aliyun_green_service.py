import json
import sys
import types

from flask import Flask

from services import aliyun_green_service


def _build_app(**config):
    app = Flask(__name__)
    app.config.update(config)
    return app


def setup_function():
    aliyun_green_service._green_client = None


def _install_fake_green_modules():
    core_client_mod = types.ModuleType("aliyunsdkcore.client")

    class AcsClient:
        def __init__(self, access_key, secret_key, region):
            self.access_key = access_key
            self.secret_key = secret_key
            self.region = region

        def do_action_with_exception(self, request):
            payload = json.loads(request.content.decode("utf-8"))
            return json.dumps(
                {
                    "code": 200,
                    "data": [
                        {
                            "code": 200,
                            "results": [
                                {
                                    "suggestion": "block" if "敏感" in payload["tasks"][0]["content"] else "pass",
                                    "label": "politics" if "敏感" in payload["tasks"][0]["content"] else "",
                                    "filteredContent": "***" if "敏感" in payload["tasks"][0]["content"] else None,
                                    "details": [],
                                }
                            ],
                        }
                    ],
                }
            ).encode("utf-8")

    core_client_mod.AcsClient = AcsClient

    profile_mod = types.ModuleType("aliyunsdkcore.profile")

    class RegionProvider:
        @staticmethod
        def modify_point(_product, _region, _endpoint):
            return None

    profile_mod.region_provider = RegionProvider

    request_mod = types.ModuleType("aliyunsdkgreen.request.v20180509.TextScanRequest")

    class TextScanRequest:
        def set_accept_format(self, value):
            self.accept_format = value

        def set_method(self, value):
            self.method = value

        def set_content(self, value):
            self.content = value

    request_mod.TextScanRequest = TextScanRequest

    green_pkg = types.ModuleType("aliyunsdkgreen")
    green_request_pkg = types.ModuleType("aliyunsdkgreen.request")
    green_v_pkg = types.ModuleType("aliyunsdkgreen.request.v20180509")
    green_v_pkg.TextScanRequest = request_mod

    sys.modules["aliyunsdkcore.client"] = core_client_mod
    sys.modules["aliyunsdkcore.profile"] = profile_mod
    sys.modules["aliyunsdkgreen"] = green_pkg
    sys.modules["aliyunsdkgreen.request"] = green_request_pkg
    sys.modules["aliyunsdkgreen.request.v20180509"] = green_v_pkg
    sys.modules["aliyunsdkgreen.request.v20180509.TextScanRequest"] = request_mod


def test_scan_text_returns_normalized_result():
    _install_fake_green_modules()
    app = _build_app(
        ALIYUN_GREEN_ENABLED=True,
        ALIYUN_GREEN_REGION="cn-shanghai",
        ALIYUN_GREEN_ENDPOINT="green.cn-shanghai.aliyuncs.com",
    )

    with app.app_context():
        import os

        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"] = "ak"
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"] = "sk"
        result = aliyun_green_service.scan_text("政治敏感内容", data_id="d1")

    assert result["suggestion"] == "block"
    assert result["reason_code"] == "POLITICAL_SENSITIVE"


def test_normalize_green_result_maps_ad_label():
    raw = {
        "data": [
            {
                "code": 200,
                "results": [
                    {
                        "suggestion": "review",
                        "label": "ad",
                        "filteredContent": None,
                        "details": [],
                    }
                ],
            }
        ]
    }

    result = aliyun_green_service.normalize_green_result(raw)

    assert result["reason_code"] == "AD_SPAM"

from datetime import datetime, timedelta

import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

import routes.answer_route as answer_route_module
import routes.auth_route as auth_route_module
import routes.diary_route as diary_route_module
import routes.plaza_route as plaza_route_module
from routes.answer_route import answer_bp
from routes.auth_route import auth_bp
from routes.diary_route import diary_bp
from routes.plaza_route import plaza_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix="/v1/auth")
    app.register_blueprint(answer_bp, url_prefix="/v1/answer")
    app.register_blueprint(diary_bp, url_prefix="/v1/diary")
    app.register_blueprint(plaza_bp, url_prefix="/v1/plaza")
    return app


@pytest.fixture(autouse=True)
def clear_sms_store():
    auth_route_module.sms_service._sms_store.clear()


@pytest.mark.parametrize(
    ("length", "expected_status"),
    [
        (200, 200),
        (201, 400),
    ],
)
def test_answer_ask_question_length_boundary(client, auth_header, monkeypatch, length, expected_status):
    monkeypatch.setattr(answer_route_module.answer_service, "ask_question", lambda **_: {"id": "a1"})
    monkeypatch.setattr(answer_route_module.UserProfileService, "update_profile_by_behavior", lambda **_: None)

    response = client.post(
        "/v1/answer/ask",
        json={"question": "q" * length},
        headers=auth_header,
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("limit", "expected_status"),
    [
        (1, 200),
        (20, 200),
        (0, 400),
        (21, 400),
    ],
)
def test_plaza_cards_limit_boundary(client, auth_header, monkeypatch, limit, expected_status):
    def _fake_list_cards(user_id, tab, cursor, limit):
        _ = (user_id, tab, cursor)
        if limit < 1 or limit > 20:
            raise ValueError("limit 范围 1-20")
        return {"list": [], "nextCursor": None, "hasMore": False}

    monkeypatch.setattr(plaza_route_module.plaza_service, "list_cards", _fake_list_cards)

    response = client.get(f"/v1/plaza/cards?tab=latest&limit={limit}", headers=auth_header)

    assert response.status_code == expected_status


def test_auth_sms_send_rate_limit_boundary(client, monkeypatch):
    class _QueryStub:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return None

    fake_user_model = type("FakeUser", (), {"query": _QueryStub()})
    monkeypatch.setattr(auth_route_module, "User", fake_user_model)
    monkeypatch.setattr(auth_route_module.sms_service, "_generate_code", lambda *_: "123456")

    first = client.post("/v1/auth/sms/send", json={"phone": "13800138000"})
    second = client.post("/v1/auth/sms/send", json={"phone": "13800138000"})

    assert first.status_code == 200
    assert second.status_code == 429


def test_auth_sms_login_expired_code_boundary(client):
    phone = "13800138000"
    auth_route_module.sms_service._sms_store[phone] = {
        "code": "123456",
        "expires_at": datetime.utcnow() - timedelta(seconds=1),
        "sent_at": datetime.utcnow() - timedelta(seconds=1),
        "action": "login",
    }

    response = client.post("/v1/auth/sms/login", json={"phone": phone, "code": "123456"})

    assert response.status_code == 400
    assert response.get_json()["message"] == "验证码已过期"


def test_diary_timeline_page_limit_boundaries(client, auth_header, monkeypatch):
    monkeypatch.setattr(diary_route_module.diary_service, "list_timeline", lambda **_: {"list": [], "totalDays": 0})

    ok = client.get("/v1/diary/timeline?page=1&limit=50", headers=auth_header)
    bad = client.get("/v1/diary/timeline?page=0&limit=51", headers=auth_header)

    assert ok.status_code == 200
    assert bad.status_code == 400

import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

import routes.fortune_route as route_module
from routes.fortune_route import fortune_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(fortune_bp, url_prefix="/v1/fortune")
    return app


def test_today_fortune_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.fortune_service, "get_today_fortune", lambda **_: {"score": 90})
    monkeypatch.setattr(route_module.UserProfileService, "update_profile_by_behavior", lambda **_: None)

    response = client.get("/v1/fortune/today", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["score"] == 90


def test_fortune_trend_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.fortune_service, "get_trend", lambda **_: {"points": []})

    response = client.get("/v1/fortune/trend", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["code"] == 200


def test_global_stats_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.fortune_service, "get_global_stats", lambda: {"users": 10})

    response = client.get("/v1/fortune/stats/global", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["users"] == 10


def test_create_fortune_pk_success(client, auth_header, monkeypatch):
    def fake_create_pk(user_id):
        assert user_id == "u-test"
        return {"token": "token-1", "pk": {"status": "pending"}}

    monkeypatch.setattr(route_module.fortune_pk_service, "create_pk", fake_create_pk)

    response = client.post("/v1/fortune/pk", headers=auth_header)

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["token"] == "token-1"
    assert body["data"]["pk"]["status"] == "pending"


def test_get_fortune_pk_allows_anonymous_view(client, monkeypatch):
    def fake_get_or_join_pk(token, current_user_id=None):
        assert token == "token-1"
        assert current_user_id is None
        return {"token": token, "status": "completed"}

    monkeypatch.setattr(route_module.fortune_pk_service, "get_or_join_pk", fake_get_or_join_pk)

    response = client.get("/v1/fortune/pk?token=token-1")

    assert response.status_code == 200
    assert response.get_json()["data"]["status"] == "completed"


def test_get_fortune_pk_auto_joins_when_authenticated(client, auth_header, monkeypatch):
    def fake_get_or_join_pk(token, current_user_id=None):
        assert token == "token-1"
        assert current_user_id == "u-test"
        return {
            "token": token,
            "status": "completed",
            "defenderId": "u-test",
            "result": "defender_win",
        }

    monkeypatch.setattr(route_module.fortune_pk_service, "get_or_join_pk", fake_get_or_join_pk)

    response = client.get("/v1/fortune/pk?token=token-1", headers=auth_header)

    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["defenderId"] == "u-test"
    assert body["data"]["result"] == "defender_win"


def test_get_fortune_pk_returns_410_when_expired(client, monkeypatch):
    def fake_get_or_join_pk(token, current_user_id=None):
        _ = (token, current_user_id)
        raise PermissionError("PK link expired")

    monkeypatch.setattr(route_module.fortune_pk_service, "get_or_join_pk", fake_get_or_join_pk)

    response = client.get("/v1/fortune/pk?token=expired")

    assert response.status_code == 410
    assert response.get_json()["message"] == "PK link expired"

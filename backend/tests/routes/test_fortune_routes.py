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

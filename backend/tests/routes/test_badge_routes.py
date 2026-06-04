import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

import routes.badge_route as route_module
from routes.badge_route import badge_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(badge_bp, url_prefix="/v1/badge")
    return app


def test_get_badge_definitions_is_public(client, monkeypatch):
    monkeypatch.setattr(
        route_module.badge_service,
        "list_definitions",
        lambda: {"list": [{"code": "share_station", "levels": []}]},
    )

    response = client.get("/v1/badge/definitions")

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["list"][0]["code"] == "share_station"


def test_get_my_badges_uses_authenticated_user(client, auth_header, monkeypatch):
    def fake_list_user_badges(user_id):
        assert user_id == "u-test"
        return {"unlockedCount": 1, "totalCount": 2, "list": []}

    monkeypatch.setattr(route_module.badge_service, "list_user_badges", fake_list_user_badges)

    response = client.get("/v1/badge/my", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["unlockedCount"] == 1


def test_evaluate_my_badges_uses_authenticated_user(client, auth_header, monkeypatch):
    def fake_evaluate_user_badges(user_id):
        assert user_id == "u-test"
        return {"newUnlocks": [{"code": "login_streak", "level": 1}], "upgrades": []}

    monkeypatch.setattr(route_module.badge_service, "evaluate_user_badges", fake_evaluate_user_badges)

    response = client.post("/v1/badge/evaluate", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["newUnlocks"][0]["code"] == "login_streak"


def test_evaluate_my_badges_returns_400_for_service_validation_error(client, auth_header, monkeypatch):
    def fake_evaluate_user_badges(user_id):
        assert user_id == "u-test"
        raise ValueError("bad badge request")

    monkeypatch.setattr(route_module.badge_service, "evaluate_user_badges", fake_evaluate_user_badges)

    response = client.post("/v1/badge/evaluate", headers=auth_header)

    assert response.status_code == 400
    assert response.get_json()["message"] == "bad badge request"

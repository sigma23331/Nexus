import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

import routes.diary_route as route_module
from routes.diary_route import diary_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(diary_bp, url_prefix="/v1/diary")
    return app


def test_save_entry_rejects_invalid_mood(client, auth_header):
    response = client.post(
        "/v1/diary/entry",
        json={"moodTag": "bad", "content": "hello"},
        headers=auth_header,
    )
    assert response.status_code == 400


def test_save_entry_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.diary_service, "create_entry", lambda **_: {"id": "d1"})
    monkeypatch.setattr(route_module.UserProfileService, "update_profile_by_behavior", lambda **_: None)

    response = client.post(
        "/v1/diary/entry",
        json={"moodTag": "happy", "content": "hello", "isPublic": False},
        headers=auth_header,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["id"] == "d1"


def test_timeline_invalid_year_month_returns_400(client, auth_header):
    response = client.get("/v1/diary/timeline?yearMonth=2026-13", headers=auth_header)
    assert response.status_code == 400


def test_timeline_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.diary_service, "list_timeline", lambda **_: {"list": [], "total": 0})

    response = client.get("/v1/diary/timeline?page=1&limit=10", headers=auth_header)
    assert response.status_code == 200


def test_get_entry_not_found(client, auth_header, monkeypatch):
    def _raise_not_found(**_):
        raise LookupError("not found")

    monkeypatch.setattr(route_module.diary_service, "get_entry", _raise_not_found)

    response = client.get("/v1/diary/entry/d-1", headers=auth_header)
    assert response.status_code == 404


def test_get_entry_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.diary_service, "get_entry", lambda **_: {"id": "d1"})

    response = client.get("/v1/diary/entry/d-1", headers=auth_header)
    assert response.status_code == 200


def test_update_entry_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.diary_service, "update_entry", lambda **_: {"id": "d1", "content": "x"})

    response = client.put("/v1/diary/entry/d-1", json={"content": "x"}, headers=auth_header)
    assert response.status_code == 200


def test_delete_entry_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.diary_service, "delete_entry", lambda **_: {"deleted": True})

    response = client.delete("/v1/diary/entry/d-1", headers=auth_header)
    assert response.status_code == 200

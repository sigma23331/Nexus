import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

import routes.answer_route as route_module
from routes.answer_route import answer_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(answer_bp, url_prefix="/v1/answer")
    return app


def test_ask_answer_rejects_empty_question(client, auth_header):
    response = client.post("/v1/answer/ask", json={"question": "   "}, headers=auth_header)

    assert response.status_code == 400
    assert response.get_json()["code"] == 400


def test_ask_answer_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.answer_service, "ask_question", lambda **_: {"answerId": "a1"})
    monkeypatch.setattr(route_module.UserProfileService, "update_profile_by_behavior", lambda **_: None)

    response = client.post("/v1/answer/ask", json={"question": "hello"}, headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["answerId"] == "a1"


def test_ask_answer_returns_400_when_review_rejects(client, auth_header, monkeypatch):
    def fake_ask_question(**_kwargs):
        raise ValueError("问题内容包含敏感或高风险信息，请调整后重试")

    monkeypatch.setattr(route_module.answer_service, "ask_question", fake_ask_question)

    response = client.post("/v1/answer/ask", json={"question": "hello"}, headers=auth_header)

    assert response.status_code == 400


def test_answer_history_bad_page_returns_400(client, auth_header):
    response = client.get("/v1/answer/history?page=bad&limit=10", headers=auth_header)
    assert response.status_code == 400


def test_answer_history_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.answer_service, "list_history", lambda **_: {"list": [], "total": 0})

    response = client.get("/v1/answer/history?page=1&limit=10", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["code"] == 200


def test_toggle_favorite_rejects_invalid_action(client, auth_header):
    response = client.post(
        "/v1/answer/favorite",
        json={"answerId": "ans_1", "action": "invalid"},
        headers=auth_header,
    )
    assert response.status_code == 400


def test_toggle_favorite_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.answer_service, "toggle_favorite", lambda **_: {"isFavorite": True})

    response = client.post(
        "/v1/answer/favorite",
        json={"answerId": "ans_1", "action": "favorite"},
        headers=auth_header,
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["isFavorite"] is True

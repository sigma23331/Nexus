import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

import routes.plaza_route as route_module
from routes.plaza_route import plaza_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(plaza_bp, url_prefix="/v1/plaza")
    return app


def test_get_comments_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(
        route_module.plaza_comment_service,
        "list_comments",
        lambda **_: {"list": [], "nextCursor": None, "hasMore": False},
    )

    response = client.get("/v1/plaza/cards/card1/comments", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["hasMore"] is False


def test_post_comment_requires_content(client, auth_header):
    response = client.post("/v1/plaza/cards/card1/comments", json={"content": "   "}, headers=auth_header)

    assert response.status_code == 400


def test_post_comment_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(
        route_module.plaza_comment_service,
        "create_comment",
        lambda **_: {"commentId": "c1", "status": "visible"},
    )

    response = client.post(
        "/v1/plaza/cards/card1/comments",
        json={"content": "hello"},
        headers=auth_header,
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["commentId"] == "c1"


def test_delete_comment_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module.plaza_comment_service, "delete_comment", lambda **_: {"success": True})

    response = client.delete("/v1/plaza/comments/c1", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["success"] is True


def test_report_comment_rejects_invalid_reason(client, auth_header):
    response = client.post(
        "/v1/plaza/comments/c1/reports",
        json={"reasonCode": "bad"},
        headers=auth_header,
    )

    assert response.status_code == 400


def test_report_comment_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(
        route_module.plaza_comment_service,
        "report_comment",
        lambda **_: {"success": True, "reportCount": 1},
    )

    response = client.post(
        "/v1/plaza/comments/c1/reports",
        json={"reasonCode": "abuse", "reasonText": "辱骂"},
        headers=auth_header,
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["reportCount"] == 1


def test_get_replies_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(
        route_module.plaza_comment_service,
        "list_replies",
        lambda **_: {"list": [], "nextCursor": None, "hasMore": False},
    )

    response = client.get("/v1/plaza/comments/c1/replies", headers=auth_header)

    assert response.status_code == 200

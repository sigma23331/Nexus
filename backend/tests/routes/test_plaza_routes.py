import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

from routes.plaza_route import plaza_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(plaza_bp, url_prefix="/v1/plaza")
    return app


def test_get_cards_requires_auth(client):
    response = client.get("/v1/plaza/cards")

    assert response.status_code == 401


def test_get_cards_rejects_invalid_tab(client, auth_header):
    response = client.get("/v1/plaza/cards?tab=invalid", headers=auth_header)

    assert response.status_code == 400
    assert response.get_json()["code"] == 400


def test_get_cards_returns_cursor_payload(client, auth_header, monkeypatch):
    def fake_list_cards(user_id, tab, cursor, limit):
        assert user_id == "u-test"
        assert tab == "hot"
        assert cursor == "abc"
        assert limit == 5
        return {
            "list": [
                {
                    "cardId": "card_1",
                    "type": "answer",
                    "owner": {"uid": "u1", "nickname": "N", "avatar": ""},
                    "snapshotUrl": "https://img.com/card.png",
                    "content": "text",
                    "stats": {"likes": 2, "isLiked": False},
                    "createdAt": "2026-04-18T10:30:00+08:00",
                }
            ],
            "nextCursor": "next",
            "hasMore": True,
        }

    monkeypatch.setattr("routes.plaza_route.plaza_service.list_cards", fake_list_cards)

    response = client.get("/v1/plaza/cards?tab=hot&cursor=abc&limit=5", headers=auth_header)

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["hasMore"] is True


def test_post_card_rejects_invalid_type(client, auth_header):
    response = client.post(
        "/v1/plaza/card",
        json={
            "type": "invalid",
            "sourceId": "ans_1002",
            "snapshotUrl": "https://img.com/card.png",
        },
        headers=auth_header,
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == 400


def test_post_card_success(client, auth_header, monkeypatch):
    def fake_create_card(user_id, payload):
        assert user_id == "u-test"
        assert payload["type"] == "answer"
        return {
            "cardId": "card_1",
            "type": "answer",
            "owner": {"uid": "u-test", "nickname": "tester", "avatar": ""},
            "snapshotUrl": "https://img.com/card.png",
            "content": "text",
            "stats": {"likes": 0, "isLiked": False},
            "createdAt": "2026-04-18T10:30:00+08:00",
        }

    monkeypatch.setattr("routes.plaza_route.plaza_service.create_card", fake_create_card)

    response = client.post(
        "/v1/plaza/card",
        json={
            "type": "answer",
            "sourceId": "ans_1002",
            "snapshotUrl": "https://img.com/card.png",
            "content": "text",
            "tags": ["grow"],
        },
        headers=auth_header,
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["cardId"] == "card_1"


def test_toggle_like_rejects_invalid_action(client, auth_header):
    response = client.post(
        "/v1/plaza/like",
        json={"cardId": "card_1", "action": "invalid"},
        headers=auth_header,
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == 400


def test_toggle_like_returns_404_when_card_missing(client, auth_header, monkeypatch):
    def fake_toggle_like(user_id, card_id, action):
        _ = (user_id, card_id, action)
        raise LookupError("card not found")

    monkeypatch.setattr("routes.plaza_route.plaza_service.toggle_like", fake_toggle_like)

    response = client.post(
        "/v1/plaza/like",
        json={"cardId": "card_x", "action": "like"},
        headers=auth_header,
    )

    assert response.status_code == 404
    assert response.get_json()["code"] == 404


def test_toggle_like_success(client, auth_header, monkeypatch):
    def fake_toggle_like(user_id, card_id, action):
        assert user_id == "u-test"
        assert card_id == "card_1"
        assert action == "like"
        return {"cardId": "card_1", "likes": 3, "isLiked": True}

    monkeypatch.setattr("routes.plaza_route.plaza_service.toggle_like", fake_toggle_like)

    response = client.post(
        "/v1/plaza/like",
        json={"cardId": "card_1", "action": "like"},
        headers=auth_header,
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["likes"] == 3


def test_delete_card_returns_403_for_non_owner(client, auth_header, monkeypatch):
    def fake_delete_card(user_id, card_id):
        _ = (user_id, card_id)
        raise PermissionError("无权删除他人卡片")

    monkeypatch.setattr("routes.plaza_route.plaza_service.delete_card", fake_delete_card)

    response = client.delete("/v1/plaza/card/card_1", headers=auth_header)

    assert response.status_code == 403
    assert response.get_json()["code"] == 403


def test_delete_card_success(client, auth_header, monkeypatch):
    def fake_delete_card(user_id, card_id):
        assert user_id == "u-test"
        assert card_id == "card_1"
        return {"success": True}

    monkeypatch.setattr("routes.plaza_route.plaza_service.delete_card", fake_delete_card)

    response = client.delete("/v1/plaza/card/card_1", headers=auth_header)

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["success"] is True

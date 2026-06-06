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


def test_get_equipped_badges_uses_authenticated_user(client, auth_header, monkeypatch):
    def fake_list_equipped_badges(user_id):
        assert user_id == "u-test"
        return {"maxEquipped": 3, "list": [{"code": "login_streak", "slotOrder": 1}]}

    monkeypatch.setattr(route_module.badge_service, "list_equipped_badges", fake_list_equipped_badges)

    response = client.get("/v1/badge/equipped", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["list"][0]["code"] == "login_streak"


def test_update_equipped_badges_uses_authenticated_user(client, auth_header, monkeypatch):
    def fake_update_equipped_badges(user_id, badge_codes):
        assert user_id == "u-test"
        assert badge_codes == ["login_streak", "share_station"]
        return {
            "maxEquipped": 3,
            "list": [
                {"code": "login_streak", "slotOrder": 1},
                {"code": "share_station", "slotOrder": 2},
            ],
        }

    monkeypatch.setattr(route_module.badge_service, "update_equipped_badges", fake_update_equipped_badges)

    response = client.put(
        "/v1/badge/equipped",
        json={"badgeCodes": ["login_streak", "share_station"]},
        headers=auth_header,
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["list"][1]["slotOrder"] == 2


@pytest.mark.parametrize(
    ("body", "content_type"),
    [
        ("{", "application/json"),
        ("", "application/json"),
        ("null", "application/json"),
    ],
)
def test_update_equipped_badges_rejects_invalid_json_body(client, auth_header, monkeypatch, body, content_type):
    def fake_update_equipped_badges(user_id, badge_codes):
        pytest.fail("update_equipped_badges should not be called for invalid JSON payloads")

    monkeypatch.setattr(route_module.badge_service, "update_equipped_badges", fake_update_equipped_badges)

    response = client.put(
        "/v1/badge/equipped",
        data=body,
        content_type=content_type,
        headers=auth_header,
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "请求体必须是有效的JSON对象"


def test_update_equipped_badges_returns_400_for_service_validation_error(client, auth_header, monkeypatch):
    def fake_update_equipped_badges(user_id, badge_codes):
        assert user_id == "u-test"
        assert badge_codes == ["locked_badge"]
        raise ValueError("只能佩戴已获取的徽章")

    monkeypatch.setattr(route_module.badge_service, "update_equipped_badges", fake_update_equipped_badges)

    response = client.put("/v1/badge/equipped", json={"badgeCodes": ["locked_badge"]}, headers=auth_header)

    assert response.status_code == 400
    assert response.get_json()["message"] == "只能佩戴已获取的徽章"


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


def test_get_badge_changes_uses_authenticated_user(client, auth_header, monkeypatch):
    def fake_list_unread_changes(user_id):
        assert user_id == "u-test"
        return {"total": 1, "list": [{"id": "n1", "badgeCode": "share_station"}]}

    monkeypatch.setattr(route_module.badge_service, "list_unread_changes", fake_list_unread_changes)

    response = client.get("/v1/badge/changes", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["list"][0]["id"] == "n1"


def test_mark_badge_changes_read_accepts_optional_ids(client, auth_header, monkeypatch):
    def fake_mark_changes_read(user_id, change_ids=None):
        assert user_id == "u-test"
        assert change_ids == ["n1"]
        return {"updated": 1}

    monkeypatch.setattr(route_module.badge_service, "mark_changes_read", fake_mark_changes_read)

    response = client.post("/v1/badge/changes/read", json={"changeIds": ["n1"]}, headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["updated"] == 1


def test_mark_badge_changes_read_accepts_omitted_body(client, auth_header, monkeypatch):
    def fake_mark_changes_read(user_id, change_ids=None):
        assert user_id == "u-test"
        assert change_ids is None
        return {"updated": 2}

    monkeypatch.setattr(route_module.badge_service, "mark_changes_read", fake_mark_changes_read)

    response = client.post("/v1/badge/changes/read", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["updated"] == 2


@pytest.mark.parametrize(
    ("body", "content_type"),
    [
        ("{", "application/json"),
        ("", "application/json"),
        ("null", "application/json"),
    ],
)
def test_mark_badge_changes_read_rejects_invalid_json_body(client, auth_header, monkeypatch, body, content_type):
    def fake_mark_changes_read(user_id, change_ids=None):
        pytest.fail("mark_changes_read should not be called for invalid JSON payloads")

    monkeypatch.setattr(route_module.badge_service, "mark_changes_read", fake_mark_changes_read)

    response = client.post(
        "/v1/badge/changes/read",
        data=body,
        content_type=content_type,
        headers=auth_header,
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "请求体必须是有效的JSON对象"


def test_mark_badge_changes_read_returns_400_for_invalid_payload(client, auth_header, monkeypatch):
    def fake_mark_changes_read(user_id, change_ids=None):
        assert user_id == "u-test"
        assert change_ids == "bad"
        raise ValueError("changeIds 必须为数组")

    monkeypatch.setattr(route_module.badge_service, "mark_changes_read", fake_mark_changes_read)

    response = client.post("/v1/badge/changes/read", json={"changeIds": "bad"}, headers=auth_header)

    assert response.status_code == 400
    assert response.get_json()["message"] == "changeIds 必须为数组"

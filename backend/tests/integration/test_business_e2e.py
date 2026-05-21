import importlib
import os

import pytest


@pytest.fixture
def app_and_db(monkeypatch):
    db_url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")

    config_module = importlib.import_module("config")
    importlib.reload(config_module)
    main_module = importlib.import_module("main")
    importlib.reload(main_module)

    app = main_module.create_app()
    app.config["TESTING"] = True

    from extensions import db

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app, db

    with app.app_context():
        db.session.remove()
        db.drop_all()


def _sms_code_for(phone):
    import routes.auth_route as auth_module

    return auth_module._sms_store[phone]["code"]


def _auth_headers(client, phone="13800138000"):
    client.post("/v1/auth/sms/send", json={"phone": phone})
    code = _sms_code_for(phone)
    login = client.post("/v1/auth/sms/login", json={"phone": phone, "code": code})
    token = login.get_json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_auth_answer_diary_user_flow_e2e(app_and_db, monkeypatch):
    app, _db = app_and_db

    import services.content_generation_service as generation_module

    monkeypatch.setattr(
        generation_module,
        "generate_answer",
        lambda **_: {"answerText": "mock answer"},
    )

    with app.test_client() as client:
        headers = _auth_headers(client)

        ask = client.post("/v1/answer/ask", json={"question": "hello"}, headers=headers)
        assert ask.status_code == 200
        answer_id = ask.get_json()["data"]["id"]

        fav = client.post(
            "/v1/answer/favorite",
            json={"answerId": answer_id, "action": "favorite"},
            headers=headers,
        )
        assert fav.status_code == 200

        diary = client.post(
            "/v1/diary/entry",
            json={"moodTag": "happy", "content": "today is good", "isPublic": True},
            headers=headers,
        )
        assert diary.status_code == 200

        profile = client.get("/v1/user/profile", headers=headers)
        assert profile.status_code == 200
        stats = profile.get_json()["data"]["stats"]
        assert stats["diaryCount"] == 1
        assert stats["answerCollected"] == 1


def test_auth_fortune_plaza_flow_e2e(app_and_db, monkeypatch):
    app, _db = app_and_db

    import services.content_generation_service as generation_module

    monkeypatch.setattr(
        generation_module,
        "generate_fortune",
        lambda **_: {
            "score": 88,
            "title": "上上签",
            "content_main": "今日状态佳",
            "content_sub": "适合推进计划",
            "love": "平稳",
            "career": "向好",
            "health": "稳定",
            "wealth": "向好",
            "yi": ["沟通"],
            "ji": ["拖延"],
            "gua_meaning_lines": ["火土相生", "顺势加速，主动求进"],
            "lucky_hour_name": "巳时",
            "lucky_hour_range": "09:00-11:00",
        },
    )

    with app.test_client() as client:
        headers = _auth_headers(client, phone="13900139000")

        today = client.get("/v1/fortune/today", headers=headers)
        assert today.status_code == 200
        fortune_id = today.get_json()["data"]["id"]

        post = client.post(
            "/v1/plaza/card",
            json={
                "type": "fortune",
                "sourceId": fortune_id,
                "snapshotUrl": "https://img.com/f.png",
                "content": "content",
                "tags": ["grow"],
            },
            headers=headers,
        )
        assert post.status_code == 200
        card_id = post.get_json()["data"]["cardId"]

        like = client.post(
            "/v1/plaza/like",
            json={"cardId": card_id, "action": "like"},
            headers=headers,
        )
        assert like.status_code == 200
        assert like.get_json()["data"]["likes"] == 1

        cards = client.get("/v1/plaza/cards?tab=latest&limit=10", headers=headers)
        assert cards.status_code == 200
        assert len(cards.get_json()["data"]["list"]) >= 1

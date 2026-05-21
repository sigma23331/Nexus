def test_get_profile_user_not_found(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: None)
    resp = client.get("/v1/user/profile", headers=auth_header)
    assert resp.status_code == 404

def test_update_profile_param_and_nickname(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())
    # 缺 payload
    resp = client.put("/v1/user/profile", headers=auth_header)
    assert resp.status_code == 400
    # 不支持字段
    resp = client.put("/v1/user/profile", json={"foo": "bar"}, headers=auth_header)
    assert resp.status_code == 400
    # 昵称为空
    resp = client.put("/v1/user/profile", json={"nickname": "   "}, headers=auth_header)
    assert resp.status_code == 400
    # 昵称过长
    resp = client.put("/v1/user/profile", json={"nickname": "a"*21}, headers=auth_header)
    assert resp.status_code == 400
    # 昵称唯一性
    class _FakeUser:
        id = "u-test"
        nickname = "abc"
        class query:
            @staticmethod
            def filter(*a, **k):
                class _F:
                    def first(self):
                        return True
                return _F()
    monkeypatch.setattr(route_module, "User", _FakeUser)
    resp = client.put("/v1/user/profile", json={"nickname": "abc"}, headers=auth_header)
    assert resp.status_code == 400

def test_update_profile_avatar_invalid(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())
    # 头像非字符串
    resp = client.put("/v1/user/profile", json={"avatar": 123}, headers=auth_header)
    assert resp.status_code == 400
    # 头像过大
    resp = client.put("/v1/user/profile", json={"avatar": "a"*2_000_001}, headers=auth_header)
    assert resp.status_code == 400

def test_update_profile_db_exception(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())
    class _Session:
        def commit(self): raise Exception("db error")
        def rollback(self): pass
    fake_db = type("FakeDB", (), {"session": _Session()})
    monkeypatch.setattr(route_module, "db", fake_db)
    class _FakeUser:
        id = "u-test"
        nickname = "abc"
        class query:
            @staticmethod
            def filter(*a, **k):
                class _F:
                    def first(self):
                        return None
                return _F()
    monkeypatch.setattr(route_module, "User", _FakeUser)
    resp = client.put("/v1/user/profile", json={"nickname": "abc"}, headers=auth_header)
    assert resp.status_code == 500

def test_get_fortune_history_user_not_found(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: None)
    resp = client.get("/v1/user/history/fortune?page=1&limit=10", headers=auth_header)
    assert resp.status_code == 404

def test_get_fortune_history_page_limit(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())
    # page/limit 非法
    resp = client.get("/v1/user/history/fortune?page=0&limit=10", headers=auth_header)
    assert resp.status_code == 400
    resp = client.get("/v1/user/history/fortune?page=1&limit=0", headers=auth_header)
    assert resp.status_code == 400
    resp = client.get("/v1/user/history/fortune?page=1&limit=51", headers=auth_header)
    assert resp.status_code == 400

def test_get_favorites_user_not_found(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: None)
    resp = client.get("/v1/user/history/favorites?page=1&limit=10", headers=auth_header)
    assert resp.status_code == 404

def test_get_favorites_page_limit(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())
    resp = client.get("/v1/user/history/favorites?page=0&limit=10", headers=auth_header)
    assert resp.status_code == 400
    resp = client.get("/v1/user/history/favorites?page=1&limit=0", headers=auth_header)
    assert resp.status_code == 400
    resp = client.get("/v1/user/history/favorites?page=1&limit=51", headers=auth_header)
    assert resp.status_code == 400
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

import routes.user_route as route_module
from routes.user_route import user_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(user_bp, url_prefix="/v1/user")
    return app


class _Counter:
    def __init__(self, value):
        self._value = value

    def count(self):
        return self._value


class _User:
    def __init__(self, uid="u-test"):
        self.id = uid
        self.nickname = "tester"
        self.avatar = ""
        self.favorites = _Counter(3)
        self.plaza_cards = _Counter(2)


class _Pagination:
    def __init__(self, items, total):
        self.items = items
        self.total = total


class _QueryStub:
    def __init__(self, pagination):
        self._pagination = pagination

    def filter_by(self, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def paginate(self, **_kwargs):
        return self._pagination


def test_get_profile_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())
    monkeypatch.setattr(route_module.ProfileAnalysisService, "trigger_analysis_if_needed", lambda **_: None)
    monkeypatch.setattr(route_module.UserProfileService, "get_by_user_id", lambda _uid: object())
    monkeypatch.setattr(route_module.UserProfileService, "to_dict", lambda _profile: {"moodTendency": "optimistic"})

    class _DiaryQuery:
        @staticmethod
        def filter_by(**_kwargs):
            return _Counter(5)

    fake_diary = type("FakeDiary", (), {"query": _DiaryQuery()})
    monkeypatch.setattr(route_module, "DiaryEntry", fake_diary)

    response = client.get("/v1/user/profile", headers=auth_header)

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["stats"]["diaryCount"] == 5


def test_get_fortune_history_invalid_page_returns_400(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())

    response = client.get("/v1/user/history/fortune?page=abc&limit=10", headers=auth_header)

    assert response.status_code == 400
    assert response.get_json()["code"] == 400


def test_get_fortune_history_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())

    class _FortuneRecord:
        def __init__(self):
            self.date = None
            self.score = 88
            self.title = "good"
            self.content = '{"main": "m", "sub": "s"}'
            self.yi = []
            self.ji = []

    fake_fortune_model = type(
        "FakeFortuneRecord",
        (),
        {
            "query": _QueryStub(_Pagination(items=[_FortuneRecord()], total=1)),
            "date": type("DateCol", (), {"desc": staticmethod(lambda: None)})(),
        },
    )
    monkeypatch.setattr(route_module, "FortuneRecord", fake_fortune_model)

    response = client.get("/v1/user/history/fortune?page=1&limit=10", headers=auth_header)

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["total"] == 1


def test_get_favorites_success(client, auth_header, monkeypatch):
    monkeypatch.setattr(route_module, "get_current_user", lambda: _User())

    class _Answer:
        def __init__(self):
            self.id = "ans-1"
            self.question = "q"
            self.answer_text = "a"
            self.created_at = None

    class _Favorite:
        def __init__(self):
            self.answer = _Answer()

    import models.association as association_module

    fake_favorite_model = type(
        "FakeFavorite",
        (),
        {
            "query": _QueryStub(_Pagination(items=[_Favorite()], total=1)),
            "created_at": type("CreatedCol", (), {"desc": staticmethod(lambda: None)})(),
        },
    )
    monkeypatch.setattr(association_module, "Favorite", fake_favorite_model)

    response = client.get("/v1/user/history/favorites?page=1&limit=10", headers=auth_header)

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["total"] == 1

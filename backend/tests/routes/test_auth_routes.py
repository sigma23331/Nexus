def test_register_db_exception(client, monkeypatch):
    # 注册时数据库异常
    class _Session:
        def add(self, _): pass
        def commit(self): raise Exception("db error")
        def rollback(self): self.rolled_back = True
        def refresh(self, _): pass
    fake_db = type("FakeDB", (), {"session": _Session()})
    monkeypatch.setattr(route_module, "db", fake_db)
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=None)})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    monkeypatch.setattr(route_module.sms_service, "verify_code", lambda **_: type("Result", (), {"success": True})())
    resp = client.post("/v1/auth/register", json={"phone": "13800138000", "code": "123456", "password": "abcdef"})
    assert resp.status_code == 500

def test_password_login_no_password_hash_and_wrong_password(client, monkeypatch):
    # 账号未设置密码
    user = _User("u1", phone="13800138000")
    user.password_hash = None
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=user)})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    resp = client.post("/v1/auth/password/login", json={"phone": "13800138000", "password": "abcdef"})
    assert resp.status_code == 400
    # 密码错误
    user.password_hash = "hashed"
    user.check_password = lambda pw: False
    resp = client.post("/v1/auth/password/login", json={"phone": "13800138000", "password": "abcdef"})
    assert resp.status_code == 400

def test_mobile_verify_exception_and_invalid_phone(client, monkeypatch):
    # 模拟 DYPNS 客户端异常
    monkeypatch.setattr(route_module, "_get_dypns_client", lambda: (_ for _ in ()).throw(Exception("dypns error")))
    resp = client.post("/v1/auth/mobile/verify", json={"access_code": "bad"})
    assert resp.status_code == 500
    # 模拟未能解析手机号
    monkeypatch.setattr(route_module, "_get_dypns_client", lambda: type("Client", (), {"get_phone_with_token": lambda self, req: None})())
    monkeypatch.setattr(route_module, "_extract_phone_number_from_response", lambda resp: None)
    resp = client.post("/v1/auth/mobile/verify", json={"access_code": "ok"})
    assert resp.status_code == 500
    # 模拟手机号格式不正确
    monkeypatch.setattr(route_module, "_extract_phone_number_from_response", lambda resp: "notaphone")
    resp = client.post("/v1/auth/mobile/verify", json={"access_code": "ok"})
    assert resp.status_code == 400
def test_register_missing_fields(client):
    # 缺字段
    resp = client.post("/v1/auth/register", json={})
    assert resp.status_code == 400
    # 缺 password
    resp = client.post("/v1/auth/register", json={"phone": "13800138000", "code": "123456"})
    assert resp.status_code == 400
    # 缺 code
    resp = client.post("/v1/auth/register", json={"phone": "13800138000", "password": "abcdef"})
    assert resp.status_code == 400

def test_register_invalid_phone_and_password(client):
    # 手机号格式错误
    resp = client.post("/v1/auth/register", json={"phone": "123", "code": "123456", "password": "abcdef"})
    assert resp.status_code == 400
    # 密码过短
    resp = client.post("/v1/auth/register", json={"phone": "13800138000", "code": "123456", "password": "123"})
    assert resp.status_code == 400
    # 密码过长
    resp = client.post("/v1/auth/register", json={"phone": "13800138000", "code": "123456", "password": "a"*21})
    assert resp.status_code == 400

def test_register_phone_already_exists(client, monkeypatch):
    # 手机号已注册
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=_User("u1", phone="13800138000"))})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    resp = client.post("/v1/auth/register", json={"phone": "13800138000", "code": "123456", "password": "abcdef"})
    assert resp.status_code == 400

def test_register_nickname_missing_fields(client):
    # 缺字段
    resp = client.post("/v1/auth/register/nickname", json={})
    assert resp.status_code == 400
    # 缺 password
    resp = client.post("/v1/auth/register/nickname", json={"nickname": "abc"})
    assert resp.status_code == 400
    # 缺 nickname
    resp = client.post("/v1/auth/register/nickname", json={"password": "abcdef"})
    assert resp.status_code == 400

def test_register_nickname_invalid_and_exists(client, monkeypatch):
    # 昵称过短/过长
    resp = client.post("/v1/auth/register/nickname", json={"nickname": "", "password": "abcdef"})
    assert resp.status_code == 400
    resp = client.post("/v1/auth/register/nickname", json={"nickname": "a"*21, "password": "abcdef"})
    assert resp.status_code == 400
    # 密码过短/过长
    resp = client.post("/v1/auth/register/nickname", json={"nickname": "abc", "password": "123"})
    assert resp.status_code == 400
    resp = client.post("/v1/auth/register/nickname", json={"nickname": "abc", "password": "a"*21})
    assert resp.status_code == 400
    # 昵称已存在
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=_User("u1", nickname="abc"))})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    resp = client.post("/v1/auth/register/nickname", json={"nickname": "abc", "password": "abcdef"})
    assert resp.status_code == 400

def test_password_login_missing_and_invalid_fields(client):
    # 缺 password
    resp = client.post("/v1/auth/password/login", json={"phone": "13800138000"})
    assert resp.status_code == 400
    # 缺 phone/nickname
    resp = client.post("/v1/auth/password/login", json={"password": "abcdef"})
    assert resp.status_code == 400
    # 手机号格式错误
    resp = client.post("/v1/auth/password/login", json={"phone": "123", "password": "abcdef"})
    assert resp.status_code == 400
    # 昵称过长
    resp = client.post("/v1/auth/password/login", json={"nickname": "a"*21, "password": "abcdef"})
    assert resp.status_code == 400

def test_password_login_user_not_found(client, monkeypatch):
    # 用户不存在
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=None)})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    resp = client.post("/v1/auth/password/login", json={"phone": "13800138000", "password": "abcdef"})
    assert resp.status_code == 400

def test_password_login_no_password_hash(client, monkeypatch):
    # 账号未设置密码
    user = _User("u1", phone="13800138000")
    user.password_hash = None
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=user)})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    resp = client.post("/v1/auth/password/login", json={"phone": "13800138000", "password": "abcdef"})
    assert resp.status_code == 400

def test_password_login_wrong_password(client, monkeypatch):
    # 密码错误
    user = _User("u1", phone="13800138000")
    user.password_hash = "hashed"
    user.check_password = lambda pw: False
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=user)})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    resp = client.post("/v1/auth/password/login", json={"phone": "13800138000", "password": "abcdef"})
    assert resp.status_code == 400
from datetime import datetime, timedelta

import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

import routes.auth_route as route_module
from routes.auth_route import auth_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix="/v1/auth")
    return app


@pytest.fixture(autouse=True)
def clear_sms_store():
    route_module.sms_service._sms_store.clear()


class _User:
    def __init__(self, uid, phone=None, nickname="tester", avatar=None):
        self.id = uid
        self.phone = phone
        self.nickname = nickname
        self.avatar = avatar


class _QueryStub:
    def __init__(self, first_result=None, get_result=None):
        self._first_result = first_result
        self._get_result = get_result

    def filter_by(self, **_kwargs):
        return self

    def first(self):
        return self._first_result

    def get(self, _uid):
        return self._get_result


def test_send_sms_success(client, monkeypatch):
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=None)})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    monkeypatch.setattr(route_module.sms_service, "_generate_code", lambda *_: "123456")

    response = client.post("/v1/auth/sms/send", json={"phone": "13800138000"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["success"] is True


def test_sms_login_success_existing_user(client, monkeypatch):
    phone = "13800138000"
    route_module.sms_service._sms_store[phone] = {
        "code": "123456",
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "sent_at": datetime.utcnow(),
        "action": "login",
    }

    existing_user = _User(uid="u-1", phone=phone, nickname="Alice")
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=existing_user)})
    monkeypatch.setattr(route_module, "User", fake_user_model)

    response = client.post("/v1/auth/sms/login", json={"phone": phone, "code": "123456"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["userInfo"]["uid"] == "u-1"


def test_send_bind_sms_success(client, auth_header, monkeypatch):
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(first_result=None)})
    monkeypatch.setattr(route_module, "User", fake_user_model)
    monkeypatch.setattr(route_module.sms_service, "_generate_code", lambda *_: "654321")

    response = client.post(
        "/v1/auth/sms/bind/send",
        json={"phone": "13900139000"},
        headers=auth_header,
    )

    assert response.status_code == 200
    assert response.get_json()["code"] == 200


def test_confirm_bind_sms_success(client, auth_header, monkeypatch):
    phone = "13900139000"
    route_module.sms_service._sms_store[phone] = {
        "code": "654321",
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
        "sent_at": datetime.utcnow(),
        "action": "bind",
    }

    current_user = _User(uid="u-test")
    fake_user_model = type(
        "FakeUser",
        (),
        {
            "query": _QueryStub(first_result=None, get_result=current_user),
        },
    )
    monkeypatch.setattr(route_module, "User", fake_user_model)

    class _Session:
        @staticmethod
        def commit():
            return None

    fake_db = type("FakeDB", (), {"session": _Session()})
    monkeypatch.setattr(route_module, "db", fake_db)

    response = client.post(
        "/v1/auth/sms/bind/confirm",
        json={"phone": phone, "code": "654321"},
        headers=auth_header,
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["success"] is True


def test_verify_success(client, auth_header, monkeypatch):
    fake_user = _User(uid="u-test", phone="13800138000", nickname="Tester")
    fake_user_model = type("FakeUser", (), {"query": _QueryStub(get_result=fake_user)})
    monkeypatch.setattr(route_module, "User", fake_user_model)

    response = client.get("/v1/auth/verify", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["valid"] is True


def test_logout_success(client, auth_header):
    response = client.post("/v1/auth/logout", headers=auth_header)

    assert response.status_code == 200
    assert response.get_json()["data"]["success"] is True


def test_register_requires_required_fields(client):
    response = client.post("/v1/auth/register", json={})
    assert response.status_code == 400


def test_password_login_requires_required_fields(client):
    response = client.post("/v1/auth/password/login", json={})
    assert response.status_code == 400


def test_wechat_login_not_implemented(client):
    response = client.post("/v1/auth/wechat/login", json={})
    assert response.status_code == 404

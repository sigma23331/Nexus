from datetime import timedelta

import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from routes.answer_route import answer_bp
from routes.auth_route import auth_bp
from routes.diary_route import diary_bp
from routes.fortune_route import fortune_bp
from routes.plaza_route import plaza_bp
from routes.user_route import user_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix="/v1/auth")
    app.register_blueprint(user_bp, url_prefix="/v1/user")
    app.register_blueprint(fortune_bp, url_prefix="/v1/fortune")
    app.register_blueprint(answer_bp, url_prefix="/v1/answer")
    app.register_blueprint(plaza_bp, url_prefix="/v1/plaza")
    app.register_blueprint(diary_bp, url_prefix="/v1/diary")
    return app


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/v1/user/profile", None),
        ("GET", "/v1/fortune/today", None),
        ("GET", "/v1/answer/history", None),
        ("POST", "/v1/answer/favorite", {"answerId": "ans1", "action": "favorite"}),
        ("GET", "/v1/plaza/cards", None),
        ("POST", "/v1/plaza/like", {"cardId": "card1", "action": "like"}),
        ("GET", "/v1/diary/timeline", None),
        ("POST", "/v1/diary/entry", {"moodTag": "happy", "content": "x"}),
        ("POST", "/v1/auth/logout", {}),
    ],
)
def test_protected_routes_require_token(client, method, path, payload):
    response = client.open(path, method=method, json=payload)

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/v1/user/profile", None),
        ("GET", "/v1/fortune/trend", None),
        ("POST", "/v1/answer/ask", {"question": "q"}),
        ("GET", "/v1/plaza/cards", None),
        ("GET", "/v1/diary/timeline", None),
    ],
)
def test_protected_routes_reject_malformed_token(client, method, path, payload):
    response = client.open(
        path,
        method=method,
        json=payload,
        headers={"Authorization": "Bearer malformed.token.value"},
    )

    assert response.status_code in {401, 422}


def test_protected_route_rejects_expired_token(client, app):
    with app.app_context():
        expired = create_access_token(identity="u-expired", expires_delta=timedelta(seconds=-1))

    response = client.get(
        "/v1/user/profile",
        headers={"Authorization": f"Bearer {expired}"},
    )

    assert response.status_code in {401, 422}

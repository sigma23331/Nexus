import sys
from pathlib import Path

import pytest
from flask_jwt_extended import create_access_token


BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_header(app):
    with app.app_context():
        token = create_access_token(identity="u-test")
    return {"Authorization": f"Bearer {token}"}

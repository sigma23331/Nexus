from pathlib import Path
import sys

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(autouse=True)
def skip_if_no_pg_url():
    import os

    pg_url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not pg_url or not pg_url.startswith("postgresql"):
        pytest.skip("integration tests require TEST_DATABASE_URL/DATABASE_URL pointing to PostgreSQL")

from datetime import datetime
import sys
import types
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if 'flask_migrate' not in sys.modules:
    flask_migrate = types.ModuleType('flask_migrate')

    class _Migrate:
        def init_app(self, *args, **kwargs):
            return None

    flask_migrate.Migrate = _Migrate
    sys.modules['flask_migrate'] = flask_migrate

if 'flask_cors' not in sys.modules:
    flask_cors = types.ModuleType('flask_cors')

    class _CORS:
        def init_app(self, *args, **kwargs):
            return None

    flask_cors.CORS = _CORS
    sys.modules['flask_cors'] = flask_cors

from services.profile_analysis_service import ProfileAnalysisService


def test_build_request_id_is_stable():
    event_time = datetime(2026, 4, 25, 10, 30)

    first = ProfileAnalysisService._build_request_id('u1', 'diary_created', event_time)
    second = ProfileAnalysisService._build_request_id('u1', 'diary_created', event_time)

    assert first == second


def test_apply_ai_analysis_result_rejects_empty_mood():
    with pytest.raises(ValueError):
        ProfileAnalysisService.apply_ai_analysis_result('u1', {'mood_tendency': '   '})

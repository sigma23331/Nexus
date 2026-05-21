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

from services.user_profile_service import UserProfileService
from models.user_profile import ActiveHourBucket, PreferredFeature


@pytest.mark.parametrize('window_days', [0, -1, True, '7'])
def test_validate_window_days_rejects_invalid_values(window_days):
    with pytest.raises(ValueError):
        UserProfileService._validate_window_days(window_days)


def test_get_or_create_profile_returns_existing(monkeypatch):
    existing_profile = object()

    monkeypatch.setattr(UserProfileService, 'get_by_user_id', staticmethod(lambda _uid: existing_profile))

    added = []
    flushed = []
    monkeypatch.setattr('services.user_profile_service.db.session.add', lambda value: added.append(value))
    monkeypatch.setattr('services.user_profile_service.db.session.flush', lambda: flushed.append(True))

    profile = UserProfileService.get_or_create_profile('u1')

    assert profile is existing_profile
    assert added == []
    assert flushed == []


def test_get_or_create_profile_creates_new_profile(monkeypatch):
    monkeypatch.setattr(UserProfileService, 'get_by_user_id', staticmethod(lambda _uid: None))

    added = []
    flushed = []
    monkeypatch.setattr('services.user_profile_service.db.session.add', lambda value: added.append(value))
    monkeypatch.setattr('services.user_profile_service.db.session.flush', lambda: flushed.append(True))

    profile = UserProfileService.get_or_create_profile('u2')

    assert profile.user_id == 'u2'
    assert profile.topic_interests == []
    assert profile.personalization_enabled is True
    assert added == [profile]
    assert flushed == [True]


def test_recompute_rule_profile_fields_in_window_skips_none_fields(monkeypatch):
    monkeypatch.setattr(
        UserProfileService,
        'calc_preferred_feature_in_window',
        staticmethod(lambda _uid, window_days, now=None: PreferredFeature.FORTUNE),
    )
    monkeypatch.setattr(
        UserProfileService,
        'calc_active_hour_bucket_in_window',
        staticmethod(lambda _uid, window_days, now=None: None),
    )

    update_data = UserProfileService.recompute_rule_profile_fields_in_window('u3', window_days=7)

    assert update_data == {'preferred_feature': PreferredFeature.FORTUNE}


def test_update_profile_by_behavior_updates_only_changed_fields(monkeypatch):
    class FakeProfile:
        preferred_feature = PreferredFeature.FORTUNE
        active_hour_bucket = ActiveHourBucket.MORNING

    profile = FakeProfile()

    monkeypatch.setattr(UserProfileService, 'get_or_create_profile', staticmethod(lambda _uid: profile))
    monkeypatch.setattr(
        UserProfileService,
        'recompute_rule_profile_fields_in_window',
        staticmethod(
            lambda **kwargs: {
                'preferred_feature': PreferredFeature.ANSWER,
                'active_hour_bucket': ActiveHourBucket.MORNING,
            }
        ),
    )

    committed = []
    monkeypatch.setattr('services.user_profile_service.db.session.commit', lambda: committed.append(True))

    result = UserProfileService.update_profile_by_behavior(
        user_id='u4',
        event_type='diary_created',
        event_time=datetime(2026, 4, 25, 10, 0, 0),
        window_days=7,
    )

    assert result is profile
    assert profile.preferred_feature == PreferredFeature.ANSWER
    assert profile.active_hour_bucket == ActiveHourBucket.MORNING
    assert committed == [True]

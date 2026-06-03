from datetime import date, timedelta
from types import SimpleNamespace

from services import badge_service


class FakeSession:
    def __init__(self):
        self.added = []
        self.committed = False
        self.flushed = False
        self.rolled_back = False

    def add(self, row):
        self.added.append(row)

    def flush(self):
        self.flushed = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class FakeColumn:
    def __eq__(self, other):
        return ("eq", other)

    def in_(self, values):
        return ("in", tuple(values))


class FakeUserBadgeQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *_args):
        return self

    def filter_by(self, **_kwargs):
        return self

    def all(self):
        return list(self.rows)

    def first(self):
        return self.rows[0] if self.rows else None


class FakeUserBadge:
    user_id = FakeColumn()
    badge_code = FakeColumn()
    query = FakeUserBadgeQuery([])

    def __init__(
        self,
        user_id,
        badge_code,
        level,
        current_progress,
        target,
        unlocked_at,
        last_evaluated_at,
    ):
        self.user_id = user_id
        self.badge_code = badge_code
        self.level = level
        self.current_progress = current_progress
        self.target = target
        self.unlocked_at = unlocked_at
        self.last_evaluated_at = last_evaluated_at


def _definition(code="share_station", metric_key="plaza_card_count"):
    return {
        "code": code,
        "name": code,
        "category": "plaza",
        "description": "",
        "icon_url": f"/{code}.png",
        "gray_icon_url": f"/{code}_gray.png",
        "sort_order": 1,
        "enabled": True,
        "levels": [
            {"level": 1, "title": "L1", "condition_type": "count", "metric_key": metric_key, "threshold": 1, "description": ""},
            {"level": 2, "title": "L2", "condition_type": "count", "metric_key": metric_key, "threshold": 10, "description": ""},
            {"level": 3, "title": "L3", "condition_type": "count", "metric_key": metric_key, "threshold": 50, "description": ""},
            {"level": 4, "title": "L4", "condition_type": "count", "metric_key": metric_key, "threshold": 200, "description": ""},
        ],
    }


def test_current_streak_from_dates_requires_current_contiguous_dates():
    today = date(2026, 6, 2)

    assert badge_service._current_streak_from_dates(
        [today, today - timedelta(days=1), today - timedelta(days=2), today - timedelta(days=2)],
        start_date=today,
    ) == 3
    assert badge_service._current_streak_from_dates([today - timedelta(days=1)], start_date=today) == 0
    assert badge_service._current_streak_from_dates([today, today - timedelta(days=2)], start_date=today) == 1


def test_max_streak_from_dates_keeps_historical_best_after_interruption():
    today = date(2026, 6, 2)

    assert badge_service._max_streak_from_dates(
        [
            today - timedelta(days=10),
            today - timedelta(days=9),
            today - timedelta(days=8),
            today - timedelta(days=2),
        ]
    ) == 3


def test_evaluate_definition_uses_highest_achieved_level_and_next_target():
    definition = _definition(metric_key="answer_count")

    partial = badge_service._evaluate_definition(definition, {"answer_count": 75})
    complete = badge_service._evaluate_definition(definition, {"answer_count": 250})

    assert partial == {"level": 3, "progress": 75, "target": 200}
    assert complete == {"level": 4, "progress": 250, "target": 200}


def test_collect_metrics_counts_shares_only_from_plaza_cards(monkeypatch):
    class PlazaCardQuery:
        def filter_by(self, **kwargs):
            assert kwargs == {"user_id": "u1"}
            return self

        def count(self):
            return 12

    class ForbiddenQuery:
        def filter_by(self, **_kwargs):
            raise AssertionError("share metrics must not read answer records")

    monkeypatch.setattr(badge_service, "PlazaCard", SimpleNamespace(query=PlazaCardQuery()))
    monkeypatch.setattr(badge_service, "AnswerRecord", SimpleNamespace(query=ForbiddenQuery()))

    metrics = badge_service.collect_metrics(user_id="u1", metric_keys={"plaza_card_count"})

    assert metrics["plaza_card_count"] == 12


def test_record_login_day_uses_user_login_day_model(monkeypatch):
    login_date = date(2026, 6, 2)
    session = FakeSession()

    class LoginDayQuery:
        def filter_by(self, **kwargs):
            assert kwargs == {"user_id": "u1", "login_date": login_date}
            return self

        def first(self):
            return None

    class FakeLoginDay:
        query = LoginDayQuery()

        def __init__(self, user_id, login_date):
            self.user_id = user_id
            self.login_date = login_date

    monkeypatch.setattr(badge_service, "UserLoginDay", FakeLoginDay)
    monkeypatch.setattr(badge_service.db, "session", session)

    result = badge_service.record_login_day(user_id="u1", login_date=login_date)

    assert result == {"created": True, "loginDate": "2026-06-02"}
    assert session.committed is True
    assert session.added[0].user_id == "u1"
    assert session.added[0].login_date == login_date


def test_evaluate_user_badges_unlocks_historical_progress_at_highest_level(monkeypatch):
    session = FakeSession()
    FakeUserBadge.query = FakeUserBadgeQuery([])

    def fake_active_definitions(badge_codes=None):
        assert badge_codes == {"share_station"}
        return [_definition()]

    def fake_collect_metrics(user_id, metric_keys):
        assert user_id == "u1"
        assert metric_keys == {"plaza_card_count"}
        return {"plaza_card_count": 250}

    monkeypatch.setattr(badge_service, "_active_definitions", fake_active_definitions)
    monkeypatch.setattr(badge_service, "collect_metrics", fake_collect_metrics)
    monkeypatch.setattr(badge_service, "UserBadge", FakeUserBadge)
    monkeypatch.setattr(badge_service.db, "session", session)

    result = badge_service.evaluate_user_badges(user_id="u1", trigger="plaza_card_created")

    assert session.committed is True
    assert session.added[0].badge_code == "share_station"
    assert session.added[0].level == 4
    assert session.added[0].current_progress == 250
    assert result["newUnlocks"][0]["level"] == 4
    assert result["newUnlocks"][0]["target"] == 200
    assert result["upgrades"] == []


def test_evaluate_user_badges_never_downgrades_existing_level(monkeypatch):
    session = FakeSession()
    existing = SimpleNamespace(
        user_id="u1",
        badge_code="share_station",
        level=3,
        current_progress=50,
        target=200,
        unlocked_at=None,
        last_evaluated_at=None,
    )
    FakeUserBadge.query = FakeUserBadgeQuery([existing])

    monkeypatch.setattr(badge_service, "_active_definitions", lambda badge_codes=None: [_definition()])
    monkeypatch.setattr(badge_service, "collect_metrics", lambda user_id, metric_keys: {"plaza_card_count": 0})
    monkeypatch.setattr(badge_service, "UserBadge", FakeUserBadge)
    monkeypatch.setattr(badge_service.db, "session", session)

    result = badge_service.evaluate_user_badges(user_id="u1")

    assert existing.level == 3
    assert existing.current_progress == 0
    assert existing.target == 1
    assert result == {"newUnlocks": [], "upgrades": []}
    assert session.committed is True

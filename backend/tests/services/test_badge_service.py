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

    def asc(self):
        return ("asc", self)


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


class FakeNotificationQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter_by(self, **_kwargs):
        return self

    def filter(self, *_args):
        return self

    def order_by(self, *_args):
        return self

    def all(self):
        return list(self.rows)


class FakeNotification:
    id = FakeColumn()
    created_at = FakeColumn()
    query = FakeNotificationQuery([])

    def __init__(self, user_id, badge_code, level, change_type):
        self.id = f"n-{badge_code}-{level}"
        self.user_id = user_id
        self.badge_code = badge_code
        self.level = level
        self.change_type = change_type
        self.created_at = None
        self.read_at = None


class FakeEquippedBadgeQuery:
    def __init__(self, rows):
        self.rows = rows
        self.deleted = False

    def filter_by(self, **_kwargs):
        return self

    def order_by(self, *_args):
        return self

    def all(self):
        return list(self.rows)

    def delete(self, synchronize_session=False):
        self.deleted = True
        count = len(self.rows)
        self.rows.clear()
        return count


class FakeEquippedBadge:
    slot_order = FakeColumn()
    query = FakeEquippedBadgeQuery([])

    def __init__(self, user_id, badge_code, slot_order):
        self.user_id = user_id
        self.badge_code = badge_code
        self.slot_order = slot_order


class FakeBadgeDefinitionQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *_args):
        return self

    def all(self):
        return list(self.rows)


class FakeBadgeDefinition:
    code = FakeColumn()
    query = FakeBadgeDefinitionQuery([])


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
    monkeypatch.setattr(badge_service, "UserBadgeNotification", FakeNotification)
    monkeypatch.setattr(badge_service.db, "session", session)

    result = badge_service.evaluate_user_badges(user_id="u1", trigger="plaza_card_created")

    assert session.committed is True
    assert session.added[0].badge_code == "share_station"
    assert session.added[0].level == 4
    assert session.added[0].current_progress == 250
    assert session.added[1].badge_code == "share_station"
    assert session.added[1].change_type == "unlock"
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
    assert existing.target == 200
    assert result == {"newUnlocks": [], "upgrades": []}
    assert session.committed is True


def test_mark_changes_read_updates_unread_rows(monkeypatch):
    session = FakeSession()
    rows = [
        SimpleNamespace(id="n1", read_at=None),
        SimpleNamespace(id="n2", read_at=None),
    ]
    FakeNotification.query = FakeNotificationQuery(rows)
    monkeypatch.setattr(badge_service, "UserBadgeNotification", FakeNotification)
    monkeypatch.setattr(badge_service.db, "session", session)

    result = badge_service.mark_changes_read("u1", change_ids=["n1"])

    assert result == {"updated": 2}
    assert rows[0].read_at is not None
    assert rows[1].read_at is not None
    assert session.committed is True


def test_list_unread_changes_formats_badge_notification(monkeypatch):
    row = SimpleNamespace(
        id="n1",
        badge_code="share_station",
        level=1,
        change_type="unlock",
        created_at=None,
    )
    FakeNotification.query = FakeNotificationQuery([row])
    monkeypatch.setattr(badge_service, "UserBadgeNotification", FakeNotification)
    monkeypatch.setattr(badge_service, "_active_definitions", lambda badge_codes=None: [_definition()])

    result = badge_service.list_unread_changes("u1")

    assert result["total"] == 1
    assert result["list"][0]["id"] == "n1"
    assert result["list"][0]["badgeName"] == "share_station"
    assert result["list"][0]["changeType"] == "unlock"


def test_update_equipped_badges_rejects_more_than_three_badges():
    try:
        badge_service.update_equipped_badges("u1", ["b1", "b2", "b3", "b4"])
    except ValueError as err:
        assert str(err) == "最多只能佩戴 3 个徽章"
    else:
        raise AssertionError("update_equipped_badges should reject more than three badges")


def test_update_equipped_badges_rejects_locked_badge(monkeypatch):
    monkeypatch.setattr(badge_service, "evaluate_user_badges", lambda user_id: None)
    monkeypatch.setattr(badge_service, "_active_definitions", lambda badge_codes=None: [_definition("share_station")])
    monkeypatch.setattr(badge_service, "BadgeDefinition", FakeBadgeDefinition)
    monkeypatch.setattr(badge_service, "UserBadge", FakeUserBadge)
    FakeBadgeDefinition.query = FakeBadgeDefinitionQuery([])
    FakeUserBadge.query = FakeUserBadgeQuery([])

    try:
        badge_service.update_equipped_badges("u1", ["share_station"])
    except ValueError as err:
        assert str(err) == "只能佩戴已获取的徽章"
    else:
        raise AssertionError("update_equipped_badges should reject locked badges")


def test_update_equipped_badges_rejects_disabled_database_badge_before_catalog_fallback(monkeypatch):
    monkeypatch.setattr(badge_service, "evaluate_user_badges", lambda user_id: None)
    monkeypatch.setattr(badge_service, "_active_definitions", lambda badge_codes=None: [_definition("share_station")])
    monkeypatch.setattr(badge_service, "BadgeDefinition", FakeBadgeDefinition)
    monkeypatch.setattr(badge_service, "UserBadge", FakeUserBadge)
    FakeBadgeDefinition.query = FakeBadgeDefinitionQuery([SimpleNamespace(code="share_station", enabled=False)])
    FakeUserBadge.query = FakeUserBadgeQuery(
        [
            SimpleNamespace(
                user_id="u1",
                badge_code="share_station",
                level=3,
                current_progress=75,
                target=200,
                unlocked_at=None,
            )
        ]
    )

    try:
        badge_service.update_equipped_badges("u1", ["share_station"])
    except ValueError as err:
        assert str(err) == "徽章不存在或不可用"
    else:
        raise AssertionError("update_equipped_badges should reject disabled database badges")


def test_update_equipped_badges_replaces_rows_and_returns_current_levels(monkeypatch):
    session = FakeSession()
    existing_equipped = [SimpleNamespace(user_id="u1", badge_code="old_badge", slot_order=1)]
    FakeEquippedBadge.query = FakeEquippedBadgeQuery(existing_equipped)
    FakeBadgeDefinition.query = FakeBadgeDefinitionQuery([])
    FakeUserBadge.query = FakeUserBadgeQuery(
        [
            SimpleNamespace(
                user_id="u1",
                badge_code="share_station",
                level=3,
                current_progress=75,
                target=200,
                unlocked_at=None,
            )
        ]
    )

    monkeypatch.setattr(badge_service, "evaluate_user_badges", lambda user_id: None)
    monkeypatch.setattr(badge_service, "_active_definitions", lambda badge_codes=None: [_definition("share_station")])
    monkeypatch.setattr(badge_service, "BadgeDefinition", FakeBadgeDefinition)
    monkeypatch.setattr(badge_service, "UserBadge", FakeUserBadge)
    monkeypatch.setattr(badge_service, "UserEquippedBadge", FakeEquippedBadge)
    monkeypatch.setattr(badge_service.db, "session", session)

    result = badge_service.update_equipped_badges("u1", ["share_station"])

    assert FakeEquippedBadge.query.deleted is True
    assert session.committed is True
    assert session.added[0].badge_code == "share_station"
    assert session.added[0].slot_order == 1
    assert result["maxEquipped"] == 3
    assert result["list"][0]["code"] == "share_station"
    assert result["list"][0]["level"] == 3
    assert result["list"][0]["slotOrder"] == 1


def test_list_equipped_badges_reflects_current_user_badge_level(monkeypatch):
    equipped_rows = [SimpleNamespace(user_id="u1", badge_code="share_station", slot_order=1)]
    FakeEquippedBadge.query = FakeEquippedBadgeQuery(equipped_rows)
    FakeUserBadge.query = FakeUserBadgeQuery(
        [
            SimpleNamespace(
                user_id="u1",
                badge_code="share_station",
                level=4,
                current_progress=250,
                target=200,
                unlocked_at=None,
            )
        ]
    )

    monkeypatch.setattr(badge_service, "evaluate_user_badges", lambda user_id: None)
    monkeypatch.setattr(badge_service, "_active_definitions", lambda badge_codes=None: [_definition("share_station")])
    monkeypatch.setattr(badge_service, "UserBadge", FakeUserBadge)
    monkeypatch.setattr(badge_service, "UserEquippedBadge", FakeEquippedBadge)

    result = badge_service.list_equipped_badges("u1")

    assert result["list"][0]["level"] == 4
    assert result["list"][0]["slotOrder"] == 1


def test_evaluate_user_badges_sets_target_from_upgraded_level(monkeypatch):
    session = FakeSession()
    existing = SimpleNamespace(
        user_id="u1",
        badge_code="share_station",
        level=2,
        current_progress=10,
        target=50,
        unlocked_at=None,
        last_evaluated_at=None,
    )
    FakeUserBadge.query = FakeUserBadgeQuery([existing])

    monkeypatch.setattr(badge_service, "_active_definitions", lambda badge_codes=None: [_definition()])
    monkeypatch.setattr(badge_service, "collect_metrics", lambda user_id, metric_keys: {"plaza_card_count": 75})
    monkeypatch.setattr(badge_service, "UserBadge", FakeUserBadge)
    monkeypatch.setattr(badge_service.db, "session", session)

    result = badge_service.evaluate_user_badges(user_id="u1")

    assert existing.level == 3
    assert existing.current_progress == 75
    assert existing.target == 200
    assert result["newUnlocks"] == []
    assert result["upgrades"][0]["level"] == 3
    assert result["upgrades"][0]["target"] == 200
    assert session.committed is True

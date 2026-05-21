from datetime import date, datetime
from types import SimpleNamespace

import pytest

from services import diary_service


class _SessionSpy:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.commits = 0

    def add(self, value):
        self.added.append(value)

    def delete(self, value):
        self.deleted.append(value)

    def commit(self):
        self.commits += 1

    def refresh(self, _value):
        return None


def test_create_entry_rejects_blank_content():
    with pytest.raises(ValueError):
        diary_service.create_entry("u1", "happy", "   ")


def test_create_entry_success_trims_content(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(diary_service.db, "session", session)

    class _DiaryEntry:
        def __init__(self, user_id, mood_tag, content, is_public, created_date):
            self.id = "d1"
            self.user_id = user_id
            self.mood_tag = mood_tag
            self.content = content
            self.is_public = is_public
            self.created_date = created_date
            self.created_at = datetime(2026, 5, 7, 11, 30, 0)

    monkeypatch.setattr(diary_service, "DiaryEntry", _DiaryEntry)

    payload = diary_service.create_entry("u1", "happy", "  good day  ", is_public=True)

    assert payload["id"] == "d1"
    assert payload["createdAt"].endswith("Z")
    assert session.added[0].content == "good day"
    assert session.commits == 1


def test_list_timeline_returns_truncated_snippet(monkeypatch):
    entry = SimpleNamespace(
        id="d1",
        created_date=date(2026, 5, 7),
        created_at=datetime(2026, 5, 7, 12, 0, 0),
        mood_tag=SimpleNamespace(value="calm"),
        content="x" * 30,
    )
    pagination = SimpleNamespace(items=[entry], total=1)

    class _Query:
        def filter_by(self, **_kwargs):
            return self

        def order_by(self, *_args):
            return self

        def paginate(self, **_kwargs):
            return pagination

    class _Field:
        @staticmethod
        def desc():
            return None

    class _DiaryEntry:
        query = _Query()
        created_date = _Field()
        created_at = _Field()

    monkeypatch.setattr(diary_service, "DiaryEntry", _DiaryEntry)

    payload = diary_service.list_timeline("u1", page=1, limit=10)

    assert payload["totalDays"] == 1
    assert payload["list"][0]["snippet"].endswith("...")


def test_update_entry_requires_mutable_fields(monkeypatch):
    class _Query:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(user_id="u1")

    class _DiaryEntry:
        query = _Query()

    monkeypatch.setattr(diary_service, "DiaryEntry", _DiaryEntry)

    with pytest.raises(ValueError):
        diary_service.update_entry("u1", "d1", {})


def test_delete_entry_success(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(diary_service.db, "session", session)

    entry = SimpleNamespace(user_id="u1")

    class _Query:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return entry

    class _DiaryEntry:
        query = _Query()

    monkeypatch.setattr(diary_service, "DiaryEntry", _DiaryEntry)

    payload = diary_service.delete_entry("u1", "d1")

    assert payload == {"success": True}
    assert session.deleted == [entry]
    assert session.commits == 1

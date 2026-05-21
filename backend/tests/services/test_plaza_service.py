from datetime import datetime
from types import SimpleNamespace

import pytest

from services import plaza_service


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


def test_cursor_encode_decode_roundtrip():
    created_at = datetime(2026, 5, 7, 12, 0, 0)

    cursor = plaza_service._encode_cursor(created_at, "c1")
    restored_time, restored_id = plaza_service._decode_cursor(cursor)

    assert restored_time == created_at
    assert restored_id == "c1"


def test_decode_cursor_rejects_invalid_value():
    with pytest.raises(ValueError):
        plaza_service._decode_cursor("invalid!!!")


def test_list_cards_rejects_invalid_limit():
    with pytest.raises(ValueError):
        plaza_service.list_cards("u1", tab="latest", limit=0)


def test_create_card_rejects_invalid_type():
    with pytest.raises(ValueError):
        plaza_service.create_card("u1", {"type": "bad", "sourceId": "x", "snapshotUrl": "https://x"})


def test_toggle_like_adds_relation_and_increments_count(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(plaza_service.db, "session", session)

    card = SimpleNamespace(id="c1", likes_count=0)

    class _CardQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return card

    class _LikeQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return None

    class _Like:
        query = _LikeQuery()

        def __init__(self, user_id, card_id):
            self.user_id = user_id
            self.card_id = card_id

    class _PlazaCard:
        query = _CardQuery()

    monkeypatch.setattr(plaza_service, "PlazaCard", _PlazaCard)
    monkeypatch.setattr(plaza_service, "Like", _Like)

    payload = plaza_service.toggle_like("u1", "c1", "like")

    assert payload == {"cardId": "c1", "likes": 1, "isLiked": True}
    assert session.commits == 1
    assert len(session.added) == 1


def test_delete_card_checks_permission(monkeypatch):
    card = SimpleNamespace(user_id="owner")

    class _CardQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return card

    class _PlazaCard:
        query = _CardQuery()

    monkeypatch.setattr(plaza_service, "PlazaCard", _PlazaCard)

    with pytest.raises(PermissionError):
        plaza_service.delete_card("other", "c1")

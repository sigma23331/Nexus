from datetime import datetime
from types import SimpleNamespace

import pytest

from services import plaza_comment_service


class _Field:
    @staticmethod
    def desc():
        return None

    @staticmethod
    def asc():
        return None

    def __lt__(self, _other):
        return True

    def __gt__(self, _other):
        return True

    def __eq__(self, _other):
        return True

    def in_(self, _values):
        return True


class _SessionSpy:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.flushed = 0

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.commits += 1

    def flush(self):
        self.flushed += 1

    def refresh(self, _value):
        return None


def _review(action):
    return plaza_comment_service.content_review_service.ReviewResult(action=action)


def test_create_comment_creates_visible_top_level(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(plaza_comment_service.db, "session", session)
    monkeypatch.setattr(plaza_comment_service, "_bump_comment_count", lambda **_: None)
    monkeypatch.setattr(
        plaza_comment_service.content_review_service,
        "review_user_generated_text",
        lambda **_: _review(plaza_comment_service.content_review_service.ACTION_PASS),
    )

    card = SimpleNamespace(id="card1")

    class _CardQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return card

    class _Card:
        query = _CardQuery()

    class _Comment:
        def __init__(self, **kwargs):
            self.id = "cm1"
            self.created_at = datetime(2026, 5, 7, 12, 0, 0)
            self.user = SimpleNamespace(id=kwargs["user_id"], nickname="nick", avatar="")
            self.reply_to_user = None
            for key, value in kwargs.items():
                setattr(self, key, value)

    monkeypatch.setattr(plaza_comment_service, "PlazaCard", _Card)
    monkeypatch.setattr(plaza_comment_service, "PlazaComment", _Comment)

    payload = plaza_comment_service.create_comment("u1", "card1", "hello")

    assert payload["commentId"] == "cm1"
    assert payload["status"] == "visible"
    assert session.commits == 1


def test_create_comment_sets_pending_review(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(plaza_comment_service.db, "session", session)
    bump_calls = []
    monkeypatch.setattr(plaza_comment_service, "_bump_comment_count", lambda **kwargs: bump_calls.append(kwargs))
    monkeypatch.setattr(
        plaza_comment_service.content_review_service,
        "review_user_generated_text",
        lambda **_: _review(plaza_comment_service.content_review_service.ACTION_REVIEW),
    )

    class _CardQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="card1")

    class _Card:
        query = _CardQuery()

    class _Comment:
        def __init__(self, **kwargs):
            self.id = "cm2"
            self.created_at = datetime(2026, 5, 7, 12, 0, 0)
            self.user = SimpleNamespace(id=kwargs["user_id"], nickname="nick", avatar="")
            self.reply_to_user = None
            for key, value in kwargs.items():
                setattr(self, key, value)

    monkeypatch.setattr(plaza_comment_service, "PlazaCard", _Card)
    monkeypatch.setattr(plaza_comment_service, "PlazaComment", _Comment)

    payload = plaza_comment_service.create_comment("u1", "card1", "待审评论")

    assert payload["status"] == "pending_review"
    assert bump_calls == []


def test_create_comment_rejects_nested_reply(monkeypatch):
    monkeypatch.setattr(
        plaza_comment_service.content_review_service,
        "review_user_generated_text",
        lambda **_: _review(plaza_comment_service.content_review_service.ACTION_PASS),
    )

    class _CardQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="card1")

    class _Card:
        query = _CardQuery()

    class _CommentQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="p2", card_id="card1", parent_id="root", user_id="u2")

    class _Comment:
        query = _CommentQuery()

    monkeypatch.setattr(plaza_comment_service, "PlazaCard", _Card)
    monkeypatch.setattr(plaza_comment_service, "PlazaComment", _Comment)

    with pytest.raises(ValueError):
        plaza_comment_service.create_comment("u1", "card1", "reply", parent_id="p2")


def test_delete_comment_soft_deletes_and_decrements(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(plaza_comment_service.db, "session", session)
    bump_calls = []
    monkeypatch.setattr(plaza_comment_service, "_bump_comment_count", lambda **kwargs: bump_calls.append(kwargs))

    comment = SimpleNamespace(id="c1", user_id="u1", status="visible", card_id="card1")

    class _CommentQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return comment

    class _Comment:
        query = _CommentQuery()

    monkeypatch.setattr(plaza_comment_service, "PlazaComment", _Comment)

    out = plaza_comment_service.delete_comment("u1", "c1")

    assert out["success"] is True
    assert comment.status == "deleted"
    assert bump_calls == [{"card_id": "card1", "delta": -1}]


def test_report_comment_rejects_duplicate(monkeypatch):
    class _CommentQuery:
        def filter_by(self, **kwargs):
            self.kwargs = kwargs
            return self

        def first(self):
            if self.kwargs.get("id") == "c1":
                return SimpleNamespace(id="c1", status="visible", card_id="card1")
            return object()

    class _Comment:
        query = _CommentQuery()

    class _Report:
        query = _CommentQuery()

    monkeypatch.setattr(plaza_comment_service, "PlazaComment", _Comment)
    monkeypatch.setattr(plaza_comment_service, "PlazaCommentReport", _Report)

    with pytest.raises(ValueError):
        plaza_comment_service.report_comment("u1", "c1", "abuse")


def test_list_comments_returns_reply_preview(monkeypatch):
    top = SimpleNamespace(
        id="top1",
        card_id="card1",
        user_id="u1",
        parent_id=None,
        reply_to_user=None,
        user=SimpleNamespace(id="u1", nickname="u1", avatar=""),
        content="top",
        status="visible",
        created_at=datetime(2026, 5, 7, 12, 0, 0),
    )
    reply = SimpleNamespace(
        id="r1",
        card_id="card1",
        user_id="u2",
        parent_id="top1",
        reply_to_user=SimpleNamespace(id="u1", nickname="u1", avatar=""),
        user=SimpleNamespace(id="u2", nickname="u2", avatar=""),
        content="reply",
        status="visible",
        created_at=datetime(2026, 5, 7, 12, 1, 0),
    )

    class _Query:
        def __init__(self, rows):
            self.rows = rows

        def filter_by(self, **_kwargs):
            return self

        def filter(self, *_args):
            return self

        def order_by(self, *_args):
            return self

        def limit(self, _n):
            return self

        def all(self):
            return self.rows

        def first(self):
            return self.rows[0] if self.rows else None

    class _Comment:
        query = _Query([top])
        created_at = _Field()
        id = _Field()
        parent_id = _Field()

    query_state = {"count": 0}

    def visible_query():
        query_state["count"] += 1
        return _Query([top] if query_state["count"] == 1 else [reply])

    class _CardQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="card1")

    class _Card:
        query = _CardQuery()

    monkeypatch.setattr(plaza_comment_service, "PlazaComment", _Comment)
    monkeypatch.setattr(plaza_comment_service, "PlazaCard", _Card)
    monkeypatch.setattr(plaza_comment_service, "_visible_comment_query", visible_query)
    monkeypatch.setattr(plaza_comment_service.db, "or_", lambda *_args: True)
    monkeypatch.setattr(plaza_comment_service.db, "and_", lambda *_args: True)

    out = plaza_comment_service.list_comments("u1", "card1", limit=20)

    assert out["list"][0]["replyCount"] == 1
    assert out["list"][0]["replies"][0]["commentId"] == "r1"

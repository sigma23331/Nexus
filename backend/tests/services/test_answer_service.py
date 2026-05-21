from datetime import datetime
from types import SimpleNamespace

import pytest

from services import answer_service


class _Field:
    def __eq__(self, _other):
        return True

    def in_(self, _values):
        return True


class _SessionSpy:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.commits = 0
        self.refreshed = []

    def add(self, value):
        self.added.append(value)

    def delete(self, value):
        self.deleted.append(value)

    def commit(self):
        self.commits += 1

    def refresh(self, value):
        self.refreshed.append(value)


def test_ask_question_creates_record_and_returns_payload(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(answer_service.db, "session", session)
    monkeypatch.setattr(
        answer_service.content_generation_service,
        "generate_answer",
        lambda **_: {"answerText": "Keep moving."},
    )

    class _AnswerRecord:
        def __init__(self, user_id, question, answer_text):
            self.id = "ans-1"
            self.user_id = user_id
            self.question = question
            self.answer_text = answer_text
            self.created_at = datetime(2026, 5, 7, 10, 0, 0)

    monkeypatch.setattr(answer_service, "AnswerRecord", _AnswerRecord)

    payload = answer_service.ask_question("u1", "  hello  ")

    assert payload["id"] == "ans-1"
    assert payload["question"] == "hello"
    assert payload["answerText"] == "Keep moving."
    assert payload["createdAt"].endswith("Z")
    assert session.commits == 1
    assert len(session.added) == 1


def test_list_history_marks_favorited_ids(monkeypatch):
    records = [
        SimpleNamespace(
            id="a1",
            question="q1",
            answer_text="t1",
            created_at=datetime(2026, 5, 7, 10, 0, 0),
        ),
        SimpleNamespace(
            id="a2",
            question="q2",
            answer_text="t2",
            created_at=datetime(2026, 5, 7, 9, 0, 0),
        ),
    ]
    pagination = SimpleNamespace(items=records, total=2)

    class _AnswerQuery:
        def filter_by(self, **_kwargs):
            return self

        def order_by(self, *_args):
            return self

        def paginate(self, **_kwargs):
            return pagination

    class _AnswerRecord:
        created_at = SimpleNamespace(desc=lambda: None)
        query = _AnswerQuery()

    class _FavoriteQuery:
        def filter(self, *_args):
            return self

        def all(self):
            return [SimpleNamespace(answer_id="a2")]

    class _Favorite:
        user_id = _Field()
        answer_id = _Field()
        query = _FavoriteQuery()

    monkeypatch.setattr(answer_service, "AnswerRecord", _AnswerRecord)
    monkeypatch.setattr(answer_service, "Favorite", _Favorite)

    payload = answer_service.list_history("u1", page=1, limit=10)

    assert payload["total"] == 2
    assert payload["list"][0]["isFavorited"] is False
    assert payload["list"][1]["isFavorited"] is True


def test_toggle_favorite_raises_when_answer_missing(monkeypatch):
    class _Query:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return None

    class _AnswerRecord:
        query = _Query()

    monkeypatch.setattr(answer_service, "AnswerRecord", _AnswerRecord)

    with pytest.raises(LookupError):
        answer_service.toggle_favorite("u1", "a-missing", "favorite")


def test_toggle_favorite_adds_relation_when_favorite(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(answer_service.db, "session", session)

    class _AnswerQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="a1")

    class _FavoriteQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return None

    class _Favorite:
        query = _FavoriteQuery()

        def __init__(self, user_id, answer_id):
            self.user_id = user_id
            self.answer_id = answer_id

    class _AnswerRecord:
        query = _AnswerQuery()

    monkeypatch.setattr(answer_service, "AnswerRecord", _AnswerRecord)
    monkeypatch.setattr(answer_service, "Favorite", _Favorite)

    result = answer_service.toggle_favorite("u1", "a1", "favorite")

    assert result == {"answerId": "a1", "isFavorited": True}
    assert session.commits == 1
    assert len(session.added) == 1

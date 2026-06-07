from datetime import datetime
from types import SimpleNamespace

import pytest

from services import plaza_service
from models.plaza import PLAZA_CARD_CONTENT_MAX_LENGTH


class _Field:
    @staticmethod
    def desc():
        return None

    def __lt__(self, _other):
        return True

    def __eq__(self, _other):
        return True

    def in_(self, _values):
        return True


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


def _make_card(cid, likes=0):
    return SimpleNamespace(
        id=cid,
        type=SimpleNamespace(value="answer"),
        user=SimpleNamespace(id="u-owner", nickname="nick", avatar=None),
        snapshot_url="https://img.com/a.png",
        content="txt",
        likes_count=likes,
        created_at=datetime(2026, 5, 7, 12, 0, 0),
    )


def test_format_card_falls_back_to_like_query(monkeypatch):
    card = _make_card("c1", likes=2)

    class _LikeQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return object()

    class _Like:
        query = _LikeQuery()

    monkeypatch.setattr(plaza_service, "Like", _Like)

    payload = plaza_service._format_card(card, current_user_id="u1", liked_card_ids=None)

    assert payload["stats"]["isLiked"] is True
    assert payload["owner"]["badges"] == []


def test_list_cards_latest_with_cursor_and_has_more(monkeypatch):
    c1 = _make_card("c1", likes=2)
    c2 = _make_card("c2", likes=1)
    c3 = _make_card("c3", likes=0)

    class _Query:
        def __init__(self):
            self.rows = [c1, c2, c3]

        def order_by(self, *_args):
            return self

        def filter(self, *_args):
            return self

        def limit(self, _n):
            return self

        def all(self):
            return self.rows

    class _PlazaCard:
        query = _Query()
        likes_count = _Field()
        created_at = _Field()
        id = _Field()

    class _LikeQuery:
        def filter(self, *_args):
            return self

        def all(self):
            return [SimpleNamespace(card_id="c1")]

    class _Like:
        query = _LikeQuery()
        user_id = _Field()
        card_id = _Field()

    monkeypatch.setattr(plaza_service.db, "or_", lambda *_args: True)
    monkeypatch.setattr(plaza_service.db, "and_", lambda *_args: True)
    monkeypatch.setattr(plaza_service, "PlazaCard", _PlazaCard)
    monkeypatch.setattr(plaza_service, "Like", _Like)
    monkeypatch.setattr(
        plaza_service,
        "_equipped_badges_by_user_ids",
        lambda user_ids: {"u-owner": [{"code": "share_station", "slotOrder": 1}]},
    )

    cursor = plaza_service._encode_cursor(datetime(2026, 5, 7, 12, 0, 0), "c9")
    out = plaza_service.list_cards("u1", tab="latest", cursor=cursor, limit=2)

    assert out["hasMore"] is True
    assert out["nextCursor"] is not None
    assert len(out["list"]) == 2
    assert out["list"][0]["stats"]["isLiked"] is True
    assert out["list"][0]["owner"]["badges"][0]["code"] == "share_station"


def test_create_card_validates_tags_type_and_count():
    with pytest.raises(ValueError):
        plaza_service.create_card("u1", {"type": "answer", "sourceId": "a1", "snapshotUrl": "https://a", "tags": "x"})

    with pytest.raises(ValueError):
        plaza_service.create_card(
            "u1",
            {"type": "answer", "sourceId": "a1", "snapshotUrl": "https://a", "tags": ["a", "b", "c", "d"]},
        )


def test_create_card_allows_fortune_content_over_100(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(plaza_service.db, "session", session)

    class _FortuneQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="f1")

    class _FortuneRecord:
        query = _FortuneQuery()

    class _UserQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="u1", nickname="n", avatar="")

    class _User:
        query = _UserQuery()

    class _LikeQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return None

    class _Like:
        query = _LikeQuery()

    class _Card:
        def __init__(self, user_id, type, snapshot_url, content, tags, likes_count):
            self.id = "c1"
            self.user_id = user_id
            self.type = type
            self.snapshot_url = snapshot_url
            self.content = content
            self.tags = tags
            self.likes_count = likes_count
            self.answer_id = None
            self.fortune_id = None
            self.created_at = datetime(2026, 5, 7, 12, 0, 0)
            self.user = None

    content = "\n".join(
        [
            "晨光微启（88分）",
            "顺势而为，稳步推进今天最重要的目标。",
            "先处理一件关键小事，再给自己留一点缓冲。",
            "宜：整理计划、主动沟通、按时休息",
            "忌：临时变卦、过度承诺、熬夜硬撑",
            "爱情：表达可以直接一点，但不要急着要回应",
            "事业：适合推进已有任务，先交付再扩展",
            "健康：留意肩颈和睡眠，晚间减少屏幕时间",
            "财富：消费前先确认预算，避免情绪化下单",
        ]
    )
    assert len(content) > 100

    monkeypatch.setattr(plaza_service, "FortuneRecord", _FortuneRecord)
    monkeypatch.setattr(plaza_service, "User", _User)
    monkeypatch.setattr(plaza_service, "Like", _Like)
    monkeypatch.setattr(plaza_service, "PlazaCard", _Card)
    monkeypatch.setattr(plaza_service, "_equipped_badges_by_user_ids", lambda user_ids: {})
    monkeypatch.setattr("services.badge_service.evaluate_after_event", lambda **_kwargs: None)

    out = plaza_service.create_card(
        "u1",
        {"type": "fortune", "sourceId": "f1", "snapshotUrl": "https://img", "content": content},
    )

    assert out["type"] == "fortune"
    assert out["content"] == content
    assert session.commits == 1


def test_create_card_rejects_content_over_limit():
    content = "x" * (PLAZA_CARD_CONTENT_MAX_LENGTH + 1)

    with pytest.raises(ValueError, match=f"content 长度不能超过{PLAZA_CARD_CONTENT_MAX_LENGTH}"):
        plaza_service.create_card(
            "u1",
            {"type": "answer", "sourceId": "a1", "snapshotUrl": "https://img", "content": content},
        )


def test_create_card_answer_and_fortune_success(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(plaza_service.db, "session", session)

    class _AnswerQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="a1")

    class _AnswerRecord:
        query = _AnswerQuery()

    class _FortuneQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="f1")

    class _FortuneRecord:
        query = _FortuneQuery()

    class _UserQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="u1", nickname="n", avatar="")

    class _User:
        query = _UserQuery()

    class _LikeQuery:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return None

    class _Like:
        query = _LikeQuery()

    class _Card:
        def __init__(self, user_id, type, snapshot_url, content, tags, likes_count):
            self.id = "c1"
            self.user_id = user_id
            self.type = type
            self.snapshot_url = snapshot_url
            self.content = content
            self.tags = tags
            self.likes_count = likes_count
            self.answer_id = None
            self.fortune_id = None
            self.created_at = datetime(2026, 5, 7, 12, 0, 0)
            self.user = None

    monkeypatch.setattr(plaza_service, "AnswerRecord", _AnswerRecord)
    monkeypatch.setattr(plaza_service, "FortuneRecord", _FortuneRecord)
    monkeypatch.setattr(plaza_service, "User", _User)
    monkeypatch.setattr(plaza_service, "Like", _Like)
    monkeypatch.setattr(plaza_service, "PlazaCard", _Card)
    monkeypatch.setattr(
        plaza_service,
        "_equipped_badges_by_user_ids",
        lambda user_ids: {"u1": [{"code": "share_station", "slotOrder": 1}]},
    )

    ans = plaza_service.create_card(
        "u1",
        {"type": "answer", "sourceId": "a1", "snapshotUrl": "https://img", "content": "ok"},
    )
    fort = plaza_service.create_card(
        "u1",
        {"type": "fortune", "sourceId": "f1", "snapshotUrl": "https://img", "content": "ok"},
    )

    assert ans["type"] == "answer"
    assert fort["type"] == "fortune"
    assert ans["owner"]["badges"][0]["code"] == "share_station"
    assert session.commits == 2


def test_toggle_like_unlike_and_not_found(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(plaza_service.db, "session", session)

    card = SimpleNamespace(id="c1", likes_count=1)
    relation = SimpleNamespace(user_id="u1", card_id="c1")

    class _CardQuery:
        def __init__(self, found=True):
            self.found = found

        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return card if self.found else None

    class _LikeQuery:
        def __init__(self, rel):
            self.rel = rel

        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return self.rel

    class _Like:
        def __init__(self, user_id, card_id):
            self.user_id = user_id
            self.card_id = card_id

    _Like.query = _LikeQuery(relation)

    class _PlazaCard:
        query = _CardQuery(found=True)

    monkeypatch.setattr(plaza_service, "PlazaCard", _PlazaCard)
    monkeypatch.setattr(plaza_service, "Like", _Like)

    out = plaza_service.toggle_like("u1", "c1", "unlike")
    assert out["isLiked"] is False
    assert session.deleted == [relation]

    _PlazaCard.query = _CardQuery(found=False)
    with pytest.raises(LookupError):
        plaza_service.toggle_like("u1", "missing", "like")


def test_delete_card_success_and_missing(monkeypatch):
    session = _SessionSpy()
    monkeypatch.setattr(plaza_service.db, "session", session)

    card = SimpleNamespace(user_id="u1")

    class _CardQuery:
        def __init__(self, found=True):
            self.found = found

        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return card if self.found else None

    class _PlazaCard:
        query = _CardQuery(found=True)

    monkeypatch.setattr(plaza_service, "PlazaCard", _PlazaCard)

    ok = plaza_service.delete_card("u1", "c1")
    assert ok["success"] is True

    _PlazaCard.query = _CardQuery(found=False)
    with pytest.raises(LookupError):
        plaza_service.delete_card("u1", "c2")

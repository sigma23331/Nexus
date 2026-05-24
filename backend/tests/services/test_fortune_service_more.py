from datetime import date
from types import SimpleNamespace

from services import fortune_service


class _Field:
    def __lt__(self, _other):
        return True

    def __le__(self, _other):
        return True

    def __ge__(self, _other):
        return True

    def __eq__(self, _other):
        return True

    @staticmethod
    def desc():
        return None

    @staticmethod
    def asc():
        return None


def test_resolve_gua_meaning_and_lucky_hour_cover_branches():
    assert fortune_service._resolve_gua_meaning(80, delta=9)[0] == "雷火丰"
    assert fortune_service._resolve_gua_meaning(78, delta=-9)[0] == "坎水偏盛"
    assert fortune_service._resolve_lucky_hour(91)["name"] == "辰时"
    assert fortune_service._resolve_lucky_hour(67)["name"] == "未时"


def test_deserialize_content_pair_with_dict_json_and_empty():
    main, sub = fortune_service._deserialize_content_pair('{"content_main":"A","content_sub":"B"}')
    assert main == "A"
    assert sub == "B"

    main2, sub2 = fortune_service._deserialize_content_pair("")
    assert main2 == ""
    assert "心静" in sub2


def test_get_global_stats_handles_empty_and_non_empty(monkeypatch):
    class _QueryEmpty:
        def filter_by(self, **_kwargs):
            return self

        def all(self):
            return []

    class _FortuneRecordEmpty:
        query = _QueryEmpty()

    monkeypatch.setattr(fortune_service, "FortuneRecord", _FortuneRecordEmpty)
    empty_payload = fortune_service.get_global_stats(date(2026, 5, 7))
    assert empty_payload["averageScore"] == 0
    assert empty_payload["totalParticipants"] == 0

    records = [
        SimpleNamespace(score=80, title="上吉"),
        SimpleNamespace(score=90, title="上吉"),
        SimpleNamespace(score=70, title="中平"),
    ]

    class _QueryFilled:
        def filter_by(self, **_kwargs):
            return self

        def all(self):
            return records

    class _FortuneRecordFilled:
        query = _QueryFilled()

    monkeypatch.setattr(fortune_service, "FortuneRecord", _FortuneRecordFilled)
    payload = fortune_service.get_global_stats(date(2026, 5, 7))
    assert payload["averageScore"] == 80.0
    assert payload["topTitle"] == "上吉"
    assert payload["topTitleRatio"] == 0.67


def test_get_trend_fills_missing_days(monkeypatch):
    records = [
        SimpleNamespace(date=date(2026, 5, 6), score=88),
    ]

    class _Query:
        def filter(self, *_args):
            return self

        def order_by(self, *_args):
            return self

        def all(self):
            return records

    class _FortuneRecord:
        query = _Query()
        user_id = _Field()
        date = _Field()

    monkeypatch.setattr(fortune_service, "FortuneRecord", _FortuneRecord)

    payload = fortune_service.get_trend("u1", days=2)

    assert len(payload["trendPoints"]) == 2
    assert payload["trendPoints"][1]["value"] in (0, 88)


def test_get_today_fortune_generates_record_when_absent(monkeypatch):
    calls = {"add": 0, "commit": 0, "refresh": 0}

    class _Session:
        def add(self, _value):
            calls["add"] += 1

        def commit(self):
            calls["commit"] += 1

        def refresh(self, _value):
            calls["refresh"] += 1

    monkeypatch.setattr(fortune_service.db, "session", _Session())
    monkeypatch.setattr(
        fortune_service.content_generation_service,
        "generate_fortune",
        lambda **_: {
            "score": 82,
            "title": "上吉",
            "content_main": "顺势",
            "content_sub": "稳住",
            "love": "平稳",
            "career": "向好",
            "health": "稳定",
            "wealth": "平稳",
            "yi": ["学习"],
            "ji": ["熬夜"],
            "gua_meaning_lines": ["木火通明", "思路清朗，宜扩展布局"],
            "lucky_hour_name": "午时",
            "lucky_hour_range": "11:00-13:00",
        },
    )
    monkeypatch.setattr(
        fortune_service.content_review_service,
        "review_ai_generated_text",
        lambda **_: fortune_service.content_review_service.ReviewResult(
            action=fortune_service.content_review_service.ACTION_PASS,
        ),
    )

    today = date.today()

    class _Query:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return None

        def filter(self, *_args):
            return self

        def order_by(self, *_args):
            return self

    query = _Query()

    class _FortuneRecord:
        user_id = _Field()
        date = _Field()

        def __init__(
            self,
            user_id,
            date,
            score,
            title,
            content,
            love,
            career,
            health,
            wealth,
            yi,
            ji,
            gua_meaning_lines,
            lucky_hour_name,
            lucky_hour_range,
        ):
            self.id = "f1"
            self.user_id = user_id
            self.date = date
            self.score = score
            self.title = title
            self.content = content
            self.love = love
            self.career = career
            self.health = health
            self.wealth = wealth
            self.yi = yi
            self.ji = ji
            self.gua_meaning_lines = gua_meaning_lines
            self.lucky_hour_name = lucky_hour_name
            self.lucky_hour_range = lucky_hour_range

    _FortuneRecord.query = query

    monkeypatch.setattr(fortune_service, "FortuneRecord", _FortuneRecord)

    payload = fortune_service.get_today_fortune("u1")

    assert payload["date"] == today.isoformat()
    assert payload["love"] == "平稳"
    assert payload["gua_meaning_lines"] == ["木火通明", "思路清朗，宜扩展布局"]
    assert calls["add"] == 1
    assert calls["commit"] == 1


def test_generate_safe_fortune_uses_fallback_when_reviews_fail(monkeypatch):
    generated = []

    def fake_generate_fortune(**_kwargs):
        generated.append(True)
        return {
            "score": 82,
            "title": "涓婂悏",
            "content_main": "unsafe",
            "content_sub": "unsafe",
            "love": "骞崇ǔ",
            "career": "鍚戝ソ",
            "health": "绋冲畾",
            "wealth": "骞崇ǔ",
            "yi": ["瀛︿範"],
            "ji": ["鐔"],
            "gua_meaning_lines": ["G1", "G2"],
            "lucky_hour_name": "N",
            "lucky_hour_range": "R",
        }

    monkeypatch.setattr(fortune_service.content_generation_service, "generate_fortune", fake_generate_fortune)
    monkeypatch.setattr(
        fortune_service.content_generation_service,
        "generate_fallback_fortune",
        lambda _target_date: {
            "score": 70,
            "title": "fallback",
            "content_main": "safe",
            "content_sub": "safe",
            "love": "safe",
            "career": "safe",
            "health": "safe",
            "wealth": "safe",
            "yi": [],
            "ji": [],
            "gua_meaning_lines": ["safe1", "safe2"],
            "lucky_hour_name": "safe",
            "lucky_hour_range": "safe",
            "generatedBy": "fallback",
        },
    )
    monkeypatch.setattr(
        fortune_service.content_review_service,
        "review_ai_generated_text",
        lambda **_: fortune_service.content_review_service.ReviewResult(
            action=fortune_service.content_review_service.ACTION_FALLBACK,
        ),
    )

    payload = fortune_service._generate_safe_fortune("u1", date(2026, 5, 24))

    assert len(generated) == 2
    assert payload["generatedBy"] == "fallback"
    assert payload["content_main"] == "safe"


def test_format_today_payload_falls_back_when_new_columns_missing():
    record = SimpleNamespace(
        id="f1",
        date=SimpleNamespace(isoformat=lambda: "2026-05-21"),
        score=72,
        title="中平",
        content='["保持节奏","先稳后进"]',
        yi=["学习"],
        ji=["拖延"],
    )

    payload = fortune_service._format_today_payload(record, delta=2)

    assert payload["love"] == "平稳"
    assert len(payload["gua_meaning_lines"]) == 2
    assert payload["lucky_hour_name"]

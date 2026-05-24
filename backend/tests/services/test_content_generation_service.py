from datetime import date

import pytest

from services import content_generation_service as cgs


def test_generate_answer_rejects_empty_question():
    with pytest.raises(ValueError, match="question"):
        cgs.generate_answer("   ", user_id="u1")


def test_generate_answer_uses_provider_result(monkeypatch):
    class _Provider:
        def generate_answer(self, question, user_id):
            assert question == "这周面试能过吗？"
            assert user_id == "u1"
            return "会有好结果。"

    monkeypatch.setattr(cgs, "get_provider", lambda: _Provider())

    payload = cgs.generate_answer("这周面试能过吗？", user_id="u1")

    assert payload["answerText"] == "会有好结果。"
    assert payload["generatedBy"] == "provider"


def test_generate_answer_fallback_when_provider_fails(monkeypatch):
    class _Provider:
        def generate_answer(self, question, user_id):
            _ = (question, user_id)
            raise RuntimeError("provider down")

    monkeypatch.setattr(cgs, "get_provider", lambda: _Provider())

    payload = cgs.generate_answer("我应该换工作吗？", user_id="u1")

    assert isinstance(payload["answerText"], str)
    assert payload["answerText"]
    assert payload["generatedBy"] == "fallback"


def test_generate_fortune_returns_required_fields(monkeypatch):
    class _Provider:
        def generate_fortune(self, user_id, target_date):
            assert user_id == "u1"
            assert target_date == date(2026, 4, 25)
            return {
                "score": 88,
                "title": "任意标题",
                "content_main": "适合开启新计划。",
                "content_sub": "稳中求进，心静则明。",
                "love": "中上",
                "career": "平稳",
                "health": "稳定",
                "wealth": "向好",
                "yi": ["学习"],
                "ji": ["熬夜"],
                "gua_meaning_lines": ["火土相生", "顺势加速，主动求进"],
                "lucky_hour_name": "巳时",
                "lucky_hour_range": "09:00-11:00",
            }

    monkeypatch.setattr(cgs, "get_provider", lambda: _Provider())

    payload = cgs.generate_fortune(user_id="u1", target_date=date(2026, 4, 25))

    assert payload["score"] == 88
    assert payload["title"] == "上上签"
    assert payload["content_main"] == "适合开启新计划。"
    assert payload["content_sub"] == "稳中求进，心静则明。"
    assert payload["love"] == "中上"
    assert payload["career"] == "平稳"
    assert payload["health"] == "稳定"
    assert payload["wealth"] == "向好"
    assert payload["gua_meaning_lines"] == ["火土相生", "顺势加速，主动求进"]
    assert payload["lucky_hour_name"] == "巳时"
    assert payload["lucky_hour_range"] == "09:00-11:00"
    assert payload["generatedBy"] == "provider"


def test_score_to_title_matches_frontend_thresholds():
    assert cgs._score_to_title(85) == "上上签"
    assert cgs._score_to_title(75) == "上吉"
    assert cgs._score_to_title(65) == "中平"
    assert cgs._score_to_title(55) == "小吉"
    assert cgs._score_to_title(54) == "守静"


def test_generate_fortune_passes_profile_context_when_available(monkeypatch):
    class _Provider:
        def generate_fortune(self, user_id, target_date, profile_context=None):
            assert user_id == "u1"
            assert profile_context["mood_tendency"] == "calm"
            return {
                "score": 80,
                "content_main": "稳步向前。",
                "content_sub": "聚焦最重要的事。",
                "love": "平稳",
                "career": "向好",
                "health": "稳定",
                "wealth": "谨慎",
                "yi": ["专注"],
                "ji": ["拖延"],
                "gua_meaning_lines": ["阴阳守中", "守正出新，稳步推进"],
                "lucky_hour_name": "午时",
                "lucky_hour_range": "11:00-13:00",
            }

    class _Profile:
        pass

    monkeypatch.setattr(cgs, "get_provider", lambda: _Provider())
    monkeypatch.setattr(cgs.UserProfileService, "get_by_user_id", lambda user_id: _Profile())
    monkeypatch.setattr(
        cgs.UserProfileService,
        "to_dict",
        lambda _profile: {"mood_tendency": "calm", "topic_interests": ["career"], "self_context_tag": "日常"},
    )

    payload = cgs.generate_fortune(user_id="u1", target_date=date(2026, 4, 25))
    assert payload["generatedBy"] == "provider"


def test_generate_fortune_falls_back_to_legacy_provider_signature(monkeypatch):
    class _Provider:
        def __init__(self):
            self.called = 0

        def generate_fortune(self, user_id, target_date):
            self.called += 1
            return {
                "score": 70,
                "content_main": "今日平稳。",
                "content_sub": "保持节奏。",
                "love": "平稳",
                "career": "平稳",
                "health": "稳定",
                "wealth": "平稳",
                "yi": [],
                "ji": [],
                "gua_meaning_lines": ["阴阳守中", "稳步前行，先稳后进"],
                "lucky_hour_name": "午时",
                "lucky_hour_range": "11:00-13:00",
            }

    provider = _Provider()
    monkeypatch.setattr(cgs, "get_provider", lambda: provider)
    monkeypatch.setattr(cgs.UserProfileService, "get_by_user_id", lambda user_id: None)

    payload = cgs.generate_fortune(user_id="u1", target_date=date(2026, 4, 25))
    assert payload["generatedBy"] == "provider"
    assert provider.called == 1


def test_generate_fortune_backfills_missing_new_fields(monkeypatch):
    class _Provider:
        def generate_fortune(self, user_id, target_date):
            _ = (user_id, target_date)
            return {
                "score": 90,
                "content_main": "适合主动出击。",
                "content_sub": "把握势头。",
                "love": "顺畅",
                "career": "高涨",
                "health": "稳定",
                "wealth": "向好",
                "yi": ["沟通"],
                "ji": ["拖延"],
            }

    monkeypatch.setattr(cgs, "get_provider", lambda: _Provider())

    payload = cgs.generate_fortune(user_id="u1", target_date=date(2026, 4, 25))

    assert payload["gua_meaning_lines"]
    assert payload["lucky_hour_name"]
    assert payload["lucky_hour_range"]


def test_generate_fortune_retries_v4_provider_once_then_succeeds(monkeypatch):
    class _Provider:
        prompt_versions = {"fortune": "v4"}
        prompts_dir = None
        max_retries = 1

        def __init__(self):
            self.calls = 0

        def generate_fortune(
            self,
            user_id,
            target_date,
            score=None,
            title_template=None,
            keywords=None,
            yiji_items=None,
        ):
            _ = (user_id, target_date, title_template, keywords, yiji_items)
            self.calls += 1
            if self.calls == 1:
                raise TimeoutError("llm timeout")
            return {
                "score": score,
                "content_main": "A",
                "content_sub": "B",
                "love": "L",
                "career": "C",
                "health": "H",
                "wealth": "W",
                "yi": ["Y"],
                "ji": ["J"],
                "gua_meaning_lines": ["G1", "G2"],
                "lucky_hour_name": "N",
                "lucky_hour_range": "R",
            }

    provider = _Provider()
    monkeypatch.setattr(cgs, "get_provider", lambda: provider)
    monkeypatch.setattr(cgs.UserProfileService, "get_by_user_id", lambda user_id: None)

    payload = cgs.generate_fortune(user_id="u1", target_date=date(2026, 4, 25))

    assert provider.calls == 2
    assert payload["generatedBy"] == "provider"
    assert payload["content_main"] == "A"


def test_generate_fortune_falls_back_after_v4_retries_exhausted(monkeypatch):
    class _Provider:
        prompt_versions = {"fortune": "v4"}
        prompts_dir = None
        max_retries = 1

        def __init__(self):
            self.calls = 0

        def generate_fortune(self, **_kwargs):
            self.calls += 1
            raise RuntimeError("bad json")

    provider = _Provider()
    monkeypatch.setattr(cgs, "get_provider", lambda: provider)
    monkeypatch.setattr(cgs.UserProfileService, "get_by_user_id", lambda user_id: None)

    payload = cgs.generate_fortune(user_id="u1", target_date=date(2026, 4, 25))

    assert provider.calls == 2
    assert payload["generatedBy"] == "fallback"
    assert payload["content_main"]
    assert payload["gua_meaning_lines"]
    assert payload["lucky_hour_name"]


def test_generate_profile_retries_then_succeeds(monkeypatch):
    class _Provider:
        max_retries = 1

        def __init__(self):
            self.calls = 0

        def analyze_user_profile(self, diary_entries, answer_questions):
            _ = (diary_entries, answer_questions)
            self.calls += 1
            if self.calls == 1:
                raise TimeoutError("profile timeout")
            return {
                "mood_tendency": "calm",
                "topic_interests": ["health", "career", "health"],
                "self_context_tag": "daily",
            }

    provider = _Provider()
    monkeypatch.setattr(cgs, "get_provider", lambda: provider)

    payload = cgs.generate_profile(
        diary_entries=[{"content": "ok"}],
        answer_questions=[{"question": "q"}],
    )

    assert provider.calls == 2
    assert payload["generatedBy"] == "provider"
    assert payload["topic_interests"] == ["health", "career"]


def test_generate_profile_falls_back_after_retries_exhausted(monkeypatch):
    class _Provider:
        max_retries = 1

        def __init__(self):
            self.calls = 0

        def analyze_user_profile(self, diary_entries, answer_questions):
            _ = (diary_entries, answer_questions)
            self.calls += 1
            raise RuntimeError("profile bad json")

    provider = _Provider()
    monkeypatch.setattr(cgs, "get_provider", lambda: provider)

    payload = cgs.generate_profile(
        diary_entries=[{"content": "ok"}],
        answer_questions=[{"question": "q"}],
    )

    assert provider.calls == 2
    assert payload["generatedBy"] == "fallback"
    assert payload["mood_tendency"]
    assert payload["topic_interests"]
    assert payload["self_context_tag"]

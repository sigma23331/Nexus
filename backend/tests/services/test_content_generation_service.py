from datetime import date

import pytest

from services import content_generation_service as cgs


def test_generate_answer_rejects_empty_question():
    with pytest.raises(ValueError, match="question 必须为非空字符串"):
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
    assert payload["generatedBy"] == "provider"


def test_score_to_title_matches_frontend_thresholds():
    assert cgs._score_to_title(85) == "上上签"
    assert cgs._score_to_title(75) == "上吉"
    assert cgs._score_to_title(65) == "中平"
    assert cgs._score_to_title(55) == "小谨"
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
            }

    provider = _Provider()
    monkeypatch.setattr(cgs, "get_provider", lambda: provider)
    monkeypatch.setattr(cgs.UserProfileService, "get_by_user_id", lambda user_id: None)

    payload = cgs.generate_fortune(user_id="u1", target_date=date(2026, 4, 25))
    assert payload["generatedBy"] == "provider"
    assert provider.called == 1

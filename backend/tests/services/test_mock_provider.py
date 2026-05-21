from datetime import date
from types import SimpleNamespace

from services.llm.providers.mock_provider import MockProvider


def test_generate_answer_covers_length_buckets():
    provider = MockProvider()

    assert "一步" in provider.generate_answer("短问题", "u1")
    assert "全心投入" in provider.generate_answer("这是一个中等长度问题", "u1")
    assert "保持耐心" in provider.generate_answer("这是一个明显超过二十个字符的长问题用于测试分支", "u1")


def test_generate_fortune_title_thresholds():
    provider = MockProvider()

    high = provider.generate_fortune("u1", date(2026, 5, 15))
    mid = provider.generate_fortune("u1", date(2026, 5, 2))

    assert high["title"] in ("大吉 · 宜行", "小吉 · 守成")
    assert mid["title"] in ("小吉 · 守成", "平稳 · 蓄力")
    assert "yi" in high and "ji" in high
    assert "gua_meaning_lines" in high
    assert "lucky_hour_name" in high


def test_analyze_user_profile_supports_dict_and_object_inputs():
    provider = MockProvider()

    diary_entries = [
        {"mood_tag": "happy", "content": "今天不错"},
        SimpleNamespace(mood_tag="sad", content="有点累"),
    ]
    answer_questions = [
        "要不要换工作",
        {"question": "要不要读研"},
        SimpleNamespace(question="要不要搬家"),
    ]

    result = provider.analyze_user_profile(diary_entries, answer_questions)

    assert result["mood_tendency"] in ("optimistic", "anxious", "calm", "reflective")
    assert isinstance(result["topic_interests"], list)
    assert 1 <= len(result["topic_interests"]) <= 3
    assert isinstance(result["self_context_tag"], str)

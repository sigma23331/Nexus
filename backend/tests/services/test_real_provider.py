from datetime import date
from pathlib import Path

from services.llm.providers.real_provider import FORTUNE_SCHEMA, RealProvider


def _provider():
    return RealProvider(
        model_name="gpt-test",
        api_key="test-key",
        timeout=5,
        max_retries=1,
        base_url="https://example.com/v1",
    )


def test_chat_json_schema_falls_back_when_response_format_unsupported(monkeypatch):
    provider = _provider()
    calls = []

    def fake_chat(messages, temperature=1.5, response_format=None, max_tokens=None):
        _ = (messages, temperature, max_tokens)
        calls.append(response_format)
        if response_format is not None:
            raise RuntimeError("unsupported response_format")
        return '{"score": 88, "title": "大吉", "content_main": "顺势而为", "content_sub": "稳中有进", "love": "中上", "career": "平稳", "health": "稳定", "wealth": "向好", "yi": ["学习"], "ji": ["熬夜"]}'

    monkeypatch.setattr(provider, "_chat", fake_chat)

    payload = provider._chat_json_schema(
        messages=[{"role": "user", "content": "test"}],
        schema_name="fortune_schema",
        schema=FORTUNE_SCHEMA,
        temperature=0.3,
    )

    assert payload["score"] == 88
    assert len(calls) == 2
    assert calls[0] is not None
    assert calls[1] is None


def test_chat_json_schema_uses_deepseek_json_object(monkeypatch):
    provider = RealProvider(
        model_name="deepseek-v4-flash",
        api_key="test-key",
        timeout=5,
        max_retries=1,
        base_url="https://api.deepseek.com",
    )
    captured = {}

    def fake_chat(messages, temperature=1.5, response_format=None, max_tokens=None):
        _ = (messages, temperature, max_tokens)
        captured["response_format"] = response_format
        return '{"score": 80, "title": "吉", "content_main": "顺势而为", "content_sub": "稳中求进", "love": "中上", "career": "平稳", "health": "稳定", "wealth": "向好", "yi": ["学习"], "ji": ["熬夜"]}'

    monkeypatch.setattr(provider, "_chat", fake_chat)

    payload = provider._chat_json_schema(
        messages=[{"role": "user", "content": "test"}],
        schema_name="fortune_schema",
        schema=FORTUNE_SCHEMA,
        temperature=0.3,
    )

    assert payload["score"] == 80
    assert captured["response_format"] == {"type": "json_object"}


def test_generate_fortune_normalizes_and_includes_lucky_fields(monkeypatch):
    provider = _provider()

    def fake_chat_json_schema(messages, schema_name, schema, temperature=0.3, max_tokens=512):
        _ = (messages, schema_name, schema, temperature, max_tokens)
        return {
            "score": 999,
            "title": "上上签上上签上上签上上签上上签上上签",
            "content_main": "A" * 200,
            "content_sub": "B" * 200,
            "love": "爱情运势很旺盛且有很多描述",
            "career": "事业运势平稳上升描述",
            "health": "健康状态总体稳定描述",
            "wealth": "财富方面谨慎增长描述",
            "yi": ["学习打卡学习打卡学习打卡", "", 123, "运动"],
            "ji": ["熬夜熬夜熬夜熬夜熬夜", "拖延"],
        }

    monkeypatch.setattr(provider, "_chat_json_schema", fake_chat_json_schema)

    payload = provider.generate_fortune(user_id="u1", target_date=date(2026, 4, 28))

    assert payload["score"] == 100
    assert len(payload["content_main"]) <= 80
    assert len(payload["content_sub"]) <= 80
    assert len(payload["love"]) <= 20
    assert len(payload["career"]) <= 20
    assert len(payload["health"]) <= 20
    assert len(payload["wealth"]) <= 20
    assert payload["yi"][0] == "学习打卡学习打卡学习打卡"
    assert payload["yi"][1] == "123"


def test_analyze_user_profile_keeps_free_text_and_normalizes_list(monkeypatch):
    provider = _provider()

    def fake_chat_json_schema(messages, schema_name, schema, temperature=0.3, max_tokens=400):
        _ = (messages, schema_name, schema, temperature, max_tokens)
        return {
            "mood_tendency": "depressed",
            "topic_interests": ["unknown", "health", "health", "finance", "career", "study"],
            "self_context_tag": "  备考冲刺阶段备考冲刺阶段备考冲刺阶段  ",
        }

    monkeypatch.setattr(provider, "_chat_json_schema", fake_chat_json_schema)

    payload = provider.analyze_user_profile(
        diary_entries=[{"mood_tag": "anxious", "content": "今天有点焦虑"}],
        answer_questions=[{"question": "要不要换专业"}],
    )

    assert payload["mood_tendency"] == "depressed"
    assert payload["topic_interests"] == ["unknown", "health", "finance"]
    assert len(payload["self_context_tag"]) <= 20


def test_generate_answer_prompt_contains_safety_constraints_and_sentence_truncate(monkeypatch):
    provider = _provider()
    captured = {}

    def fake_chat(messages, temperature=1.5, response_format=None, max_tokens=None):
        captured["messages"] = messages
        captured["temperature"] = temperature
        captured["response_format"] = response_format
        captured["max_tokens"] = max_tokens
        return "第一句完整。" + ("很长" * 60)

    monkeypatch.setattr(provider, "_chat", fake_chat)

    payload = provider.generate_answer("我最近有点迷茫", user_id="u1")

    assert payload == "第一句完整。"
    assert captured["temperature"] == 0.7
    assert captured["response_format"] is None
    prompt_content = captured["messages"][0]["content"]
    assert "我最近有点迷茫" in prompt_content


def test_generate_answer_uses_versioned_prompt_template(monkeypatch, tmp_path):
    provider = RealProvider(
        model_name="gpt-test",
        api_key="test-key",
        timeout=5,
        max_retries=1,
        base_url="https://example.com/v1",
        prompts_dir=tmp_path,
        prompt_versions={"answer": "v9"},
    )
    answer_dir = Path(tmp_path) / "answer"
    answer_dir.mkdir(parents=True)
    (answer_dir / "v9.txt").write_text("Q={{question}}", encoding="utf-8")

    captured = {}

    def fake_chat(messages, temperature=0.7, response_format=None, max_tokens=None):
        _ = (temperature, response_format, max_tokens)
        captured["content"] = messages[0]["content"]
        return "可以"

    monkeypatch.setattr(provider, "_chat", fake_chat)
    out = provider.generate_answer("测试问题", user_id="u1")
    assert out == "可以"
    assert captured["content"] == "Q=测试问题"


def test_generate_fortune_renders_profile_context_into_prompt(monkeypatch, tmp_path):
    provider = RealProvider(
        model_name="gpt-test",
        api_key="test-key",
        timeout=5,
        max_retries=1,
        base_url="https://example.com/v1",
        prompts_dir=tmp_path,
        prompt_versions={"fortune": "v3"},
    )
    fortune_dir = Path(tmp_path) / "fortune"
    fortune_dir.mkdir(parents=True)
    (fortune_dir / "v3.txt").write_text(
        "m={{mood_tendency}};t={{topic_interests}};c={{self_context_tag}};d={{target_date}}",
        encoding="utf-8",
    )

    captured = {}

    def fake_chat_json_schema(messages, schema_name, schema, temperature=0.7, max_tokens=512):
        _ = (schema_name, schema, temperature, max_tokens)
        captured["content"] = messages[0]["content"]
        return {
            "score": 80,
            "content_main": "顺势而为",
            "content_sub": "稳中求进",
            "love": "中上",
            "career": "平稳",
            "health": "稳定",
            "wealth": "向好",
            "yi": ["学习"],
            "ji": ["熬夜"],
        }

    monkeypatch.setattr(provider, "_chat_json_schema", fake_chat_json_schema)
    payload = provider.generate_fortune(
        user_id="u1",
        target_date=date(2026, 4, 28),
        profile_context={
            "mood_tendency": "anxious",
            "topic_interests": ["career", "health"],
            "self_context_tag": "备考期",
        },
    )
    assert payload["score"] == 80
    assert "m=anxious" in captured["content"]
    assert "t=career,health" in captured["content"]


def test_generate_profile_uses_versioned_prompt_template(monkeypatch, tmp_path):
    provider = RealProvider(
        model_name="gpt-test",
        api_key="test-key",
        timeout=5,
        max_retries=1,
        base_url="https://example.com/v1",
        prompts_dir=tmp_path,
        prompt_versions={"profile": "v2"},
    )
    profile_dir = Path(tmp_path) / "profile"
    profile_dir.mkdir(parents=True)
    (profile_dir / "v2.txt").write_text("D={{diary_summary}}|Q={{question_summary}}", encoding="utf-8")

    captured = {}

    def fake_chat_json_schema(messages, schema_name, schema, temperature=0.7, max_tokens=400):
        _ = (schema_name, schema, temperature, max_tokens)
        captured["content"] = messages[0]["content"]
        return {
            "mood_tendency": "calm",
            "topic_interests": ["health"],
            "self_context_tag": "日常",
        }

    monkeypatch.setattr(provider, "_chat_json_schema", fake_chat_json_schema)
    payload = provider.analyze_user_profile(
        diary_entries=[{"mood_tag": "happy", "content": "今天不错"}],
        answer_questions=[{"question": "接下来怎么办"}],
    )
    assert payload["mood_tendency"] == "calm"
    assert "D=[happy] 今天不错" in captured["content"]

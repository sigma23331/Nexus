from backend.tools.prompt_lab.provider_adapter import PromptLabProviderAdapter


def test_mock_answer_sets_nullable_parse_fields():
    adapter = PromptLabProviderAdapter(provider_mode="mock")
    row = adapter.run_answer(question="Q", prompt_text="{{question}}", temperature=0.7)

    assert row["success"] is True
    assert row["parse_success"] is None
    assert row["schema_valid"] is None
    assert row["fallback_used"] is False
    assert row["error_code"] is None
    assert isinstance(row["output_text"], str)


def test_mock_fortune_has_boolean_parse_and_schema():
    adapter = PromptLabProviderAdapter(provider_mode="mock")
    row = adapter.run_fortune(target_date="2026-04-29", prompt_text="{{target_date}}", temperature=0.58)

    assert row["success"] is True
    assert isinstance(row["parse_success"], bool)
    assert isinstance(row["schema_valid"], bool)
    assert row["schema_valid"] is True
    assert '"content_main"' in row["output_preview"]
    assert '"content_main"' in row["output_text"]


def test_real_mode_maps_model_to_real_provider_constructor(monkeypatch):
    captured = {}

    class FakeRealProvider:
        def __init__(self, model_name, api_key, timeout, max_retries, base_url=None):
            captured["model_name"] = model_name
            captured["api_key"] = api_key
            captured["timeout"] = timeout
            captured["max_retries"] = max_retries
            captured["base_url"] = base_url

        def _chat(self, messages, temperature=1.5):
            _ = (messages, temperature)
            return "ok"

        def _extract_json(self, text):
            _ = text
            return {}

    monkeypatch.setattr("backend.tools.prompt_lab.provider_adapter.RealProvider", FakeRealProvider)

    PromptLabProviderAdapter(
        provider_mode="real",
        model="test-model",
        api_key="test-key",
        base_url="https://example.com/v1",
        timeout=9,
        max_retries=2,
    )

    assert captured["model_name"] == "test-model"
    assert captured["api_key"] == "test-key"
    assert captured["timeout"] == 9
    assert captured["max_retries"] == 2


def test_profile_parse_error_sets_error_code(monkeypatch):
    class FakeRealProvider:
        def __init__(self, model_name, api_key, timeout, max_retries, base_url=None):
            _ = (model_name, api_key, timeout, max_retries, base_url)

        def _chat(self, messages, temperature=1.5, frequency_penalty=None, top_p=None):
            _ = (messages, temperature, frequency_penalty, top_p)
            return "not-json"

        def _extract_json(self, text):
            _ = text
            raise ValueError("bad json")

    monkeypatch.setattr("backend.tools.prompt_lab.provider_adapter.RealProvider", FakeRealProvider)

    adapter = PromptLabProviderAdapter(provider_mode="real", model="m", api_key="k")
    row = adapter.run_profile(
        diary_entries=[],
        answer_questions=[],
        prompt_text="{{diary_summary}}\n{{question_summary}}",
        temperature=0.3,
    )

    assert row["success"] is False
    assert row["parse_success"] is False
    assert row["schema_valid"] is False
    assert row["error_code"] == "parse_error"

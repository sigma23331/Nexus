from flask import Flask

from backend.services import prompt_lab_service


def _app_context():
    app = Flask(__name__)
    app.config.update(
        LLM_PROVIDER="mock",
        LLM_BASE_URL="https://example.local/v1",
        LLM_MODEL_NAME="test-model",
        LLM_API_KEY="test-key",
        LLM_TIMEOUT=9,
        LLM_MAX_RETRIES=2,
    )
    return app.app_context()


def test_run_answer_success_returns_normalized_fields_and_uses_runtime_config(monkeypatch):
    captured = {}

    class FakeAdapter:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run_answer(self, question, prompt_text, temperature, frequency_penalty=None, top_p=None):
            _ = (prompt_text, frequency_penalty, top_p)
            return {
                "success": True,
                "output_text": f"A:{question}:{temperature}",
                "output_preview": "x" * 300,
                "latency_ms": 12,
                "parse_success": None,
                "schema_valid": None,
                "fallback_used": False,
                "error_code": None,
                "error_message": None,
            }

    monkeypatch.setattr(prompt_lab_service, "PromptLabProviderAdapter", FakeAdapter)

    with _app_context():
        result = prompt_lab_service.run_prompt_lab(
            task="answer",
            prompt_text="You are concise.",
            temperature=0.7,
            input_payload={"question": "今天运势如何"},
        )

    assert result["task"] == "answer"
    assert result["success"] is True
    assert result["output_text"].startswith("A:")
    assert result["parse_success"] is None
    assert result["schema_valid"] is None
    assert len(result["output_preview"]) <= 120
    assert result["error_code"] is None
    assert captured["provider_mode"] == "mock"
    assert captured["base_url"] == "https://example.local/v1"
    assert captured["model"] == "test-model"
    assert captured["api_key"] == "test-key"
    assert captured["timeout"] == 9
    assert captured["max_retries"] == 2


def test_run_answer_forwards_frequency_penalty_and_top_p(monkeypatch):
    captured = {}

    class FakeAdapter:
        def __init__(self, **kwargs):
            _ = kwargs

        def run_answer(self, question, prompt_text, temperature, frequency_penalty=None, top_p=None):
            captured["question"] = question
            captured["prompt_text"] = prompt_text
            captured["temperature"] = temperature
            captured["frequency_penalty"] = frequency_penalty
            captured["top_p"] = top_p
            return {
                "success": True,
                "output_text": "ok",
                "output_preview": "ok",
                "latency_ms": 10,
                "parse_success": None,
                "schema_valid": None,
                "fallback_used": False,
                "error_code": None,
                "error_message": None,
            }

    monkeypatch.setattr(prompt_lab_service, "PromptLabProviderAdapter", FakeAdapter)

    with _app_context():
        result = prompt_lab_service.run_prompt_lab(
            task="answer",
            prompt_text="prompt",
            temperature=0.9,
            input_payload={"question": "q"},
            frequency_penalty=0.6,
            top_p=0.75,
        )

    assert result["success"] is True
    assert captured["frequency_penalty"] == 0.6
    assert captured["top_p"] == 0.75


def test_frequency_penalty_out_of_range_returns_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="answer",
        prompt_text="prompt",
        temperature=0.6,
        input_payload={"question": "q"},
        frequency_penalty=2.1,
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_top_p_out_of_range_returns_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="answer",
        prompt_text="prompt",
        temperature=0.6,
        input_payload={"question": "q"},
        top_p=1.2,
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_run_fortune_invalid_date_returns_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="fortune",
        prompt_text="prompt",
        temperature=0.6,
        input_payload={"target_date": "2026-99-99"},
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_prompt_too_long_returns_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="answer",
        prompt_text="x" * 12001,
        temperature=0.6,
        input_payload={"question": "q"},
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_invalid_task_returns_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="unknown",
        prompt_text="prompt",
        temperature=0.6,
        input_payload={},
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_temperature_out_of_range_returns_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="answer",
        prompt_text="prompt",
        temperature=2.1,
        input_payload={"question": "q"},
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_run_profile_missing_fields_returns_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="profile",
        prompt_text="prompt",
        temperature=0.6,
        input_payload={"diary_entries": []},
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_answer_question_too_long_returns_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="answer",
        prompt_text="prompt",
        temperature=0.6,
        input_payload={"question": "q" * 201},
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_profile_array_limits_return_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="profile",
        prompt_text="prompt",
        temperature=0.6,
        input_payload={
            "diary_entries": [{"content": "ok"}] * 51,
            "answer_questions": [],
        },
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_profile_answer_question_item_limits_return_validation_error():
    result = prompt_lab_service.run_prompt_lab(
        task="profile",
        prompt_text="prompt",
        temperature=0.6,
        input_payload={
            "diary_entries": [{"content": "ok"}],
            "answer_questions": [{"question": "q" * 501, "answer": "ok"}],
        },
    )
    assert result["success"] is False
    assert result["error_code"] == "validation_error"


def test_provider_row_with_unknown_error_code_maps_to_unexpected(monkeypatch):
    class FakeAdapter:
        def __init__(self, **kwargs):
            _ = kwargs

        def run_answer(self, question, prompt_text, temperature, frequency_penalty=None, top_p=None):
            _ = (question, prompt_text, temperature, frequency_penalty, top_p)
            return {
                "success": False,
                "output_text": "",
                "output_preview": "",
                "latency_ms": 1,
                "parse_success": None,
                "schema_valid": None,
                "fallback_used": False,
                "error_code": "bad_code",
                "error_message": "boom",
            }

    monkeypatch.setattr(prompt_lab_service, "PromptLabProviderAdapter", FakeAdapter)

    with _app_context():
        result = prompt_lab_service.run_prompt_lab(
            task="answer",
            prompt_text="x",
            temperature=1.0,
            input_payload={"question": "q"},
        )

    assert result["success"] is False
    assert result["error_code"] == "unexpected_error"


def test_run_fortune_success_dispatch_and_boolean_fields_preserved(monkeypatch):
    class FakeAdapter:
        def __init__(self, **kwargs):
            _ = kwargs

        def run_fortune(self, target_date, prompt_text, temperature, frequency_penalty=None, top_p=None):
            _ = (target_date, prompt_text, temperature, frequency_penalty, top_p)
            return {
                "success": True,
                "output_text": '{"ok":true}',
                "output_preview": "preview",
                "latency_ms": 8,
                "parse_success": True,
                "schema_valid": True,
                "fallback_used": False,
                "error_code": None,
                "error_message": None,
            }

    monkeypatch.setattr(prompt_lab_service, "PromptLabProviderAdapter", FakeAdapter)

    with _app_context():
        result = prompt_lab_service.run_prompt_lab(
            task="fortune",
            prompt_text="{{target_date}}",
            temperature=0.7,
            input_payload={"target_date": "2026-04-29"},
        )

    assert result["success"] is True
    assert result["parse_success"] is True
    assert result["schema_valid"] is True


def test_run_profile_success_dispatch_and_boolean_fields_preserved(monkeypatch):
    class FakeAdapter:
        def __init__(self, **kwargs):
            _ = kwargs

        def run_profile(self, diary_entries, answer_questions, prompt_text, temperature, frequency_penalty=None, top_p=None):
            _ = (diary_entries, answer_questions, prompt_text, temperature, frequency_penalty, top_p)
            return {
                "success": True,
                "output_text": '{"mood_tendency":"calm"}',
                "output_preview": "preview",
                "latency_ms": 9,
                "parse_success": False,
                "schema_valid": False,
                "fallback_used": False,
                "error_code": None,
                "error_message": None,
            }

    monkeypatch.setattr(prompt_lab_service, "PromptLabProviderAdapter", FakeAdapter)

    with _app_context():
        result = prompt_lab_service.run_prompt_lab(
            task="profile",
            prompt_text="{{diary_summary}}\n{{question_summary}}",
            temperature=0.7,
            input_payload={
                "diary_entries": [{"content": "abc"}],
                "answer_questions": [{"question": "q", "answer": "a"}],
            },
        )

    assert result["success"] is True
    assert result["parse_success"] is False
    assert result["schema_valid"] is False


def test_unexpected_exception_returns_unexpected_error(monkeypatch):
    class FakeAdapter:
        def __init__(self, **kwargs):
            _ = kwargs

        def run_answer(self, question, prompt_text, temperature, frequency_penalty=None, top_p=None):
            _ = (question, prompt_text, temperature, frequency_penalty, top_p)
            raise RuntimeError("crash")

    monkeypatch.setattr(prompt_lab_service, "PromptLabProviderAdapter", FakeAdapter)

    with _app_context():
        result = prompt_lab_service.run_prompt_lab(
            task="answer",
            prompt_text="x",
            temperature=1.0,
            input_payload={"question": "q"},
        )

    assert result["success"] is False
    assert result["error_code"] == "unexpected_error"


def test_non_dict_provider_row_normalizes_to_error(monkeypatch):
    class FakeAdapter:
        def __init__(self, **kwargs):
            _ = kwargs

        def run_answer(self, question, prompt_text, temperature, frequency_penalty=None, top_p=None):
            _ = (question, prompt_text, temperature, frequency_penalty, top_p)
            return "not-a-dict"

    monkeypatch.setattr(prompt_lab_service, "PromptLabProviderAdapter", FakeAdapter)

    with _app_context():
        result = prompt_lab_service.run_prompt_lab(
            task="answer",
            prompt_text="x",
            temperature=1.0,
            input_payload={"question": "q"},
        )

    assert result["success"] is False
    assert result["error_code"] == "provider_error"


def test_invalid_latency_is_recomputed(monkeypatch):
    class FakeAdapter:
        def __init__(self, **kwargs):
            _ = kwargs

        def run_answer(self, question, prompt_text, temperature):
            _ = (question, prompt_text, temperature)
            return {
                "success": True,
                "output_text": "ok",
                "output_preview": "ok",
                "latency_ms": -1,
                "parse_success": None,
                "schema_valid": None,
                "fallback_used": False,
                "error_code": None,
                "error_message": None,
            }

    monkeypatch.setattr(prompt_lab_service, "PromptLabProviderAdapter", FakeAdapter)

    with _app_context():
        result = prompt_lab_service.run_prompt_lab(
            task="answer",
            prompt_text="x",
            temperature=1.0,
            input_payload={"question": "q"},
        )

    assert isinstance(result["latency_ms"], int)
    assert result["latency_ms"] >= 0

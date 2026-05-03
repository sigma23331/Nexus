import re
import time
from datetime import datetime

from flask import current_app

try:
    from tools.prompt_lab.provider_adapter import PromptLabProviderAdapter
except ImportError:
    try:
        from backend.tools.prompt_lab.provider_adapter import PromptLabProviderAdapter
    except ImportError:
        PromptLabProviderAdapter = None


ALLOWED_TASKS = {"answer", "fortune", "profile"}
ERROR_CODES = {
    "validation_error",
    "provider_error",
    "parse_error",
    "schema_error",
    "unexpected_error",
}
MAX_PROMPT_LEN = 12000
MAX_OUTPUT_PREVIEW_LEN = 120


def run_prompt_lab(task, prompt_text, temperature, input_payload, frequency_penalty=None, top_p=None):
    started_at = time.perf_counter()
    try:
        validated = _validate_and_normalize(task, prompt_text, temperature, input_payload, frequency_penalty, top_p)
        adapter = _build_adapter_from_runtime_config()
        task_name = validated["task"]

        if task_name == "answer":
            answer_kwargs = {
                "question": validated["input_payload"]["question"],
                "prompt_text": validated["prompt_text"],
                "temperature": validated["temperature"],
            }
            if validated["frequency_penalty"] is not None:
                answer_kwargs["frequency_penalty"] = validated["frequency_penalty"]
            if validated["top_p"] is not None:
                answer_kwargs["top_p"] = validated["top_p"]
            row = adapter.run_answer(**answer_kwargs)
        elif task_name == "fortune":
            fortune_kwargs = {
                "target_date": validated["input_payload"]["target_date"],
                "prompt_text": validated["prompt_text"],
                "temperature": validated["temperature"],
            }
            if validated["frequency_penalty"] is not None:
                fortune_kwargs["frequency_penalty"] = validated["frequency_penalty"]
            if validated["top_p"] is not None:
                fortune_kwargs["top_p"] = validated["top_p"]
            profile_input = validated["input_payload"]
            context = {
                "mood_tendency": profile_input.get("mood_tendency"),
                "topic_interests": profile_input.get("topic_interests"),
                "self_context_tag": profile_input.get("self_context_tag"),
            }
            if any(v is not None for v in context.values()):
                fortune_kwargs["profile_context"] = context
            row = adapter.run_fortune(**fortune_kwargs)
        else:
            profile_kwargs = {
                "diary_entries": validated["input_payload"]["diary_entries"],
                "answer_questions": validated["input_payload"]["answer_questions"],
                "prompt_text": validated["prompt_text"],
                "temperature": validated["temperature"],
            }
            if validated["frequency_penalty"] is not None:
                profile_kwargs["frequency_penalty"] = validated["frequency_penalty"]
            if validated["top_p"] is not None:
                profile_kwargs["top_p"] = validated["top_p"]
            row = adapter.run_profile(**profile_kwargs)

        return _normalize_row(task_name, row, started_at)
    except ValueError as exc:
        return _error_row(
            task=task,
            error_code="validation_error",
            error_message=str(exc),
            started_at=started_at,
        )
    except Exception as exc:
        try:
            current_app.logger.exception("prompt_lab_service_unexpected_error")
        except Exception:
            pass
        return _error_row(
            task=task,
            error_code="unexpected_error",
            error_message=str(exc),
            started_at=started_at,
        )


def _build_adapter_from_runtime_config():
    global PromptLabProviderAdapter
    if PromptLabProviderAdapter is None:
        try:
            from tools.prompt_lab.provider_adapter import PromptLabProviderAdapter as adapter_cls
        except ImportError:
            from backend.tools.prompt_lab.provider_adapter import PromptLabProviderAdapter as adapter_cls
        PromptLabProviderAdapter = adapter_cls

    cfg = current_app.config
    return PromptLabProviderAdapter(
        provider_mode=cfg.get("LLM_PROVIDER", "real"),
        base_url=cfg.get("LLM_BASE_URL"),
        model=cfg.get("LLM_MODEL_NAME"),
        api_key=cfg.get("LLM_API_KEY"),
        timeout=cfg.get("LLM_TIMEOUT", 12),
        max_retries=cfg.get("LLM_MAX_RETRIES", 1),
    )


def _validate_and_normalize(task, prompt_text, temperature, input_payload, frequency_penalty, top_p):
    if task not in ALLOWED_TASKS:
        raise ValueError("task 必须是 answer|fortune|profile")

    if not isinstance(prompt_text, str) or not prompt_text.strip():
        raise ValueError("prompt_text 必须为非空字符串")
    if len(prompt_text) > MAX_PROMPT_LEN:
        raise ValueError("prompt_text 长度不能超过12000")

    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise ValueError("temperature 必须为数字")
    if temperature < 0 or temperature > 2:
        raise ValueError("temperature 必须在[0,2]区间内")

    if frequency_penalty is not None:
        if isinstance(frequency_penalty, bool) or not isinstance(frequency_penalty, (int, float)):
            raise ValueError("frequency_penalty 必须为数字")
        if frequency_penalty < -2 or frequency_penalty > 2:
            raise ValueError("frequency_penalty 必须在[-2,2]区间内")

    if top_p is not None:
        if isinstance(top_p, bool) or not isinstance(top_p, (int, float)):
            raise ValueError("top_p 必须为数字")
        if top_p < 0 or top_p > 1:
            raise ValueError("top_p 必须在[0,1]区间内")

    if not isinstance(input_payload, dict):
        raise ValueError("input 必须为对象")

    if task == "answer":
        _validate_answer_input(input_payload)
    elif task == "fortune":
        _validate_fortune_input(input_payload)
    else:
        _validate_profile_input(input_payload)

    return {
        "task": task,
        "prompt_text": prompt_text,
        "temperature": float(temperature),
        "frequency_penalty": float(frequency_penalty) if frequency_penalty is not None else None,
        "top_p": float(top_p) if top_p is not None else None,
        "input_payload": input_payload,
    }


def _validate_answer_input(input_payload):
    question = input_payload.get("question")
    if not isinstance(question, str):
        raise ValueError("answer.question 必须为字符串")
    question_len = len(question.strip())
    if question_len < 1 or question_len > 200:
        raise ValueError("answer.question 长度必须在1到200之间")


def _validate_fortune_input(input_payload):
    target_date = input_payload.get("target_date")
    if not isinstance(target_date, str):
        raise ValueError("fortune.target_date 必须为字符串")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", target_date):
        raise ValueError("fortune.target_date 必须是 YYYY-MM-DD")
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("fortune.target_date 不是有效日期")


def _validate_profile_input(input_payload):
    diary_entries = input_payload.get("diary_entries")
    answer_questions = input_payload.get("answer_questions")

    if not isinstance(diary_entries, list):
        raise ValueError("profile.diary_entries 必须为数组")
    if len(diary_entries) > 50:
        raise ValueError("profile.diary_entries 数量不能超过50")
    for item in diary_entries:
        if not isinstance(item, dict):
            raise ValueError("profile.diary_entries 元素必须为对象")
        content = item.get("content")
        if not isinstance(content, str):
            raise ValueError("profile.diary_entries.content 必须为字符串")
        content_len = len(content.strip())
        if content_len < 1 or content_len > 2000:
            raise ValueError("profile.diary_entries.content 长度必须在1到2000之间")

    if not isinstance(answer_questions, list):
        raise ValueError("profile.answer_questions 必须为数组")
    if len(answer_questions) > 50:
        raise ValueError("profile.answer_questions 数量不能超过50")
    for item in answer_questions:
        if not isinstance(item, dict):
            raise ValueError("profile.answer_questions 元素必须为对象")
        question = item.get("question")
        answer = item.get("answer")
        if not isinstance(question, str) or not isinstance(answer, str):
            raise ValueError("profile.answer_questions.question/answer 必须为字符串")
        question_len = len(question.strip())
        answer_len = len(answer.strip())
        if question_len < 1 or question_len > 500:
            raise ValueError("profile.answer_questions.question 长度必须在1到500之间")
        if answer_len < 1 or answer_len > 500:
            raise ValueError("profile.answer_questions.answer 长度必须在1到500之间")


def _normalize_row(task, row, started_at):
    row = row if isinstance(row, dict) else {}
    success = bool(row.get("success", False))
    output_text = str(row.get("output_text") or "")
    output_preview = str(row.get("output_preview") or output_text)[:MAX_OUTPUT_PREVIEW_LEN]

    latency_ms = row.get("latency_ms")
    if not isinstance(latency_ms, int) or latency_ms < 0:
        latency_ms = int((time.perf_counter() - started_at) * 1000)

    error_code = _normalize_error_code(row.get("error_code"), success)
    if success:
        error_message = None
    else:
        error_message = str(row.get("error_message") or "")

    return {
        "task": task,
        "success": success,
        "output_text": output_text,
        "output_preview": output_preview,
        "latency_ms": latency_ms,
        "parse_success": row.get("parse_success"),
        "schema_valid": row.get("schema_valid"),
        "fallback_used": bool(row.get("fallback_used", False)),
        "error_code": error_code,
        "error_message": error_message,
    }


def _normalize_error_code(code, success):
    if success:
        return None
    if code in ERROR_CODES:
        return code
    if code is None:
        return "provider_error"
    return "unexpected_error"


def _error_row(task, error_code, error_message, started_at):
    return {
        "task": task,
        "success": False,
        "output_text": "",
        "output_preview": "",
        "latency_ms": int((time.perf_counter() - started_at) * 1000),
        "parse_success": None,
        "schema_valid": None,
        "fallback_used": False,
        "error_code": error_code,
        "error_message": error_message,
    }

from datetime import date, datetime
from flask import current_app

from services.llm.providers.mock_provider import MockProvider
from services.llm.providers.real_provider import RealProvider


_provider_cache = None


def _fallback_answer(question):
    return MockProvider().generate_answer(question=question, user_id="")


def _fallback_fortune(target_date):
    return MockProvider().generate_fortune(user_id="", target_date=target_date)


def get_provider(force_refresh=False):
    global _provider_cache
    if _provider_cache is not None and not force_refresh:
        return _provider_cache

    provider_name = None
    try:
        provider_name = current_app.config.get("LLM_PROVIDER", "mock")
    except RuntimeError:
        provider_name = "mock"

    if provider_name == "real":
        try:
            _provider_cache = RealProvider(
                model_name=current_app.config.get("LLM_MODEL_NAME", ""),
                api_key=current_app.config.get("LLM_API_KEY", ""),
                timeout=current_app.config.get("LLM_TIMEOUT", 12),
                max_retries=current_app.config.get("LLM_MAX_RETRIES", 1),
                base_url=current_app.config.get("LLM_BASE_URL", "https://api.openai.com/v1"),
            )
            return _provider_cache
        except Exception:
            pass

    _provider_cache = MockProvider()
    return _provider_cache


def generate_answer(question, user_id):
    text = (question or "").strip()
    if not text:
        raise ValueError("question 必须为非空字符串")
    if len(text) > 200:
        raise ValueError("question 长度不能超过200")

    provider = get_provider()
    try:
        answer_text = provider.generate_answer(question=text, user_id=user_id)
        generated_by = "provider"
    except Exception:
        answer_text = _fallback_answer(text)
        generated_by = "fallback"

    return {
        "answerText": answer_text,
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "generatedBy": generated_by,
    }


def generate_fortune(user_id, target_date):
    if not isinstance(target_date, date):
        raise ValueError("target_date 必须为 date")

    provider = get_provider()
    try:
        payload = provider.generate_fortune(user_id=user_id, target_date=target_date)
        generated_by = "provider"
    except Exception:
        payload = _fallback_fortune(target_date)
        generated_by = "fallback"

    return {
        "score": payload["score"],
        "title": payload["title"],
        "content_main": payload["content_main"],
        "content_sub": payload["content_sub"],
        "love": payload["love"],
        "career": payload["career"],
        "health": payload["health"],
        "wealth": payload["wealth"],
        "yi": payload.get("yi", []),
        "ji": payload.get("ji", []),
        "generatedBy": generated_by,
    }

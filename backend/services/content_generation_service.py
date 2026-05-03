from datetime import date, datetime
from pathlib import Path
from flask import current_app
import random as _random

from services.llm.providers.mock_provider import MockProvider
from services.llm.providers.real_provider import RealProvider
from services.user_profile_service import UserProfileService
from tools.prompt_lab.selector import FortuneContentSelector


_provider_cache = None


def _fallback_answer(question):
    return MockProvider().generate_answer(question=question, user_id="")


def _fallback_fortune(target_date):
    return MockProvider().generate_fortune(user_id="", target_date=target_date)


def _normalize_score(score):
    try:
        value = int(score)
    except Exception:
        value = 70
    return max(0, min(value, 100))


def _score_to_title(score):
    if score >= 85:
        return "上上签"
    if score >= 75:
        return "上吉"
    if score >= 65:
        return "中平"
    if score >= 55:
        return "小谨"
    return "守静"


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
                prompts_dir=current_app.config.get("LLM_PROMPTS_DIR"),
                prompt_versions={
                    "answer": current_app.config.get("LLM_PROMPT_ANSWER_VERSION", "v1"),
                    "fortune": current_app.config.get("LLM_PROMPT_FORTUNE_VERSION", "v1"),
                    "profile": current_app.config.get("LLM_PROMPT_PROFILE_VERSION", "v1"),
                },
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
    version = getattr(provider, "prompt_versions", {}).get("fortune", "")

    if version == "v4":
        score = _random.randint(0, 100)
        profile = None
        try:
            profile_model = UserProfileService.get_by_user_id(user_id)
            if profile_model:
                profile = UserProfileService.to_dict(profile_model)
        except Exception:
            profile = None

        prompts_dir = getattr(provider, "prompts_dir", None)
        if prompts_dir:
            selector = FortuneContentSelector(Path(prompts_dir) / "fortune")
            title_template = selector.select_title(score)
            keywords = selector.select_keywords(profile)
            yiji_items = selector.select_yiji(profile)
        else:
            title_template = {"main": "今日宜静待时机", "sub": "稳中求进"}
            keywords = {"love": "平稳", "career": "平稳", "health": "稳定", "wealth": "平稳"}
            yiji_items = {"yi": [], "ji": []}

        try:
            payload = provider.generate_fortune(
                user_id=user_id,
                target_date=target_date,
                score=score,
                title_template=title_template,
                keywords=keywords,
                yiji_items=yiji_items,
            )
            generated_by = "provider"
        except TypeError:
            payload = _fallback_fortune(target_date)
            generated_by = "fallback"
    else:
        profile_context = None
        try:
            profile = UserProfileService.get_by_user_id(user_id)
            if profile:
                profile_context = UserProfileService.to_dict(profile)
        except Exception:
            profile_context = None

        try:
            try:
                payload = provider.generate_fortune(user_id=user_id, target_date=target_date, profile_context=profile_context)
            except TypeError:
                payload = provider.generate_fortune(user_id=user_id, target_date=target_date)
            generated_by = "provider"
        except Exception:
            payload = _fallback_fortune(target_date)
            generated_by = "fallback"

    score = _normalize_score(payload.get("score"))

    return {
        "score": score,
        "title": _score_to_title(score),
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

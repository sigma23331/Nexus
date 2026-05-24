import random as _random
from datetime import date, datetime
from pathlib import Path

from flask import current_app

from services.llm.providers.mock_provider import MockProvider
from services.llm.providers.real_provider import RealProvider
from services.user_profile_service import UserProfileService
from tools.prompt_lab.selector import FortuneContentSelector


_provider_cache = None


def _fallback_answer(question):
    return MockProvider().generate_answer(question=question, user_id="")


def _fallback_fortune(target_date):
    return MockProvider().generate_fortune(user_id="", target_date=target_date)


def _fallback_profile(diary_entries=None, answer_questions=None):
    return MockProvider().analyze_user_profile(
        diary_entries=diary_entries or [],
        answer_questions=answer_questions or [],
    )


def _get_generation_attempts(provider):
    try:
        retries = int(getattr(provider, "max_retries", 0) or 0)
    except Exception:
        retries = 0
    return max(1, retries + 1)


def _log_generation_retry(task, attempt, max_attempts, exc):
    try:
        current_app.logger.warning(
            "llm_generation_retry task=%s attempt=%s/%s error=%s",
            task,
            attempt,
            max_attempts,
            str(exc)[:200],
            exc_info=True,
        )
    except RuntimeError:
        pass


def _log_generation_fallback(task, exc):
    try:
        current_app.logger.warning(
            "llm_generation_fallback task=%s error=%s",
            task,
            str(exc)[:200],
        )
    except RuntimeError:
        pass


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
        return "小吉"
    return "守静"


def _default_gua_meaning(score):
    if score >= 85:
        return ["乾元得势", "顺势而为，主动推进"]
    if score >= 75:
        return ["木火通明", "节奏清朗，宜扩展布局"]
    if score >= 65:
        return ["阴阳守中", "稳步前行，先稳后进"]
    if score >= 55:
        return ["地山谦", "以退为进，夯实基础"]
    return ["坎离未济", "先养精神，再谋后动"]


def _default_lucky_hour(score):
    if score >= 90:
        return {"name": "辰时", "range": "07:00-09:00"}
    if score >= 82:
        return {"name": "巳时", "range": "09:00-11:00"}
    if score >= 74:
        return {"name": "午时", "range": "11:00-13:00"}
    if score >= 66:
        return {"name": "未时", "range": "13:00-15:00"}
    return {"name": "酉时", "range": "17:00-19:00"}


def _normalize_text(value, default="", limit=80):
    text = str(value or "").strip()
    if not text:
        text = default
    return text[:limit]


def _normalize_list(value, limit=5, item_limit=20):
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        text = str(item or "").strip()
        if not text:
            continue
        result.append(text[:item_limit])
        if len(result) >= limit:
            break
    return result


def _normalize_gua_meaning_lines(value, score):
    lines = _normalize_list(value, limit=2, item_limit=40)
    if len(lines) == 2:
        return lines
    return _default_gua_meaning(score)


def _normalize_lucky_hour(payload, score):
    default = _default_lucky_hour(score)
    name = _normalize_text(payload.get("lucky_hour_name"), default["name"], limit=20)
    hour_range = _normalize_text(payload.get("lucky_hour_range"), default["range"], limit=20)
    return {"name": name, "range": hour_range}


def _normalize_fortune_payload(payload):
    payload = payload if isinstance(payload, dict) else {}
    score = _normalize_score(payload.get("score"))
    lucky_hour = _normalize_lucky_hour(payload, score)
    return {
        "score": score,
        "title": _score_to_title(score),
        "content_main": _normalize_text(
            payload.get("content_main"),
            default="今日节奏平稳，先完成最重要的一件事。",
            limit=80,
        ),
        "content_sub": _normalize_text(
            payload.get("content_sub"),
            default="稳中求进，心静则通达。",
            limit=80,
        ),
        "love": _normalize_text(payload.get("love"), default="平稳", limit=20),
        "career": _normalize_text(payload.get("career"), default="平稳", limit=20),
        "health": _normalize_text(payload.get("health"), default="稳定", limit=20),
        "wealth": _normalize_text(payload.get("wealth"), default="平稳", limit=20),
        "yi": _normalize_list(payload.get("yi"), limit=5, item_limit=20),
        "ji": _normalize_list(payload.get("ji"), limit=5, item_limit=20),
        "gua_meaning_lines": _normalize_gua_meaning_lines(payload.get("gua_meaning_lines"), score),
        "lucky_hour_name": lucky_hour["name"],
        "lucky_hour_range": lucky_hour["range"],
    }


def _normalize_profile_payload(payload):
    payload = payload if isinstance(payload, dict) else {}
    mood_tendency = _normalize_text(payload.get("mood_tendency"), default="calm", limit=50)
    topic_interests = []
    for item in _normalize_list(payload.get("topic_interests"), limit=5, item_limit=30):
        if item not in topic_interests:
            topic_interests.append(item)
        if len(topic_interests) >= 3:
            break
    if not topic_interests:
        topic_interests = ["health"]
    self_context_tag = _normalize_text(payload.get("self_context_tag"), default="daily", limit=20)
    return {
        "mood_tendency": mood_tendency,
        "topic_interests": topic_interests,
        "self_context_tag": self_context_tag,
    }


def get_provider(force_refresh=False):
    global _provider_cache
    if _provider_cache is not None and not force_refresh:
        return _provider_cache

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


def generate_profile(diary_entries, answer_questions):
    provider = get_provider()
    payload = None
    generated_by = "fallback"
    max_attempts = _get_generation_attempts(provider)
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            payload = provider.analyze_user_profile(
                diary_entries=diary_entries or [],
                answer_questions=answer_questions or [],
            )
            generated_by = "provider"
            last_error = None
            break
        except Exception as exc:
            last_error = exc
            if attempt < max_attempts:
                _log_generation_retry("profile", attempt, max_attempts, exc)

    if generated_by != "provider":
        if last_error is not None:
            _log_generation_fallback("profile", last_error)
        payload = _fallback_profile(diary_entries=diary_entries, answer_questions=answer_questions)

    normalized = _normalize_profile_payload(payload)
    normalized["generatedBy"] = generated_by
    return normalized


def generate_fallback_fortune(target_date):
    normalized = _normalize_fortune_payload(_fallback_fortune(target_date))
    normalized["generatedBy"] = "fallback"
    return normalized


def generate_fortune(user_id, target_date):
    if not isinstance(target_date, date):
        raise ValueError("target_date must be a date")

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

        payload = None
        generated_by = "fallback"
        max_attempts = _get_generation_attempts(provider)
        last_error = None
        for attempt in range(1, max_attempts + 1):
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
                last_error = None
                break
            except TypeError as exc:
                last_error = exc
                break
            except Exception as exc:
                last_error = exc
                if attempt < max_attempts:
                    _log_generation_retry("fortune", attempt, max_attempts, exc)

        if generated_by != "provider":
            if last_error is not None:
                _log_generation_fallback("fortune", last_error)
            payload = _fallback_fortune(target_date)
    else:
        profile_context = None
        try:
            profile = UserProfileService.get_by_user_id(user_id)
            if profile:
                profile_context = UserProfileService.to_dict(profile)
        except Exception:
            profile_context = None

        payload = None
        generated_by = "fallback"
        max_attempts = _get_generation_attempts(provider)
        last_error = None
        for attempt in range(1, max_attempts + 1):
            try:
                try:
                    payload = provider.generate_fortune(
                        user_id=user_id,
                        target_date=target_date,
                        profile_context=profile_context,
                    )
                except TypeError:
                    payload = provider.generate_fortune(user_id=user_id, target_date=target_date)
                generated_by = "provider"
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                if attempt < max_attempts:
                    _log_generation_retry("fortune", attempt, max_attempts, exc)

        if generated_by != "provider":
            if last_error is not None:
                _log_generation_fallback("fortune", last_error)
            payload = _fallback_fortune(target_date)

    normalized = _normalize_fortune_payload(payload)
    normalized["generatedBy"] = generated_by
    return normalized

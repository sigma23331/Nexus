import random
import re
from collections import Counter
from datetime import date

from models.answer import AnswerRecord
from models.fortune import FortuneRecord
from services.user_profile_service import UserProfileService


DEFAULT_TABOO_TERMS = ["稳中求进", "调整节奏", "静待时机", "静待花开"]
SENTENCE_SHAPES = ["短句 + 留白", "短句 + 轻动作", "转折短句", "状态 + 边界", "动作 + 余地"]
TONES = ["温和", "克制", "明亮", "干净"]
RHYTHMS = ["短促", "慢速", "留白"]
ANSWER_LENGTH_RULES = ["8-10 个汉字", "11-14 个汉字", "15-18 个汉字"]
ACTION_DOMAINS = ["整理", "沟通", "复盘", "交付", "休息"]


def _enum_value(value):
    return getattr(value, "value", value)


def _safe_profile_dict(user_id):
    if not user_id:
        return None
    try:
        profile = UserProfileService.get_by_user_id(user_id)
        return UserProfileService.to_dict(profile) if profile else None
    except Exception:
        return None


def _profile_enabled(profile):
    if not profile:
        return False
    return profile.get("personalization_enabled", True) is not False


def _profile_field(profile, key, default=""):
    if not profile:
        return default
    value = profile.get(key)
    if isinstance(value, list):
        return ",".join(str(item).strip() for item in value if str(item).strip()) or default
    value = _enum_value(value)
    return str(value or default).strip()


def _profile_tokens(profile):
    if not profile:
        return []
    raw = []
    for key in ("topic_interests", "mood_tendency", "self_context_tag"):
        value = profile.get(key)
        if isinstance(value, list):
            raw.extend(value)
        elif value:
            raw.append(value)
    tokens = []
    for value in raw:
        for token in str(value).replace("|", ",").replace("，", ",").split(","):
            token = token.strip()
            if token and token not in tokens:
                tokens.append(token)
    return tokens


def _personalization_plan(profile, task):
    if not _profile_enabled(profile):
        return "不使用用户画像，仅保留随机书页感、通用安全边界和隐私约束。"

    mood = _profile_field(profile, "mood_tendency", "calm")
    interests = _profile_field(profile, "topic_interests", "health")
    context_tag = _profile_field(profile, "self_context_tag", "日常")
    parts = []

    if "anxious" in mood or "焦虑" in mood:
        parts.append("语气温和，低压力，不催促")
    if "low_energy" in mood or "tired" in mood or "恢复" in context_tag:
        parts.append("低负担，避免高压动作")
    if "optimistic" in mood or "energetic" in mood:
        parts.append("语气明亮，但不做确定承诺")

    if "career" in interests or "job" in interests or "study" in interests:
        parts.append("事业/学习字段更具体，偏交付、沟通、复盘或推进")
    if "health" in interests or "sleep" in interests:
        parts.append("健康字段更轻柔，偏恢复和自我照看")
    if "love" in interests or "relationship" in interests:
        parts.append("关系字段保留余地，不制造情绪压力")
    if "wealth" in interests or "finance" in interests:
        parts.append("财富字段保持谨慎，不给投资判断")

    if not parts:
        parts.append("语气平稳，动作轻巧，保留留白")

    if task == "answer":
        parts.append("答案不得复述问题或画像标签")
    return "；".join(parts)


def _material_hints(profile, task):
    tokens = _profile_tokens(profile) if _profile_enabled(profile) else []
    shape = random.choice(SENTENCE_SHAPES)
    tone = _select_tone(tokens)
    rhythm = random.choice(RHYTHMS)
    length_rule = random.choice(ANSWER_LENGTH_RULES) if task == "answer" else "按字段长度约束"
    if any(token in {"career", "job_seek", "study"} for token in tokens):
        action = "交付、沟通、复盘"
    elif any(token in {"health", "low_energy", "sleep_low"} for token in tokens):
        action = "休息、补水、轻整理"
    else:
        action = random.choice(ACTION_DOMAINS)
    return f"sentence_shape={shape}；tone={tone}；rhythm={rhythm}；length_rule={length_rule}；行动域：{action}"


def _select_tone(tokens):
    low_pressure_tokens = {"anxious", "焦虑", "low_energy", "tired", "recovery", "sleep_low"}
    if any(token in low_pressure_tokens for token in tokens):
        return random.choice(["温和", "克制"])
    return random.choice(TONES)


def _collect_answer_history(user_id, limit=8):
    try:
        return (
            AnswerRecord.query.filter_by(user_id=user_id)
            .order_by(AnswerRecord.created_at.desc())
            .limit(limit)
            .all()
        )
    except Exception:
        return []


def _collect_fortune_history(user_id, limit=8):
    try:
        return (
            FortuneRecord.query.filter_by(user_id=user_id)
            .order_by(FortuneRecord.date.desc())
            .limit(limit)
            .all()
        )
    except Exception:
        return []


def _history_text(records, task):
    chunks = []
    for record in records or []:
        if task == "answer":
            chunks.append(getattr(record, "answer_text", "") or "")
        else:
            chunks.extend(
                [
                    getattr(record, "content", "") or "",
                    getattr(record, "love", "") or "",
                    getattr(record, "career", "") or "",
                    getattr(record, "health", "") or "",
                    getattr(record, "wealth", "") or "",
                ]
            )
            chunks.extend(getattr(record, "yi", None) or [])
            chunks.extend(getattr(record, "ji", None) or [])
            chunks.extend(getattr(record, "gua_meaning_lines", None) or [])
    return "\n".join(str(item) for item in chunks if str(item).strip())


def _extract_frequent_terms(text, limit=8):
    text = str(text or "")
    candidates = []
    for match in re.findall(r"[\u4e00-\u9fff]{2,6}|[A-Za-z_]{3,}", text):
        if re.fullmatch(r"[\u4e00-\u9fff]{2,6}", match):
            for size in (2, 3, 4):
                if len(match) >= size:
                    candidates.extend(match[i : i + size] for i in range(0, len(match) - size + 1))
        else:
            candidates.append(match.lower())
    counter = Counter(candidates)
    terms = [
        term
        for term, count in counter.most_common()
        if count >= 2 and term not in {"今日", "平稳", "稳定"}
    ]
    return terms[:limit]


def _birthday_context(profile):
    birthday = None
    try:
        birthday = getattr(getattr(profile, "user", None), "birthday", None)
    except Exception:
        birthday = None

    if not birthday:
        return "", ""
    try:
        if isinstance(birthday, date):
            return birthday.isoformat(), birthday.strftime("%m-%d")
        return str(birthday), str(birthday)[5:10]
    except Exception:
        return "", ""


def _safe_profile_model(user_id):
    try:
        return UserProfileService.get_by_user_id(user_id)
    except Exception:
        return None


def _base_context(profile, task):
    enabled = _profile_enabled(profile)
    visible_profile = profile if enabled else None
    answer_style = _profile_field(visible_profile, "answer_style", "philosophical")
    selected_style = random.choice(
        [
            "寓言式短句",
            "禅意留白短句",
            "直觉书页短句",
            "冥想式短句",
        ]
    )
    tokens = _profile_tokens(visible_profile)
    sentence_shape = random.choice(SENTENCE_SHAPES)
    tone = _select_tone(tokens)
    rhythm = random.choice(RHYTHMS)
    length_rule = random.choice(ANSWER_LENGTH_RULES) if task == "answer" else "按字段长度约束"
    return {
        "answer_style": answer_style,
        "topic_interests": _profile_field(visible_profile, "topic_interests", ""),
        "self_context_tag": _profile_field(visible_profile, "self_context_tag", ""),
        "mood_tendency": _profile_field(visible_profile, "mood_tendency", ""),
        "active_hour_bucket": _profile_field(visible_profile, "active_hour_bucket", ""),
        "selected_style": selected_style,
        "sentence_shape": sentence_shape,
        "tone": tone,
        "rhythm": rhythm,
        "length_rule": length_rule,
        "personalization_plan": _personalization_plan(profile, task),
        "material_hints": _material_hints(visible_profile, task),
        "privacy_constraints": "不得复述用户问题、画像标签、生日或可识别个人信息。",
    }


def build_answer_context(user_id, question=None):
    _ = question
    profile = _safe_profile_dict(user_id)
    context = _base_context(profile, task="answer")
    history_terms = _extract_frequent_terms(_history_text(_collect_answer_history(user_id), "answer"))
    context["diversity_taboo_terms"] = "、".join(history_terms)
    context["avoid_instructions"] = (
        "避免使用：" + "、".join(history_terms)
        if history_terms
        else "避免复用近期答案的高频表达和固定模板句。"
    )
    return context


def build_fortune_context(user_id, target_date, score):
    profile_model = _safe_profile_model(user_id)
    try:
        profile = UserProfileService.to_dict(profile_model) if profile_model else None
    except Exception:
        profile = None

    context = _base_context(profile, task="fortune")
    history_terms = _extract_frequent_terms(_history_text(_collect_fortune_history(user_id), "fortune"))
    taboo_terms = history_terms or DEFAULT_TABOO_TERMS
    birthday, birth_month_day = _birthday_context(profile_model)
    action_domain = random.choice(ACTION_DOMAINS)

    context.update(
        {
            "target_date": target_date.isoformat() if isinstance(target_date, date) else str(target_date),
            "score": str(max(0, min(int(score), 100))) if str(score).strip().lstrip("-").isdigit() else "70",
            "birthday": birthday,
            "birth_month_day": birth_month_day,
            "imagery_domain": "",
            "action_domain": action_domain,
            "lucky_hour_guidance": "由 LLM 根据分数、今日基调和画像生成合法时辰，避免全部坍缩为同一时辰。",
            "assigned_lucky_hour_name": "",
            "assigned_lucky_hour_range": "",
            "diversity_taboo_terms": "、".join(taboo_terms),
            "avoid_instructions": "避免使用：" + "、".join(taboo_terms),
            "diversify_key": f"{user_id}-{target_date}-{score}",
            "recent_shown_ids": [],
        }
    )
    return context

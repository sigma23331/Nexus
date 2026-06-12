import json
import hashlib
import time
from datetime import datetime
from pathlib import Path

try:
    from services.llm.providers.mock_provider import MockProvider
    from services.llm.providers.real_provider import RealProvider
except ImportError:
    from backend.services.llm.providers.mock_provider import MockProvider
    from backend.services.llm.providers.real_provider import RealProvider

try:
    from tools.prompt_lab.selector import AnswerStyleSelector, FortuneContentSelector, stable_fortune_score
except ImportError:
    from backend.tools.prompt_lab.selector import AnswerStyleSelector, FortuneContentSelector, stable_fortune_score


DEFAULT_TABOO_TERMS = "稳中求进、调整节奏、静待时机、静待花开、低潮是缓冲区、先修复状态、再决定下一步、早睡早起、出门散步、整理书桌、冲动消费、收支平稳、多看少动"
SENTENCE_SHAPES = ["短句 + 留白", "短句 + 轻动作", "转折短句", "状态 + 边界", "动作 + 余地"]
TONES = ["温和", "克制", "明亮", "干净"]
RHYTHMS = ["短促", "慢速", "留白"]
CHINESE_HOURS = [
    ("子时", "23:00-01:00"),
    ("丑时", "01:00-03:00"),
    ("寅时", "03:00-05:00"),
    ("卯时", "05:00-07:00"),
    ("辰时", "07:00-09:00"),
    ("巳时", "09:00-11:00"),
    ("午时", "11:00-13:00"),
    ("未时", "13:00-15:00"),
    ("申时", "15:00-17:00"),
    ("酉时", "17:00-19:00"),
    ("戌时", "19:00-21:00"),
    ("亥时", "21:00-23:00"),
]


def _preview(value, limit=80):
    text = str(value or "").replace("\n", " ").strip()
    return text[:limit]


def _render_inline(prompt_text, variables):
    rendered = str(prompt_text or "")
    for key, value in (variables or {}).items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
        rendered = rendered.replace("{" + key + "}", str(value))
    return rendered


def _stable_choice(values, key):
    if not values:
        return ""
    digest = hashlib.sha256(str(key).encode("utf-8")).hexdigest()
    return values[int(digest[:12], 16) % len(values)]


def _join_context_value(value):
    if isinstance(value, list):
        return ",".join(str(item).strip() for item in value if str(item).strip())
    return str(value or "").strip()


def _personalization_plan(context):
    mood = str(context.get("mood_tendency") or "")
    topics = _join_context_value(context.get("topic_interests"))
    state = str(context.get("self_context_tag") or "")
    parts = []
    if "anxious" in mood or "sensitive" in mood or "tense" in mood:
        parts.append("语气温和，低压力，不催促")
    if "low_energy" in mood or "very_low_energy" in mood or "sleep_low" in state or "recovery" in state:
        parts.append("低负担，避免高压动作")
    if any(token in topics for token in ("career", "job", "study", "goal_exam")):
        parts.append("事业/学习字段略偏秩序、清明和可承接，不写具体任务")
    if any(token in topics for token in ("health", "sleep", "recovery")):
        parts.append("健康字段更轻柔，偏恢复和自我照看")
    if any(token in topics for token in ("wealth", "finance")):
        parts.append("财富字段保持谨慎，不给投资判断")
    if any(token in topics for token in ("relationship", "love", "social")):
        parts.append("关系字段保留余地，不制造情绪压力")
    if not parts:
        parts.append("语气平稳，动作轻巧，保留留白")
    return "；".join(parts)


def _action_domain(context):
    topics = _join_context_value(context.get("topic_interests"))
    if "career" in topics or "job" in topics or "study" in topics:
        return "秩序"
    if "health" in topics or "sleep" in topics:
        return "照看"
    if "wealth" in topics or "finance" in topics:
        return "收束"
    return "余地"


def _default_generation_variables(context, target_date, score):
    context = context if isinstance(context, dict) else {}
    birthday = str(context.get("birthday") or "")
    birth_month_day = str(context.get("birth_month_day") or "")
    if not birth_month_day and len(birthday) >= 10:
        birth_month_day = birthday[5:10]
    diversify_key = str(
        context.get("diversify_key")
        or f"{context.get('user_id') or context.get('virtual_user_id') or context.get('id') or 'prompt-lab'}-{target_date}-{score}"
    )
    mood = str(context.get("mood_tendency") or "")
    state = str(context.get("self_context_tag") or "")
    low_pressure = any(
        token in mood or token in state
        for token in ("anxious", "tense", "low_energy", "very_low_energy", "sleep_low", "recovery")
    )
    tone_pool = ["温和", "克制"] if low_pressure else TONES
    hour_name, hour_range = CHINESE_HOURS[int(hashlib.sha256(diversify_key.encode("utf-8")).hexdigest()[:12], 16) % len(CHINESE_HOURS)]
    sentence_shape = str(context.get("sentence_shape") or _stable_choice(SENTENCE_SHAPES, diversify_key + "|shape"))
    tone = str(context.get("tone") or _stable_choice(tone_pool, diversify_key + "|tone"))
    rhythm = str(context.get("rhythm") or _stable_choice(RHYTHMS, diversify_key + "|rhythm"))
    action_domain = str(context.get("action_domain") or _action_domain(context))
    length_rule = str(context.get("length_rule") or "按字段长度约束")
    material_hints = (
        f"sentence_shape={sentence_shape}；tone={tone}；rhythm={rhythm}；"
        f"length_rule={length_rule}；行动域：{action_domain}"
    )
    return {
        "answer_style": str(context.get("answer_style") or "philosophical"),
        "topic_interests": _join_context_value(context.get("topic_interests")),
        "self_context_tag": str(context.get("self_context_tag") or ""),
        "mood_tendency": str(context.get("mood_tendency") or ""),
        "active_hour_bucket": str(context.get("active_hour_bucket") or ""),
        "selected_style": str(context.get("selected_style") or ""),
        "personalization_plan": str(context.get("personalization_plan") or _personalization_plan(context)),
        "material_hints": str(context.get("material_hints") or material_hints),
        "privacy_constraints": str(context.get("privacy_constraints") or "不得复述用户问题、画像标签、生日或可识别个人信息。"),
        "avoid_instructions": str(context.get("avoid_instructions") or f"避免使用：{DEFAULT_TABOO_TERMS}"),
        "diversity_taboo_terms": str(context.get("diversity_taboo_terms") or DEFAULT_TABOO_TERMS),
        "birthday": birthday,
        "birth_month_day": birth_month_day,
        "imagery_domain": str(context.get("imagery_domain") or ""),
        "sentence_shape": sentence_shape,
        "tone": tone,
        "rhythm": rhythm,
        "length_rule": length_rule,
        "action_domain": action_domain,
        "lucky_hour_guidance": str(context.get("lucky_hour_guidance") or f"使用指定时辰：{hour_name} {hour_range}。"),
        "assigned_lucky_hour_name": str(context.get("assigned_lucky_hour_name") or hour_name),
        "assigned_lucky_hour_range": str(context.get("assigned_lucky_hour_range") or hour_range),
        "diversify_key": diversify_key,
    }


def _fortune_schema_valid(data):
    if not isinstance(data, dict):
        return False
    required = {
        "score",
        "content_main",
        "content_sub",
        "love",
        "career",
        "health",
        "wealth",
        "yi",
        "ji",
        "gua_meaning_lines",
        "lucky_hour_name",
        "lucky_hour_range",
    }
    if not required.issubset(set(data.keys())):
        return False
    if not isinstance(data.get("score"), int):
        return False
    scalar_keys = [
        "content_main",
        "content_sub",
        "love",
        "career",
        "health",
        "wealth",
        "lucky_hour_name",
        "lucky_hour_range",
    ]
    if any(not isinstance(data.get(key), str) for key in scalar_keys):
        return False
    if not isinstance(data.get("yi"), list) or not isinstance(data.get("ji"), list):
        return False
    if not isinstance(data.get("gua_meaning_lines"), list) or len(data.get("gua_meaning_lines")) != 2:
        return False
    return True


def _normalize_fortune_contract(data):
    data = data if isinstance(data, dict) else {}
    content_main = str(data.get("content_main") or data.get("content") or "").strip()
    content_sub = str(data.get("content_sub") or "稳中求进，心静则通达。").strip()
    gua_lines = data.get("gua_meaning_lines") if isinstance(data.get("gua_meaning_lines"), list) else []
    normalized_gua_lines = [str(item or "").strip()[:40] for item in gua_lines[:2] if str(item or "").strip()]
    if len(normalized_gua_lines) < 2:
        normalized_gua_lines = ["阴阳守中", "稳步前行，先稳后进"]
    return {
        "score": int(data.get("score", 70)) if str(data.get("score", "")).isdigit() else 70,
        "content_main": content_main,
        "content_sub": content_sub,
        "love": str(data.get("love") or "平稳").strip(),
        "career": str(data.get("career") or "平稳").strip(),
        "health": str(data.get("health") or "稳定").strip(),
        "wealth": str(data.get("wealth") or "平稳").strip(),
        "yi": data.get("yi") if isinstance(data.get("yi"), list) else [],
        "ji": data.get("ji") if isinstance(data.get("ji"), list) else [],
        "gua_meaning_lines": normalized_gua_lines,
        "lucky_hour_name": str(data.get("lucky_hour_name") or "午时").strip(),
        "lucky_hour_range": str(data.get("lucky_hour_range") or "11:00-13:00").strip(),
    }


def _profile_schema_valid(data):
    if not isinstance(data, dict):
        return False
    if not isinstance(data.get("mood_tendency"), str):
        return False
    if not isinstance(data.get("topic_interests"), list):
        return False
    if not isinstance(data.get("self_context_tag"), str):
        return False
    return True


def _error_row(start_ts, error_code, message, parse_success=False, schema_valid=False):
    return {
        "success": False,
        "parse_success": parse_success,
        "schema_valid": schema_valid,
        "fallback_used": False,
        "error_code": error_code,
        "error_message": str(message or "")[:200],
        "latency_ms": int((time.perf_counter() - start_ts) * 1000),
        "output_chars": 0,
        "output_preview": "",
        "output_text": "",
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


class PromptLabProviderAdapter:
    def __init__(self, provider_mode="real", base_url=None, model=None, api_key=None, timeout=12, max_retries=1):
        self.provider_mode = provider_mode
        if provider_mode == "mock":
            self.provider = MockProvider()
        elif provider_mode == "real":
            self.provider = RealProvider(
                model_name=model or "",
                api_key=api_key or "",
                timeout=timeout,
                max_retries=max_retries,
                base_url=base_url,
            )
        else:
            raise ValueError("provider_mode must be real or mock")

    def run_answer(self, question, prompt_text, temperature, frequency_penalty=None, top_p=None, profile_context=None):
        start = time.perf_counter()
        try:
            context = profile_context or {}
            style = ""
            provider_prompts_dir = getattr(self.provider, "prompts_dir", None)
            if provider_prompts_dir:
                try:
                    selector = AnswerStyleSelector(Path(provider_prompts_dir) / "answer" / "styles")
                    style = selector.select()
                except Exception:
                    style = ""
            default_variables = _default_generation_variables(context, target_date="answer", score="")
            rendered = _render_inline(
                prompt_text,
                {
                    **default_variables,
                    "question": question,
                    "selected_style": style or default_variables["selected_style"],
                },
            )
            if self.provider_mode == "mock":
                output = self.provider.generate_answer(question=question, user_id="prompt-lab")
            else:
                output = self.provider._chat(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": rendered},
                    ],
                    temperature=temperature,
                    frequency_penalty=frequency_penalty,
                    top_p=top_p,
                )
            return {
                "success": True,
                "parse_success": None,
                "schema_valid": None,
                "fallback_used": False,
                "error_code": None,
                "error_message": "",
                "latency_ms": int((time.perf_counter() - start) * 1000),
                "output_chars": len(str(output)),
                "output_preview": _preview(output),
                "output_text": str(output),
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
        except Exception as exc:
            return _error_row(start, "provider_error", exc, parse_success=None, schema_valid=None)

    def run_fortune(self, target_date, prompt_text, temperature, frequency_penalty=None, top_p=None, profile_context=None):
        start = time.perf_counter()
        try:
            context = profile_context or {}
            score = stable_fortune_score(context, target_date)
            default_variables = _default_generation_variables(context, target_date, score)
            title_template = {"main": "今日宜静待时机", "sub": "稳中求进"}
            keywords = {"love": "平稳", "career": "平稳", "health": "稳定", "wealth": "平稳"}
            yiji_items = {"yi": [], "ji": []}

            provider_prompts_dir = getattr(self.provider, "prompts_dir", None)
            if provider_prompts_dir:
                try:
                    selector = FortuneContentSelector(Path(provider_prompts_dir) / "fortune")
                    title_template = selector.select_title(score)
                    keywords = selector.select_keywords(context)
                    yiji_items = selector.select_yiji(context)
                except Exception:
                    pass

            rendered = _render_inline(
                prompt_text,
                {
                    **default_variables,
                    "target_date": target_date,
                    "score": str(score),
                    "title_main": title_template.get("main", "今日宜静待时机"),
                    "title_sub": title_template.get("sub", "稳中求进"),
                    "love_keyword": keywords.get("love", "平稳"),
                    "career_keyword": keywords.get("career", "平稳"),
                    "health_keyword": keywords.get("health", "稳定"),
                    "wealth_keyword": keywords.get("wealth", "平稳"),
                    "yi_samples": "\n".join(yiji_items.get("yi", [])),
                    "ji_samples": "\n".join(yiji_items.get("ji", [])),
                },
            )
            if self.provider_mode == "mock":
                data = self.provider.generate_fortune(
                    user_id="prompt-lab",
                    target_date=datetime.strptime(target_date, "%Y-%m-%d").date(),
                )
                parse_success = True
            else:
                output = self.provider._chat(
                    messages=[
                        {"role": "system", "content": "Output JSON only."},
                        {"role": "user", "content": rendered},
                    ],
                    temperature=temperature,
                    frequency_penalty=frequency_penalty,
                    top_p=top_p,
                )
                data = self.provider._extract_json(output)
                parse_success = True
            data = _normalize_fortune_contract(data)
            data["score"] = score
            data["lucky_hour_name"] = default_variables["assigned_lucky_hour_name"]
            data["lucky_hour_range"] = default_variables["assigned_lucky_hour_range"]
            schema_valid = _fortune_schema_valid(data)
            if not schema_valid:
                return _error_row(start, "schema_error", "fortune schema mismatch", parse_success=True, schema_valid=False)
            payload = json.dumps(data, ensure_ascii=False)
            return {
                "success": True,
                "parse_success": parse_success,
                "schema_valid": True,
                "fallback_used": False,
                "error_code": None,
                "error_message": "",
                "latency_ms": int((time.perf_counter() - start) * 1000),
                "output_chars": len(payload),
                "output_preview": _preview(payload),
                "output_text": payload,
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
        except ValueError as exc:
            return _error_row(start, "parse_error", exc, parse_success=False, schema_valid=False)
        except Exception as exc:
            return _error_row(start, "provider_error", exc, parse_success=False, schema_valid=False)

    def run_profile(self, diary_entries, answer_questions, prompt_text, temperature, frequency_penalty=None, top_p=None):
        start = time.perf_counter()
        try:
            diary_summary = "\n".join(
                str((item or {}).get("content", ""))[:100]
                for item in (diary_entries or [])
                if isinstance(item, dict)
            )
            question_summary = "\n".join(
                str((item or {}).get("question", ""))[:100]
                for item in (answer_questions or [])
                if isinstance(item, dict)
            )
            rendered = _render_inline(
                prompt_text,
                {
                    "diary_summary": diary_summary or "无日记记录",
                    "question_summary": question_summary or "无提问记录",
                },
            )
            if self.provider_mode == "mock":
                data = self.provider.analyze_user_profile(
                    diary_entries=diary_entries,
                    answer_questions=answer_questions,
                )
                parse_success = True
            else:
                output = self.provider._chat(
                    messages=[
                        {"role": "system", "content": "Output JSON only."},
                        {"role": "user", "content": rendered},
                    ],
                    temperature=temperature,
                    frequency_penalty=frequency_penalty,
                    top_p=top_p,
                )
                data = self.provider._extract_json(output)
                parse_success = True

            schema_valid = _profile_schema_valid(data)
            if not schema_valid:
                return _error_row(start, "schema_error", "profile schema mismatch", parse_success=True, schema_valid=False)

            payload = json.dumps(data, ensure_ascii=False)
            return {
                "success": True,
                "parse_success": parse_success,
                "schema_valid": True,
                "fallback_used": False,
                "error_code": None,
                "error_message": "",
                "latency_ms": int((time.perf_counter() - start) * 1000),
                "output_chars": len(payload),
                "output_preview": _preview(payload),
                "output_text": payload,
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
        except ValueError as exc:
            return _error_row(start, "parse_error", exc, parse_success=False, schema_valid=False)
        except Exception as exc:
            return _error_row(start, "provider_error", exc, parse_success=False, schema_valid=False)

import json
import time
from datetime import datetime

try:
    from services.llm.providers.mock_provider import MockProvider
    from services.llm.providers.real_provider import RealProvider
except ImportError:
    from backend.services.llm.providers.mock_provider import MockProvider
    from backend.services.llm.providers.real_provider import RealProvider


def _preview(value, limit=80):
    text = str(value or "").replace("\n", " ").strip()
    return text[:limit]


def _render_inline(prompt_text, variables):
    rendered = str(prompt_text or "")
    for key, value in (variables or {}).items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    return rendered


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
    }
    if not required.issubset(set(data.keys())):
        return False
    if not isinstance(data.get("score"), int):
        return False
    scalar_keys = ["content_main", "content_sub", "love", "career", "health", "wealth"]
    if any(not isinstance(data.get(key), str) for key in scalar_keys):
        return False
    if not isinstance(data.get("yi"), list) or not isinstance(data.get("ji"), list):
        return False
    return True


def _normalize_fortune_contract(data):
    data = data if isinstance(data, dict) else {}
    content_main = str(data.get("content_main") or data.get("content") or "").strip()
    content_sub = str(data.get("content_sub") or "稳中求进，心静则通达。").strip()
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

    def run_answer(self, question, prompt_text, temperature, frequency_penalty=None, top_p=None):
        start = time.perf_counter()
        try:
            rendered = _render_inline(prompt_text, {"question": question})
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

    def run_fortune(self, target_date, prompt_text, temperature, frequency_penalty=None, top_p=None):
        start = time.perf_counter()
        try:
            rendered = _render_inline(prompt_text, {"target_date": target_date})
            if self.provider_mode == "mock":
                data = self.provider.generate_fortune(user_id="prompt-lab", target_date=datetime.strptime(target_date, "%Y-%m-%d").date())
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
            diary_summary = "\n".join((str((item or {}).get("content", ""))[:100] for item in (diary_entries or []) if isinstance(item, dict)))
            question_summary = "\n".join((str((item or {}).get("question", ""))[:100] for item in (answer_questions or []) if isinstance(item, dict)))
            rendered = _render_inline(
                prompt_text,
                {
                    "diary_summary": diary_summary or "无日记记录",
                    "question_summary": question_summary or "无提问记录",
                },
            )
            if self.provider_mode == "mock":
                data = self.provider.analyze_user_profile(diary_entries=diary_entries, answer_questions=answer_questions)
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

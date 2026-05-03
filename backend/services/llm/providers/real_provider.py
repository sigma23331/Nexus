from datetime import date
import json
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

from .base import LLMProvider
from tools.prompt_lab.selector import AnswerStyleSelector, FortuneContentSelector


FORTUNE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["score", "content_main", "content_sub", "love", "career", "health", "wealth", "yi", "ji"],
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "content_main": {"type": "string", "maxLength": 80},
        "content_sub": {"type": "string", "maxLength": 80},
        "love": {"type": "string", "maxLength": 20},
        "career": {"type": "string", "maxLength": 20},
        "health": {"type": "string", "maxLength": 20},
        "wealth": {"type": "string", "maxLength": 20},
        "yi": {"type": "array", "maxItems": 5, "items": {"type": "string", "maxLength": 20}},
        "ji": {"type": "array", "maxItems": 5, "items": {"type": "string", "maxLength": 20}},
    },
}

PROFILE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["mood_tendency", "topic_interests", "self_context_tag"],
    "properties": {
        "mood_tendency": {"type": "string"},
        "topic_interests": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string"},
        },
        "self_context_tag": {"type": "string", "maxLength": 20},
    },
}


DEFAULT_PROMPT_VERSIONS = {
    "answer": "v4",
    "fortune": "v4",
    "profile": "v1",
}


DEFAULT_PROMPT_TEXT = {
    "answer": (
        "你是心运岛的答案之书。"
        "你会根据用户的问题，给出简短、富含哲思的回答。"
        "请用中文回答，尽量一句话，20字以内。"
        "不做医疗、法律、投资等专业诊断；不做绝对化承诺；避免高风险建议。"
        "问题：{{question}}"
    ),
    "fortune": (
        "你是心运岛的中文运势文案助手。"
        "请仅输出json对象，不要输出markdown或额外解释。"
        "字段必须包含：score,content_main,content_sub,love,career,health,wealth,yi,ji。"
        "日期：{{target_date}}"
    ),
    "profile": (
        "你是专业的心理与行为分析助手。"
        "请仅输出json对象，不要输出额外说明。"
        "字段必须包含：mood_tendency,topic_interests,self_context_tag。"
        "历史样本：{{diary_summary}}\n{{question_summary}}"
    ),
}


class RealProvider(LLMProvider):
    def __init__(self, model_name, api_key, timeout, max_retries, base_url=None, prompts_dir=None, prompt_versions=None):
        if not model_name:
            raise ValueError("LLM_MODEL_NAME is required")
        if not api_key:
            raise ValueError("LLM_API_KEY is required")

        self.model_name = model_name
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        backend_root = Path(__file__).resolve().parents[3]
        self.prompts_dir = Path(prompts_dir) if prompts_dir else (backend_root / "tools" / "prompt_lab" / "prompts")
        self.prompt_versions = dict(DEFAULT_PROMPT_VERSIONS)
        if isinstance(prompt_versions, dict):
            for key, value in prompt_versions.items():
                if key in self.prompt_versions and isinstance(value, str) and value.strip():
                    self.prompt_versions[key] = value.strip()

    def _render_inline(self, template, variables):
        rendered = str(template or "")
        for key, value in (variables or {}).items():
            rendered = rendered.replace("{{" + key + "}}", str(value))
            rendered = rendered.replace("{" + key + "}", str(value))
        return rendered

    def _load_prompt_template(self, task):
        version = self.prompt_versions.get(task, DEFAULT_PROMPT_VERSIONS.get(task, "v1"))
        path = self.prompts_dir / task / f"{version}.txt"
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return DEFAULT_PROMPT_TEXT[task]

    def _chat(self, messages, temperature=0.7, response_format=None, max_tokens=None, frequency_penalty=None, top_p=None):
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format is not None:
            payload["response_format"] = response_format
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if top_p is not None:
            payload["top_p"] = top_p
        body = json.dumps(payload).encode("utf-8")
        req = urlrequest.Request(
            url=f"{self.base_url}/chat/completions",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urlerror.HTTPError as err:
            detail = err.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"llm_http_{err.code}: {detail[:800]}") from err

        data = json.loads(raw)
        text = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
        if not text:
            raise RuntimeError("empty model output")
        return text

    def _extract_json(self, text):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start : end + 1])
            raise

    def _is_response_format_unsupported(self, err: Exception):
        text = str(err).lower()
        keys = ["response_format", "json_schema", "unsupported", "unknown parameter", "not support"]
        return any(key in text for key in keys)

    def _is_deepseek_base_url(self):
        return "deepseek.com" in (self.base_url or "").lower()

    def _chat_json_schema(self, messages, schema_name, schema, temperature=0.7, max_tokens=512):
        if self._is_deepseek_base_url():
            response_format = {"type": "json_object"}
        else:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            }
        try:
            text = self._chat(
                messages=messages,
                temperature=temperature,
                response_format=response_format,
                max_tokens=max_tokens,
            )
        except Exception as err:
            if not self._is_response_format_unsupported(err):
                raise
            text = self._chat(messages=messages, temperature=temperature, max_tokens=max_tokens)
        return self._extract_json(text)

    def _normalize_fortune(self, data):
        try:
            score = int(data.get("score", 70))
        except Exception:
            score = 70
        score = max(0, min(score, 100))

        yi = data.get("yi") if isinstance(data.get("yi"), list) else []
        ji = data.get("ji") if isinstance(data.get("ji"), list) else []

        return {
            "score": score,
            "content_main": str(data.get("content_main", "今日节奏平衡，先完成最重要的一件事。")).strip()[:80],
            "content_sub": str(data.get("content_sub", "稳中求进，心静则通达。")).strip()[:80],
            "love": str(data.get("love", "平稳")).strip()[:20],
            "career": str(data.get("career", "平稳")).strip()[:20],
            "health": str(data.get("health", "稳定")).strip()[:20],
            "wealth": str(data.get("wealth", "平稳")).strip()[:20],
            "yi": [str(item).strip()[:20] for item in yi[:5] if str(item).strip()],
            "ji": [str(item).strip()[:20] for item in ji[:5] if str(item).strip()],
        }

    def _normalize_profile(self, data):
        mood_tendency = str(data.get("mood_tendency", "calm")).strip()[:50] or "calm"

        raw_interests = data.get("topic_interests", [])
        topic_interests = []
        if isinstance(raw_interests, list):
            for item in raw_interests:
                value = str(item).strip()
                if value not in topic_interests:
                    topic_interests.append(value)
                if len(topic_interests) >= 3:
                    break
        if not topic_interests:
            topic_interests = ["health"]

        self_context_tag = str(data.get("self_context_tag", "日常")).strip()[:20] or "日常"

        return {
            "mood_tendency": mood_tendency,
            "topic_interests": topic_interests,
            "self_context_tag": self_context_tag,
        }

    def _truncate_answer_by_sentence(self, text, limit=100):
        raw = str(text or "").strip()
        if not raw:
            return ""

        if len(raw) <= limit:
            return raw

        sentence_endings = "。！？!?"
        cutoff_text = raw[:limit]
        last_end = -1
        for mark in sentence_endings:
            pos = cutoff_text.rfind(mark)
            if pos > last_end:
                last_end = pos

        if last_end >= 0:
            return cutoff_text[: last_end + 1].strip()

        return cutoff_text.strip()

    def generate_answer(self, question, user_id):
        _ = user_id
        version = self.prompt_versions.get("answer")
        if version == "v4":
            selector = AnswerStyleSelector(self.prompts_dir / "answer" / "styles")
            style = selector.select()
        else:
            style = ""
        prompt_text = self._load_prompt_template("answer")
        rendered = self._render_inline(
            prompt_text,
            {
                "question": question,
                "selected_style": style,
            },
        )
        text = self._chat(
            messages=[
                {
                    "role": "user",
                    "content": rendered,
                }
            ],
            temperature=1.2,
        )
        return self._truncate_answer_by_sentence(text, limit=100)

    def generate_fortune(self, user_id, target_date: date, profile_context=None, score=None, title_template=None, keywords=None, yiji_items=None):
        _ = user_id
        profile_context = profile_context or {}
        if score is not None and title_template is not None:
            version = "v4"
        else:
            version = self.prompt_versions.get("fortune")
        prompt_text = self._load_prompt_template("fortune")
        if version == "v4":
            selector = None
            if title_template is None or keywords is None or yiji_items is None:
                selector = FortuneContentSelector(self.prompts_dir / "fortune")

            score_value = int(score) if score is not None else 70
            score_value = max(0, min(score_value, 100))
            title_template = title_template or selector.select_title(score_value)
            keywords = keywords or selector.select_keywords(profile_context)
            yiji_items = yiji_items or selector.select_yiji(profile_context)

            rendered = self._render_inline(
                prompt_text,
                {
                    "target_date": target_date.isoformat(),
                    "score": str(score_value),
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
        else:
            rendered = self._render_inline(
                prompt_text,
                {
                    "target_date": target_date.isoformat(),
                    "mood_tendency": profile_context.get("mood_tendency", "calm"),
                    "topic_interests": ",".join(profile_context.get("topic_interests", [])) if isinstance(profile_context.get("topic_interests"), list) else profile_context.get("topic_interests", "health"),
                    "self_context_tag": profile_context.get("self_context_tag", "日常"),
                },
            )
        data = self._chat_json_schema(
            messages=[
                {
                    "role": "user",
                    "content": rendered,
                }
            ],
            schema_name="fortune_schema",
            schema=FORTUNE_SCHEMA,
            temperature=1.2,
            max_tokens=512,
        )
        return self._normalize_fortune(data if isinstance(data, dict) else {})

    def analyze_user_profile(self, diary_entries: list, answer_questions: list) -> dict:
        diary_summary = "\n".join(
            f"[{e.get('mood_tag', 'unknown')}] {e.get('content', '')[:100]}"
            if isinstance(e, dict)
            else f"[{getattr(e, 'mood_tag', 'unknown')}] {getattr(e, 'content', '')[:100]}"
            for e in (diary_entries or [])
        ) or "无日记记录"

        question_summary = "\n".join(
            q[:100] if isinstance(q, str) else (q.get("question", "")[:100] if isinstance(q, dict) else getattr(q, "question", "")[:100])
            for q in (answer_questions or [])
        ) or "无提问记录"

        prompt_text = self._load_prompt_template("profile")
        prompt = self._render_inline(
            prompt_text,
            {
                "diary_summary": diary_summary,
                "question_summary": question_summary,
            },
        )

        data = self._chat_json_schema(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            schema_name="profile_schema",
            schema=PROFILE_SCHEMA,
            temperature=0.6,
            max_tokens=400,
        )
        return self._normalize_profile(data if isinstance(data, dict) else {})

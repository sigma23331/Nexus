from datetime import date
import json
from urllib import request as urlrequest

from .base import LLMProvider


class RealProvider(LLMProvider):
    def __init__(self, model_name, api_key, timeout, max_retries, base_url=None):
        if not model_name:
            raise ValueError("LLM_MODEL_NAME is required")
        if not api_key:
            raise ValueError("LLM_API_KEY is required")

        self.model_name = model_name
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

    def _chat(self, messages, temperature=1.5):
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }
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

        with urlrequest.urlopen(req, timeout=self.timeout) as resp:
            raw = resp.read().decode("utf-8")

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

    def generate_answer(self, question, user_id):
        _ = user_id
        text = self._chat(
            messages=[
                {"role": "system", "content": "你是温和的中文陪伴助手。只回答一句话，100字以内。"},
                {"role": "user", "content": question},
            ],
            temperature=0.9,
        )
        return text[:100]

    def generate_fortune(self, user_id, target_date: date):
        _ = user_id
        text = self._chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "请输出JSON对象，包含字段：score,title,content,yi,ji,luckyColor,luckyDirection。"
                        "score是0-100整数；title不超过20字；content不超过200字；"
                        "yi和ji是字符串数组且最多5项；luckyColor和luckyDirection是字符串各最多10字。"
                        "只输出JSON。"
                    ),
                },
                {"role": "user", "content": f"日期: {target_date.isoformat()}"},
            ],
            temperature=0.9,
        )
        data = self._extract_json(text)
        score = int(data.get("score", 70))
        score = max(0, min(score, 100))

        yi = data.get("yi") if isinstance(data.get("yi"), list) else []
        ji = data.get("ji") if isinstance(data.get("ji"), list) else []

        return {
            "score": score,
            "title": str(data.get("title", "平稳 · 蓄力"))[:20],
            "content": str(data.get("content", "今日节奏平衡，先完成最重要的一件事。"))[:200],
            "yi": [str(item)[:20] for item in yi[:5]],
            "ji": [str(item)[:20] for item in ji[:5]],
            "luckyColor": str(data.get("luckyColor", ""))[:10] or None,
            "luckyDirection": str(data.get("luckyDirection", ""))[:10] or None,
        }

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

        prompt = f"""请根据以下用户数据，分析其情绪状态、兴趣主题和当前生活情景。

近期的日记记录（情绪标签 + 内容）：
{diary_summary}

近期的提问记录：
{question_summary}

请仅输出JSON，不要附带任何说明：
{{
  "mood_tendency": "用一个英文词概括用户的情绪倾向，如optimistic/calm/anxious/reflective/energetic",
  "topic_interests": ["最关注的1-3个兴趣领域，英文，从career/health/love/study/family/social/finance中选择"],
  "self_context_tag": "用5字以内的中文描述用户当前生活情景，如备考期/职场新人/情感波动期/成长期/日常"
}}"""

        text = self._chat(
            messages=[
                {"role": "system", "content": "你是专业的心理与行为分析助手，擅长从文本中洞察用户状态。请严格按格式输出JSON。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        data = self._extract_json(text)
        return {
            "mood_tendency": str(data.get("mood_tendency", "calm"))[:50],
            "topic_interests": data.get("topic_interests", ["health"]) if isinstance(data.get("topic_interests"), list) else ["health"],
            "self_context_tag": str(data.get("self_context_tag", "日常"))[:20],
        }

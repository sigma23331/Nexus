from datetime import date

from .base import LLMProvider


_MOOD_TENDENCIES = ["optimistic", "calm", "anxious", "reflective", "energetic"]
_INTEREST_POOL = ["career", "health", "love", "study", "family", "social", "finance"]
_CONTEXT_TAGS = ["日常", "备考期", "职场新人", "情感波动期", "成长期"]


class MockProvider(LLMProvider):
    def generate_answer(self, question, user_id):
        _ = user_id
        text = (question or "").strip()
        length = len(text)
        if length <= 8:
            return "先把今天能做的一步做好，答案会更清晰。"
        if length <= 20:
            return "现在不是犹豫的时候，全心投入。"
        return "方向已在路上，保持耐心与行动。"

    def generate_fortune(self, user_id, target_date: date):
        _ = user_id
        score = 70 + (target_date.day % 25)
        if score >= 85:
            title = "大吉 · 宜行"
        elif score >= 70:
            title = "小吉 · 守成"
        else:
            title = "平稳 · 蓄力"

        return {
            "score": score,
            "title": title,
            "content": "今日节奏平衡，先完成最重要的一件事。",
            "yi": ["规律作息", "专注学习", "温和沟通"],
            "ji": ["冲动决定", "过度熬夜", "拖延"],
        }

    def analyze_user_profile(self, diary_entries: list, answer_questions: list) -> dict:
        if diary_entries:
            mood_counts = {}
            for entry in diary_entries:
                tag = entry.get("mood_tag", "calm") if isinstance(entry, dict) else getattr(entry, "mood_tag", "calm")
                mood_counts[tag] = mood_counts.get(tag, 0) + 1
            dominant_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "calm"
        else:
            dominant_mood = "calm"

        mood_map = {"happy": "optimistic", "calm": "calm", "sad": "anxious", "angry": "anxious", "tired": "reflective"}
        mood_tendency = mood_map.get(str(dominant_mood).lower(), "calm")

        content_text = ""
        for entry in (diary_entries or []):
            text = entry.get("content", "") if isinstance(entry, dict) else getattr(entry, "content", "")
            content_text += text + " "
        for q in (answer_questions or []):
            text = q if isinstance(q, str) else q.get("question", "") if isinstance(q, dict) else getattr(q, "question", "")
            content_text += text + " "

        import random
        seed = len(content_text)
        rng = random.Random(seed)
        interests = rng.sample(_INTEREST_POOL, min(3, len(_INTEREST_POOL)))
        context_tag = _CONTEXT_TAGS[len(content_text) % len(_CONTEXT_TAGS)]

        return {
            "mood_tendency": mood_tendency,
            "topic_interests": interests,
            "self_context_tag": context_tag,
        }

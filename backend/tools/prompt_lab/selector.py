import random
import hashlib
from pathlib import Path


def stable_fortune_score(context, target_date=None):
    context = context if isinstance(context, dict) else {}
    user_id = (
        context.get("user_id")
        or context.get("virtual_user_id")
        or context.get("id")
        or context.get("sample_id")
        or "prompt-lab"
    )
    birthday = context.get("birthday") or context.get("birth_month_day") or ""
    date_value = target_date or context.get("target_date") or ""
    key = f"{user_id}|{birthday}|{date_value}"
    digest = hashlib.sha256(str(key).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % 101


class AnswerStyleSelector:
    def __init__(self, styles_dir):
        self.styles_dir = Path(styles_dir)
        self.styles = self._load()

    def _load(self):
        files = sorted(self.styles_dir.glob("*.txt"))
        if not files:
            raise ValueError("no style files found in " + str(self.styles_dir))
        styles = []
        for path in files:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                styles.append(text)
        if not styles:
            raise ValueError("no style files found in " + str(self.styles_dir))
        return styles

    def select(self):
        return random.choice(self.styles)


class FortuneContentSelector:
    def __init__(self, base_dir, default_explore_rate=0.25):
        self.base_dir = Path(base_dir)
        self.default_explore_rate = default_explore_rate
        self._titles = self._load_titles()
        self._keywords = self._load_keywords()
        self._yiji = self._load_yiji()

    def _score_to_segment(self, score):
        score = max(0, min(int(score), 100))
        if score >= 90:
            return "90-100"
        if score >= 75:
            return "75-89"
        if score >= 60:
            return "60-74"
        if score >= 40:
            return "40-59"
        return "0-39"

    def _parse_title_line(self, line):
        parts = line.split("||", 1)
        main = parts[0].strip() if parts else ""
        sub = parts[1].strip() if len(parts) > 1 else main
        return {"main": main, "sub": sub}

    def _load_titles(self):
        titles = {}
        for path in sorted((self.base_dir / "titles").glob("*.txt")):
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            titles[path.stem] = [self._parse_title_line(line) for line in lines if line.strip()]
        return titles

    def _load_keywords(self):
        keywords = {}
        for path in sorted((self.base_dir / "keywords").glob("*.txt")):
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            keywords[path.stem] = [line.strip() for line in lines if line.strip()]
        return keywords

    def _load_yiji(self):
        yiji = {}
        for path in sorted((self.base_dir / "yiji").glob("*.txt")):
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            yiji[path.stem] = [line.strip() for line in lines if line.strip()]
        return yiji

    def select_title(self, score):
        segment = self._score_to_segment(score)
        candidates = self._titles.get(segment, [])
        if not candidates:
            all_candidates = [item for group in self._titles.values() for item in group]
            if not all_candidates:
                return {"main": "今日宜静待时机", "sub": "稳中求进"}
            return random.choice(all_candidates)
        return random.choice(candidates)

    def _profile_tokens(self, profile):
        if not isinstance(profile, dict):
            return []

        values = []
        for key in ("topic_interests", "mood_tendency", "self_context_tag", "preferred_feature"):
            value = profile.get(key)
            if isinstance(value, list):
                values.extend(value)
            elif value:
                values.append(value)

        tokens = []
        for value in values:
            for token in str(value).replace("|", ",").replace("，", ",").split(","):
                token = token.strip().lower()
                if token and token not in tokens:
                    tokens.append(token)
        return tokens

    def _context_terms(self, context, *keys):
        if not isinstance(context, dict):
            return []

        terms = []
        for key in keys:
            value = context.get(key)
            if isinstance(value, list):
                raw_items = value
            else:
                raw_items = str(value or "").replace("，", ",").replace("、", ",").split(",")
            for item in raw_items:
                text = str(item or "").strip()
                if text and text not in terms:
                    terms.append(text)
        return terms

    def _stable_rank(self, key, category, candidate):
        digest = hashlib.sha256(f"{key}|{category}|{candidate}".encode("utf-8")).hexdigest()
        return int(digest[:12], 16)

    def _item_score(self, candidate, category, profile_tokens, context, bucket=None):
        text = str(candidate or "")
        lowered = text.lower()
        score = 1.0

        category_aliases = {
            "career": {"career", "job", "job_seek", "goal_job_change", "study", "work"},
            "health": {"health", "sleep", "sleep_low", "low_energy", "recovery"},
            "love": {"love", "relationship", "family", "social"},
            "wealth": {"wealth", "finance", "money"},
        }
        if set(profile_tokens) & category_aliases.get(category, set()):
            score += 2.0

        for token in profile_tokens:
            if token and token in lowered:
                score += 8.0

        taboo_terms = self._context_terms(context, "diversity_taboo_terms", "taboo_terms")
        if any(term and term in text for term in taboo_terms):
            score -= 20.0

        recent_ids = self._context_terms(context, "recent_shown_ids")
        item_id = f"{bucket}:{text}" if bucket else text
        score -= recent_ids.count(item_id) * 6.0
        score -= recent_ids.count(text) * 6.0

        low_energy = any(token in {"low_energy", "recovery", "sleep_low"} for token in profile_tokens)
        high_pressure_terms = ("冲刺", "突破", "全力推进", "主动推进", "加速", "发力")
        if low_energy and bucket == "yi" and any(term in text for term in high_pressure_terms):
            score -= 30.0

        return score

    def _rank_candidates(self, candidates, category, profile, context=None, bucket=None):
        profile_tokens = self._profile_tokens(profile)
        diversify_key = ""
        if isinstance(context, dict):
            diversify_key = str(context.get("diversify_key") or "")

        ranked = []
        for candidate in candidates:
            score = self._item_score(candidate, category, profile_tokens, context, bucket=bucket)
            tie_rank = self._stable_rank(diversify_key, category, candidate) if diversify_key else 0
            ranked.append(
                {
                    "value": candidate,
                    "score": score,
                    "tie_rank": tie_rank,
                }
            )
        ranked.sort(key=lambda item: (-item["score"], item["tie_rank"], item["value"]))
        return ranked

    def select_keywords_ranked(self, profile, context=None, k=3, explore_rate=None):
        if explore_rate is None:
            explore_rate = self.default_explore_rate

        strategy = "exploit"
        result = {}
        debug_candidates = {}
        for category in ("love", "career", "health", "wealth"):
            pool = self._keywords.get(category, [])
            if not pool:
                result[category] = "平稳"
                debug_candidates[category] = []
                continue

            ranked = self._rank_candidates(pool, category, profile, context=context)
            top = ranked[: max(1, min(k, len(ranked)))]
            debug_candidates[category] = top

            if len(top) > 1 and random.random() < explore_rate:
                strategy = "explore"
                result[category] = random.choice([item["value"] for item in top[1:]])
            else:
                result[category] = top[0]["value"]

        return result, {"strategy": strategy, "candidates": debug_candidates}

    def select_keywords(self, profile, context=None):
        selected, _debug = self.select_keywords_ranked(
            profile,
            context=context,
            explore_rate=self.default_explore_rate,
        )
        return selected

    def select_yiji_ranked(self, profile, context=None, k=6, per_bucket=3, explore_rate=None):
        if explore_rate is None:
            explore_rate = self.default_explore_rate

        selected = {}
        debug_candidates = {}
        strategy = "exploit"

        for bucket in ("yi", "ji"):
            pool = self._yiji.get(bucket, [])
            if not pool:
                selected[bucket] = []
                debug_candidates[bucket] = []
                continue

            ranked = self._rank_candidates(pool, bucket, profile, context=context, bucket=bucket)
            top = ranked[: max(1, min(k, len(ranked)))]
            debug_candidates[bucket] = top

            chosen = []
            prefixes = set()
            candidate_values = [item["value"] for item in top]
            if len(candidate_values) > 1 and random.random() < explore_rate:
                strategy = "explore"
                candidate_values = candidate_values[1:] + candidate_values[:1]

            for item in candidate_values:
                prefix = str(item)[:2]
                if prefix in prefixes and len(candidate_values) > per_bucket:
                    continue
                chosen.append(item)
                prefixes.add(prefix)
                if len(chosen) >= per_bucket:
                    break

            if len(chosen) < per_bucket:
                for item in candidate_values:
                    if item not in chosen:
                        chosen.append(item)
                    if len(chosen) >= per_bucket:
                        break

            selected[bucket] = chosen

        return selected, {"strategy": strategy, "candidates": debug_candidates}

    def select_yiji(self, profile, context=None):
        selected, _debug = self.select_yiji_ranked(
            profile,
            context=context,
            explore_rate=self.default_explore_rate,
        )
        return selected

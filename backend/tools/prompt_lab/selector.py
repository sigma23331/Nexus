import random
from pathlib import Path


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
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
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

    def select_keywords(self, profile):
        _ = profile or {}
        result = {}
        for category in ("love", "career", "health", "wealth"):
            pool = self._keywords.get(category, [])
            if pool:
                result[category] = random.choice(pool)
            else:
                result[category] = "平稳"
        return result

    def select_yiji(self, profile):
        _ = profile

        def _sample(pool, count=3):
            if not pool:
                return []
            if len(pool) <= count:
                return pool[:]
            return random.sample(pool, count)

        return {
            "yi": _sample(self._yiji.get("yi", [])),
            "ji": _sample(self._yiji.get("ji", [])),
        }

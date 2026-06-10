import math
import json
import re
from collections import Counter


def _to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _nearest_rank(values, percentile):
    if not values:
        return 0
    sorted_values = sorted(values)
    rank = int(math.ceil(percentile * len(sorted_values))) - 1
    rank = max(0, min(rank, len(sorted_values) - 1))
    return sorted_values[rank]


def _safe_ratio(num, den):
    if den == 0:
        return 0.0
    return num / den


def _output_text(row):
    text = str(row.get("output_text") or row.get("output_preview") or "").strip()
    if not text:
        return ""

    try:
        parsed = json.loads(text)
    except Exception:
        return text

    if not isinstance(parsed, dict):
        return text

    chunks = []
    for value in parsed.values():
        if isinstance(value, list):
            chunks.extend(str(item) for item in value)
        else:
            chunks.append(str(value))
    return " ".join(item.strip() for item in chunks if item.strip())


def _duplicate_rate(texts):
    values = [text for text in texts if text]
    if not values:
        return 0.0
    return _safe_ratio(len(values) - len(set(values)), len(values))


def _prefix_duplicate_rate(texts, size=4):
    prefixes = [text[:size] for text in texts if text]
    if not prefixes:
        return 0.0
    return _safe_ratio(len(prefixes) - len(set(prefixes)), len(prefixes))


def _extract_terms(texts):
    counter = Counter()
    for text in texts:
        for match in re.findall(r"[\u4e00-\u9fff]{2,6}|[A-Za-z_]{3,}", str(text or "")):
            if re.fullmatch(r"[\u4e00-\u9fff]{2,6}", match):
                for size in (2, 3, 4):
                    if len(match) >= size:
                        counter.update(match[i : i + size] for i in range(0, len(match) - size + 1))
            else:
                counter.update([match.lower()])
    return counter


def _top_terms_summary(texts, limit=5):
    counter = _extract_terms(texts)
    total = sum(counter.values())
    top = [{"term": term, "count": count} for term, count in counter.most_common(limit)]
    coverage = _safe_ratio(sum(item["count"] for item in top), total)
    return top, coverage


def build_group_summary(rows):
    grouped = {}
    for row in rows or []:
        task = row.get("task")
        prompt_version = row.get("prompt_version")
        temperature = round(_to_float(row.get("temperature")), 3)
        key = (task, prompt_version, temperature)
        grouped.setdefault(key, []).append(row)

    groups = []
    for key in sorted(grouped.keys(), key=lambda item: (str(item[0]), str(item[1]), item[2])):
        task, prompt_version, temperature = key
        items = grouped[key]

        latency_values = [int(_to_float(item.get("latency_ms"), 0)) for item in items]
        success_count = sum(1 for item in items if item.get("success") is True)
        fallback_count = sum(1 for item in items if item.get("fallback_used") is True)
        successful_texts = [_output_text(item) for item in items if item.get("success") is True]
        top_terms, top_terms_coverage = _top_terms_summary(successful_texts)

        parse_values = [item.get("parse_success") for item in items if item.get("parse_success") is not None]
        parse_fail_count = sum(1 for value in parse_values if value is False)

        schema_values = [item.get("schema_valid") for item in items if item.get("schema_valid") is not None]
        schema_valid_count = sum(1 for value in schema_values if value is True)

        groups.append(
            {
                "task": task,
                "prompt_version": prompt_version,
                "temperature": temperature,
                "sample_count": len(items),
                "success_rate": _safe_ratio(success_count, len(items)),
                "parse_fail_rate": _safe_ratio(parse_fail_count, len(parse_values)),
                "schema_valid_rate": _safe_ratio(schema_valid_count, len(schema_values)),
                "fallback_rate": _safe_ratio(fallback_count, len(items)),
                "p50_latency_ms": _nearest_rank(latency_values, 0.5),
                "p95_latency_ms": _nearest_rank(latency_values, 0.95),
                "duplicate_rate": _duplicate_rate(successful_texts),
                "prefix_duplicate_rate": _prefix_duplicate_rate(successful_texts),
                "top_terms": top_terms,
                "top_terms_coverage": top_terms_coverage,
            }
        )

    return groups

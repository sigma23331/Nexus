import math


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
            }
        )

    return groups

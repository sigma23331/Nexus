from backend.tools.prompt_lab.metrics import build_group_summary


def test_summary_uses_non_null_denominator_for_parse_schema():
    rows = [
        {
            "task": "answer",
            "prompt_version": "v1",
            "temperature": 0.7,
            "parse_success": None,
            "schema_valid": None,
            "fallback_used": False,
            "success": True,
            "latency_ms": 20,
        },
        {
            "task": "fortune",
            "prompt_version": "v1",
            "temperature": 0.58,
            "parse_success": False,
            "schema_valid": False,
            "fallback_used": True,
            "success": False,
            "latency_ms": 40,
        },
    ]

    groups = build_group_summary(rows)
    fortune = [g for g in groups if g["task"] == "fortune"][0]
    assert fortune["parse_fail_rate"] == 1.0
    assert fortune["schema_valid_rate"] == 0.0


def test_summary_computes_latency_percentiles():
    rows = [
        {
            "task": "answer",
            "prompt_version": "v1",
            "temperature": 0.7,
            "parse_success": None,
            "schema_valid": None,
            "fallback_used": False,
            "success": True,
            "latency_ms": x,
        }
        for x in [10, 20, 30, 40, 50]
    ]

    groups = build_group_summary(rows)
    assert groups[0]["p50_latency_ms"] == 30
    assert groups[0]["p95_latency_ms"] == 50

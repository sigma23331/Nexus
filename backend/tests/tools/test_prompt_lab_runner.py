import pytest

from backend.tools.prompt_lab.runner import expand_cases, run_experiment


def test_expand_cases_cartesian_product():
    cases = expand_cases(
        samples={"fortune": [{"id": "f1"}, {"id": "f2"}]},
        versions={"fortune": ["v1", "v2"]},
        temps={"fortune": [0.58, 0.3]},
        repeat=2,
    )
    assert len(cases) == 2 * 2 * 2 * 2


def test_expand_cases_dedupes_versions_and_temps_stably():
    cases = expand_cases(
        samples={"answer": [{"id": "a1"}]},
        versions={"answer": ["v1", "v1", "v2"]},
        temps={"answer": [0.7, 0.7, 0.9]},
        repeat=1,
    )
    pairs = [(c["prompt_version"], c["temperature"]) for c in cases]
    assert pairs == [("v1", 0.7), ("v1", 0.9), ("v2", 0.7), ("v2", 0.9)]


def test_expand_cases_requires_non_empty_per_task():
    with pytest.raises(ValueError, match="invalid_cli_args"):
        expand_cases(
            samples={"answer": [{"id": "a1"}]},
            versions={"answer": []},
            temps={"answer": [0.7]},
            repeat=1,
        )


def test_run_experiment_continues_after_row_error():
    def executor(case):
        if case["sample_id"] == "bad":
            raise RuntimeError("boom")
        return {"success": True, "error_code": None, "error_message": "", "sample_id": case["sample_id"]}

    cases = [
        {"sample_id": "ok1"},
        {"sample_id": "bad"},
        {"sample_id": "ok2"},
    ]

    results = run_experiment(cases, executor)
    assert len(results) == 3
    assert [r["success"] for r in results] == [True, False, True]
    assert results[1]["error_code"] == "provider_error"
    assert results[1]["output_text"] == ""

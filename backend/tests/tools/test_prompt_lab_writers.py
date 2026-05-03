import json

from backend.tools.prompt_lab.writers import (
    write_meta_json,
    write_results_jsonl,
    write_summary_json,
)


def test_write_results_jsonl_creates_line_delimited_json(tmp_path):
    out = tmp_path / "results.jsonl"
    write_results_jsonl(out, [{"task": "answer", "sample_id": "a1"}])
    assert out.exists()
    assert out.read_text(encoding="utf-8").count("\n") == 1


def test_write_summary_and_meta_have_required_keys(tmp_path):
    write_summary_json(tmp_path / "summary.json", run_id="r1", groups=[])
    write_meta_json(tmp_path / "meta.json", {"provider": "mock"})

    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))

    assert {"run_id", "generated_at_utc", "groups"} <= set(summary.keys())
    assert meta["provider"] == "mock"

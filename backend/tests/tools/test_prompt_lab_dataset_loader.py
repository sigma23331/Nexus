from backend.tools.prompt_lab.dataset_loader import load_dataset


def test_load_dataset_accepts_three_tasks(tmp_path):
    p = tmp_path / "ok.jsonl"
    p.write_text(
        '{"task":"answer","id":"a1","question":"Q"}\n'
        '{"task":"fortune","id":"f1","target_date":"2026-04-29"}\n'
        '{"task":"profile","id":"p1","diary_entries":[],"answer_questions":[]}\n',
        encoding="utf-8",
    )
    rows, errors = load_dataset(p)
    assert len(rows) == 3
    assert errors == []


def test_load_dataset_collects_row_errors(tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text(
        '{"task":"answer","id":"dup","question":"Q"}\n'
        '{"task":"fortune","id":"dup","target_date":"2026-04-29"}\n'
        '{"task":"answer","id":"a2"}\n'
        '{"task":"unknown","id":"x1","question":"x"}\n'
        '{"task":"fortune","id":"f2","target_date":"2026/04/29"}\n'
        '{not-json}\n',
        encoding="utf-8",
    )
    rows, errors = load_dataset(p)
    assert len(rows) == 1
    codes = {e["error_code"] for e in errors}
    assert {"duplicate_sample_id", "missing_required_field", "unsupported_task", "invalid_date", "invalid_json"} <= codes

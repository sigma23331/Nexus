import json
from datetime import datetime
from pathlib import Path


def _ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def write_results_jsonl(path, rows):
    path = Path(path)
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_summary_json(path, run_id, groups):
    path = Path(path)
    _ensure_parent(path)
    payload = {
        "run_id": run_id,
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "groups": groups or [],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_meta_json(path, meta):
    path = Path(path)
    _ensure_parent(path)
    payload = dict(meta or {})
    payload.setdefault("generated_at_utc", datetime.utcnow().isoformat() + "Z")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

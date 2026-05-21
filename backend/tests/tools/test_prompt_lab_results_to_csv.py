import csv
import json

from tools.prompt_lab.results_to_csv import convert_results_jsonl_to_csv


def test_convert_results_jsonl_to_csv_extracts_fortune_fields(tmp_path):
    input_path = tmp_path / "results.jsonl"
    output_path = tmp_path / "results.csv"

    output_payload = {
        "score": 88,
        "content_main": "今天节奏顺畅，宜稳步推进。",
        "content_sub": "先做最重要的一件事。",
        "love": "升温",
        "career": "向好",
        "health": "稳定",
        "wealth": "谨慎",
        "yi": ["复盘", "运动"],
        "ji": ["熬夜"],
    }
    row = {
        "task": "fortune",
        "sample_id": "tu_001",
        "repeat_index": 0,
        "success": True,
        "error_code": None,
        "generated_at": "2026-05-04T06:59:00Z",
        "output_text": json.dumps(output_payload, ensure_ascii=False),
    }
    input_path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")

    written = convert_results_jsonl_to_csv(input_path, output_path)

    assert written == 1
    with output_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["sample_id"] == "tu_001"
    assert rows[0]["score"] == "88"
    assert rows[0]["content_main"] == "今天节奏顺畅，宜稳步推进。"
    assert rows[0]["yi"] == "复盘|运动"
    assert rows[0]["ji"] == "熬夜"

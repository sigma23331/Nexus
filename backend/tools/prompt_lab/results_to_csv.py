import argparse
import csv
import json
from pathlib import Path


CSV_HEADERS = [
    "task",
    "sample_id",
    "repeat_index",
    "success",
    "error_code",
    "generated_at",
    "score",
    "content_main",
    "content_sub",
    "love",
    "career",
    "health",
    "wealth",
    "yi",
    "ji",
    "gua_meaning_lines",
    "lucky_hour_name",
    "lucky_hour_range",
]


def _parse_output_payload(output_text):
    if not isinstance(output_text, str) or not output_text.strip():
        return {}
    try:
        parsed = json.loads(output_text)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _join_list(value):
    if not isinstance(value, list):
        return ""
    return "|".join(str(item).strip() for item in value if str(item).strip())


def convert_results_jsonl_to_csv(input_path, output_path):
    source = Path(input_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with source.open("r", encoding="utf-8") as reader, target.open("w", encoding="utf-8-sig", newline="") as writer:
        csv_writer = csv.DictWriter(writer, fieldnames=CSV_HEADERS)
        csv_writer.writeheader()

        for raw in reader:
            line = raw.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except Exception:
                continue
            if not isinstance(row, dict):
                continue

            payload = _parse_output_payload(row.get("output_text", ""))
            csv_row = {
                "task": row.get("task", ""),
                "sample_id": row.get("sample_id", ""),
                "repeat_index": row.get("repeat_index", ""),
                "success": row.get("success", ""),
                "error_code": row.get("error_code", ""),
                "generated_at": row.get("generated_at", ""),
                "score": payload.get("score", ""),
                "content_main": payload.get("content_main", ""),
                "content_sub": payload.get("content_sub", ""),
                "love": payload.get("love", ""),
                "career": payload.get("career", ""),
                "health": payload.get("health", ""),
                "wealth": payload.get("wealth", ""),
                "yi": _join_list(payload.get("yi", [])),
                "ji": _join_list(payload.get("ji", [])),
                "gua_meaning_lines": _join_list(payload.get("gua_meaning_lines", [])),
                "lucky_hour_name": payload.get("lucky_hour_name", ""),
                "lucky_hour_range": payload.get("lucky_hour_range", ""),
            }
            csv_writer.writerow(csv_row)
            count += 1
    return count


def build_parser():
    parser = argparse.ArgumentParser(description="Convert Prompt Lab results.jsonl to CSV")
    parser.add_argument("--input", required=True, help="Path to results.jsonl")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    rows = convert_results_jsonl_to_csv(args.input, args.output)
    print(f"converted_rows={rows}")
    print(f"csv_path={Path(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import json
from datetime import datetime
from pathlib import Path


SUPPORTED_TASKS = {"answer", "fortune", "profile"}


def _error(line, error_code, error_message):
    return {
        "line": line,
        "error_code": error_code,
        "error_message": error_message,
    }


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _validate_task_payload(task, item):
    if task == "answer":
        if not _is_non_empty_string(item.get("question")):
            return "missing_required_field", "answer.question is required"
        return None, None

    if task == "fortune":
        target_date = item.get("target_date")
        if not _is_non_empty_string(target_date):
            return "missing_required_field", "fortune.target_date is required"
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            return "invalid_date", "target_date must use YYYY-MM-DD"
        return None, None

    if task == "profile":
        if "diary_entries" not in item or "answer_questions" not in item:
            return "missing_required_field", "profile arrays are required"
        if not isinstance(item.get("diary_entries"), list) or not isinstance(item.get("answer_questions"), list):
            return "missing_required_field", "profile arrays must be lists"
        return None, None

    return "unsupported_task", "task is not supported"


def load_dataset(path):
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = []
    errors = []
    seen_ids = set()

    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue

        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            errors.append(_error(line_no, "invalid_json", "line is not valid json"))
            continue

        if not isinstance(item, dict):
            errors.append(_error(line_no, "invalid_json", "line must be a json object"))
            continue

        sample_id = item.get("id")
        if not _is_non_empty_string(sample_id):
            errors.append(_error(line_no, "missing_required_field", "id is required"))
            continue

        if sample_id in seen_ids:
            errors.append(_error(line_no, "duplicate_sample_id", "id must be globally unique"))
            continue

        task = item.get("task")
        if task not in SUPPORTED_TASKS:
            errors.append(_error(line_no, "unsupported_task", "task is not supported"))
            continue

        error_code, error_message = _validate_task_payload(task, item)
        if error_code:
            errors.append(_error(line_no, error_code, error_message))
            continue

        seen_ids.add(sample_id)
        rows.append(item)

    return rows, errors

def _stable_unique(values):
    seen = set()
    output = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def expand_cases(samples, versions, temps, repeat):
    if repeat < 1:
        raise ValueError("invalid_cli_args: repeat must be >=1")

    cases = []
    for task_name, task_samples in (samples or {}).items():
        version_list = _stable_unique(list((versions or {}).get(task_name) or []))
        temp_list = _stable_unique(list((temps or {}).get(task_name) or []))

        if not task_samples or not version_list or not temp_list:
            raise ValueError("invalid_cli_args")

        for sample in task_samples:
            sample_id = sample.get("id")
            for prompt_version in version_list:
                for temperature in temp_list:
                    for repeat_index in range(repeat):
                        cases.append(
                            {
                                "task": task_name,
                                "sample": sample,
                                "sample_id": sample_id,
                                "prompt_version": prompt_version,
                                "temperature": temperature,
                                "repeat_index": repeat_index,
                            }
                        )
    return cases


def run_experiment(cases, executor):
    results = []
    for case in (cases or []):
        try:
            row = executor(case)
            row.setdefault("success", True)
            row.setdefault("error_code", None)
            row.setdefault("error_message", "")
        except Exception as exc:
            row = {
                "task": case.get("task"),
                "prompt_version": case.get("prompt_version"),
                "temperature": case.get("temperature"),
                "success": False,
                "error_code": "provider_error",
                "error_message": str(exc)[:200],
            }
        if "sample_id" not in row:
            row["sample_id"] = case.get("sample_id")
        row.setdefault("task", case.get("task"))
        row.setdefault("prompt_version", case.get("prompt_version"))
        row.setdefault("temperature", case.get("temperature"))
        row.setdefault("parse_success", None)
        row.setdefault("schema_valid", None)
        row.setdefault("fallback_used", False)
        row.setdefault("latency_ms", 0)
        row.setdefault("output_chars", 0)
        row.setdefault("output_preview", "")
        row.setdefault("output_text", "")
        results.append(row)
    return results

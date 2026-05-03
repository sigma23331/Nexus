from pathlib import Path


def _to_str(value):
    return "" if value is None else str(value)


def build_diary_summary(entries):
    entries = entries or []
    if not entries:
        return "无日记记录"

    lines = []
    for entry in entries[:20]:
        if not isinstance(entry, dict):
            continue
        mood_tag = _to_str(entry.get("mood_tag") or "unknown").strip()
        content = _to_str(entry.get("content")).strip()[:100]
        lines.append(f"[{mood_tag}] {content}")

    return "\n".join(lines) if lines else "无日记记录"


def build_question_summary(questions):
    questions = questions or []
    if not questions:
        return "无提问记录"

    lines = []
    for question in questions[:20]:
        if isinstance(question, dict):
            text = _to_str(question.get("question")).strip()
        else:
            text = _to_str(question).strip()
        lines.append(text[:100])

    filtered = [line for line in lines if line]
    return "\n".join(filtered) if filtered else "无提问记录"


def render_template(template_path, variables):
    variables = variables or {}
    template = Path(template_path).read_text(encoding="utf-8")

    mapping = {
        "question": _to_str(variables.get("question")),
        "target_date": _to_str(variables.get("target_date")),
        "diary_summary": build_diary_summary(variables.get("diary_entries")),
        "question_summary": build_question_summary(variables.get("answer_questions")),
    }

    output = template
    for key, value in mapping.items():
        output = output.replace("{{" + key + "}}", value)
        output = output.replace("{" + key + "}", value)
    for key, value in variables.items():
        text = _to_str(value)
        output = output.replace("{{" + key + "}}", text)
        output = output.replace("{" + key + "}", text)
    return output

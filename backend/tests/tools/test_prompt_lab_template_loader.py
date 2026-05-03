from backend.tools.prompt_lab.template_loader import (
    build_diary_summary,
    build_question_summary,
    render_template,
)


def test_render_template_replaces_known_placeholders(tmp_path):
    t = tmp_path / "t.txt"
    t.write_text("Q={{question}} D={{target_date}}", encoding="utf-8")
    out = render_template(t, {"question": "hello", "target_date": "2026-04-29"})
    assert out == "Q=hello D=2026-04-29"


def test_profile_summary_uses_fixed_limits_and_fallbacks():
    diary = [{"mood_tag": "happy", "content": "x" * 120}]
    questions = [{"question": "y" * 120}]

    d = build_diary_summary(diary)
    q = build_question_summary(questions)

    assert d.startswith("[happy] ")
    assert len(d.split("\n")[0]) <= len("[happy] ") + 100
    assert len(q.split("\n")[0]) == 100


def test_profile_summary_uses_empty_fallbacks():
    assert build_diary_summary([]) == "无日记记录"
    assert build_question_summary([]) == "无提问记录"

import json

from backend.tools.prompt_lab_cli import main


def test_cli_returns_2_for_invalid_args():
    rc = main(["run", "--task", "all"])
    assert rc == 2


def test_cli_run_creates_required_artifacts(tmp_path):
    dataset = tmp_path / "smoke.jsonl"
    dataset.write_text(
        '{"task":"answer","id":"a1","question":"今天会顺利吗"}\n'
        '{"task":"fortune","id":"f1","target_date":"2026-04-29"}\n'
        '{"task":"profile","id":"p1","diary_entries":[],"answer_questions":[]}\n',
        encoding="utf-8",
    )

    prompts_dir = tmp_path / "prompts"
    (prompts_dir / "answer").mkdir(parents=True)
    (prompts_dir / "fortune").mkdir(parents=True)
    (prompts_dir / "profile").mkdir(parents=True)
    (prompts_dir / "answer" / "v1.txt").write_text("{{question}}", encoding="utf-8")
    (prompts_dir / "fortune" / "v1.txt").write_text("{{target_date}}", encoding="utf-8")
    (prompts_dir / "profile" / "v1.txt").write_text("{{diary_summary}}\n{{question_summary}}", encoding="utf-8")

    runs_dir = tmp_path / "runs"
    rc = main(
        [
            "run",
            "--dataset",
            str(dataset),
            "--prompts-dir",
            str(prompts_dir),
            "--runs-dir",
            str(runs_dir),
            "--task",
            "all",
            "--version",
            "answer:v1",
            "--version",
            "fortune:v1",
            "--version",
            "profile:v1",
            "--temp",
            "answer:0.7",
            "--temp",
            "fortune:0.58",
            "--temp",
            "profile:0.3",
            "--provider",
            "mock",
        ]
    )
    assert rc == 0

    run_dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
    assert len(run_dirs) == 1

    run_dir = run_dirs[0]
    assert (run_dir / "results.jsonl").exists()
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "meta.json").exists()

    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["run_id"]
    assert isinstance(summary["groups"], list)

import argparse
import random
import sys
import uuid
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from tools.prompt_lab.dataset_loader import load_dataset
from tools.prompt_lab.metrics import build_group_summary
from tools.prompt_lab.provider_adapter import PromptLabProviderAdapter
from tools.prompt_lab.runner import expand_cases, run_experiment
from tools.prompt_lab.selector import AnswerStyleSelector, FortuneContentSelector
from tools.prompt_lab.template_loader import render_template
from tools.prompt_lab.writers import write_meta_json, write_results_jsonl, write_summary_json


TASKS = ["answer", "fortune", "profile"]


def _parse_key_values(entries, parser, kind):
    result = {}
    for raw in entries or []:
        if ":" not in raw:
            parser.error(f"invalid {kind} format: {raw}")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key not in TASKS or not value:
            parser.error(f"invalid {kind} item: {raw}")
        result.setdefault(key, []).append(value)
    return result


def _parse_temps(entries, parser):
    parsed = {}
    raw_map = _parse_key_values(entries, parser, "temp")
    for task, values in raw_map.items():
        parsed_values = []
        for raw_value in values:
            try:
                value = float(raw_value)
            except ValueError:
                parser.error(f"invalid temperature value: {raw_value}")
            if value < 0 or value > 2:
                parser.error(f"temperature out of range [0,2]: {raw_value}")
            parsed_values.append(round(value, 3))
        parsed[task] = parsed_values
    return parsed


def _selected_tasks(task_option):
    if task_option == "all":
        return TASKS[:]
    return [task_option]


def _validate_combo_coverage(selected, versions, temps, parser):
    selected_set = set(selected)
    provided = set(versions.keys()) | set(temps.keys())
    if not provided.issubset(selected_set):
        parser.error("invalid_cli_args: provided version/temp for unselected task")

    for task in selected:
        if task not in versions or not versions.get(task):
            parser.error(f"invalid_cli_args: missing --version for task {task}")
        if task not in temps or not temps.get(task):
            parser.error(f"invalid_cli_args: missing --temp for task {task}")


def _build_dataset_error_rows(errors):
    rows = []
    for error in errors or []:
        rows.append(
            {
                "task": "dataset",
                "sample_id": f"line-{error.get('line')}",
                "prompt_version": "n/a",
                "temperature": 0.0,
                "success": False,
                "parse_success": None,
                "schema_valid": None,
                "fallback_used": False,
                "error_code": error.get("error_code"),
                "error_message": str(error.get("error_message") or "")[:200],
                "latency_ms": 0,
                "output_chars": 0,
                "output_preview": "",
            }
        )
    return rows


def _make_executor(adapter, prompts_dir):
    prompts_dir = Path(prompts_dir)
    answer_selector = None
    fortune_selector = None
    try:
        answer_selector = AnswerStyleSelector(prompts_dir / "answer" / "styles")
    except Exception:
        answer_selector = None
    try:
        fortune_selector = FortuneContentSelector(prompts_dir / "fortune")
    except Exception:
        fortune_selector = None

    def _executor(case):
        sample = case["sample"]
        task = case["task"]
        prompt_version = case["prompt_version"]
        temperature = case["temperature"]

        template_path = prompts_dir / task / f"{prompt_version}.txt"
        if not template_path.exists():
            raise FileNotFoundError(f"template_missing: {template_path}")

        if task == "answer":
            style = answer_selector.select() if answer_selector else ""
            prompt_text = render_template(template_path, {"question": sample["question"], "selected_style": style})
            row = adapter.run_answer(question=sample["question"], prompt_text=prompt_text, temperature=temperature)
        elif task == "fortune":
            context = {
                "mood_tendency": sample.get("mood_tendency"),
                "topic_interests": sample.get("topic_interests"),
                "self_context_tag": sample.get("self_context_tag"),
            }
            score = random.randint(0, 100)
            if fortune_selector:
                title_template = fortune_selector.select_title(score)
                keywords = fortune_selector.select_keywords(context)
                yiji_items = fortune_selector.select_yiji(context)
            else:
                title_template = {"main": "今日宜静待时机", "sub": "稳中求进"}
                keywords = {"love": "平稳", "career": "平稳", "health": "稳定", "wealth": "平稳"}
                yiji_items = {"yi": [], "ji": []}

            prompt_text = render_template(
                template_path,
                {
                    "target_date": sample["target_date"],
                    "score": str(score),
                    "title_main": title_template.get("main", "今日宜静待时机"),
                    "title_sub": title_template.get("sub", "稳中求进"),
                    "love_keyword": keywords.get("love", "平稳"),
                    "career_keyword": keywords.get("career", "平稳"),
                    "health_keyword": keywords.get("health", "稳定"),
                    "wealth_keyword": keywords.get("wealth", "平稳"),
                    "yi_samples": "\n".join(yiji_items.get("yi", [])),
                    "ji_samples": "\n".join(yiji_items.get("ji", [])),
                    "mood_tendency": context.get("mood_tendency") or "calm",
                    "topic_interests": context.get("topic_interests") or "",
                    "self_context_tag": context.get("self_context_tag") or "日常",
                },
            )
            row = adapter.run_fortune(target_date=sample["target_date"], prompt_text=prompt_text, temperature=temperature, profile_context=context)
        else:
            prompt_text = render_template(
                template_path,
                {
                    "diary_entries": sample.get("diary_entries", []),
                    "answer_questions": sample.get("answer_questions", []),
                },
            )
            row = adapter.run_profile(
                diary_entries=sample.get("diary_entries", []),
                answer_questions=sample.get("answer_questions", []),
                prompt_text=prompt_text,
                temperature=temperature,
            )

        row["task"] = task
        row["sample_id"] = sample.get("id")
        row["prompt_version"] = prompt_version
        row["temperature"] = temperature
        row["repeat_index"] = case.get("repeat_index", 0)
        return row

    return _executor


def _run_command(args, parser):
    selected = _selected_tasks(args.task)
    versions = _parse_key_values(args.version, parser, "version")
    temps = _parse_temps(args.temp, parser)
    _validate_combo_coverage(selected, versions, temps, parser)

    dataset_rows, dataset_errors = load_dataset(args.dataset)
    by_task = {task: [] for task in selected}
    for row in dataset_rows:
        task = row.get("task")
        if task in by_task:
            by_task[task].append(row)

    for task in selected:
        if not by_task.get(task):
            parser.error(f"invalid_cli_args: no dataset rows for selected task {task}")

    adapter = PromptLabProviderAdapter(
        provider_mode=args.provider,
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key,
        timeout=args.timeout,
        max_retries=args.max_retries,
    )

    cases = expand_cases(by_task, versions, temps, args.repeat)
    results = _build_dataset_error_rows(dataset_errors)
    results.extend(run_experiment(cases, _make_executor(adapter, args.prompts_dir)))

    groups = build_group_summary(results)

    run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_dir = Path(args.runs_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    write_results_jsonl(run_dir / "results.jsonl", results)
    write_summary_json(run_dir / "summary.json", run_id=run_id, groups=groups)
    write_meta_json(
        run_dir / "meta.json",
        {
            "run_id": run_id,
            "dataset": str(args.dataset),
            "prompts_dir": str(args.prompts_dir),
            "task": args.task,
            "versions": versions,
            "temps": temps,
            "repeat": args.repeat,
            "provider": args.provider,
            "base_url": args.base_url,
            "model": args.model,
            "max_workers": args.max_workers,
        },
    )
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Prompt Lab CLI — 离线实验工具，支持多版本多温度的提示词组合测试与指标汇总")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="运行一组 Prompt Lab 实验并产出结果/summary/meta 文件")
    run_parser.add_argument("--dataset", required=True, help="JSONL 数据集文件路径")
    run_parser.add_argument("--prompts-dir", default=str(BACKEND_ROOT / "tools" / "prompt_lab" / "prompts"), help="提示词模板目录（按 task/version.txt 组织）")
    run_parser.add_argument("--runs-dir", default=str(BACKEND_ROOT / "tools" / "prompt_lab" / "runs"), help="运行产物输出目录")
    run_parser.add_argument("--task", required=True, choices=["answer", "fortune", "profile", "all"], help="运行任务类型，all 表示全部三种")
    run_parser.add_argument("--version", action="append", default=[], help="指定提示词版本，可重复，格式 task:version（如 answer:v3）")
    run_parser.add_argument("--temp", action="append", default=[], help="指定温度，可重复，格式 task:value（如 fortune:0.58）")
    run_parser.add_argument("--repeat", type=int, default=1, help="每组实验重复次数")
    run_parser.add_argument("--provider", choices=["real", "mock"], default="real", help="LLM 提供方，real 调真实模型，mock 用模板兜底")
    run_parser.add_argument("--base-url", default=None, help="LLM API 基础地址")
    run_parser.add_argument("--model", default=None, help="模型名称")
    run_parser.add_argument("--api-key", default=None, help="API 密钥")
    run_parser.add_argument("--timeout", type=int, default=12, help="请求超时秒数")
    run_parser.add_argument("--max-retries", type=int, default=1, help="失败重试次数")
    run_parser.add_argument("--max-workers", type=int, default=1, help="并发工作数（当前仅单线程）")
    return parser


def main(argv=None):
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if args.command != "run":
        return 2

    try:
        return _run_command(args, parser)
    except SystemExit as exc:
        return int(exc.code)
    except Exception as exc:
        print(f"prompt_lab_error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

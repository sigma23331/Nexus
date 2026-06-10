import argparse
import hashlib
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
from tools.prompt_lab.selector import AnswerStyleSelector, FortuneContentSelector, stable_fortune_score
from tools.prompt_lab.template_loader import render_template
from tools.prompt_lab.writers import write_meta_json, write_results_jsonl, write_summary_json


TASKS = ["answer", "fortune", "profile"]
DEFAULT_TABOO_TERMS = "稳中求进、调整节奏、静待时机、静待花开、低潮是缓冲区、先修复状态、再决定下一步、早睡早起、出门散步、整理书桌、冲动消费、收支平稳、多看少动"
SENTENCE_SHAPES = ["短句 + 留白", "短句 + 轻动作", "转折短句", "状态 + 边界", "动作 + 余地"]
TONES = ["温和", "克制", "明亮", "干净"]
RHYTHMS = ["短促", "慢速", "留白"]
ANSWER_LENGTH_RULES = ["8-10 个汉字", "11-14 个汉字", "15-18 个汉字"]
CHINESE_HOURS = [
    ("子时", "23:00-01:00"),
    ("丑时", "01:00-03:00"),
    ("寅时", "03:00-05:00"),
    ("卯时", "05:00-07:00"),
    ("辰时", "07:00-09:00"),
    ("巳时", "09:00-11:00"),
    ("午时", "11:00-13:00"),
    ("未时", "13:00-15:00"),
    ("申时", "15:00-17:00"),
    ("酉时", "17:00-19:00"),
    ("戌时", "19:00-21:00"),
    ("亥时", "21:00-23:00"),
]


def _join_profile_value(value):
    if isinstance(value, list):
        return ",".join(str(item).strip() for item in value if str(item).strip())
    return str(value or "").strip()


def _profile_context_from_sample(sample):
    return {
        "user_id": sample.get("user_id") or "",
        "virtual_user_id": sample.get("virtual_user_id") or "",
        "id": sample.get("id") or "",
        "birthday": sample.get("birthday") or "",
        "birth_month_day": sample.get("birth_month_day") or "",
        "answer_style": sample.get("answer_style") or "philosophical",
        "mood_tendency": sample.get("mood_tendency") or "",
        "topic_interests": sample.get("topic_interests") or [],
        "self_context_tag": sample.get("self_context_tag") or "",
    }


def _personalization_plan(context, task):
    mood = str(context.get("mood_tendency") or "")
    topics = _join_profile_value(context.get("topic_interests"))
    state = str(context.get("self_context_tag") or "")
    parts = []
    if "anxious" in mood or "sensitive" in mood or "tense" in mood:
        parts.append("语气温和，低压力，不催促")
    if "low_energy" in mood or "very_low_energy" in mood or "sleep_low" in state or "recovery" in state:
        parts.append("低负担，避免高压动作")
    if any(token in topics for token in ("career", "job", "study", "goal_exam")):
        parts.append("事业/学习字段略偏秩序、清明和可承接，不写具体任务")
    if any(token in topics for token in ("health", "sleep", "recovery")):
        parts.append("健康字段更轻柔，偏恢复和自我照看")
    if any(token in topics for token in ("wealth", "finance")):
        parts.append("财富字段保持谨慎，不给投资判断")
    if any(token in topics for token in ("relationship", "love", "social")):
        parts.append("关系字段保留余地，不制造情绪压力")
    if not parts:
        parts.append("语气平稳，动作轻巧，保留留白")
    if task == "answer":
        parts.append("答案不得复述问题或画像标签")
    return "；".join(parts)


def _low_cost_diversity_controls(context, task):
    mood = str(context.get("mood_tendency") or "")
    state = str(context.get("self_context_tag") or "")
    low_pressure = any(token in mood or token in state for token in ("anxious", "tense", "low_energy", "very_low_energy", "sleep_low", "recovery"))
    tone_pool = ["温和", "克制"] if low_pressure else TONES
    return {
        "sentence_shape": random.choice(SENTENCE_SHAPES),
        "tone": random.choice(tone_pool),
        "rhythm": random.choice(RHYTHMS),
        "length_rule": random.choice(ANSWER_LENGTH_RULES) if task == "answer" else "按字段长度约束",
    }


def _stable_index(key, modulo):
    if modulo <= 0:
        return 0
    digest = hashlib.sha256(str(key).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % modulo


def _generation_context_for_sample(sample, task, score=None, repeat_index=0):
    profile = _profile_context_from_sample(sample)
    topics = _join_profile_value(profile.get("topic_interests"))
    diversify_key = f"{sample.get('virtual_user_id') or sample.get('id')}-{sample.get('target_date')}-{score}-{repeat_index}"
    hour_name, hour_range = CHINESE_HOURS[_stable_index(diversify_key, len(CHINESE_HOURS))]
    if "career" in topics or "job" in topics or "study" in topics:
        action_domain = "秩序"
    elif "health" in topics or "sleep" in topics:
        action_domain = "照看"
    elif "wealth" in topics or "finance" in topics:
        action_domain = "收束"
    else:
        action_domain = "余地"
    diversity_controls = _low_cost_diversity_controls(profile, task)

    return {
        "answer_style": profile.get("answer_style") or "philosophical",
        "mood_tendency": profile.get("mood_tendency") or "",
        "topic_interests": topics,
        "self_context_tag": profile.get("self_context_tag") or "",
        "selected_style": sample.get("answer_style") or "寓言式短句",
        "personalization_plan": _personalization_plan(profile, task),
        "material_hints": (
            f"sentence_shape={diversity_controls['sentence_shape']}；"
            f"tone={diversity_controls['tone']}；"
            f"rhythm={diversity_controls['rhythm']}；"
            f"length_rule={diversity_controls['length_rule']}；"
            f"行动域：{action_domain}"
        ),
        "privacy_constraints": "不得复述用户问题、画像标签、生日或可识别个人信息。",
        "avoid_instructions": f"避免使用：{DEFAULT_TABOO_TERMS}",
        "diversity_taboo_terms": DEFAULT_TABOO_TERMS,
        "birthday": profile.get("birthday") or "",
        "birth_month_day": profile.get("birth_month_day") or "",
        "imagery_domain": "",
        "sentence_shape": diversity_controls["sentence_shape"],
        "tone": diversity_controls["tone"],
        "rhythm": diversity_controls["rhythm"],
        "length_rule": diversity_controls["length_rule"],
        "action_domain": action_domain,
        "lucky_hour_guidance": f"使用指定时辰：{hour_name} {hour_range}。",
        "assigned_lucky_hour_name": hour_name,
        "assigned_lucky_hour_range": hour_range,
        "score": "" if score is None else str(score),
        "diversify_key": diversify_key,
    }


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
            generation_context = _generation_context_for_sample(sample, task="answer", repeat_index=case.get("repeat_index", 0))
            generation_context["question"] = sample["question"]
            generation_context["selected_style"] = style or generation_context["selected_style"]
            prompt_text = render_template(template_path, generation_context)
            row = adapter.run_answer(question=sample["question"], prompt_text=prompt_text, temperature=temperature)
        elif task == "fortune":
            context = _profile_context_from_sample(sample)
            score = stable_fortune_score(context, sample.get("target_date"))
            generation_context = _generation_context_for_sample(sample, task="fortune", score=score, repeat_index=case.get("repeat_index", 0))
            if fortune_selector:
                title_template = fortune_selector.select_title(score)
                keywords = fortune_selector.select_keywords(context, context=generation_context)
                yiji_items = fortune_selector.select_yiji(context, context=generation_context)
            else:
                title_template = {"main": "今日宜静待时机", "sub": "稳中求进"}
                keywords = {"love": "平稳", "career": "平稳", "health": "稳定", "wealth": "平稳"}
                yiji_items = {"yi": [], "ji": []}

            generation_context.update(
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
                }
            )
            prompt_text = render_template(
                template_path,
                generation_context,
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
    run_parser.add_argument("--timeout", type=int, default=30, help="请求超时秒数")
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

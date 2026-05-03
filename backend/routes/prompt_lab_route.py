from flask import Blueprint, current_app, request
from pathlib import Path

from services import prompt_lab_service
from utils.api_response import fail, success

prompt_lab_bp = Blueprint("prompt_lab", __name__)
MAX_REQUEST_BYTES = 256 * 1024
ALLOWED_TASKS = {"answer", "fortune", "profile"}


@prompt_lab_bp.route("/run", methods=["POST"])
def run_prompt_lab_once():
    if request.content_length is not None and request.content_length > MAX_REQUEST_BYTES:
        return fail("请求体过大", code=400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("请求体必须是有效的JSON对象", code=400)

    try:
        result = prompt_lab_service.run_prompt_lab(
            task=data.get("task"),
            prompt_text=data.get("prompt_text"),
            temperature=data.get("temperature"),
            input_payload=data.get("input"),
            frequency_penalty=data.get("frequency_penalty"),
            top_p=data.get("top_p"),
        )
    except Exception:
        current_app.logger.exception("prompt_lab_route_unexpected_error")
        return fail("服务器内部错误", code=500)

    error_code = result.get("error_code")
    if error_code == "validation_error":
        return fail(result.get("error_message") or "参数错误", code=400)
    if error_code == "unexpected_error":
        return fail("服务器内部错误", code=500)
    return success(data=result, message="success", code=200)


@prompt_lab_bp.route("/prompt-template", methods=["GET"])
def get_prompt_template():
    task = (request.args.get("task") or "").strip()
    version = (request.args.get("version") or "").strip()

    if task not in ALLOWED_TASKS:
        return fail("task 必须是 answer|fortune|profile", code=400)

    if not version:
        key = f"LLM_PROMPT_{task.upper()}_VERSION"
        version = str(current_app.config.get(key) or "").strip() or "v1"

    prompts_dir = current_app.config.get("LLM_PROMPTS_DIR")
    if prompts_dir:
        base = Path(prompts_dir)
    else:
        base = Path(__file__).resolve().parents[1] / "tools" / "prompt_lab" / "prompts"

    path = base / task / f"{version}.txt"
    if not path.exists():
        return fail("prompt template not found", code=404)

    try:
        prompt_text = path.read_text(encoding="utf-8")
    except Exception:
        current_app.logger.exception("prompt_lab_read_template_failed")
        return fail("服务器内部错误", code=500)

    return success(
        data={
            "task": task,
            "version": version,
            "prompt_text": prompt_text,
        },
        message="success",
        code=200,
    )

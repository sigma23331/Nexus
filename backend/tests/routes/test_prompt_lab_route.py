import importlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _build_client(monkeypatch, flask_env, enabled):
    monkeypatch.setenv("FLASK_ENV", flask_env)
    monkeypatch.setenv("PROMPT_LAB_DEV_ENABLED", "true" if enabled else "false")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    config_module = importlib.import_module("config")
    importlib.reload(config_module)

    main_module = importlib.import_module("backend.main")
    importlib.reload(main_module)

    app = main_module.create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_prompt_lab_route_returns_404_when_disabled(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=False)
    response = client.post("/v1/dev/prompt-lab/run", json={})
    assert response.status_code == 404


def test_prompt_lab_route_enabled_and_returns_success(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)

    import backend.routes.prompt_lab_route as route_module

    monkeypatch.setattr(
        route_module.prompt_lab_service,
        "run_prompt_lab",
        lambda **_: {
            "task": "answer",
            "success": True,
            "output_text": "ok",
            "output_preview": "ok",
            "latency_ms": 12,
            "parse_success": None,
            "schema_valid": None,
            "fallback_used": False,
            "error_code": None,
            "error_message": None,
        },
    )

    response = client.post(
        "/v1/dev/prompt-lab/run",
        json={
            "task": "answer",
            "prompt_text": "ok",
            "temperature": 0.7,
            "frequency_penalty": 0.4,
            "top_p": 0.85,
            "input": {"question": "q"},
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["code"] == 200
    assert body["data"]["success"] is True


def test_prompt_lab_route_top_p_out_of_range_returns_400(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)
    response = client.post(
        "/v1/dev/prompt-lab/run",
        json={"task": "answer", "prompt_text": "ok", "temperature": 0.7, "top_p": 1.5, "input": {"question": "q"}},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["code"] == 400
    assert body["data"] is None


def test_prompt_lab_route_returns_400_for_validation_error(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)

    import backend.routes.prompt_lab_route as route_module

    monkeypatch.setattr(
        route_module.prompt_lab_service,
        "run_prompt_lab",
        lambda **_: {
            "task": "answer",
            "success": False,
            "error_code": "validation_error",
            "error_message": "bad request",
        },
    )

    response = client.post(
        "/v1/dev/prompt-lab/run",
        json={"task": "answer", "prompt_text": "", "temperature": 0.7, "input": {}},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["code"] == 400
    assert body["data"] is None


def test_prompt_lab_route_returns_200_with_success_false_on_provider_failure(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)

    import backend.routes.prompt_lab_route as route_module

    monkeypatch.setattr(
        route_module.prompt_lab_service,
        "run_prompt_lab",
        lambda **_: {
            "task": "answer",
            "success": False,
            "output_text": "",
            "output_preview": "",
            "latency_ms": 1,
            "parse_success": None,
            "schema_valid": None,
            "fallback_used": False,
            "error_code": "provider_error",
            "error_message": "boom",
        },
    )

    response = client.post(
        "/v1/dev/prompt-lab/run",
        json={"task": "answer", "prompt_text": "ok", "temperature": 0.7, "input": {"question": "q"}},
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["success"] is False


def test_prompt_lab_route_rejects_oversized_request(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)

    import backend.routes.prompt_lab_route as route_module

    monkeypatch.setattr(
        route_module.prompt_lab_service,
        "run_prompt_lab",
        lambda **_: {
            "task": "answer",
            "success": True,
            "output_text": "ok",
            "output_preview": "ok",
            "latency_ms": 1,
            "parse_success": None,
            "schema_valid": None,
            "fallback_used": False,
            "error_code": None,
            "error_message": None,
        },
    )

    tiny_payload = json.dumps(
        {
            "task": "answer",
            "prompt_text": "ok",
            "temperature": 0.7,
            "input": {"question": "q"},
        }
    )
    assert len(tiny_payload.encode("utf-8")) < 256 * 1024
    ok_response = client.post(
        "/v1/dev/prompt-lab/run",
        data=tiny_payload,
        content_type="application/json",
    )
    assert ok_response.status_code in {200, 400}

    huge_prompt = "x" * (256 * 1024)
    oversized_payload = json.dumps(
        {
            "task": "answer",
            "prompt_text": huge_prompt,
            "temperature": 0.7,
            "input": {"question": "q"},
        }
    )
    assert len(oversized_payload.encode("utf-8")) > 256 * 1024
    response = client.post(
        "/v1/dev/prompt-lab/run",
        data=oversized_payload,
        content_type="application/json",
    )
    assert response.status_code == 400


def test_prompt_lab_route_invalid_task_returns_400(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)
    response = client.post(
        "/v1/dev/prompt-lab/run",
        json={"task": "oops", "prompt_text": "ok", "temperature": 0.7, "input": {"question": "q"}},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["code"] == 400
    assert body["data"] is None


def test_prompt_lab_route_temperature_out_of_range_returns_400(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)
    response = client.post(
        "/v1/dev/prompt-lab/run",
        json={"task": "answer", "prompt_text": "ok", "temperature": 2.1, "input": {"question": "q"}},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["code"] == 400
    assert body["data"] is None


def test_prompt_lab_route_temperature_boundaries_are_valid(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)
    called = []

    import backend.routes.prompt_lab_route as route_module

    def _fake_run_prompt_lab(**kwargs):
        called.append(kwargs["temperature"])
        return {
            "task": "answer",
            "success": True,
            "output_text": "ok",
            "output_preview": "ok",
            "latency_ms": 1,
            "parse_success": None,
            "schema_valid": None,
            "fallback_used": False,
            "error_code": None,
            "error_message": None,
        }

    monkeypatch.setattr(route_module.prompt_lab_service, "run_prompt_lab", _fake_run_prompt_lab)

    low = client.post(
        "/v1/dev/prompt-lab/run",
        json={"task": "answer", "prompt_text": "ok", "temperature": 0, "input": {"question": "q"}},
    )
    high = client.post(
        "/v1/dev/prompt-lab/run",
        json={"task": "answer", "prompt_text": "ok", "temperature": 2, "input": {"question": "q"}},
    )
    assert low.status_code == 200
    assert high.status_code == 200
    assert called == [0, 2]


def test_prompt_lab_route_rejects_non_json(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)
    response = client.post(
        "/v1/dev/prompt-lab/run",
        data="not-json",
        content_type="text/plain",
    )
    assert response.status_code == 400


def test_prompt_lab_route_rejects_wrong_top_level_json_type(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)
    response = client.post(
        "/v1/dev/prompt-lab/run",
        json=["not", "object"],
    )
    assert response.status_code == 400


def test_prompt_lab_route_rejects_wrong_input_type(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)
    response = client.post(
        "/v1/dev/prompt-lab/run",
        json={
            "task": "answer",
            "prompt_text": "ok",
            "temperature": 0.7,
            "input": "not-an-object",
        },
    )
    assert response.status_code == 400


def test_prompt_lab_route_returns_500_on_unexpected_exception(monkeypatch):
    client = _build_client(monkeypatch, flask_env="development", enabled=True)

    import backend.routes.prompt_lab_route as route_module

    def _boom(**_):
        raise RuntimeError("boom")

    monkeypatch.setattr(route_module.prompt_lab_service, "run_prompt_lab", _boom)

    response = client.post(
        "/v1/dev/prompt-lab/run",
        json={"task": "answer", "prompt_text": "ok", "temperature": 0.7, "input": {"question": "q"}},
    )
    assert response.status_code == 500


def test_prompt_lab_route_not_registered_in_non_dev_env_even_if_enabled(monkeypatch):
    client = _build_client(monkeypatch, flask_env="production", enabled=True)
    response = client.post("/v1/dev/prompt-lab/run", json={})
    assert response.status_code == 404

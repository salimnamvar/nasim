"""Deterministic server-wiring tests via FastAPI TestClient (no live bridge).

These prove the transport-only guarantees that do not need a real model: the
count_tokens endpoint (B03) and the full error-mapping contract (B13). The
Ollama HTTP layer is mocked so 502/503 are forced without breaking a real
server. Happy-path endpoints (B01/B02/B04/B05) are proven live in the
integration layer.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from nasim.bridge import server

client = TestClient(server.app)


def test_b03_count_tokens_endpoint():
    """POST /v1/messages/count_tokens returns a positive input_tokens estimate."""
    resp = client.post(
        "/v1/messages/count_tokens",
        json={"messages": [{"role": "user", "content": "hello world"}]},
    )
    assert resp.status_code == 200
    assert resp.json()["input_tokens"] >= 1


def test_b13_invalid_json_returns_400():
    """A non-JSON body yields 400 invalid_request_error (Anthropic-shaped)."""
    resp = client.post("/v1/messages", content="not json", headers={"content-type": "application/json"})
    assert resp.status_code == 400
    body = resp.json()
    assert body["type"] == "error"
    assert body["error"]["type"] == "invalid_request_error"


def test_b13_ollama_unreachable_returns_503(monkeypatch):
    """An unreachable Ollama maps to 503 overloaded_error."""

    class _Down:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(server.httpx, "AsyncClient", _Down)
    resp = client.post(
        "/v1/messages",
        json={"model": "opus", "stream": False, "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 503
    assert resp.json()["error"]["type"] == "overloaded_error"


def test_b13_ollama_error_returns_502(monkeypatch):
    """A non-200 from Ollama maps to 502 api_error."""

    class _Resp:
        status_code = 500
        text = "internal ollama failure"

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            return _Resp()

    monkeypatch.setattr(server.httpx, "AsyncClient", _Client)
    resp = client.post(
        "/v1/messages",
        json={"model": "opus", "stream": False, "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 502
    assert resp.json()["error"]["type"] == "api_error"


def test_non_streaming_happy_path_with_mocked_ollama(monkeypatch):
    """A mocked Ollama 200 round-trips to a valid Anthropic message (B04 wiring)."""

    class _Resp:
        status_code = 200

        def json(self):
            return {
                "message": {"content": "hello back"},
                "done_reason": "stop",
                "prompt_eval_count": 4,
                "eval_count": 2,
            }

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            return _Resp()

    monkeypatch.setattr(server.httpx, "AsyncClient", _Client)
    resp = client.post(
        "/v1/messages",
        json={"model": "opus", "stream": False, "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["type"] == "message"
    assert body["role"] == "assistant"
    assert body["content"] == [{"type": "text", "text": "hello back"}]
    assert body["stop_reason"] == "end_turn"


@pytest.mark.parametrize("path", ["/v1/messages/count_tokens"])
def test_count_tokens_handles_tools_and_system(path):
    """count_tokens accounts for system + tools without error (B03 robustness)."""
    resp = client.post(
        path,
        json={
            "system": "you are terse",
            "messages": [{"role": "user", "content": "hi"}],
            "tools": [{"name": "Write", "input_schema": {"type": "object"}}],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["input_tokens"] >= 1


def test_health_vram_warning_when_model_cpu_offloaded(monkeypatch):
    """Health reports vram_warning when a running model exceeds GPU VRAM (AP-12)."""
    _GPU_SIZE = 12_000_000_000  # 12 GB GPU
    _MODEL_SIZE = 24_000_000_000  # 24 GB model — cannot fit, gets split
    _VRAM_USED = int(_GPU_SIZE * 0.45)  # ~45% on GPU, 55% on CPU

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url: str, **k):
            class _R:
                status_code = 200

                def json(self_inner):
                    if url.endswith("/api/tags"):
                        return {"models": [{"name": "big-model:latest", "size": _MODEL_SIZE}]}
                    if url.endswith("/api/ps"):
                        return {"models": [{"name": "big-model:latest", "size": _MODEL_SIZE, "size_vram": _VRAM_USED}]}
                    return {}

            return _R()

    monkeypatch.setattr(server.httpx, "AsyncClient", _Client)
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "vram_warning" in body
    assert "big-model:latest" in body["vram_warning"]
    assert "CPU" in body["vram_warning"]


def test_health_no_vram_warning_when_model_gpu_resident(monkeypatch):
    """Health omits vram_warning when the running model fits fully in VRAM."""
    _MODEL_SIZE = 5_000_000_000  # 5 GB model — fits on GPU
    _VRAM_USED = _MODEL_SIZE  # all in VRAM

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url: str, **k):
            class _R:
                status_code = 200

                def json(self_inner):
                    if url.endswith("/api/tags"):
                        return {"models": [{"name": "small-model:7b", "size": _MODEL_SIZE}]}
                    if url.endswith("/api/ps"):
                        return {"models": [{"name": "small-model:7b", "size": _MODEL_SIZE, "size_vram": _VRAM_USED}]}
                    return {}

            return _R()

    monkeypatch.setattr(server.httpx, "AsyncClient", _Client)
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "vram_warning" not in body

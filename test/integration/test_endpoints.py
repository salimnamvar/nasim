"""Live integration tests — bridge endpoints over the SSH tunnel (B01-B05).

Require the bridge to be reachable (the ``bridge`` fixture skips otherwise).
These assert transport correctness with a real model; they do not assert exact
model text (that is model-bound), only that the wire contract holds.
"""

import httpx
import pytest

pytestmark = pytest.mark.integration


def test_b01_health_reports_ok_and_inventory(bridge):
    """B01 — /health reports ok plus the model inventory."""
    resp = httpx.get(f"{bridge}/health", timeout=5)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["ollama"] == "connected"
    assert isinstance(body["available_models"], list) and body["available_models"]
    for key in ("default_model", "fast_model", "recommended_model"):
        assert key in body


def test_b02_models_list_for_picker(bridge, cfg):
    """B02 — /v1/models returns a picker list including default + fast aliases."""
    resp = httpx.get(f"{bridge}/v1/models", timeout=5)
    assert resp.status_code == 200
    body = resp.json()
    ids = {entry["id"] for entry in body["data"]}
    assert cfg.default_model in ids
    assert cfg.fast_model in ids
    assert body["has_more"] is False


def test_b03_count_tokens_live(bridge):
    """B03 — /v1/messages/count_tokens estimates input tokens over the wire."""
    resp = httpx.post(
        f"{bridge}/v1/messages/count_tokens",
        json={"messages": [{"role": "user", "content": "count these words please"}]},
        timeout=10,
    )
    assert resp.status_code == 200
    assert resp.json()["input_tokens"] >= 1


def test_b04_non_streaming_text_round_trip(bridge, cfg, post_message):
    """B04 — a non-streaming request returns a valid Anthropic message with text."""
    body = {
        "model": cfg.recommended_model,
        "max_tokens": 64,
        "stream": False,
        "messages": [{"role": "user", "content": "Reply with exactly the word: pong"}],
    }
    resp = post_message(bridge, body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "message"
    assert data["role"] == "assistant"
    text = "".join(b.get("text", "") for b in data["content"] if b["type"] == "text")
    assert text.strip() != ""
    assert data["stop_reason"] in ("end_turn", "max_tokens")
    assert data["usage"]["input_tokens"] >= 1


def test_b05_streaming_text_event_order(bridge, cfg, stream_message):
    """B05 — a streaming text request emits the required SSE event sequence."""
    body = {
        "model": cfg.recommended_model,
        "max_tokens": 64,
        "stream": True,
        "messages": [{"role": "user", "content": "Reply with exactly the word: pong"}],
    }
    events = stream_message(bridge, body)
    names = [e for e, _ in events]
    assert names[0] == "message_start"
    assert names[-1] == "message_stop"
    assert names[-2] == "message_delta"
    assert "content_block_start" in names
    assert "content_block_stop" in names
    # message_delta carries a terminal stop_reason
    _, final = next((e, d) for e, d in reversed(events) if e == "message_delta")
    assert final["delta"]["stop_reason"] in ("end_turn", "max_tokens")

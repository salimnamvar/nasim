"""Live capability tests — tool use end-to-end on the recommended model.

These exercise the bridge's tool-call path with a real model. Tool *elicitation*
is model-bound (AP-01); the bridge *guarantee* is that whatever the model emits
(native or text-encoded) becomes a valid, schema-coerced tool_use block. They run
against ``models.recommended`` (qwen2.5-coder:14b), which reliably emits tool
calls for a direct instruction. A failure to emit is a model regression to record
in docs/model-guidance.md, not a bridge defect.
"""

import json

import pytest

pytestmark = pytest.mark.capability

_WRITE_TOOL = {
    "name": "Write",
    "description": "Write text content to a file at the given absolute path.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Absolute path to write."},
            "content": {"type": "string", "description": "Exact content to write."},
        },
        "required": ["file_path", "content"],
    },
}

_PROMPT = "Use the Write tool to create the file /tmp/nasim_cap.txt containing exactly: hi"


def _tool_uses(a_content):
    """Return the tool_use blocks from an Anthropic content list."""
    return [b for b in a_content if b.get("type") == "tool_use"]


def test_b06_single_tool_use_non_streaming(bridge, cfg, post_message):
    """B06 — a non-streaming tool request yields a well-formed tool_use block."""
    body = {
        "model": cfg.recommended_model,
        "max_tokens": 512,
        "stream": False,
        "tools": [_WRITE_TOOL],
        "messages": [{"role": "user", "content": _PROMPT}],
    }
    resp = post_message(bridge, body)
    assert resp.status_code == 200
    data = resp.json()
    blocks = _tool_uses(data["content"])
    assert blocks, f"model emitted no tool_use (model-bound); content={data['content']}"
    block = blocks[0]
    assert block["name"] == "Write"
    assert isinstance(block["input"], dict)
    # required fields are present (schema_coerce guarantees this even if omitted)
    assert "file_path" in block["input"]
    assert "content" in block["input"]
    assert data["stop_reason"] == "tool_use"


def test_b07_single_tool_use_streaming(bridge, cfg, stream_message):
    """B07 — a streaming tool request emits tool_use with valid input_json_delta."""
    body = {
        "model": cfg.recommended_model,
        "max_tokens": 512,
        "stream": True,
        "tools": [_WRITE_TOOL],
        "messages": [{"role": "user", "content": _PROMPT}],
    }
    events = stream_message(bridge, body)
    starts = [d for e, d in events if e == "content_block_start" and d["content_block"]["type"] == "tool_use"]
    assert starts, "model emitted no tool_use in stream (model-bound)"
    assert starts[0]["content_block"]["name"] == "Write"
    assert starts[0]["content_block"]["input"] == {}  # input arrives via deltas

    # the input_json_delta partials concatenate to valid JSON
    partials = [
        d["delta"]["partial_json"]
        for e, d in events
        if e == "content_block_delta" and d["delta"].get("type") == "input_json_delta"
    ]
    assert partials
    parsed = json.loads("".join(partials))
    assert "file_path" in parsed and "content" in parsed

    _, final = next((e, d) for e, d in reversed(events) if e == "message_delta")
    assert final["delta"]["stop_reason"] == "tool_use"


def test_b09_multi_turn_tool_chain(bridge, cfg, post_message):
    """B09 — a tool_use -> tool_result -> continue chain produces a coherent reply."""
    # Turn 1: elicit a tool call.
    first = post_message(
        bridge,
        {
            "model": cfg.recommended_model,
            "max_tokens": 512,
            "stream": False,
            "tools": [_WRITE_TOOL],
            "messages": [{"role": "user", "content": _PROMPT}],
        },
    ).json()
    blocks = _tool_uses(first["content"])
    if not blocks:
        pytest.skip("model did not emit a tool call (model-bound) — see docs/model-guidance.md")
    call = blocks[0]

    # Turn 2: feed the tool_result back and continue.
    second = post_message(
        bridge,
        {
            "model": cfg.recommended_model,
            "max_tokens": 256,
            "stream": False,
            "tools": [_WRITE_TOOL],
            "messages": [
                {"role": "user", "content": _PROMPT},
                {"role": "assistant", "content": first["content"]},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": call["id"],
                            "content": "File written successfully.",
                        }
                    ],
                },
            ],
        },
    )
    assert second.status_code == 200
    data = second.json()
    assert data["type"] == "message"
    assert data["stop_reason"] in ("end_turn", "tool_use", "max_tokens")

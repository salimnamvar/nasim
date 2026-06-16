"""Unit tests for streaming translation — the SSE event contract (B05, B07).

The Anthropic SDK requires exactly: message_start, then per content block
(content_block_start -> content_block_delta+ -> content_block_stop), then
message_delta (stop_reason + usage), then message_stop. These tests drive the
async generator to completion with asyncio.run (no pytest-asyncio dependency).
"""

import asyncio
import json
from typing import Any, Dict, List, Tuple

from nasim.bridge.translator.streaming import stream_ollama_to_anthropic


async def _agen(a_items: List[Dict[str, Any]]):
    """Yield each item as an async stream of Ollama chunks."""
    for item in a_items:
        yield item


def _collect(a_chunks: List[Dict[str, Any]], a_model: str, a_schemas=None) -> List[Tuple[str, Dict[str, Any]]]:
    """Run the streaming translator and parse its SSE strings to (event, data)."""

    async def _run() -> List[Tuple[str, Dict[str, Any]]]:
        events: List[Tuple[str, Dict[str, Any]]] = []
        async for raw in stream_ollama_to_anthropic(_agen(a_chunks), a_model, a_schemas):
            lines = raw.strip().split("\n")
            event = lines[0].removeprefix("event: ")
            data = json.loads(lines[1].removeprefix("data: "))
            events.append((event, data))
        return events

    return asyncio.run(_run())


def test_b05_streaming_text_event_order():
    """Plain text (no tools) streams live in the exact required SSE order."""
    chunks = [
        {"message": {"content": "Hel"}, "done": False},
        {"message": {"content": "lo"}, "done": False},
        {"message": {"content": ""}, "done": True, "done_reason": "stop", "prompt_eval_count": 5, "eval_count": 2},
    ]
    events = _collect(chunks, "opus")
    names = [e for e, _ in events]
    assert names == [
        "message_start",
        "content_block_start",
        "content_block_delta",
        "content_block_delta",
        "content_block_stop",
        "message_delta",
        "message_stop",
    ]
    # text deltas carry text_delta and reconstruct the message
    deltas = [d["delta"]["text"] for e, d in events if e == "content_block_delta"]
    assert "".join(deltas) == "Hello"
    final = next(d for e, d in events if e == "message_delta")
    assert final["delta"]["stop_reason"] == "end_turn"
    assert final["usage"] == {"input_tokens": 5, "output_tokens": 2}


def test_b07_streaming_single_tool_use():
    """A native tool call streams as start(input={}) -> input_json_delta -> stop."""
    schemas = {"Write": {"properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}
    chunks = [
        {
            "message": {
                "content": "",
                "tool_calls": [{"function": {"name": "Write", "arguments": {"file_path": "/a"}}}],
            },
            "done": False,
        },
        {"message": {"content": ""}, "done": True, "done_reason": "stop"},
    ]
    events = _collect(chunks, "opus", schemas)
    names = [e for e, _ in events]
    assert names == [
        "message_start",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
        "message_delta",
        "message_stop",
    ]

    start = next(d for e, d in events if e == "content_block_start")
    assert start["content_block"]["type"] == "tool_use"
    assert start["content_block"]["name"] == "Write"
    assert start["content_block"]["input"] == {}  # input arrives via the delta

    delta = next(d for e, d in events if e == "content_block_delta")
    assert delta["delta"]["type"] == "input_json_delta"
    assert json.loads(delta["delta"]["partial_json"]) == {"file_path": "/a"}

    final = next(d for e, d in events if e == "message_delta")
    assert final["delta"]["stop_reason"] == "tool_use"


def test_streaming_salvages_text_encoded_call_at_end():
    """With tools offered, a text-encoded call is buffered and salvaged (AP-05)."""
    schemas = {"Read": {"properties": {"file_path": {"type": "string"}}}}
    chunks = [
        {"message": {"content": '{"name": "Read", '}, "done": False},
        {"message": {"content": '"arguments": {"file_path": "/b"}}'}, "done": False},
        {"message": {"content": ""}, "done": True, "done_reason": "stop"},
    ]
    events = _collect(chunks, "opus", schemas)
    # No live text deltas were emitted (text was buffered for salvage).
    tool_starts = [d for e, d in events if e == "content_block_start" and d["content_block"]["type"] == "tool_use"]
    assert len(tool_starts) == 1
    assert tool_starts[0]["content_block"]["name"] == "Read"
    delta = next(d for e, d in events if e == "content_block_delta")
    assert json.loads(delta["delta"]["partial_json"]) == {"file_path": "/b"}


def test_streaming_message_start_echoes_model():
    """message_start echoes the requested model name and assistant role."""
    chunks = [{"message": {"content": "hi"}, "done": True, "done_reason": "stop"}]
    events = _collect(chunks, "claude-opus-4-8")
    _, start = events[0]
    assert start["message"]["model"] == "claude-opus-4-8"
    assert start["message"]["role"] == "assistant"

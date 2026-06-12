"""Unit tests for the Anthropic <-> Ollama translator."""

import asyncio
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import translator  # noqa: E402


class TestMapModel:
    def test_claude_names_map_to_default(self):
        assert translator.map_model("claude-sonnet-4-6") == translator.DEFAULT_MODEL
        assert translator.map_model("naseem-opus-4-8") == translator.DEFAULT_MODEL

    def test_haiku_maps_to_fast(self):
        assert translator.map_model("claude-haiku-4-5-20251001") == translator.FAST_MODEL
        assert translator.map_model("naseem-3-5-haiku-20241022") == translator.FAST_MODEL

    def test_ollama_tag_passes_through(self):
        assert translator.map_model("qwen2.5-coder:7b") == "qwen2.5-coder:7b"
        assert translator.map_model("llama3.3:70b") == "llama3.3:70b"


class TestRequestTranslation:
    def test_simple_text(self):
        body = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 100,
            "messages": [{"role": "user", "content": "hello"}],
        }
        out = translator.anthropic_to_ollama(body)
        assert out["model"] == translator.DEFAULT_MODEL
        assert out["messages"] == [{"role": "user", "content": "hello"}]
        assert out["options"]["num_predict"] == 100
        assert out["options"]["num_ctx"] == translator.NUM_CTX
        assert out["stream"] is False

    def test_system_blocks_flattened(self):
        body = {
            "system": [
                {"type": "text", "text": "part one", "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": "part two"},
            ],
            "messages": [{"role": "user", "content": "hi"}],
        }
        out = translator.anthropic_to_ollama(body)
        assert out["messages"][0] == {"role": "system", "content": "part one\npart two"}

    def test_tools_translated(self):
        body = {
            "messages": [{"role": "user", "content": "read a file"}],
            "tools": [
                {
                    "name": "read_file",
                    "description": "Read a file",
                    "input_schema": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"],
                    },
                }
            ],
        }
        out = translator.anthropic_to_ollama(body)
        assert out["tools"][0]["type"] == "function"
        assert out["tools"][0]["function"]["name"] == "read_file"
        assert out["tools"][0]["function"]["parameters"]["required"] == ["path"]

    def test_tool_use_and_result_round_trip(self):
        body = {
            "messages": [
                {"role": "user", "content": "read main.py"},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Reading it."},
                        {
                            "type": "tool_use",
                            "id": "toolu_01",
                            "name": "read_file",
                            "input": {"path": "main.py"},
                        },
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu_01",
                            "content": "print('hi')",
                        }
                    ],
                },
            ],
        }
        out = translator.anthropic_to_ollama(body)
        assistant = out["messages"][1]
        assert assistant["tool_calls"][0]["function"]["name"] == "read_file"
        assert assistant["tool_calls"][0]["function"]["arguments"] == {"path": "main.py"}
        tool_msg = out["messages"][2]
        assert tool_msg["role"] == "tool"
        assert tool_msg["content"] == "print('hi')"
        assert tool_msg["tool_name"] == "read_file"

    def test_tool_result_error_flag(self):
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu_02",
                            "content": "no such file",
                            "is_error": True,
                        }
                    ],
                }
            ],
        }
        out = translator.anthropic_to_ollama(body)
        assert out["messages"][0]["content"] == "ERROR: no such file"

    def test_stop_sequences_and_sampling(self):
        body = {
            "messages": [{"role": "user", "content": "x"}],
            "temperature": 0.2,
            "top_p": 0.9,
            "stop_sequences": ["END"],
        }
        out = translator.anthropic_to_ollama(body)
        assert out["options"]["temperature"] == 0.2
        assert out["options"]["top_p"] == 0.9
        assert out["options"]["stop"] == ["END"]


class TestResponseTranslation:
    def test_text_response(self):
        resp = {
            "message": {"role": "assistant", "content": "hello there"},
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 10,
            "eval_count": 5,
        }
        out = translator.ollama_to_anthropic(resp, "claude-sonnet-4-6")
        assert out["type"] == "message"
        assert out["model"] == "claude-sonnet-4-6"
        assert out["content"] == [{"type": "text", "text": "hello there"}]
        assert out["stop_reason"] == "end_turn"
        assert out["usage"]["input_tokens"] == 10
        assert out["usage"]["output_tokens"] == 5

    def test_tool_call_response(self):
        resp = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": "a.py"}}}],
            },
            "done": True,
            "done_reason": "stop",
        }
        out = translator.ollama_to_anthropic(resp, "m")
        block = out["content"][0]
        assert block["type"] == "tool_use"
        assert block["name"] == "read_file"
        assert block["input"] == {"path": "a.py"}
        assert block["id"].startswith("toolu_")
        assert out["stop_reason"] == "tool_use"

    def test_string_arguments_parsed(self):
        resp = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": "f", "arguments": '{"k": 1}'}}],
            },
            "done": True,
        }
        out = translator.ollama_to_anthropic(resp, "m")
        assert out["content"][0]["input"] == {"k": 1}

    def test_max_tokens_stop_reason(self):
        resp = {"message": {"content": "trunc"}, "done": True, "done_reason": "length"}
        out = translator.ollama_to_anthropic(resp, "m")
        assert out["stop_reason"] == "max_tokens"


def _events_from(a_chunks):
    """Run the stream translator over a list of chunks, return parsed events."""

    async def gen():
        for c in a_chunks:
            yield c

    async def collect():
        return [e async for e in translator.stream_ollama_to_anthropic(gen(), "m")]

    raw = asyncio.run(collect())
    events = []
    for item in raw:
        lines = item.strip().split("\n")
        etype = lines[0].removeprefix("event: ")
        data = json.loads(lines[1].removeprefix("data: "))
        events.append((etype, data))
    return events


class TestStreaming:
    def test_text_stream_event_sequence(self):
        events = _events_from(
            [
                {"message": {"content": "hel"}, "done": False},
                {"message": {"content": "lo"}, "done": False},
                {
                    "message": {"content": ""},
                    "done": True,
                    "done_reason": "stop",
                    "prompt_eval_count": 7,
                    "eval_count": 2,
                },
            ]
        )
        types = [e[0] for e in events]
        assert types == [
            "message_start",
            "content_block_start",
            "content_block_delta",
            "content_block_delta",
            "content_block_stop",
            "message_delta",
            "message_stop",
        ]
        deltas = [d["delta"]["text"] for t, d in events if t == "content_block_delta"]
        assert "".join(deltas) == "hello"
        msg_delta = next(d for t, d in events if t == "message_delta")
        assert msg_delta["delta"]["stop_reason"] == "end_turn"
        assert msg_delta["usage"]["output_tokens"] == 2

    def test_tool_call_stream(self):
        events = _events_from(
            [
                {"message": {"content": "Let me check."}, "done": False},
                {
                    "message": {
                        "content": "",
                        "tool_calls": [{"function": {"name": "bash", "arguments": {"cmd": "ls"}}}],
                    },
                    "done": False,
                },
                {"message": {"content": ""}, "done": True, "done_reason": "stop"},
            ]
        )
        types = [e[0] for e in events]
        assert types == [
            "message_start",
            "content_block_start",
            "content_block_delta",
            "content_block_stop",
            "content_block_start",
            "content_block_delta",
            "content_block_stop",
            "message_delta",
            "message_stop",
        ]
        tool_start = events[4][1]
        assert tool_start["content_block"]["type"] == "tool_use"
        assert tool_start["content_block"]["name"] == "bash"
        assert tool_start["content_block"]["input"] == {}
        tool_delta = events[5][1]
        assert json.loads(tool_delta["delta"]["partial_json"]) == {"cmd": "ls"}
        msg_delta = events[7][1]
        assert msg_delta["delta"]["stop_reason"] == "tool_use"

    def test_indexes_increment(self):
        events = _events_from(
            [
                {"message": {"content": "a"}, "done": False},
                {
                    "message": {
                        "content": "",
                        "tool_calls": [{"function": {"name": "f", "arguments": {}}}],
                    },
                    "done": False,
                },
                {"message": {"content": ""}, "done": True},
            ]
        )
        starts = [d["index"] for t, d in events if t == "content_block_start"]
        assert starts == [0, 1]


class TestSalvageToolCalls:
    def test_tagged_form(self):
        text = 'Sure.\n<tool_call>{"name": "read_file", "arguments": {"path": "a.py"}}</tool_call>'
        residual, calls = translator.salvage_tool_calls(text, ["read_file"])
        assert residual == "Sure."
        assert calls[0]["function"]["name"] == "read_file"
        assert calls[0]["function"]["arguments"] == {"path": "a.py"}

    def test_bare_json_form(self):
        text = '{\n  "name": "read_file",\n  "arguments": {"path": "src/main.py"}\n}'
        residual, calls = translator.salvage_tool_calls(text, ["read_file"])
        assert calls[0]["function"]["arguments"] == {"path": "src/main.py"}
        assert residual == ""

    def test_unknown_name_stays_text(self):
        text = '{"name": "not_a_tool", "arguments": {}}'
        residual, calls = translator.salvage_tool_calls(text, ["read_file"])
        assert calls == []
        assert residual == text

    def test_no_tools_offered_is_noop(self):
        text = '{"name": "read_file", "arguments": {}}'
        residual, calls = translator.salvage_tool_calls(text, [])
        assert calls == []
        assert residual == text

    def test_salvage_in_response(self):
        resp = {
            "message": {
                "content": '{"name": "read_file", "arguments": {"path": "x"}}',
                "tool_calls": [],
            },
            "done": True,
        }
        out = translator.ollama_to_anthropic(resp, "m", ["read_file"])
        assert out["content"][0]["type"] == "tool_use"
        assert out["stop_reason"] == "tool_use"

    def test_native_tool_calls_skip_salvage(self):
        resp = {
            "message": {
                "content": "",
                "tool_calls": [{"function": {"name": "bash", "arguments": {"cmd": "ls"}}}],
            },
            "done": True,
        }
        out = translator.ollama_to_anthropic(resp, "m", ["bash"])
        assert len([b for b in out["content"] if b["type"] == "tool_use"]) == 1


class TestStreamingSalvage:
    def test_buffered_text_salvaged_to_tool_use(self):
        events = _events_from_with_tools(
            [
                {"message": {"content": '{"name": "read_file",'}, "done": False},
                {"message": {"content": ' "arguments": {"path": "a.py"}}'}, "done": False},  # noqa: E501
                {"message": {"content": ""}, "done": True, "done_reason": "stop"},
            ],
            ["read_file"],
        )
        types = [e[0] for e in events]
        assert "content_block_start" in types
        tool_starts = [d for t, d in events if t == "content_block_start" and d["content_block"]["type"] == "tool_use"]
        assert tool_starts[0]["content_block"]["name"] == "read_file"
        msg_delta = next(d for t, d in events if t == "message_delta")
        assert msg_delta["delta"]["stop_reason"] == "tool_use"

    def test_plain_text_with_tools_offered_still_renders(self):
        events = _events_from_with_tools(
            [
                {"message": {"content": "Just a normal answer."}, "done": False},
                {"message": {"content": ""}, "done": True, "done_reason": "stop"},
            ],
            ["read_file"],
        )
        text_deltas = [
            d["delta"]["text"]
            for t, d in events
            if t == "content_block_delta" and d["delta"].get("type") == "text_delta"
        ]
        assert "".join(text_deltas) == "Just a normal answer."
        msg_delta = next(d for t, d in events if t == "message_delta")
        assert msg_delta["delta"]["stop_reason"] == "end_turn"


def _events_from_with_tools(a_chunks, a_tool_names):
    """Run the stream translator with tool names, return parsed events."""

    async def gen():
        for c in a_chunks:
            yield c

    async def collect():
        return [e async for e in translator.stream_ollama_to_anthropic(gen(), "m", a_tool_names)]

    raw = asyncio.run(collect())
    events = []
    for item in raw:
        lines = item.strip().split("\n")
        etype = lines[0].removeprefix("event: ")
        data = json.loads(lines[1].removeprefix("data: "))
        events.append((etype, data))
    return events


class TestEstimateTokens:
    def test_minimum_one(self):
        assert translator.estimate_tokens({"messages": []}) == 1

    def test_scales_with_content(self):
        small = translator.estimate_tokens({"messages": [{"role": "user", "content": "hi"}]})
        large = translator.estimate_tokens({"messages": [{"role": "user", "content": "x" * 3600}]})
        assert large > small
        assert large == pytest.approx(1000, rel=0.1)

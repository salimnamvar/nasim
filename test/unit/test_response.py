"""Unit tests for non-streaming response translation (B04, B06, B08, B12)."""

from nasim.bridge.translator.blocks import stop_reason
from nasim.bridge.translator.response import ollama_to_anthropic

_SCHEMAS = {"Write": {"properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}


def test_b04_non_streaming_text_round_trip():
    """A plain text response becomes a single text block with end_turn."""
    resp = {"message": {"content": "hello world"}, "done_reason": "stop", "prompt_eval_count": 10, "eval_count": 3}
    out = ollama_to_anthropic(resp, "opus")
    assert out["content"] == [{"type": "text", "text": "hello world"}]
    assert out["stop_reason"] == "end_turn"
    assert out["model"] == "opus"
    assert out["usage"]["input_tokens"] == 10
    assert out["usage"]["output_tokens"] == 3


def test_b06_single_native_tool_use():
    """A native tool_call becomes a coerced tool_use block; stop_reason tool_use."""
    resp = {
        "message": {"content": "", "tool_calls": [{"function": {"name": "Write", "arguments": {"file_path": "/a"}}}]},
        "done_reason": "stop",
    }
    out = ollama_to_anthropic(resp, "opus", _SCHEMAS)
    blocks = [b for b in out["content"] if b["type"] == "tool_use"]
    assert len(blocks) == 1
    assert blocks[0]["name"] == "Write"
    assert blocks[0]["input"] == {"file_path": "/a"}
    assert out["stop_reason"] == "tool_use"


def test_b06_tool_use_required_field_filled():
    """A native call missing a required field is repaired by schema_coerce."""
    resp = {"message": {"content": "", "tool_calls": [{"function": {"name": "Write", "arguments": {}}}]}}
    out = ollama_to_anthropic(resp, "opus", _SCHEMAS)
    block = next(b for b in out["content"] if b["type"] == "tool_use")
    assert block["input"] == {"file_path": ""}


def test_b08_multiple_tool_use_blocks():
    """Multiple native calls produce multiple tool_use blocks in one turn."""
    schemas = {"Read": {}, "Bash": {}}
    resp = {
        "message": {
            "content": "",
            "tool_calls": [
                {"function": {"name": "Read", "arguments": {"file_path": "/a"}}},
                {"function": {"name": "Bash", "arguments": {"command": "ls"}}},
            ],
        }
    }
    out = ollama_to_anthropic(resp, "opus", schemas)
    names = [b["name"] for b in out["content"] if b["type"] == "tool_use"]
    assert names == ["Read", "Bash"]


def test_salvaged_tool_call_when_no_native_calls():
    """When the model emits a call as text, it is salvaged into a tool_use block."""
    resp = {"message": {"content": '{"name": "Write", "arguments": {"file_path": "/x"}}'}}
    out = ollama_to_anthropic(resp, "opus", _SCHEMAS)
    block = next(b for b in out["content"] if b["type"] == "tool_use")
    assert block["input"] == {"file_path": "/x"}
    assert out["stop_reason"] == "tool_use"


def test_text_and_tool_use_emitted_in_order():
    """Residual text precedes tool_use blocks in the content list."""
    resp = {
        "message": {
            "content": "working on it",
            "tool_calls": [{"function": {"name": "Write", "arguments": {"file_path": "/a"}}}],
        },
    }
    out = ollama_to_anthropic(resp, "opus", _SCHEMAS)
    assert out["content"][0] == {"type": "text", "text": "working on it"}
    assert out["content"][1]["type"] == "tool_use"


def test_empty_response_yields_empty_text_block():
    """A response with no content yields a single empty text block (valid shape)."""
    out = ollama_to_anthropic({"message": {"content": ""}}, "opus")
    assert out["content"] == [{"type": "text", "text": ""}]


def test_b12_stop_reason_mapping():
    """stop_reason maps: tool_use > max_tokens(length) > end_turn."""
    assert stop_reason("stop", True) == "tool_use"
    assert stop_reason("length", False) == "max_tokens"
    assert stop_reason("stop", False) == "end_turn"
    assert stop_reason(None, False) == "end_turn"

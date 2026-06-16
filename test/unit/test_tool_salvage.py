"""Unit tests for tool-call salvage (capability B16)."""

from nasim.bridge.translator.tool_salvage import salvage_tool_calls

_NAMES = ["Write", "Read", "Bash"]


def test_b16_recovers_tool_call_tag_form():
    """A ``<tool_call>{...}</tool_call>`` block is recovered as a call."""
    text = 'Sure.<tool_call>{"name": "Write", "arguments": {"file_path": "/a"}}</tool_call>'
    residual, calls = salvage_tool_calls(text, _NAMES)
    assert residual == "Sure."
    assert calls == [{"function": {"name": "Write", "arguments": {"file_path": "/a"}}}]


def test_b16_recovers_bare_json_form():
    """A bare top-level JSON object whose name matches a tool is recovered."""
    text = '{"name": "Read", "arguments": {"file_path": "/b"}}'
    residual, calls = salvage_tool_calls(text, _NAMES)
    assert residual == ""
    assert calls == [{"function": {"name": "Read", "arguments": {"file_path": "/b"}}}]


def test_b16_accepts_parameters_alias():
    """``parameters`` is accepted as an alias for ``arguments``."""
    text = '{"name": "Bash", "parameters": {"command": "ls"}}'
    _, calls = salvage_tool_calls(text, _NAMES)
    assert calls == [{"function": {"name": "Bash", "arguments": {"command": "ls"}}}]


def test_b16_ignores_json_that_is_not_a_known_tool():
    """JSON whose name is not an offered tool is left as prose, not a call."""
    text = '{"name": "NotATool", "arguments": {}}'
    residual, calls = salvage_tool_calls(text, _NAMES)
    assert calls == []
    assert "NotATool" in residual


def test_b16_ignores_prose_with_braces():
    """Prose containing braces but no matching tool name yields no calls."""
    text = "Use the config {a: 1} to proceed."
    residual, calls = salvage_tool_calls(text, _NAMES)
    assert calls == []
    assert residual == text


def test_b16_no_tools_offered_is_noop():
    """With no offered tools, nothing is salvaged."""
    text = '{"name": "Write", "arguments": {}}'
    residual, calls = salvage_tool_calls(text, [])
    assert calls == []
    assert residual == text


def test_b16_recovers_multiple_bare_calls():
    """Multiple matching bare JSON objects are each recovered (supports B08)."""
    text = '{"name": "Read", "arguments": {"file_path": "/a"}} then {"name": "Bash", "arguments": {"command": "ls"}}'
    _, calls = salvage_tool_calls(text, _NAMES)
    names = [c["function"]["name"] for c in calls]
    assert names == ["Read", "Bash"]

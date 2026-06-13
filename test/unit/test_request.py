"""Unit tests for request translation (capabilities B11, B17, B18, tool plumbing)."""

from nasim.bridge.translator.request import anthropic_to_ollama

_DEF = "qwen2.5-coder:14b"
_FAST = "qwen2.5-coder:7b"


def _translate(a_body):
    """Translate with fixed ctx/keep_alive for terse assertions."""
    return anthropic_to_ollama(a_body, _DEF, _FAST, 32768, "60m")


def test_b11_system_as_string():
    """A string system prompt becomes a leading system message."""
    out = _translate({"system": "be terse", "messages": [{"role": "user", "content": "hi"}]})
    assert out["messages"][0] == {"role": "system", "content": "be terse"}


def test_b11_system_as_block_list():
    """A system block list is flattened (text blocks newline-joined)."""
    body = {
        "system": [{"type": "text", "text": "line one"}, {"type": "text", "text": "line two"}],
        "messages": [{"role": "user", "content": "hi"}],
    }
    out = _translate(body)
    assert out["messages"][0] == {"role": "system", "content": "line one\nline two"}


def test_no_system_message_when_absent():
    """No system message is prepended when there is no system field."""
    out = _translate({"messages": [{"role": "user", "content": "hi"}]})
    assert all(m["role"] != "system" for m in out["messages"])


def test_b17_image_block_becomes_omitted_text():
    """An image block degrades to '[image omitted]' (coder models aren't vision)."""
    body = {
        "messages": [
            {"role": "user", "content": [{"type": "image", "source": {}}, {"type": "text", "text": "what is this"}]}
        ]
    }
    out = _translate(body)
    assert out["messages"][-1]["content"] == "[image omitted]\nwhat is this"


def test_b18_sampling_params_and_stop_sequences_passthrough():
    """temperature/top_p/top_k/max_tokens/stop_sequences map into options."""
    body = {
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 256,
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": 40,
        "stop_sequences": ["STOP"],
    }
    opts = _translate(body)["options"]
    assert opts["num_predict"] == 256
    assert opts["temperature"] == 0.2
    assert opts["top_p"] == 0.9
    assert opts["top_k"] == 40
    assert opts["stop"] == ["STOP"]
    assert opts["num_ctx"] == 32768


def test_tools_with_schema_are_translated_and_others_dropped():
    """Only tools carrying an input_schema are forwarded as Ollama functions."""
    body = {
        "messages": [{"role": "user", "content": "hi"}],
        "tools": [
            {"name": "Write", "description": "w", "input_schema": {"type": "object"}},
            {"name": "NoSchema"},
        ],
    }
    out = _translate(body)
    assert len(out["tools"]) == 1
    fn = out["tools"][0]
    assert fn["type"] == "function"
    assert fn["function"]["name"] == "Write"
    assert fn["function"]["parameters"] == {"type": "object"}


def test_assistant_tool_use_becomes_tool_calls():
    """An assistant tool_use block becomes an Ollama tool_calls entry."""
    body = {
        "messages": [
            {"role": "user", "content": "do it"},
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "calling"},
                    {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "ls"}},
                ],
            },
        ]
    }
    out = _translate(body)
    assistant = out["messages"][-1]
    assert assistant["content"] == "calling"
    assert assistant["tool_calls"] == [{"function": {"name": "Bash", "arguments": {"command": "ls"}}}]


def test_b09_tool_result_labeled_and_ordered():
    """A user tool_result becomes a 'tool' message labelled via the recorded id."""
    body = {
        "messages": [
            {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "t1", "name": "Read", "input": {}}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "file body"},
                    {"type": "text", "text": "now continue"},
                ],
            },
        ]
    }
    out = _translate(body)
    tool_msg = next(m for m in out["messages"] if m["role"] == "tool")
    assert tool_msg["content"] == "file body"
    assert tool_msg["tool_name"] == "Read"
    # text after the tool_result is preserved as a separate, later user message.
    assert out["messages"][-1] == {"role": "user", "content": "now continue"}


def test_b10_tool_result_error_prefixed():
    """A tool_result with is_error gets an 'ERROR:' prefix."""
    body = {
        "messages": [
            {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}]},
            {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "boom", "is_error": True}],
            },
        ]
    }
    out = _translate(body)
    tool_msg = next(m for m in out["messages"] if m["role"] == "tool")
    assert tool_msg["content"] == "ERROR: boom"


def test_stream_flag_and_model_mapping():
    """The stream flag is honoured and the model name is mapped."""
    out = _translate({"model": "haiku", "stream": True, "messages": [{"role": "user", "content": "x"}]})
    assert out["stream"] is True
    assert out["model"] == _FAST

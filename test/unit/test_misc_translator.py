"""Unit tests for the small pure helpers: content, sse, tokens (B03)."""

import json

from nasim.bridge.translator.content import content_to_text, system_to_text
from nasim.bridge.translator.sse import sse
from nasim.bridge.translator.tokens import estimate_tokens


def test_system_to_text_string_and_blocks():
    """system_to_text handles both a string and a text-block list."""
    assert system_to_text("plain") == "plain"
    assert system_to_text([{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]) == "a\nb"
    assert system_to_text(None) == ""


def test_content_to_text_blocks_and_image():
    """content_to_text joins text blocks and omits images."""
    blocks = [{"type": "text", "text": "x"}, {"type": "image", "source": {}}, {"type": "text", "text": "y"}]
    assert content_to_text(blocks) == "x\n[image omitted]\ny"
    assert content_to_text("raw") == "raw"


def test_sse_format():
    """sse emits the 'event:'/'data:' pair with compact JSON and blank-line terminator."""
    out = sse("message_stop", {"type": "message_stop"})
    assert out == 'event: message_stop\ndata: {"type":"message_stop"}\n\n'


def test_b03_estimate_tokens_positive_and_grows():
    """Token estimate is >= 1 and grows with more input."""
    small = estimate_tokens({"messages": [{"role": "user", "content": "hi"}]})
    large = estimate_tokens({"messages": [{"role": "user", "content": "hi " * 500}]})
    assert small >= 1
    assert large > small


def test_b03_estimate_counts_system_and_tools():
    """System prompt and tool definitions contribute to the estimate."""
    base = estimate_tokens({"messages": [{"role": "user", "content": "hi"}]})
    withtools = estimate_tokens(
        {
            "system": "x" * 100,
            "messages": [{"role": "user", "content": "hi"}],
            "tools": [{"name": "T", "input_schema": {"type": "object"}}],
        }
    )
    assert withtools > base


def test_b03_estimate_handles_block_content():
    """List (block) message content is measured via its JSON length."""
    blocks = [{"type": "text", "text": "hello"}]
    assert estimate_tokens({"messages": [{"role": "user", "content": blocks}]}) >= len(json.dumps(blocks)) // 4

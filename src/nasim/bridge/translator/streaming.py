"""Streaming translation — Ollama chat chunks -> Anthropic SSE events.

Emits the exact event sequence the Anthropic SDK requires: ``message_start``,
``content_block_start``/``delta``/``stop`` (text and tool_use), ``message_delta``
(stop_reason + usage), ``message_stop``.

When tools are offered, text is buffered rather than streamed live so a tool
call the model writes as plain text can be salvaged at end-of-stream. With no
tools, text streams live for responsiveness.

Functions:
    stream_ollama_to_anthropic: Async generator of Anthropic SSE event strings.
"""

import json
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional

from nasim.bridge.translator.blocks import stop_reason, tool_use_block
from nasim.bridge.translator.sse import sse
from nasim.bridge.translator.tool_salvage import salvage_tool_calls


def _block_events(a_index: int, a_block: Dict[str, Any]) -> List[str]:
    """SSE start/delta/stop events for one fully-known content block.

    Args:
        a_index (int): The block's index in the message.
        a_block (Dict[str, Any]): A text or tool_use content block.

    Returns:
        List[str]: The three SSE event strings for the block.
    """
    if a_block["type"] == "text":
        return [
            sse(
                "content_block_start",
                {"type": "content_block_start", "index": a_index, "content_block": {"type": "text", "text": ""}},
            ),
            sse(
                "content_block_delta",
                {
                    "type": "content_block_delta",
                    "index": a_index,
                    "delta": {"type": "text_delta", "text": a_block["text"]},
                },
            ),
            sse("content_block_stop", {"type": "content_block_stop", "index": a_index}),
        ]
    return [
        sse(
            "content_block_start",
            {"type": "content_block_start", "index": a_index, "content_block": {**a_block, "input": {}}},
        ),
        sse(
            "content_block_delta",
            {
                "type": "content_block_delta",
                "index": a_index,
                "delta": {
                    "type": "input_json_delta",
                    "partial_json": json.dumps(a_block["input"], separators=(",", ":")),
                },
            },
        ),
        sse("content_block_stop", {"type": "content_block_stop", "index": a_index}),
    ]


async def stream_ollama_to_anthropic(
    a_chunks: AsyncIterator[Dict[str, Any]],
    a_requested_model: str,
    a_tool_schemas: Optional[Dict[str, Any]] = None,
) -> AsyncIterator[str]:
    """Translate a stream of Ollama chat chunks into Anthropic SSE events.

    Args:
        a_chunks (AsyncIterator[Dict[str, Any]]): Parsed Ollama JSONL chunks.
        a_requested_model (str): Model name to echo in ``message_start``.
        a_tool_schemas (Optional[Dict[str, Any]]): Map of tool name ->
            ``input_schema``. When set, text is buffered for end-of-stream
            salvage and tool-call arguments are coerced.

    Yields:
        str: SSE-formatted event strings.
    """
    tool_names = list(a_tool_schemas or {})
    msg_id = f"msg_{uuid.uuid4().hex[:24]}"
    yield sse(
        "message_start",
        {
            "type": "message_start",
            "message": {
                "id": msg_id,
                "type": "message",
                "role": "assistant",
                "model": a_requested_model,
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                },
            },
        },
    )

    buffer_text = bool(tool_names)
    index = -1
    text_open = False
    text_buffer = ""
    native_calls: List[Dict[str, Any]] = []
    saw_tool_calls = False
    input_tokens = 0
    output_tokens = 0
    done_reason: Optional[str] = None

    async for chunk in a_chunks:
        message = chunk.get("message", {})

        delta_text = message.get("content", "")
        if delta_text:
            if buffer_text:
                text_buffer += delta_text
            else:
                if not text_open:
                    index += 1
                    text_open = True
                    yield sse(
                        "content_block_start",
                        {
                            "type": "content_block_start",
                            "index": index,
                            "content_block": {"type": "text", "text": ""},
                        },
                    )
                yield sse(
                    "content_block_delta",
                    {
                        "type": "content_block_delta",
                        "index": index,
                        "delta": {"type": "text_delta", "text": delta_text},
                    },
                )

        for call in message.get("tool_calls") or []:
            native_calls.append(call)

        if chunk.get("done"):
            input_tokens = chunk.get("prompt_eval_count", 0)
            output_tokens = chunk.get("eval_count", 0)
            done_reason = chunk.get("done_reason")

    if text_open:
        yield sse("content_block_stop", {"type": "content_block_stop", "index": index})

    # Determine tool calls: native first; salvage from buffered text otherwise.
    tool_calls = list(native_calls)
    if buffer_text:
        residual = text_buffer
        if not tool_calls:
            residual, salvaged = salvage_tool_calls(text_buffer, tool_names)
            tool_calls.extend(salvaged)
        if residual:
            index += 1
            for event in _block_events(index, {"type": "text", "text": residual}):
                yield event

    for call in tool_calls:
        saw_tool_calls = True
        index += 1
        for event in _block_events(index, tool_use_block(call, a_tool_schemas)):
            yield event

    yield sse(
        "message_delta",
        {
            "type": "message_delta",
            "delta": {"stop_reason": stop_reason(done_reason, saw_tool_calls), "stop_sequence": None},
            "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
        },
    )
    yield sse("message_stop", {"type": "message_stop"})

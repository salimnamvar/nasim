"""Translator — Anthropic Messages API <-> Ollama native chat API.

Pure translation functions used by the Bridge server. No I/O happens here;
everything is dict-in / dict-out so the module is fully unit-testable.

Anthropic Messages API reference: https://docs.anthropic.com/en/api/messages
Ollama chat API reference: https://github.com/ollama/ollama/blob/main/docs/api.md

Functions:
    map_model: Resolve a requested (Claude/Naseem) model name to an Ollama tag.
    anthropic_to_ollama: Translate an Anthropic request body to an Ollama one.
    ollama_to_anthropic: Translate a final Ollama response to Anthropic format.
    stream_ollama_to_anthropic: Async generator emitting Anthropic SSE events.
    estimate_tokens: Rough token estimate for the count_tokens endpoint.
"""

import json
import os
import re
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "qwen2.5-coder:14b")
FAST_MODEL = os.environ.get("FAST_MODEL", "qwen2.5-coder:7b")
NUM_CTX = int(os.environ.get("BRIDGE_NUM_CTX", "32768"))
KEEP_ALIVE = os.environ.get("BRIDGE_KEEP_ALIVE", "60m")


def map_model(a_model: str) -> str:
    """Map a requested model name to an Ollama model tag.

    Rules, in order:
        1. A name containing ":" is already an Ollama tag — pass through.
           This enables hot-swap: `/model qwen2.5-coder:7b` inside the CLI.
        2. A name containing "haiku" (any case) maps to the fast model.
        3. Everything else (sonnet/opus/fable/unknown) maps to the default model.

    Args:
        a_model (str): Model name as sent by the client.

    Returns:
        str: Ollama model tag.
    """
    result = DEFAULT_MODEL
    if ":" in a_model:
        result = a_model
    elif "haiku" in a_model.lower():
        result = FAST_MODEL
    return result


def _system_to_text(a_system: Any) -> str:
    """Flatten an Anthropic `system` field (string or block list) to plain text."""
    result = ""
    if isinstance(a_system, str):
        result = a_system
    elif isinstance(a_system, list):
        result = "\n".join(b.get("text", "") for b in a_system if b.get("type") == "text")
    return result


def _content_to_text(a_content: Any) -> str:
    """Flatten an Anthropic content value (string or block list) to plain text."""
    result = ""
    if isinstance(a_content, str):
        result = a_content
    elif isinstance(a_content, list):
        parts: List[str] = []
        for block in a_content:
            btype = block.get("type")
            if btype == "text":
                parts.append(block.get("text", ""))
            elif btype == "image":
                parts.append("[image omitted]")
        result = "\n".join(parts)
    return result


def anthropic_to_ollama(a_body: Dict[str, Any]) -> Dict[str, Any]:
    """Translate an Anthropic Messages request body to an Ollama /api/chat body.

    Handles: system blocks, text blocks, tool definitions, tool_use blocks
    (assistant history), tool_result blocks (user history), sampling params,
    and stop sequences. Thinking blocks are dropped. Images are noted as
    omitted (coder models are not vision models).

    Args:
        a_body (Dict[str, Any]): Anthropic Messages API request body.

    Returns:
        Dict[str, Any]: Ollama /api/chat request body.
    """
    messages: List[Dict[str, Any]] = []

    system_text = _system_to_text(a_body.get("system", ""))
    if system_text:
        messages.append({"role": "system", "content": system_text})

    # tool_use_id -> tool name, needed to label tool results for the template
    tool_id_to_name: Dict[str, str] = {}

    for msg in a_body.get("messages", []):
        role = msg.get("role")
        content = msg.get("content")

        if isinstance(content, str):
            messages.append({"role": role, "content": content})
            continue

        if role == "assistant":
            text_parts: List[str] = []
            tool_calls: List[Dict[str, Any]] = []
            for block in content or []:
                btype = block.get("type")
                if btype == "text":
                    text_parts.append(block.get("text", ""))
                elif btype == "tool_use":
                    tool_id_to_name[block.get("id", "")] = block.get("name", "")
                    tool_calls.append(
                        {
                            "function": {
                                "name": block.get("name", ""),
                                "arguments": block.get("input", {}),
                            }
                        }
                    )
            entry: Dict[str, Any] = {"role": "assistant", "content": "\n".join(text_parts)}
            if tool_calls:
                entry["tool_calls"] = tool_calls
            messages.append(entry)
        else:
            # user message: may interleave text and tool_result blocks; order matters
            pending_text: List[str] = []
            for block in content or []:
                btype = block.get("type")
                if btype == "tool_result":
                    if pending_text:
                        messages.append({"role": "user", "content": "\n".join(pending_text)})
                        pending_text = []
                    tool_entry: Dict[str, Any] = {
                        "role": "tool",
                        "content": _content_to_text(block.get("content", "")),
                    }
                    name = tool_id_to_name.get(block.get("tool_use_id", ""))
                    if name:
                        tool_entry["tool_name"] = name
                    if block.get("is_error"):
                        tool_entry["content"] = f"ERROR: {tool_entry['content']}"
                    messages.append(tool_entry)
                elif btype == "text":
                    pending_text.append(block.get("text", ""))
                elif btype == "image":
                    pending_text.append("[image omitted]")
            if pending_text:
                messages.append({"role": "user", "content": "\n".join(pending_text)})

    options: Dict[str, Any] = {"num_ctx": NUM_CTX}
    if "max_tokens" in a_body:
        options["num_predict"] = a_body["max_tokens"]
    for src, dst in (("temperature", "temperature"), ("top_p", "top_p"), ("top_k", "top_k")):
        if src in a_body:
            options[dst] = a_body[src]
    if a_body.get("stop_sequences"):
        options["stop"] = a_body["stop_sequences"]

    result: Dict[str, Any] = {
        "model": map_model(a_body.get("model", DEFAULT_MODEL)),
        "messages": messages,
        "stream": bool(a_body.get("stream", False)),
        "options": options,
        "keep_alive": KEEP_ALIVE,
    }

    tools = [t for t in a_body.get("tools", []) if t.get("input_schema")]
    if tools:
        result["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ]

    return result


_TOOL_CALL_TAG = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)


def _iter_json_objects(a_text: str) -> List[str]:
    """Yield top-level brace-balanced JSON object substrings from text."""
    result: List[str] = []
    depth = 0
    start = -1
    in_str = False
    escape = False
    for i, ch in enumerate(a_text):
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start >= 0:
                    result.append(a_text[start : i + 1])
                    start = -1
    return result


def salvage_tool_calls(a_text: str, a_tool_names: List[str]) -> Tuple[str, List[Dict[str, Any]]]:
    """Recover tool calls a model emitted as text instead of structured output.

    Smaller Ollama models (e.g. qwen2.5-coder:14b) sometimes ignore the chat
    template's tool-call protocol and write the call as plain text — either
    wrapped in <tool_call>...</tool_call> or as a bare JSON object with "name"
    and "arguments" keys. This recovers both forms so tool use stays reliable.

    Args:
        a_text (str): Assistant text content from the model.
        a_tool_names (List[str]): Names of tools offered in the request; only
            JSON whose "name" matches one of these is treated as a tool call.

    Returns:
        Tuple[str, List[Dict[str, Any]]]: (residual text with calls removed,
        list of Ollama-shaped tool_call dicts).
    """
    calls: List[Dict[str, Any]] = []
    if not a_tool_names or not a_text:
        return (a_text, calls)

    names = set(a_tool_names)
    candidates: List[str] = _TOOL_CALL_TAG.findall(a_text)
    text = _TOOL_CALL_TAG.sub("", a_text)

    if not candidates and "{" in text:
        # No tags: scan bare JSON objects only if one names a known tool.
        bare = _iter_json_objects(text)
        for blob in bare:
            try:
                obj = json.loads(blob)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and obj.get("name") in names:
                candidates.append(blob)
                text = text.replace(blob, "", 1)

    for blob in candidates:
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or obj.get("name") not in names:
            continue
        args = obj.get("arguments", obj.get("parameters", {}))
        calls.append({"function": {"name": obj["name"], "arguments": args}})

    return (text.strip(), calls)


def _stop_reason(a_done_reason: Optional[str], a_has_tool_calls: bool) -> str:
    """Map an Ollama done_reason to an Anthropic stop_reason."""
    result = "end_turn"
    if a_has_tool_calls:
        result = "tool_use"
    elif a_done_reason == "length":
        result = "max_tokens"
    return result


def _tool_use_block(a_call: Dict[str, Any]) -> Dict[str, Any]:
    """Convert one Ollama tool_call entry to an Anthropic tool_use block."""
    fn = a_call.get("function", {})
    arguments = fn.get("arguments", {})
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            arguments = {"_raw": arguments}
    return {
        "type": "tool_use",
        "id": f"toolu_{uuid.uuid4().hex[:24]}",
        "name": fn.get("name", ""),
        "input": arguments,
    }


def ollama_to_anthropic(
    a_resp: Dict[str, Any],
    a_requested_model: str,
    a_tool_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Translate a final (non-streaming) Ollama chat response to Anthropic format.

    Args:
        a_resp (Dict[str, Any]): Ollama /api/chat response with done=true.
        a_requested_model (str): Model name originally requested by the client,
            echoed back so the client sees the name it asked for.
        a_tool_names (Optional[List[str]]): Tool names offered in the request,
            used to salvage text-encoded tool calls. None disables salvage.

    Returns:
        Dict[str, Any]: Anthropic Messages API response body.
    """
    message = a_resp.get("message", {})
    content: List[Dict[str, Any]] = []

    text = message.get("content", "")
    tool_calls = list(message.get("tool_calls") or [])

    if not tool_calls and a_tool_names:
        text, salvaged = salvage_tool_calls(text, a_tool_names)
        tool_calls.extend(salvaged)

    if text:
        content.append({"type": "text", "text": text})

    for call in tool_calls:
        content.append(_tool_use_block(call))

    if not content:
        content.append({"type": "text", "text": ""})

    return {
        "id": f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "model": a_requested_model,
        "content": content,
        "stop_reason": _stop_reason(a_resp.get("done_reason"), bool(tool_calls)),
        "stop_sequence": None,
        "usage": {
            "input_tokens": a_resp.get("prompt_eval_count", 0),
            "output_tokens": a_resp.get("eval_count", 0),
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
        },
    }


def _sse(a_event: str, a_data: Dict[str, Any]) -> str:
    """Format one server-sent event."""
    return f"event: {a_event}\ndata: {json.dumps(a_data, separators=(',', ':'))}\n\n"


def _block_events(a_index: int, a_block: Dict[str, Any]) -> List[str]:
    """SSE start/delta/stop events for one fully-known content block."""
    if a_block["type"] == "text":
        return [
            _sse(
                "content_block_start",
                {
                    "type": "content_block_start",
                    "index": a_index,
                    "content_block": {"type": "text", "text": ""},
                },
            ),
            _sse(
                "content_block_delta",
                {
                    "type": "content_block_delta",
                    "index": a_index,
                    "delta": {"type": "text_delta", "text": a_block["text"]},
                },
            ),
            _sse("content_block_stop", {"type": "content_block_stop", "index": a_index}),
        ]
    return [
        _sse(
            "content_block_start",
            {
                "type": "content_block_start",
                "index": a_index,
                "content_block": {**a_block, "input": {}},
            },
        ),
        _sse(
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
        _sse("content_block_stop", {"type": "content_block_stop", "index": a_index}),
    ]


async def stream_ollama_to_anthropic(
    a_chunks: AsyncIterator[Dict[str, Any]],
    a_requested_model: str,
    a_tool_names: Optional[List[str]] = None,
) -> AsyncIterator[str]:
    """Translate a stream of Ollama chat chunks into Anthropic SSE events.

    Emits the event sequence the Anthropic SDK requires: message_start,
    content_block_start/delta/stop (text and tool_use), message_delta
    (stop_reason + usage), message_stop.

    When `a_tool_names` is set, text is buffered rather than streamed live so a
    tool call the model emits as plain text can be salvaged into a tool_use
    block (see :func:`salvage_tool_calls`). With no tools, text streams live.

    Args:
        a_chunks: Async iterator of parsed Ollama JSONL chunk dicts.
        a_requested_model (str): Model name to echo in message_start.
        a_tool_names (Optional[List[str]]): Tool names offered in the request.

    Yields:
        str: SSE-formatted event strings.
    """
    msg_id = f"msg_{uuid.uuid4().hex[:24]}"
    yield _sse(
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

    buffer_text = bool(a_tool_names)
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
                    yield _sse(
                        "content_block_start",
                        {
                            "type": "content_block_start",
                            "index": index,
                            "content_block": {"type": "text", "text": ""},
                        },
                    )
                yield _sse(
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
        yield _sse("content_block_stop", {"type": "content_block_stop", "index": index})

    # Determine tool calls: native first; salvage from buffered text otherwise.
    tool_calls = list(native_calls)
    if buffer_text:
        residual = text_buffer
        if not tool_calls:
            residual, salvaged = salvage_tool_calls(text_buffer, a_tool_names or [])
            tool_calls.extend(salvaged)
        if residual:
            index += 1
            for event in _block_events(index, {"type": "text", "text": residual}):
                yield event

    for call in tool_calls:
        saw_tool_calls = True
        index += 1
        for event in _block_events(index, _tool_use_block(call)):
            yield event

    yield _sse(
        "message_delta",
        {
            "type": "message_delta",
            "delta": {
                "stop_reason": _stop_reason(done_reason, saw_tool_calls),
                "stop_sequence": None,
            },
            "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
        },
    )
    yield _sse("message_stop", {"type": "message_stop"})


def estimate_tokens(a_body: Dict[str, Any]) -> int:
    """Estimate input token count for the count_tokens endpoint.

    Uses a chars/3.6 heuristic over system, messages, and tool definitions.
    Good enough for the CLI's context-window accounting; not exact.

    Args:
        a_body (Dict[str, Any]): Anthropic count_tokens request body.

    Returns:
        int: Estimated input token count.
    """
    chars = len(_system_to_text(a_body.get("system", "")))
    for msg in a_body.get("messages", []):
        content = msg.get("content")
        if isinstance(content, str):
            chars += len(content)
        elif isinstance(content, list):
            chars += len(json.dumps(content))
    if a_body.get("tools"):
        chars += len(json.dumps(a_body["tools"]))
    return max(1, int(chars / 3.6))

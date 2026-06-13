"""Content-block builders shared by response and streaming translation.

Functions:
    tool_use_block: Build an Anthropic ``tool_use`` block from an Ollama call.
    stop_reason: Map an Ollama ``done_reason`` to an Anthropic ``stop_reason``.
"""

import uuid
from typing import Any, Dict, Optional

from nasim.bridge.translator.schema_coerce import coerce_arguments


def tool_use_block(a_call: Dict[str, Any], a_tool_schemas: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convert one Ollama ``tool_call`` to an Anthropic ``tool_use`` block.

    The call's arguments are passed through :func:`coerce_arguments` against the
    tool's input schema so the resulting ``input`` survives the CLI's strict
    client-side validation.

    Args:
        a_call (Dict[str, Any]): Ollama tool_call with a ``function`` key.
        a_tool_schemas (Optional[Dict[str, Any]]): Map of tool name ->
            ``input_schema``. Used to coerce arguments; None disables coercion
            beyond JSON-string parsing.

    Returns:
        Dict[str, Any]: An Anthropic ``tool_use`` content block.
    """
    fn = a_call.get("function", {})
    name = fn.get("name", "")
    schema = (a_tool_schemas or {}).get(name, {})
    coerced = coerce_arguments(fn.get("arguments", {}), schema)
    return {
        "type": "tool_use",
        "id": f"toolu_{uuid.uuid4().hex[:24]}",
        "name": name,
        "input": coerced,
    }


def stop_reason(a_done_reason: Optional[str], a_has_tool_calls: bool) -> str:
    """Map an Ollama ``done_reason`` to an Anthropic ``stop_reason``.

    Args:
        a_done_reason (Optional[str]): Ollama's ``done_reason`` (e.g. ``length``).
        a_has_tool_calls (bool): Whether the turn produced any tool calls.

    Returns:
        str: ``tool_use`` if any calls, else ``max_tokens`` if truncated, else
        ``end_turn``.
    """
    result = "end_turn"
    if a_has_tool_calls:
        result = "tool_use"
    elif a_done_reason == "length":
        result = "max_tokens"
    return result

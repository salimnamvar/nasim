"""Response translation — final Ollama chat response -> Anthropic Messages.

Functions:
    ollama_to_anthropic: Translate a non-streaming Ollama response to Anthropic.
"""

import uuid
from typing import Any, Dict, List, Optional

from nasim.bridge.translator.blocks import stop_reason, tool_use_block
from nasim.bridge.translator.tool_salvage import salvage_tool_calls


def ollama_to_anthropic(
    a_resp: Dict[str, Any],
    a_requested_model: str,
    a_tool_schemas: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Translate a final (non-streaming) Ollama chat response to Anthropic format.

    Args:
        a_resp (Dict[str, Any]): Ollama ``/api/chat`` response with ``done=true``.
        a_requested_model (str): Model name the client asked for, echoed back.
        a_tool_schemas (Optional[Dict[str, Any]]): Map of tool name ->
            ``input_schema`` for offered tools. Enables text-encoded tool-call
            salvage and argument coercion. None disables both.

    Returns:
        Dict[str, Any]: Anthropic Messages API response body.
    """
    message = a_resp.get("message", {})
    content: List[Dict[str, Any]] = []

    text = message.get("content", "")
    tool_calls = list(message.get("tool_calls") or [])
    tool_names = list(a_tool_schemas or {})

    if not tool_calls and tool_names:
        text, salvaged = salvage_tool_calls(text, tool_names)
        tool_calls.extend(salvaged)

    if text:
        content.append({"type": "text", "text": text})
    for call in tool_calls:
        content.append(tool_use_block(call, a_tool_schemas))
    if not content:
        content.append({"type": "text", "text": ""})

    return {
        "id": f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "model": a_requested_model,
        "content": content,
        "stop_reason": stop_reason(a_resp.get("done_reason"), bool(tool_calls)),
        "stop_sequence": None,
        "usage": {
            "input_tokens": a_resp.get("prompt_eval_count", 0),
            "output_tokens": a_resp.get("eval_count", 0),
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
        },
    }

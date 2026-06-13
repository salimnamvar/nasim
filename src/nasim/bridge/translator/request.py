"""Request translation — Anthropic Messages body -> Ollama /api/chat body.

Handles system blocks, text blocks, tool definitions, assistant ``tool_use``
history, user ``tool_result`` history, sampling params, and stop sequences.
Thinking blocks are dropped; images are noted as omitted (coder models are not
vision models).

Functions:
    anthropic_to_ollama: Build an Ollama chat request body from an Anthropic one.
"""

from typing import Any, Dict, List

from nasim.bridge.translator.content import content_to_text, system_to_text
from nasim.bridge.translator.model_map import map_model


def anthropic_to_ollama(
    a_body: Dict[str, Any],
    a_default_model: str,
    a_fast_model: str,
    a_num_ctx: int,
    a_keep_alive: str,
    a_tool_temperature: float = 0.0,
) -> Dict[str, Any]:
    """Translate an Anthropic Messages request body to an Ollama chat body.

    Args:
        a_body (Dict[str, Any]): Anthropic Messages API request body.
        a_default_model (str): Default Ollama tag for non-haiku names.
        a_fast_model (str): Ollama tag for haiku names.
        a_num_ctx (int): Ollama context window to request.
        a_keep_alive (str): Ollama ``keep_alive`` duration.
        a_tool_temperature (float, optional): Temperature applied when the
            request offers tools and the client set none — low values keep small
            coder models on the tool-call format. Defaults to 0.0.

    Returns:
        Dict[str, Any]: Ollama ``/api/chat`` request body.
    """
    messages: List[Dict[str, Any]] = []

    system_text = system_to_text(a_body.get("system", ""))
    if system_text:
        messages.append({"role": "system", "content": system_text})

    # tool_use_id -> tool name, to label tool results for the chat template.
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
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    text_parts.append(block.get("text", ""))
                elif btype == "tool_use":
                    tool_id_to_name[block.get("id", "")] = block.get("name", "")
                    tool_calls.append(
                        {"function": {"name": block.get("name", ""), "arguments": block.get("input", {})}}
                    )
            entry: Dict[str, Any] = {"role": "assistant", "content": "\n".join(text_parts)}
            if tool_calls:
                entry["tool_calls"] = tool_calls
            messages.append(entry)
        else:
            # user message: may interleave text and tool_result blocks; order matters.
            pending_text: List[str] = []
            for block in content or []:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "tool_result":
                    if pending_text:
                        messages.append({"role": "user", "content": "\n".join(pending_text)})
                        pending_text = []
                    tool_entry: Dict[str, Any] = {
                        "role": "tool",
                        "content": content_to_text(block.get("content", "")),
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

    options: Dict[str, Any] = {"num_ctx": a_num_ctx}
    if "max_tokens" in a_body:
        options["num_predict"] = a_body["max_tokens"]
    for src, dst in (("temperature", "temperature"), ("top_p", "top_p"), ("top_k", "top_k")):
        if src in a_body:
            options[dst] = a_body[src]
    if a_body.get("stop_sequences"):
        options["stop"] = a_body["stop_sequences"]

    result: Dict[str, Any] = {
        "model": map_model(a_body.get("model", a_default_model), a_default_model, a_fast_model),
        "messages": messages,
        "stream": bool(a_body.get("stream", False)),
        "options": options,
        "keep_alive": a_keep_alive,
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
        # Small coder models emit far cleaner tool calls at low temperature; pin
        # it for tool-bearing requests unless the client explicitly chose one.
        if "temperature" not in options:
            options["temperature"] = a_tool_temperature

    return result

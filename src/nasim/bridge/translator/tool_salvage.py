"""Tool-call salvage — recover tool calls a model emitted as text.

Smaller Ollama models sometimes ignore the chat template's tool-call protocol
and write the call as plain text — either wrapped in
``<tool_call>...</tool_call>`` or as a bare JSON object with ``name`` and
``arguments`` keys. This module recovers both forms so tool use stays reliable.
It only treats JSON whose ``name`` matches an offered tool as a call, so prose
that merely contains braces is never misread.

Functions:
    salvage_tool_calls: Recover Ollama-shaped tool calls from assistant text.
"""

import json
import re
from typing import Any, Dict, List, Tuple

_TOOL_CALL_TAG = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)


def _iter_json_objects(a_text: str) -> List[str]:
    """Yield top-level brace-balanced JSON object substrings from text.

    Args:
        a_text (str): Text possibly containing JSON objects.

    Returns:
        List[str]: Each top-level ``{...}`` substring, in order.
    """
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

    Handles ``<tool_call>{...}</tool_call>`` tags and bare top-level JSON
    objects whose ``name`` matches an offered tool. Returns the residual text
    (with recovered calls removed) and the recovered calls in Ollama shape.

    Args:
        a_text (str): Assistant text content from the model.
        a_tool_names (List[str]): Names of tools offered in the request; only
            JSON whose ``name`` matches one of these becomes a tool call.

    Returns:
        Tuple[str, List[Dict[str, Any]]]: ``(residual_text, ollama_tool_calls)``
        where each call is ``{"function": {"name", "arguments"}}``.
    """
    calls: List[Dict[str, Any]] = []
    if not a_tool_names or not a_text:
        return (a_text, calls)

    names = set(a_tool_names)
    candidates: List[str] = _TOOL_CALL_TAG.findall(a_text)
    text = _TOOL_CALL_TAG.sub("", a_text)

    if not candidates and "{" in text:
        for blob in _iter_json_objects(text):
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

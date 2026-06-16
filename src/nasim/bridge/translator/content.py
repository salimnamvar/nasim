"""Content flatteners — Anthropic content/system blocks to plain text.

Coder models take plain prompts, so structured Anthropic content (a string or a
list of typed blocks) is reduced to the text an Ollama chat message carries.
Shared by :mod:`request` and :mod:`tokens` so the flattening rule lives once.

Functions:
    system_to_text: Flatten an Anthropic ``system`` field to plain text.
    content_to_text: Flatten an Anthropic message ``content`` to plain text.
"""

from typing import Any, List


def system_to_text(a_system: Any) -> str:
    """Flatten an Anthropic ``system`` field (string or block list) to text.

    Args:
        a_system (Any): A string, or a list of content blocks.

    Returns:
        str: Concatenated text of all text blocks (newline-joined).
    """
    result = ""
    if isinstance(a_system, str):
        result = a_system
    elif isinstance(a_system, list):
        result = "\n".join(b.get("text", "") for b in a_system if isinstance(b, dict) and b.get("type") == "text")
    return result


def content_to_text(a_content: Any) -> str:
    """Flatten an Anthropic content value (string or block list) to text.

    Text blocks pass through; image blocks become ``[image omitted]`` (coder
    models are not vision models); other block types are skipped.

    Args:
        a_content (Any): A string, or a list of content blocks.

    Returns:
        str: Newline-joined plain text.
    """
    result = ""
    if isinstance(a_content, str):
        result = a_content
    elif isinstance(a_content, list):
        parts: List[str] = []
        for block in a_content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                parts.append(block.get("text", ""))
            elif btype == "image":
                parts.append("[image omitted]")
        result = "\n".join(parts)
    return result

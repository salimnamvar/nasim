"""Token estimation for the ``count_tokens`` endpoint (heuristic).

Functions:
    estimate_tokens: Rough input-token estimate over system, messages, tools.
"""

import json
from typing import Any, Dict

from nasim.bridge.translator.content import system_to_text


def estimate_tokens(a_body: Dict[str, Any]) -> int:
    """Estimate input token count for the ``count_tokens`` endpoint.

    Uses a chars/3.6 heuristic over the system prompt, messages, and tool
    definitions. Good enough for the CLI's context-window accounting; not exact.

    Args:
        a_body (Dict[str, Any]): Anthropic ``count_tokens`` request body.

    Returns:
        int: Estimated input token count (>= 1).
    """
    chars = len(system_to_text(a_body.get("system", "")))
    for msg in a_body.get("messages", []):
        content = msg.get("content")
        if isinstance(content, str):
            chars += len(content)
        elif isinstance(content, list):
            chars += len(json.dumps(content))
    if a_body.get("tools"):
        chars += len(json.dumps(a_body["tools"]))
    return max(1, int(chars / 3.6))

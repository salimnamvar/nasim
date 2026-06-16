"""SSE — format a single Anthropic server-sent event.

Functions:
    sse: Format one ``event:``/``data:`` server-sent event line pair.
"""

import json
from typing import Any, Dict


def sse(a_event: str, a_data: Dict[str, Any]) -> str:
    """Format one server-sent event.

    Args:
        a_event (str): SSE event name (e.g. ``message_start``).
        a_data (Dict[str, Any]): JSON-serialisable event payload.

    Returns:
        str: ``event: <name>\\ndata: <compact-json>\\n\\n``.
    """
    return f"event: {a_event}\ndata: {json.dumps(a_data, separators=(',', ':'))}\n\n"

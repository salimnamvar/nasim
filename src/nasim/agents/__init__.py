"""Agent launch dispatch + detection (pluggable strategy map).

``launch_agent`` routes to the concrete launcher for the chosen agent; ``detect_agent``
returns the first available agent in priority order. Each launcher returns the child
process exit code.

Functions:
    launch_agent: Dispatch to the concrete launcher.
    detect_agent: First available agent in priority order.
"""

from __future__ import annotations

from typing import Optional, Sequence

from nasim.agents.aider import launch_aider
from nasim.agents.claude import launch_claude, one_shot_claude
from nasim.agents.grok import launch_grok
from nasim.agents.opencode import launch_opencode
from nasim.agents.terminal import launch_terminal
from nasim.util import have, log

__all__ = [
    "launch_agent",
    "detect_agent",
    "launch_claude",
    "one_shot_claude",
    "launch_aider",
    "launch_opencode",
    "launch_grok",
    "launch_terminal",
]


def launch_agent(a_agent: str, a_url: str, a_model: str, a_extra: Optional[Sequence[str]] = None) -> int:
    """Dispatch to the concrete launcher for an agent.

    Args:
        a_agent (str): Agent key (claude/code, grok, aider, opencode, terminal/shell).
        a_url (str): Transport URL.
        a_model (str): Model tag.
        a_extra (Optional[Sequence[str]]): Extra args for the agent.

    Returns:
        int: The agent's exit code.
    """
    extra = list(a_extra or [])
    if a_agent in ("claude", "code"):
        rc = launch_claude(a_url, a_model, extra)
    elif a_agent == "grok":
        rc = launch_grok(a_url, a_model, extra)
    elif a_agent == "aider":
        rc = launch_aider(a_url, a_model, extra)
    elif a_agent in ("opencode", "open"):
        rc = launch_opencode(a_url, a_model, extra)
    elif a_agent in ("terminal", "shell"):
        rc = launch_terminal(a_url, a_model)
    else:
        log(f"unknown agent '{a_agent}' — falling back to terminal shell")
        rc = launch_terminal(a_url, a_model)
    return rc


def detect_agent() -> str:
    """Return the first available agent in priority order.

    Returns:
        str: Agent key (claude > grok > aider > opencode > terminal).
    """
    result = "terminal"
    for name in ("claude", "grok", "aider", "opencode"):
        if have(name):
            result = name
            break
    return result

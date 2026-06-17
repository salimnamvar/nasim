"""Shared environment construction for Anthropic-compatible agents.

A single source for the full ``ANTHROPIC_*`` / ``CLAUDE_CODE_*`` surface that Claude
Code (and the branded terminal) need to talk to a remote Ollama model — replacing
the duplicated inline env blocks in the bash ``claude.sh`` and ``terminal.sh``.

Functions:
    build_anthropic_env: Return the env dict pointing Claude Code at a model/URL.
    ensure_workspace: Create and return the Claude workspace directory.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def ensure_workspace() -> str:
    """Create the Claude workspace directory and return its path.

    Returns:
        str: Path to ``$CLAUDE_WORKSPACE`` (default ``~/.fcc/agent_workspace``).
    """
    ws = os.environ.get("CLAUDE_WORKSPACE") or os.path.expanduser("~/.fcc/agent_workspace")
    Path(ws).mkdir(parents=True, exist_ok=True)
    return ws


def build_anthropic_env(a_model: str, a_base_url: str, a_workspace: Optional[str] = None) -> dict[str, str]:
    """Build the full Anthropic-compat environment for Claude Code.

    Mirrors the variable surface used by free-claude-code and the Claude adapter so
    that tool-calling works against the remote model. All three model tiers are
    mapped to the chosen tag.

    Args:
        a_model (str): The Ollama tag to serve as every Claude tier.
        a_base_url (str): The target base URL (tunnel or fcc proxy), no ``/v1``.
        a_workspace (Optional[str]): Workspace dir; created if omitted.

    Returns:
        dict[str, str]: Environment overrides to merge onto ``os.environ``.
    """
    base = a_base_url.rstrip("/")
    ws = a_workspace or ensure_workspace()
    env = {
        "ANTHROPIC_API_URL": f"{base}/v1",
        "ANTHROPIC_BASE_URL": base,
        "ANTHROPIC_AUTH_TOKEN": "ollama",
        "ANTHROPIC_API_KEY": "",
        "ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS": "81920",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": a_model,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": a_model,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": a_model,
        "CLAUDE_CODE_SUBAGENT_MODEL": a_model,
        "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1",
        "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "190000",
        "CLAUDE_CLI_BIN": os.environ.get("CLAUDE_CLI_BIN", "claude"),
        "CLAUDE_WORKSPACE": ws,
        "TERM": "dumb",
        "PYTHONIOENCODING": "utf-8",
        "DISABLE_TELEMETRY": "1",
    }
    return env

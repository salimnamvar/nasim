"""Nasim — remote Ollama on black + frontier agents on the laptop.

A thin glue package that brings up a private transport (SSH tunnel, Tailscale, or
LiteLLM proxy) to an Ollama server on the remote GPU host ``black`` and launches a
frontier agentic-coding CLI (Claude Code, Aider, OpenCode, Grok, or a branded
terminal) pointed at it.

Design goal beyond parity with the original bash tool: a *clean toggle*. When nasim
exits — cleanly, via Ctrl-C, or on a crash — Claude Code returns to its defaults
with zero Ollama leakage (no ``_nasim`` picker entries in ``~/.claude.json`` and the
original ``~/.claude/settings.json`` model restored). See :mod:`nasim.claude_settings`
and :mod:`nasim.rollback`.

Modules:
    config: Effective configuration (defaults < file < env < CLI).
    util: Shared logging and process helpers.
    rollback: Environment backup/restore and crash-safe cleanup hooks.
    claude_settings: Reversible Claude Code ``/model`` picker injection.
    probe: Endpoint reachability and model discovery.
    transport: Pluggable transport adapters (ssh, tailscale, litellm).
    agents: Pluggable agent launchers (claude, aider, opencode, grok, terminal).
    daemon: Persistent tunnel lifecycle.
    code: Smart ``nasim code`` launch with context injection.
    cli: Command dispatch.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "2026-06-17-py1-full-parity+clean-toggle"

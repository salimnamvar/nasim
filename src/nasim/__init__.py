"""Nasim — route Claude Code to local Ollama models with one-command rollback.

The package splits cleanly into two sides that share only :mod:`nasim.config`:

- :mod:`nasim.runtime` — the client-side start/stop toggle.
- :mod:`nasim.bridge` — the server-side Anthropic <-> Ollama translating proxy.
"""

__version__ = "1.0.0"

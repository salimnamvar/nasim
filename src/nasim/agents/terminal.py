"""Branded terminal launcher — manual escape hatch with full env + picker.

Drops into an interactive ``$SHELL`` whose environment has the full Anthropic-compat
surface set and the Ollama model injected into Claude's ``/model`` picker, so the
user can run ``claude``/``aider``/raw ``curl`` against black manually. Unlike the
bash version (which ``exec``'d the shell), this waits for the shell to exit so it can
eject the picker entries and restore Claude defaults afterwards.
"""

from __future__ import annotations

import os
import subprocess

from nasim.agents.base import build_anthropic_env, ensure_workspace
from nasim.claude_settings import ClaudeSettings
from nasim.util import is_dry, log


def launch_terminal(a_url: str, a_model: str) -> int:
    """Drop into a branded interactive shell wired to the remote model.

    Args:
        a_url (str): Ollama base URL from the active transport.
        a_model (str): Model tag.

    Returns:
        int: The shell's exit code (0 in dry-run).
    """
    base = a_url.rstrip("/")
    log("dropping into configured shell (all envs set). Run your agents manually.")
    if is_dry():
        print(f"DRY: export ANTHROPIC_BASE_URL={base} OLLAMA_API_BASE={a_url} NASIM_MODEL={a_model}")
        print(f'DRY: PS1="nasim[black:{a_model}] $ " ; exec $SHELL -i')
        return 0

    ws = ensure_workspace()
    env = dict(os.environ, **build_anthropic_env(a_model, base, ws))
    env.update(
        {
            "OLLAMA_API_BASE": a_url,
            "NASIM_REMOTE_URL": a_url,
            "NASIM_MODEL": a_model,
            "NASIM_ACTIVE": "1",
            "PS1": f"nasim[black:{a_model}] $ ",
        }
    )
    # Interactive shells need a real terminal type, not the "dumb" used for claude.
    env["TERM"] = os.environ.get("TERM", "xterm")

    settings = ClaudeSettings()
    rc = 0
    try:
        settings.inject(a_model)
        print("nasim: remote env active in this shell (branded prompt).")
        print("  Running 'claude', 'aider', etc. here will use Ollama models on black.")
        print("  Type 'exit' to leave and return to normal shells (default real APIs).")
        shell = os.environ.get("SHELL", "/bin/bash")
        rc = subprocess.run([shell, "-i"], env=env).returncode
    finally:
        settings.eject()
    return rc

"""Grok Code launcher — OpenAI-compatible endpoints, falls back to terminal.

If the ``grok`` CLI is absent we drop into the branded terminal so the user can run
any agent manually.
"""

from __future__ import annotations

import os
import subprocess
from typing import Optional, Sequence

from nasim.util import have, is_dry, log


def launch_grok(a_url: str, a_model: str, a_extra: Optional[Sequence[str]] = None) -> int:
    """Launch the Grok CLI against a remote Ollama model.

    Args:
        a_url (str): Ollama base URL from the active transport.
        a_model (str): Model tag.
        a_extra (Optional[Sequence[str]]): Extra args forwarded to ``grok``.

    Returns:
        int: Grok's exit code, or the terminal's when grok is unavailable.
    """
    extra = list(a_extra or [])
    base = a_url.rstrip("/") + "/v1"
    log(f"launching grok -> {base} model={a_model} (OpenAI compat)")
    if is_dry():
        print(f"DRY: GROK_API_BASE={base} GROK_API_KEY=ollama grok --model {a_model} " + " ".join(extra))
        return 0
    if not have("grok"):
        log("grok CLI not found. Install with: pip install grok-cli (or similar)")
        log("falling back to terminal mode...")
        from nasim.agents.terminal import launch_terminal

        return launch_terminal(a_url, a_model)
    env = dict(
        os.environ,
        GROK_API_BASE=base,
        GROK_API_KEY="ollama",
        OPENAI_BASE_URL=base,
        OPENAI_API_KEY="ollama",
    )
    return subprocess.run(["grok", "--model", a_model, *extra], env=env).returncode

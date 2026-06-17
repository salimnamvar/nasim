"""OpenCode launcher — prefers the OpenAI-compat surface for broad support.

Exports ``OPENAI_BASE_URL=.../v1`` (+ ``OLLAMA_API_BASE``) and runs ``opencode``
against the forwarded black endpoint. We do not invoke ``ollama launch opencode``
(that would target the laptop's local Ollama, not the forwarded remote).
"""

from __future__ import annotations

import os
import subprocess
from typing import Optional, Sequence

from nasim.util import is_dry, log


def launch_opencode(a_url: str, a_model: str, a_extra: Optional[Sequence[str]] = None) -> int:
    """Launch OpenCode against a remote Ollama model.

    Args:
        a_url (str): Ollama base URL from the active transport.
        a_model (str): Model tag.
        a_extra (Optional[Sequence[str]]): Extra args forwarded to ``opencode``.

    Returns:
        int: OpenCode's exit code (0 in dry-run).
    """
    extra = list(a_extra or [])
    base = a_url.rstrip("/")
    log(f"launching opencode -> {a_url} model={a_model} (OpenAI compat)")
    if is_dry():
        print(f"DRY: OPENAI_BASE_URL={base}/v1 OPENAI_API_KEY=ollama opencode --model {a_model} " + " ".join(extra))
        return 0
    env = dict(
        os.environ,
        OPENAI_BASE_URL=f"{base}/v1",
        OPENAI_API_KEY="ollama",
        OLLAMA_API_BASE=a_url,
    )
    rc = subprocess.run(["opencode", "--model", a_model, *extra], env=env).returncode
    return rc

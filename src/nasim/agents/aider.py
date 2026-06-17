"""Aider launcher — OpenAI-compat over Ollama via ``OLLAMA_API_BASE``.

Aider is robust with local models; it expects the ``ollama/<tag>`` model form and
the ``OLLAMA_API_BASE`` pointing at the transport URL.
"""

from __future__ import annotations

import os
import subprocess
from typing import Optional, Sequence

from nasim.util import is_dry, log


def launch_aider(a_url: str, a_model: str, a_extra: Optional[Sequence[str]] = None) -> int:
    """Launch Aider against a remote Ollama model.

    Args:
        a_url (str): Ollama base URL from the active transport.
        a_model (str): Model tag (``ollama/`` prefix added if absent).
        a_extra (Optional[Sequence[str]]): Extra args forwarded to ``aider``.

    Returns:
        int: Aider's exit code (0 in dry-run).
    """
    extra = list(a_extra or [])
    model = a_model if a_model.startswith("ollama/") else f"ollama/{a_model}"
    log(f"launching aider -> {a_url} model={model}")
    if is_dry():
        print(f"DRY: OLLAMA_API_BASE={a_url} aider --model {model} " + " ".join(extra))
        return 0
    env = dict(os.environ, OLLAMA_API_BASE=a_url)
    return subprocess.run(["aider", "--model", model, *extra], env=env).returncode

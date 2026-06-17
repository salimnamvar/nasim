"""Claude Code launcher — env-scoped subprocess with reversible picker injection.

This is the load-bearing path for the clean-toggle guarantee:

* Claude runs as a **child process** whose ``ANTHROPIC_*`` environment is built by
  :func:`nasim.agents.base.build_anthropic_env` and passed only to that child — the
  parent shell's environment is never touched.
* The chosen model is injected into Claude's ``/model`` picker
  (:class:`nasim.claude_settings.ClaudeSettings`) before launch and **ejected in a
  ``finally``** after Claude exits, so the picker is clean the instant the session
  ends. The same eject runs from the crash-safe hooks in :mod:`nasim.rollback`.
* When a free-claude-code checkout is present, an isolated fcc proxy is started for
  richer tool-calling and stopped in the same ``finally``.

Functions:
    launch_claude: Interactive Claude Code session.
    one_shot_claude: Single-prompt, non-interactive Claude run.
"""

from __future__ import annotations

import subprocess
from typing import Optional, Sequence

from nasim import fcc
from nasim.agents.base import build_anthropic_env, ensure_workspace
from nasim.claude_settings import ClaudeSettings
from nasim.util import is_dry, log


def _resolve_target(a_url: str, a_model: str) -> tuple[str, bool]:
    """Resolve the base URL Claude should use, starting fcc when available.

    Args:
        a_url (str): The Ollama base URL from the active transport.
        a_model (str): The model tag.

    Returns:
        tuple[str, bool]: (target_base_url, using_fcc).
    """
    import os

    base = a_url.rstrip("/")
    target = base
    using_fcc = False
    if not is_dry() and os.environ.get("NASIM_USE_FCC", "1") != "0" and fcc.available():
        log("fcc proxy available — starting isolated free-claude-code gateway (set NASIM_USE_FCC=0 to force direct)")
        ok, proxy_url = fcc.start_proxy(base, a_model)
        if ok:
            target = proxy_url.rstrip("/")
            using_fcc = True
        else:
            log("fcc proxy did not start; using direct ollama compat url")
    return target, using_fcc


def launch_claude(a_url: str, a_model: str, a_extra: Optional[Sequence[str]] = None) -> int:
    """Launch an interactive Claude Code session against a remote Ollama model.

    Args:
        a_url (str): Ollama base URL from the active transport.
        a_model (str): Model tag to use as every Claude tier.
        a_extra (Optional[Sequence[str]]): Extra args forwarded to ``claude``.

    Returns:
        int: Claude's exit code (0 in dry-run).
    """
    extra = list(a_extra or [])
    target, using_fcc = _resolve_target(a_url, a_model)
    ws = ensure_workspace()
    log(f"launching claude -> {target} model={a_model} (using_fcc={int(using_fcc)})")

    if is_dry():
        env = build_anthropic_env(a_model, target, ws)
        print(
            "DRY: "
            + " ".join(f"{k}={v}" for k, v in env.items())
            + f" claude --model {a_model} "
            + " ".join(extra)
        )
        return 0

    log("Tip: strong tool-calling models (deepseek-r1:*, qwen3*) work best with claude-code.")
    settings = ClaudeSettings()
    rc = 0
    try:
        settings.inject(a_model)
        import os

        env = dict(os.environ, **build_anthropic_env(a_model, target, ws))
        rc = subprocess.run(["claude", "--model", a_model, *extra], env=env).returncode
    finally:
        settings.eject()
        fcc.stop_proxy()
    return rc


def one_shot_claude(a_url: str, a_model: str, a_prompt: str, a_extra: Optional[Sequence[str]] = None) -> int:
    """Run a single Claude prompt non-interactively, then clean up.

    Args:
        a_url (str): Ollama base URL.
        a_model (str): Model tag.
        a_prompt (str): The full prompt (context already prepended by the caller).
        a_extra (Optional[Sequence[str]]): Extra args forwarded to ``claude``.

    Returns:
        int: Claude's exit code (0 in dry-run).
    """
    extra = list(a_extra or [])
    target, _ = _resolve_target(a_url, a_model)
    ws = ensure_workspace()

    if is_dry():
        print(f"DRY: claude -p <prompt> --model {a_model} --output-format text")
        return 0

    settings = ClaudeSettings()
    rc = 0
    try:
        settings.inject(a_model)
        import os

        env = dict(os.environ, **build_anthropic_env(a_model, target, ws))
        cmd = [
            "claude", "-p", a_prompt, "--model", a_model,
            "--output-format", "text", "--allow-dangerously-skip-permissions", *extra,
        ]
        rc = subprocess.run(cmd, env=env).returncode
    finally:
        settings.eject()
        fcc.stop_proxy()
    return rc

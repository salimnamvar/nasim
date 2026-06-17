"""Interactive ``nasim select`` — zero-dependency numbered menus.

Presents transport and agent choices in the configured order, reads a model tag,
applies the weak-model guard, then delegates to ``choose_and_launch``.

Functions:
    do_select: Run the interactive selection flow.
"""

from __future__ import annotations

from typing import Optional

from nasim import config
from nasim.orchestration import choose_and_launch
from nasim.util import log

_ACCESS_LABELS = {
    "ssh-tunnel": "ssh-tunnel (recommended, always works here)",
    "ssh": "ssh-tunnel (recommended, always works here)",
    "tailscale": "tailscale (if up)",
    "ts": "tailscale (if up)",
    "litellm": "litellm (proxy on top)",
    "llm": "litellm (proxy on top)",
}
_ACCESS_KEY = {"ssh-tunnel": "ssh-tunnel", "ssh": "ssh-tunnel", "tailscale": "tailscale", "ts": "tailscale", "litellm": "litellm", "llm": "litellm"}

_AGENT_LABELS = {
    "claude": "claude (native Anthropic compat — full frontier agent)",
    "code": "claude (native Anthropic compat — full frontier agent)",
    "aider": "aider (git-centric, excellent local)",
    "opencode": "opencode (open Claude Code alt)",
    "open": "opencode (open Claude Code alt)",
    "terminal": "terminal (branded shell — manual any agent)",
    "shell": "terminal (branded shell — manual any agent)",
}
_AGENT_KEY = {"claude": "claude", "code": "claude", "aider": "aider", "opencode": "opencode", "open": "opencode", "terminal": "terminal", "shell": "terminal"}


def _menu(a_title: str, a_keys: list[str], a_labels: dict, a_keymap: dict) -> str:
    """Render a numbered menu and return the chosen canonical key.

    Args:
        a_title (str): Prompt title.
        a_keys (list[str]): Ordered raw keys from config.
        a_labels (dict): key -> display label.
        a_keymap (dict): key -> canonical key.

    Returns:
        str: The chosen canonical key.
    """
    seen: list[tuple[str, str]] = []
    for key in a_keys:
        canon = a_keymap.get(key)
        if canon and canon not in [c for c, _ in seen]:
            seen.append((canon, a_labels.get(key, canon)))
    for idx, (_, label) in enumerate(seen, 1):
        print(f"  {idx}) {label}")
    choice = ""
    while not choice:
        try:
            raw = input(f"{a_title} (1-{len(seen)}): ").strip()
            n = int(raw)
            if 1 <= n <= len(seen):
                choice = seen[n - 1][0]
        except (ValueError, EOFError):
            choice = seen[0][0]
    return choice


def do_select(a_args: Optional[list] = None) -> int:
    """Run the interactive select flow and launch the chosen combination.

    Args:
        a_args (Optional[list]): Unused; present for dispatch symmetry.

    Returns:
        int: The launched agent's exit code (0 if aborted at the guard).
    """
    cfg = config.get_config()
    log("nasim select — choose access to black + frontier agent (Ctrl-C aborts)")
    print()

    access = _menu("Access method", cfg.access_order.split(), _ACCESS_LABELS, _ACCESS_KEY)
    print(f"Selected access: {access}\n")
    agent = _menu("Agent / terminal", cfg.agent_order.split(), _AGENT_LABELS, _AGENT_KEY)
    print(f"Selected agent: {agent}\n")

    try:
        raw = input(f"Model tag on black [{cfg.default_model}]: ").strip()
    except EOFError:
        raw = ""
    model = raw or cfg.default_model

    if "qwen2.5" in model or "qwen2" in model:
        log(f"WARNING: {model} is a weak/older tag for agentic coding (malformed turns with claude/opencode).")
        log("Strong picks: deepseek-r1:14b, deepseek-r1:32b, qwen3:8b, gemma4:31b (GPU-resident).")
        try:
            yn = input("Proceed with weak model anyway? (y/N): ").strip()
        except EOFError:
            yn = ""
        if not yn.lower().startswith("y"):
            log("Aborting select. Re-run and choose a strong tag (or edit DEFAULT_MODEL).")
            return 0

    print()
    log(f"Bringing up {access} + {agent} + {model} ...")
    return choose_and_launch(access, agent, model)

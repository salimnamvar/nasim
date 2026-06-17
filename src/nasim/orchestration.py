"""Core select/launch coordination (the service layer).

``choose_and_launch`` brings up the chosen transport, surfaces the model inventory
(authoritative SSH list + existence warning), then delegates to the agent launcher.
``legacy_claude`` / ``legacy_aider`` keep the thin back-compat entry points working,
preferring an active daemon tunnel before opening an ad-hoc one.

Functions:
    choose_and_launch: Transport bring-up + probe + launch.
    legacy_claude: Back-compat ``nasim claude``.
    legacy_aider: Back-compat ``nasim aider``.
"""

from __future__ import annotations

import os
from typing import Optional, Sequence

from nasim import config, daemon
from nasim.agents import launch_aider, launch_agent, launch_claude
from nasim.rollback import get_guard
from nasim.util import is_dry, log


def choose_and_launch(a_access: str, a_agent: str, a_model: str, a_extra: Optional[Sequence[str]] = None) -> int:
    """Bring up a transport, show models, and launch the chosen agent.

    Args:
        a_access (str): Transport key.
        a_agent (str): Agent key.
        a_model (str): Model tag.
        a_extra (Optional[Sequence[str]]): Extra args for the agent.

    Returns:
        int: The agent's exit code.
    """
    cfg = config.get_config()
    extra = list(a_extra or [])
    get_guard().save_env_state()
    get_guard().install_cleanup()

    if is_dry():
        url = f"http://127.0.0.1:{cfg.default_local_port}"
        log(f"(dry) would setup access={a_access} (no real tunnel)")
    else:
        from nasim.transport import setup_transport

        url = setup_transport(a_access, a_model)

    if not is_dry():
        from nasim.probe import model_exists_on_black, nasim_models, probe_url

        if not probe_url(url):
            log(f"WARNING: final probe failed for {url} (proceeding; litellm /api/tags differs by design)")
        log(f"models at {url} (for {a_agent}):")
        nasim_models()
        if not model_exists_on_black(a_model):
            log(f"WARNING: '{a_model}' not found in black inventory. The agent may fail or trigger a slow pull.")

    return launch_agent(a_agent, url, a_model, extra)


def legacy_claude(a_extra: Optional[Sequence[str]] = None) -> int:
    """Back-compat ``nasim claude`` — reuse daemon tunnel or open ad-hoc.

    Args:
        a_extra (Optional[Sequence[str]]): Extra args for ``claude``.

    Returns:
        int: Claude's exit code.
    """
    cfg = config.get_config()
    extra = list(a_extra or [])
    get_guard().save_env_state()
    get_guard().install_cleanup()
    model = os.environ.get("NASIM_MODEL", cfg.default_model)
    url = os.environ.get("NASIM_REMOTE_URL", "")
    if not url and daemon.is_running():
        url = daemon.url()
    if not url:
        log("no active tunnel; starting ad-hoc ssh tunnel for legacy claude...")
        from nasim.transport import setup_ssh_tunnel

        url = setup_ssh_tunnel()
    return launch_claude(url, model, extra)


def legacy_aider(a_extra: Optional[Sequence[str]] = None) -> int:
    """Back-compat ``nasim aider`` — reuse daemon tunnel or open ad-hoc.

    Args:
        a_extra (Optional[Sequence[str]]): Extra args for ``aider``.

    Returns:
        int: Aider's exit code.
    """
    cfg = config.get_config()
    extra = list(a_extra or [])
    get_guard().install_cleanup()
    model = os.environ.get("NASIM_MODEL", f"ollama/{cfg.default_model}")
    url = os.environ.get("NASIM_REMOTE_URL", "")
    if not url:
        if daemon.is_running():
            url = daemon.url()
        else:
            log("no NASIM_REMOTE_URL; starting ad-hoc ssh tunnel for legacy aider...")
            from nasim.transport import setup_ssh_tunnel

            url = setup_ssh_tunnel()
    return launch_aider(url, model, extra)

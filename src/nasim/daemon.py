"""Persistent tunnel daemon + lifecycle.

``nasim start`` brings up a background transport and records its URL so every later
``nasim code``/``nasim claude`` reuses it; ``nasim stop`` tears it down and restores
the environment (and Claude defaults). State persists across shells via files under
``~/.local/share/nasim/``.

Functions:
    start: Start the persistent tunnel.
    stop: Tear down the tunnel and restore env + Claude defaults.
    status: Print daemon health, models, context, KB status.
    is_running: Whether a usable tunnel is recorded.
    url: The active URL ("" if none).
    ensure_running: Auto-start if not already running.
"""

from __future__ import annotations

import os
import signal

from nasim import config
from nasim.rollback import get_guard
from nasim.util import capture, is_dry, log


def _ensure_state() -> None:
    """Ensure the runtime state directory exists."""
    config.STATE_DIR.mkdir(parents=True, exist_ok=True)


def start(a_access: str = "ssh-tunnel") -> int:
    """Start the persistent background tunnel.

    Saves the environment before any modification (rollback guarantee), brings up
    the transport, and records the active URL.

    Args:
        a_access (str): Transport to use (ssh-tunnel/tailscale/litellm).

    Returns:
        int: 0 on success, 1 on failure.
    """
    _ensure_state()
    if is_running():
        log(f"daemon already running ({url()})")
        print("Run 'nasim stop' first, or 'nasim status' for details.")
        return 0

    get_guard().save_env_state()
    log(f"starting nasim daemon (access={a_access})...")

    cfg = config.get_config()
    if is_dry():
        new_url = f"http://127.0.0.1:{cfg.default_local_port}"
        log(f"(dry) would start daemon with url={new_url}")
    else:
        from nasim.transport import setup_transport

        new_url = setup_transport(a_access)

    if not new_url:
        log("ERROR: failed to establish transport")
        get_guard().restore_env_state()
        return 1

    config.ACTIVE_URL_FILE.write_text(new_url, encoding="utf-8")
    if a_access in ("ssh-tunnel", "ssh"):
        ssh_pid = capture(["pgrep", "-f", f"ssh.*{cfg.default_local_port}.*{cfg.black_host}"])
        if ssh_pid:
            config.DAEMON_PID_FILE.write_text(ssh_pid.splitlines()[0], encoding="utf-8")

    os.environ["NASIM_REMOTE_URL"] = new_url
    os.environ["NASIM_ACTIVE"] = "1"
    log(f"daemon active — url={new_url}")
    log("all 'nasim code', 'nasim claude', 'nasim aider' calls will reuse this tunnel")
    print("Run 'nasim status' for health, 'nasim stop' to tear down + restore env.")
    return 0


def stop() -> int:
    """Tear down the tunnel and restore env + Claude defaults.

    Returns:
        int: 0 always.
    """
    _ensure_state()
    cfg = config.get_config()
    if not is_running():
        log("no active daemon")
        get_guard().restore_env_state()
        return 0

    log("stopping nasim daemon...")
    if config.DAEMON_PID_FILE.exists():
        try:
            pid = int(config.DAEMON_PID_FILE.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            log(f"terminated tunnel PID {pid}")
        except (ValueError, ProcessLookupError, OSError):
            pass
        config.DAEMON_PID_FILE.unlink(missing_ok=True)

    # Best-effort sweep of any lingering forwards for this host/port.
    from nasim.util import run

    run(["pkill", "-f", f"ssh.*{cfg.default_local_port}.*{cfg.black_host}"])

    get_guard().restore_env_state()
    config.ACTIVE_URL_FILE.unlink(missing_ok=True)
    log("daemon stopped — env restored, cloud agents back to normal")
    return 0


def status() -> int:
    """Print daemon state, endpoint health, models, context, and KB status.

    Returns:
        int: 0 always.
    """
    _ensure_state()
    cfg = config.get_config()
    print("nasim daemon status")
    print("===================")
    if not is_running():
        print("  state: STOPPED")
        print("  tip: run 'nasim start' to connect to black")
        return 0

    from nasim import context, kb
    from nasim.probe import list_models_on_black, probe_and_show

    active = url()
    print("  state: RUNNING")
    print(f"  url:   {active}")
    print(f"  host:  {cfg.black_host}")
    print(f"  model: {os.environ.get('NASIM_MODEL', cfg.default_model)}")
    print("\n  health check:")
    print("  + endpoint reachable" if probe_and_show(active) else "  - endpoint NOT reachable (tunnel may be stale)")
    print("")
    list_models_on_black()
    print("")
    print(f"  project context: ACTIVE ({context.context_file()})" if context.is_active() else "  project context: none")
    print("")
    print(f"  knowledge base:  indexed ({kb.index_path()})" if kb.is_indexed() else "  knowledge base:  not indexed")
    return 0


def is_running() -> bool:
    """Return whether a usable tunnel is recorded.

    Returns:
        bool: True if the active-url file exists and any tracked PID is alive.
    """
    if not config.ACTIVE_URL_FILE.is_file():
        return False
    if not config.ACTIVE_URL_FILE.read_text().strip():
        return False
    if config.DAEMON_PID_FILE.is_file():
        try:
            pid = int(config.DAEMON_PID_FILE.read_text().strip())
            os.kill(pid, 0)
        except (ValueError, ProcessLookupError, OSError):
            return False
    return True


def url() -> str:
    """Return the active tunnel URL, or empty string.

    Returns:
        str: Active URL.
    """
    out = ""
    if config.ACTIVE_URL_FILE.is_file():
        out = config.ACTIVE_URL_FILE.read_text().strip()
    return out


def ensure_running() -> None:
    """Auto-start the daemon with the default transport if not running."""
    if not is_running():
        log("no active daemon — auto-starting...")
        start("ssh-tunnel")

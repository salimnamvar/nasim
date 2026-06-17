"""Transport adapters: bring up a private path to black's Ollama and return a URL.

``setup_transport`` is the strategy dispatcher. ``ssh-tunnel`` and ``tailscale`` are
direct Ollama forwards; ``litellm`` starts an inner SSH tunnel then a LiteLLM proxy
on top. Shared helpers (``free_port``, ``cleanup_tunnel``) live here.

Functions:
    setup_transport: Dispatch to the chosen transport, returning the agent URL.
    free_port: Find the next free local TCP port at/above a base.
    cleanup_tunnel: Kill a tunnel process recorded in a pidfile.
"""

from __future__ import annotations

import os
import signal
import socket
from pathlib import Path

from nasim import config
from nasim.util import die, is_dry, log
from nasim.transport.ssh import setup_ssh_tunnel
from nasim.transport.tailscale import setup_tailscale
from nasim.transport.litellm import setup_litellm

__all__ = ["setup_transport", "free_port", "cleanup_tunnel", "setup_ssh_tunnel"]


def free_port(a_base: int = 0) -> int:
    """Return the next free local TCP port at or above a base.

    Args:
        a_base (int): Starting port; 0 means use the configured default.

    Returns:
        int: A free port.

    Raises:
        NasimError: If no free port is found within base+100.
    """
    cfg = config.get_config()
    base = a_base or cfg.default_local_port
    chosen = base
    found = False
    for port in range(base, base + 101):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                chosen = port
                found = True
                break
            except OSError:
                continue
    if not found:
        die(f"no free port found near {base}")
    return chosen


def cleanup_tunnel(a_pidfile: str) -> None:
    """Terminate a tunnel process recorded in a pidfile and remove the file.

    Args:
        a_pidfile (str): Path to a file holding the tunnel PID.
    """
    path = Path(a_pidfile)
    if not path.is_file():
        return
    try:
        pid = int(path.read_text().strip())
        os.kill(pid, signal.SIGTERM)
    except (ValueError, ProcessLookupError, OSError):
        pass
    path.unlink(missing_ok=True)


def setup_transport(a_access: str, a_model: str = "") -> str:
    """Bring up the chosen transport and return the URL agents should use.

    Args:
        a_access (str): One of ``ssh-tunnel``/``ssh``, ``tailscale``/``ts``,
            ``litellm``/``llm``.
        a_model (str): Model tag (only used to seed the LiteLLM config).

    Returns:
        str: The base URL agents should target.

    Raises:
        NasimError: On an unknown access type.
    """
    url = ""
    if a_access in ("ssh-tunnel", "ssh"):
        url = setup_ssh_tunnel()
    elif a_access in ("tailscale", "ts"):
        url = setup_tailscale()
        if not url:
            log("Tailscale unavailable — trying ssh-tunnel")
            url = setup_ssh_tunnel()
    elif a_access in ("litellm", "llm"):
        inner = setup_ssh_tunnel()
        url = setup_litellm(inner, a_model)
    else:
        die(f"unknown access: {a_access} (ssh-tunnel | tailscale | litellm)")
    return url

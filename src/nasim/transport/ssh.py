"""SSH tunnel transport — the primary, always-reliable private path (P01/P04).

Allocates a free local port, opens a backgrounded ``ssh -f -N -L`` forward to
``black:11434``, records the PID, probes, and returns the local URL. The tunnel is
intentionally *not* torn down when an agent exits; its lifetime is managed by the
daemon (``nasim stop``) or ``nasim tunnel`` helpers.
"""

from __future__ import annotations

import time

from nasim import config
from nasim.util import capture, die, is_dry, log


def setup_ssh_tunnel() -> str:
    """Open an SSH forward to black's Ollama and return the local URL.

    Returns:
        str: ``http://127.0.0.1:{port}`` for the live forward.

    Raises:
        NasimError: If the tunnel comes up but the endpoint does not answer.
    """
    cfg = config.get_config()
    if is_dry():
        return f"http://127.0.0.1:{cfg.default_local_port}"

    # Local imports avoid a circular import at module load time.
    from nasim.probe import probe_and_show
    from nasim.transport import cleanup_tunnel, free_port

    lport = free_port(cfg.default_local_port)
    pidfile = f"/tmp/nasim-ssh-tunnel-{_pid()}.pid"

    log(f"starting SSH tunnel: {lport} -> {cfg.black_host}:11434")
    ok, _ = _run(
        [
            "ssh",
            "-o",
            f"ConnectTimeout={cfg.ssh_connect_timeout}",
            "-o",
            f"ServerAliveInterval={cfg.ssh_server_alive_interval}",
            "-o",
            "ServerAliveCountMax=3",
            "-o",
            "ExitOnForwardFailure=yes",
            "-f",
            "-N",
            "-L",
            f"{lport}:localhost:11434",
            cfg.black_host,
        ]
    )
    time.sleep(0.6)

    pid = capture(["pgrep", "-f", f"ssh.*{lport}.*{cfg.black_host}"])
    if pid:
        with open(pidfile, "w", encoding="utf-8") as fh:
            fh.write(pid.splitlines()[0])

    url = f"http://127.0.0.1:{lport}"
    if not probe_and_show(url):
        cleanup_tunnel(pidfile)
        die("SSH tunnel came up but probe failed. Is ollama running on black?")

    log(f"SSH forward active (pidfile {pidfile}). It stays until killed (see 'nasim tunnel status').")
    return url


def _pid() -> int:
    """Return the current process PID.

    Returns:
        int: PID.
    """
    import os

    return os.getpid()


def _run(a_cmd):
    """Run a command, returning the util.run tuple.

    Args:
        a_cmd (list): argv to execute.

    Returns:
        tuple: (success, completed_process).
    """
    from nasim.util import run

    return run(a_cmd, a_check=True)

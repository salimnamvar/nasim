"""Tailscale transport — graceful-degrade strategy.

If Tailscale is up, try MagicDNS ``black:11434`` and probe; otherwise ask black for
its Tailscale IP over SSH and try that. Returns an empty string on any failure so
the dispatcher falls back to the SSH tunnel.
"""

from __future__ import annotations

from nasim import config
from nasim.util import capture, have, is_dry, log, run


def setup_tailscale() -> str:
    """Return a reachable Tailscale URL for black's Ollama, or "" on failure.

    Returns:
        str: ``http://{host}:11434`` if reachable, else empty string.
    """
    cfg = config.get_config()
    if is_dry():
        return "http://black:11434"

    from nasim.probe import probe_and_show

    url = ""
    ok, _ = run(["tailscale", "status"], a_check=True, a_capture=True)
    if not have("tailscale") or not ok:
        log("Tailscale not running or not installed. Falling back or choose another access.")
        return ""

    candidate = "http://black:11434"
    if probe_and_show(candidate):
        return candidate

    if have("ssh"):
        tsip = capture(
            ["ssh", "-o", f"ConnectTimeout={cfg.ssh_connect_timeout}", cfg.black_host, "tailscale ip -4 2>/dev/null | head -1"],
            a_timeout=cfg.ssh_connect_timeout + 8,
        )
        if tsip:
            candidate = f"http://{tsip.splitlines()[0]}:11434"
            if probe_and_show(candidate):
                return candidate

    log("Tailscale present but could not reach black:11434. Is black in the same tailnet and ollama listening?")
    return url

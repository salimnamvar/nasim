"""Reachability probing and model discovery (the "models are shown" layer).

Discovery always has an authoritative fallback: a direct ``ssh black`` query of
``/api/tags`` that does not depend on a local tunnel, matching the bash fix for the
"models not shown" class of bugs. HTTP is done with the standard library
``urllib`` rather than shelling out to curl/python.

Functions:
    probe_url: True if ``{url}/api/tags`` answers within the timeout.
    probe_and_show: Probe and print the first few model names.
    list_models_on_black: Print the authoritative black inventory over SSH.
    nasim_doctor: Full health check (url probe + black inventory + ps).
    nasim_models: ``nasim models`` command (url or SSH inventory).
    model_exists_on_black: True if an exact tag is present on black.
    fetch_models: Return model dicts from an Ollama endpoint.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from nasim import config
from nasim.util import capture, have, log


def fetch_models(a_url: str, a_timeout: Optional[float] = None) -> list[dict]:
    """Fetch the model list from an Ollama ``/api/tags`` endpoint.

    Args:
        a_url (str): Base URL (without ``/api/tags``).
        a_timeout (Optional[float]): Override request timeout in seconds.

    Returns:
        list[dict]: Model entries, or empty list on any failure.
    """
    cfg = config.get_config()
    timeout = a_timeout if a_timeout is not None else cfg.probe_timeout
    models: list[dict] = []
    url = a_url.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read())
        models = data.get("models", []) or []
    except (urllib.error.URLError, ValueError, OSError):
        models = []
    return models


def probe_url(a_url: str) -> bool:
    """Return whether an Ollama endpoint answers ``/api/tags``.

    Args:
        a_url (str): Base URL.

    Returns:
        bool: True if reachable.
    """
    cfg = config.get_config()
    reachable = False
    url = a_url.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=cfg.probe_timeout) as resp:
            reachable = resp.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        reachable = False
    return reachable


def probe_and_show(a_url: str) -> bool:
    """Probe an endpoint and, if reachable, print the first model names.

    Args:
        a_url (str): Base URL.

    Returns:
        bool: True if reachable.
    """
    log(f"probing {a_url} ...")
    ok = probe_url(a_url)
    if ok:
        log("OK: endpoint reachable")
        names = [m.get("name", "?") for m in fetch_models(a_url, a_timeout=5)][:8]
        if names:
            log("  models: " + " ".join(names))
        else:
            log("  (could not parse model list)")
    else:
        log(f"FAIL: {a_url} not reachable")
    return ok


def _ssh_tags_json(a_host: str) -> Optional[dict]:
    """Fetch ``/api/tags`` JSON from black over SSH.

    Args:
        a_host (str): SSH host alias.

    Returns:
        Optional[dict]: Parsed JSON or None.
    """
    cfg = config.get_config()
    out = capture(
        [
            "ssh",
            "-o",
            f"ConnectTimeout={cfg.ssh_connect_timeout}",
            a_host,
            "curl -s --max-time 8 http://localhost:11434/api/tags",
        ],
        a_timeout=cfg.ssh_connect_timeout + 12,
    )
    result: Optional[dict] = None
    if out:
        try:
            result = json.loads(out)
        except ValueError:
            result = None
    return result


def list_models_on_black() -> None:
    """Print the authoritative model inventory on black over SSH (no tunnel)."""
    cfg = config.get_config()
    if not have("ssh"):
        print("  (ssh not available; cannot list black models)")
        return
    print(f"  models available on black (via ssh to {cfg.black_host}:11434):")
    data = _ssh_tags_json(cfg.black_host)
    if not data:
        print("    (ssh to black for /api/tags failed)")
        return
    for m in data.get("models", []):
        name = m.get("name", "?")
        details = m.get("details", {})
        psize = details.get("parameter_size", "?")
        quant = details.get("quantization_level", "?")
        print(f"    - {name} ({psize}, {quant})")


def model_exists_on_black(a_want: str) -> bool:
    """Return whether an exact tag is present in black's inventory.

    Args:
        a_want (str): Exact model tag to look for.

    Returns:
        bool: True if present.
    """
    cfg = config.get_config()
    exists = False
    if have("ssh"):
        data = _ssh_tags_json(cfg.black_host)
        if data:
            names = [m.get("name", "") for m in data.get("models", [])]
            exists = a_want in names
    return exists


def nasim_doctor(a_url: Optional[str] = None) -> None:
    """Run a full health check: url probe + black inventory + ``ollama ps``.

    Args:
        a_url (Optional[str]): Endpoint to probe; defaults to the active/default url.
    """
    import os

    cfg = config.get_config()
    url = a_url or os.environ.get("NASIM_REMOTE_URL") or f"http://127.0.0.1:{cfg.default_local_port}"

    log(f"nasim doctor (version {cfg.version_override or _version()})")
    print(f"  effective url: {url}")
    print(f"  black host:    {cfg.black_host}")

    if not probe_and_show(url) and not os.environ.get("NASIM_REMOTE_URL"):
        log("No active local tunnel (or NASIM_REMOTE_URL) on the default port.")
        log("Tip: run 'nasim select' or 'nasim tunnel ssh' first, or export NASIM_REMOTE_URL.")

    list_models_on_black()

    if have("ssh"):
        print("  black ollama ps (via ssh):")
        ps = capture(
            [
                "ssh",
                "-o",
                f"ConnectTimeout={cfg.ssh_connect_timeout}",
                cfg.black_host,
                "ollama ps 2>/dev/null || curl -s http://localhost:11434/api/ps | head -c 300",
            ],
            a_timeout=cfg.ssh_connect_timeout + 10,
        )
        print(ps if ps else "    (ssh to black for ps failed)")


def nasim_models(a_url: Optional[str] = None) -> None:
    """Print models, either from a provided URL or the SSH inventory.

    Args:
        a_url (Optional[str]): If given, list via this endpoint instead of SSH.
    """
    if a_url:
        print(f"Models via provided url {a_url} :")
        names = [m.get("name", "?") for m in fetch_models(a_url, a_timeout=6)]
        if names:
            for n in names:
                print(f"  - {n}")
        else:
            print("  (failed)")
    else:
        list_models_on_black()


def _version() -> str:
    """Return the package version string.

    Returns:
        str: Version.
    """
    from nasim import __version__

    return __version__

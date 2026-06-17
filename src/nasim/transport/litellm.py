"""LiteLLM proxy transport — an OpenAI/Anthropic-compat layer over a base tunnel.

Writes a temp ``litellm.yaml`` registering the chosen model (plus a stable default
and a reasoner alias), starts ``litellm --config`` in the background, and uses
LiteLLM-specific readiness (``/health`` or ``/v1/models``) — not Ollama's
``/api/tags`` — to confirm it is up. Returns the proxy URL even on a soft readiness
failure so the caller can still surface the SSH inventory and a warning.
"""

from __future__ import annotations

import subprocess
import time

from nasim import config
from nasim.util import have, is_dry, log


def setup_litellm(a_inner_url: str, a_model: str = "") -> str:
    """Start a LiteLLM proxy in front of a verified inner Ollama URL.

    Args:
        a_inner_url (str): A verified Ollama base URL (ssh or tailscale).
        a_model (str): The exact tag to register; defaults to config default.

    Returns:
        str: ``http://127.0.0.1:{litellm_port}``.
    """
    cfg = config.get_config()
    if is_dry():
        return f"http://127.0.0.1:{cfg.litellm_port}"

    import os

    chosen = a_model or cfg.default_model
    pid = os.getpid()
    cfg_path = f"/tmp/nasim-litellm-{pid}.yaml"
    pidfile = f"/tmp/nasim-litellm-{pid}.pid"
    logf = f"/tmp/nasim-litellm-{pid}.log"

    with open(cfg_path, "w", encoding="utf-8") as fh:
        fh.write(
            "model_list:\n"
            f"  - model_name: {chosen}\n"
            "    litellm_params:\n"
            f"      model: ollama/{chosen}\n"
            f"      api_base: {a_inner_url}\n"
            "  - model_name: black-default\n"
            "    litellm_params:\n"
            f"      model: ollama/{chosen}\n"
            f"      api_base: {a_inner_url}\n"
            "  - model_name: black-reasoner\n"
            "    litellm_params:\n"
            "      model: ollama/deepseek-r1:14b\n"
            f"      api_base: {a_inner_url}\n"
        )

    log(f"litellm config: {cfg_path} (inner: {a_inner_url}, chosen: {chosen})")

    if not have("litellm"):
        log("litellm not installed. pip install 'litellm[proxy]' then re-run, or use direct transport.")
        return f"http://127.0.0.1:{cfg.litellm_port}"

    with open(logf, "w", encoding="utf-8") as out:
        proc = subprocess.Popen(
            ["litellm", "--config", cfg_path, "--port", str(cfg.litellm_port), "--num_workers", "1"],
            stdout=out,
            stderr=subprocess.STDOUT,
        )
    with open(pidfile, "w", encoding="utf-8") as fh:
        fh.write(str(proc.pid))
    time.sleep(1.5)

    url = f"http://127.0.0.1:{cfg.litellm_port}"
    if _litellm_ready(url):
        log(f"OK: litellm reachable at {url} (OpenAI/Anthropic compat)")
    else:
        log(f"WARNING: litellm did not respond on /health or /v1/models (see {logf}). Proceeding anyway.")
    return url


def _litellm_ready(a_url: str) -> bool:
    """Poll LiteLLM readiness endpoints.

    Args:
        a_url (str): Proxy base URL.

    Returns:
        bool: True if ``/health`` or ``/v1/models`` answers.
    """
    import urllib.error
    import urllib.request

    ready = False
    for _ in range(4):
        for path in ("/health", "/v1/models"):
            try:
                with urllib.request.urlopen(a_url + path, timeout=3) as resp:
                    if resp.status == 200:
                        ready = True
                        break
            except (urllib.error.URLError, OSError):
                continue
        if ready:
            break
        time.sleep(0.8)
    return ready

"""Shared fixtures for the live layers (integration, capability, e2e).

The ``bridge`` fixture yields a base URL reachable over the SSH tunnel. It reuses
an already-open nasim tunnel on the default port if one is up; otherwise it opens
a dedicated test tunnel on a separate port so a developer's active session is
never disturbed. If neither works, the whole live module is skipped (so the
CI-safe unit layer is unaffected). Unit tests never request these fixtures, so no
network happens during ``make test``.

Fixtures:
    cfg: Resolved configuration (session-scoped).
    bridge: Base URL of the reachable bridge (session-scoped; skips if down).
    post_message: Callable to POST /v1/messages and return the httpx response.
    stream_message: Callable to POST a streaming request and return parsed SSE.
"""

import json
import time
from typing import Any, Callable, Dict, List, Tuple

import httpx
import pytest

from nasim.config import Config
from nasim.runtime.tunnel import SSHTunnel

_TEST_PORT = 18099


def _healthy(a_base: str) -> bool:
    """Return True if the bridge at a_base answers /health with status ok."""
    result = False
    try:
        resp = httpx.get(f"{a_base}/health", timeout=4)
        result = resp.status_code == 200 and resp.json().get("status") == "ok"
    except (httpx.HTTPError, ValueError):
        result = False
    return result


@pytest.fixture(scope="session")
def cfg() -> Config:
    """Return the resolved Nasim configuration."""
    return Config.load()


@pytest.fixture(scope="session")
def bridge(cfg: Config, tmp_path_factory: pytest.TempPathFactory):
    """Yield a reachable bridge base URL, or skip the module if none is available."""
    if _healthy(cfg.base_url):
        yield cfg.base_url
        return

    pid_file = tmp_path_factory.mktemp("nasim") / "test_tunnel.pid"
    tunnel = SSHTunnel(_TEST_PORT, cfg.remote_host, cfg.bridge_port, pid_file, cfg.ssh_connect_timeout)
    ok, _ = tunnel.start(a_raise_on_error=False)
    base = f"http://localhost:{_TEST_PORT}"
    deadline = time.time() + 8
    while ok and time.time() < deadline and not _healthy(base):
        time.sleep(0.3)
    if not _healthy(base):
        tunnel.stop(a_raise_on_error=False)
        pytest.skip("bridge not reachable (SSH tunnel or nasim-bridge service down)")
    yield base
    tunnel.stop(a_raise_on_error=False)


@pytest.fixture
def post_message() -> Callable[..., httpx.Response]:
    """Return a function that POSTs /v1/messages and returns the response."""

    def _post(a_base: str, a_body: Dict[str, Any], a_timeout: float = 180) -> httpx.Response:
        return httpx.post(f"{a_base}/v1/messages", json=a_body, timeout=a_timeout)

    return _post


@pytest.fixture
def stream_message() -> Callable[..., List[Tuple[str, Dict[str, Any]]]]:
    """Return a function that POSTs a streaming request and returns parsed SSE."""

    def _stream(a_base: str, a_body: Dict[str, Any], a_timeout: float = 180) -> List[Tuple[str, Dict[str, Any]]]:
        events: List[Tuple[str, Dict[str, Any]]] = []
        with httpx.stream("POST", f"{a_base}/v1/messages", json=a_body, timeout=a_timeout) as resp:
            event = None
            for line in resp.iter_lines():
                if line.startswith("event: "):
                    event = line[len("event: ") :]
                elif line.startswith("data: ") and event is not None:
                    events.append((event, json.loads(line[len("data: ") :])))
        return events

    return _stream

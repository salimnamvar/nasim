"""Shared fixtures for the unit layer (no network, no real home).

Fixtures:
    config: A :class:`~nasim.config.Config` resolved to built-in defaults.
    paths: A :class:`~nasim.runtime.paths.RuntimePaths` rooted in a temp dir.
"""

from pathlib import Path

import pytest

from nasim.config import Config
from nasim.runtime.paths import RuntimePaths


@pytest.fixture
def config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    """Return a Config resolved from built-in defaults only.

    Environment overrides are stripped so the result is deterministic regardless
    of the shell the tests run in.
    """
    for env_var in (
        "NASIM_REMOTE_HOST",
        "NASIM_REMOTE_PORT",
        "NASIM_LOCAL_PORT",
        "NASIM_SSH_TIMEOUT",
        "OLLAMA_URL",
        "BRIDGE_NUM_CTX",
        "BRIDGE_KEEP_ALIVE",
        "BRIDGE_TIMEOUT",
        "BRIDGE_LOG_LEVEL",
        "DEFAULT_MODEL",
        "FAST_MODEL",
        "NASIM_RECOMMENDED_MODEL",
    ):
        monkeypatch.delenv(env_var, raising=False)
    return Config.load(a_cfg_dir=tmp_path / "nocfg")


@pytest.fixture
def paths(tmp_path: Path) -> RuntimePaths:
    """Return a RuntimePaths rooted at an isolated temp home, dirs created."""
    runtime_paths = RuntimePaths(root=tmp_path / "home")
    runtime_paths.ensure()
    return runtime_paths

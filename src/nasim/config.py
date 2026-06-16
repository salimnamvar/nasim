"""Configuration — the single source of truth for Nasim.

Settings resolve through this precedence (lowest to highest)::

    built-in defaults -> cfg/nasim.toml -> cfg/nasim.local.toml -> environment

Both the client runtime and the server bridge import :class:`Config`; neither
reads ``os.environ`` directly. ``tomllib`` (Python >= 3.11) parses the files.

Classes:
    Config: Immutable, fully-resolved configuration.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

# (field, toml_section, toml_key, env_var, caster)
_SCHEMA: Tuple[Tuple[str, str, str, str, Callable[[str], Any]], ...] = (
    ("remote_host", "server", "host", "NASIM_REMOTE_HOST", str),
    ("bridge_port", "server", "bridge_port", "NASIM_REMOTE_PORT", int),
    ("local_port", "client", "local_port", "NASIM_LOCAL_PORT", int),
    ("ssh_connect_timeout", "client", "ssh_connect_timeout", "NASIM_SSH_TIMEOUT", int),
    ("ollama_url", "bridge", "ollama_url", "OLLAMA_URL", str),
    ("num_ctx", "bridge", "num_ctx", "BRIDGE_NUM_CTX", int),
    ("keep_alive", "bridge", "keep_alive", "BRIDGE_KEEP_ALIVE", str),
    ("tool_temperature", "bridge", "tool_temperature", "BRIDGE_TOOL_TEMPERATURE", float),
    ("request_timeout", "bridge", "request_timeout", "BRIDGE_TIMEOUT", float),
    ("log_level", "bridge", "log_level", "BRIDGE_LOG_LEVEL", str),
    ("default_model", "models", "default", "DEFAULT_MODEL", str),
    ("fast_model", "models", "fast", "FAST_MODEL", str),
    ("recommended_model", "models", "recommended", "NASIM_RECOMMENDED_MODEL", str),
    ("debug_dump", "bridge", "debug_dump", "BRIDGE_DEBUG_DUMP", str),
)

_DEFAULTS: Dict[str, Any] = {
    "remote_host": "black",
    "bridge_port": 8080,
    "local_port": 18080,
    "ssh_connect_timeout": 8,
    "ollama_url": "http://localhost:11434",
    "num_ctx": 32768,
    "keep_alive": "60m",
    "tool_temperature": 0.0,
    "request_timeout": 600.0,
    "log_level": "INFO",
    "default_model": "qwen2.5-coder:14b",
    "fast_model": "qwen2.5-coder:7b",
    "recommended_model": "qwen2.5-coder:14b",
    "debug_dump": "",
}


def _repo_root() -> Path:
    """Return the repository root (this file is src/nasim/config.py)."""
    return Path(__file__).resolve().parents[2]


def _default_cfg_dir() -> Path:
    """Return the cfg/ directory, overridable via ``NASIM_CFG_DIR``."""
    override = os.environ.get("NASIM_CFG_DIR")
    return Path(override) if override else _repo_root() / "cfg"


def _read_toml(a_path: Path) -> Dict[str, Any]:
    """Return a parsed TOML mapping, or an empty dict if the file is absent.

    Args:
        a_path (Path): Path to a TOML file.

    Returns:
        Dict[str, Any]: Parsed mapping, or ``{}`` when the file does not exist.
    """
    result: Dict[str, Any] = {}
    if a_path.is_file():
        with a_path.open("rb") as handle:
            result = tomllib.load(handle)
    return result


@dataclass(frozen=True)
class Config:
    """Immutable, fully-resolved Nasim configuration.

    Attributes:
        remote_host (str): SSH host alias / hostname of the Ollama+bridge server.
        bridge_port (int): Port the bridge listens on (localhost, on the server).
        local_port (int): Local end of the SSH ``-L`` forward.
        ssh_connect_timeout (int): SSH connect timeout in seconds.
        ollama_url (str): Ollama base URL as seen on the server.
        num_ctx (int): Ollama context window passed on every request.
        keep_alive (str): Ollama ``keep_alive`` duration.
        tool_temperature (float): Temperature pinned for tool-bearing requests
            when the client sets none — low values sharpen tool-call format
            adherence on small coder models.
        request_timeout (float): Upstream request timeout in seconds.
        log_level (str): Bridge log level.
        default_model (str): Ollama tag for opus/sonnet/fable/unknown.
        fast_model (str): Ollama tag for haiku.
        recommended_model (str): Model steered on start for agentic work.
        debug_dump (str): If non-empty, a directory the bridge dumps each
            translated Ollama request/response to (diagnostics; off by default).
    """

    remote_host: str
    bridge_port: int
    local_port: int
    ssh_connect_timeout: int
    ollama_url: str
    num_ctx: int
    keep_alive: str
    tool_temperature: float
    request_timeout: float
    log_level: str
    default_model: str
    fast_model: str
    recommended_model: str
    debug_dump: str

    @property
    def base_url(self) -> str:
        """Anthropic base URL the CLI is pointed at (the tunnel entrance)."""
        return f"http://localhost:{self.local_port}"

    @classmethod
    def load(cls, a_cfg_dir: Optional[Path] = None) -> "Config":
        """Resolve configuration across defaults, TOML files, and environment.

        Args:
            a_cfg_dir (Optional[Path]): Directory holding ``nasim.toml`` /
                ``nasim.local.toml``. Defaults to the repo ``cfg/`` (or the
                ``NASIM_CFG_DIR`` override).

        Returns:
            Config: The resolved, immutable configuration.

        Raises:
            ValueError: If an environment override cannot be cast to its type.
        """
        cfg_dir = a_cfg_dir if a_cfg_dir is not None else _default_cfg_dir()
        base = _read_toml(cfg_dir / "nasim.toml")
        local = _read_toml(cfg_dir / "nasim.local.toml")

        values: Dict[str, Any] = dict(_DEFAULTS)
        for field_name, section, key, env_var, caster in _SCHEMA:
            for source in (base, local):
                if section in source and key in source[section]:
                    values[field_name] = source[section][key]
            raw = os.environ.get(env_var)
            if raw not in (None, ""):
                try:
                    values[field_name] = caster(raw)  # type: ignore[arg-type]
                except (TypeError, ValueError) as exc:
                    msg = f"invalid value for {env_var}={raw!r}: {exc}"
                    raise ValueError(msg) from exc

        return cls(**values)

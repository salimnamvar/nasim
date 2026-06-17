"""Effective configuration with precedence: built-in defaults < file < env < CLI.

The config file is the same zero-dependency ``KEY=val`` format the bash tool used,
at ``~/.config/nasim/nasim.conf``. Environment variables of the same name override
the file; explicit CLI flags (applied by callers) override everything.

Classes:
    Config: Immutable-ish snapshot of effective tunables and resolved paths.

Functions:
    get_config: Return the process-wide cached Config (loading on first use).
    reload_config: Force a fresh load (used by tests).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Optional

# --- Resolved runtime paths (state survives across shells, like the bash tool) ---
HOME = Path(os.path.expanduser("~"))
STATE_DIR = HOME / ".local" / "share" / "nasim"
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", str(HOME / ".config"))) / "nasim"
CONFIG_FILE = Path(os.environ.get("NASIM_CONFIG_FILE", str(CONFIG_DIR / "nasim.conf")))

ENV_BACKUP_DIR = STATE_DIR / "env-backups"
SESSION_DIR = STATE_DIR / "sessions"
KB_DIR = STATE_DIR / "kb"
GLOBAL_CONTEXT_DIR = STATE_DIR / "contexts"
ACTIVE_URL_FILE = STATE_DIR / "active-url"
DAEMON_PID_FILE = STATE_DIR / "daemon.pid"
FCC_PID_FILE = STATE_DIR / "fcc.pid"
FCC_PORT_FILE = STATE_DIR / "fcc.port"
FCC_ENV_FILE = STATE_DIR / "fcc.env"

# Claude config backup lives under ~/.nasim (per the canonical toggle design).
NASIM_HOME = HOME / ".nasim"
CLAUDE_BACKUP_FILE = NASIM_HOME / "claude-backup.json"

# Keys accepted from the config file (whitelist, matching the bash loader).
_FILE_KEYS = {
    "BLACK_HOST",
    "DEFAULT_MODEL",
    "DEFAULT_LOCAL_PORT",
    "LITELLM_PORT",
    "ACCESS_ORDER",
    "AGENT_ORDER",
    "PROBE_TIMEOUT",
    "PROBE_CONNECT_TIMEOUT",
    "SSH_CONNECT_TIMEOUT",
    "SSH_SERVER_ALIVE_INTERVAL",
    "NASIM_VERSION_OVERRIDE",
    "NASIM_FCC_SRC_DIR",
    "NASIM_GPU_VRAM_GB",
}


@dataclass
class Config:
    """Effective nasim configuration.

    Attributes:
        black_host (str): SSH host alias for the remote Ollama box.
        default_model (str): Default Ollama tag for agent loops.
        default_local_port (int): Base local port for the SSH forward.
        litellm_port (int): Port LiteLLM listens on when used as a proxy.
        access_order (str): Space-separated transport presentation order.
        agent_order (str): Space-separated agent presentation order.
        probe_timeout (int): Curl max-time for endpoint probes (seconds).
        probe_connect_timeout (int): Curl connect-timeout for probes (seconds).
        ssh_connect_timeout (int): SSH ConnectTimeout (seconds).
        ssh_server_alive_interval (int): SSH ServerAliveInterval (seconds).
        gpu_vram_gb (int): GPU VRAM budget for fit checks.
        fcc_src_dir (Optional[str]): free-claude-code checkout for the proxy.
        version_override (Optional[str]): Overrides the reported version (tests).
    """

    black_host: str = field(default="black", metadata={"description": "Remote Ollama SSH host"})
    default_model: str = field(
        default="deepseek-r1:14b", metadata={"description": "Default Ollama tag for agent loops"}
    )
    default_local_port: int = field(default=11435, metadata={"description": "Base local forward port"})
    litellm_port: int = field(default=4000, metadata={"description": "LiteLLM proxy port"})
    access_order: str = field(
        default="ssh-tunnel tailscale litellm", metadata={"description": "Transport menu order"}
    )
    agent_order: str = field(
        default="claude aider opencode terminal", metadata={"description": "Agent menu order"}
    )
    probe_timeout: int = field(default=6, metadata={"description": "Probe max-time seconds"})
    probe_connect_timeout: int = field(default=3, metadata={"description": "Probe connect-timeout seconds"})
    ssh_connect_timeout: int = field(default=8, metadata={"description": "SSH ConnectTimeout seconds"})
    ssh_server_alive_interval: int = field(
        default=20, metadata={"description": "SSH ServerAliveInterval seconds"}
    )
    gpu_vram_gb: int = field(default=11, metadata={"description": "GPU VRAM budget (GB)"})
    fcc_src_dir: Optional[str] = field(default=None, metadata={"description": "free-claude-code source dir"})
    version_override: Optional[str] = field(default=None, metadata={"description": "Version override for tests"})

    @classmethod
    def load(cls) -> "Config":
        """Build a Config applying defaults < file < environment.

        Returns:
            Config: The effective configuration snapshot.
        """
        values: dict = {}
        _read_file(CONFIG_FILE, values)
        _read_env(values)
        cfg = cls(**values)
        return cfg


def _coerce(a_name: str, a_raw: str) -> object:
    """Coerce a raw string to the field's annotated type.

    Args:
        a_name (str): Config attribute name.
        a_raw (str): Raw string value.

    Returns:
        object: Coerced value (int or str).
    """
    int_fields = {
        "default_local_port",
        "litellm_port",
        "probe_timeout",
        "probe_connect_timeout",
        "ssh_connect_timeout",
        "ssh_server_alive_interval",
        "gpu_vram_gb",
    }
    result: object = a_raw
    if a_name in int_fields:
        try:
            result = int(a_raw)
        except ValueError:
            result = getattr(Config(), a_name)
    return result


# Map config-file KEY -> dataclass attribute name.
_KEY_TO_ATTR = {
    "BLACK_HOST": "black_host",
    "DEFAULT_MODEL": "default_model",
    "DEFAULT_LOCAL_PORT": "default_local_port",
    "LITELLM_PORT": "litellm_port",
    "ACCESS_ORDER": "access_order",
    "AGENT_ORDER": "agent_order",
    "PROBE_TIMEOUT": "probe_timeout",
    "PROBE_CONNECT_TIMEOUT": "probe_connect_timeout",
    "SSH_CONNECT_TIMEOUT": "ssh_connect_timeout",
    "SSH_SERVER_ALIVE_INTERVAL": "ssh_server_alive_interval",
    "NASIM_GPU_VRAM_GB": "gpu_vram_gb",
    "NASIM_FCC_SRC_DIR": "fcc_src_dir",
    "NASIM_VERSION_OVERRIDE": "version_override",
}


def _read_file(a_path: Path, a_values: dict) -> None:
    """Parse a KEY=val config file into attribute values (in place).

    Only whitelisted keys are honoured; comments and blanks are ignored. Quotes
    around values are stripped, matching the bash loader behaviour.

    Args:
        a_path (Path): Config file path.
        a_values (dict): Target dict updated with attribute-name keys.
    """
    if not a_path.is_file():
        return
    for line in a_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, raw = stripped.partition("=")
        key = key.strip()
        raw = raw.split("#", 1)[0].strip()  # drop inline comments
        if key not in _FILE_KEYS:
            continue
        raw = raw.strip().strip('"').strip("'")
        attr = _KEY_TO_ATTR.get(key)
        if attr:
            a_values[attr] = _coerce(attr, raw)


def _read_env(a_values: dict) -> None:
    """Apply same-named environment variables over file/default values.

    Args:
        a_values (dict): Target dict updated with attribute-name keys.
    """
    for env_key, attr in _KEY_TO_ATTR.items():
        val = os.environ.get(env_key)
        if val is not None and val != "":
            a_values[attr] = _coerce(attr, val)


_CACHE: Optional[Config] = None


def get_config() -> Config:
    """Return the process-wide Config, loading it once.

    Returns:
        Config: Cached effective configuration.
    """
    global _CACHE
    if _CACHE is None:
        _CACHE = Config.load()
    return _CACHE


def reload_config() -> Config:
    """Discard the cache and reload configuration (used by tests).

    Returns:
        Config: Freshly loaded configuration.
    """
    global _CACHE
    _CACHE = Config.load()
    return _CACHE


def field_names() -> list[str]:
    """Return the list of Config attribute names.

    Returns:
        list[str]: Attribute names in declaration order.
    """
    return [f.name for f in fields(Config)]

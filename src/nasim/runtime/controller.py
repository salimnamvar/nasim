"""Toggle orchestration — start / stop / status / models.

:class:`NasimController` composes the four single-responsibility helpers
(:class:`~nasim.runtime.tunnel.SSHTunnel`, :class:`~nasim.runtime.picker.ModelPicker`,
:class:`~nasim.runtime.settings.ClaudeSettings`, :class:`~nasim.runtime.state.StateStore`)
and the bridge HTTP probes into the four user-facing operations. It holds **no**
transport details of its own beyond two stdlib GETs over the localhost tunnel,
and it reads no settings from the environment — everything comes from the
injected :class:`~nasim.config.Config` and :class:`~nasim.runtime.paths.RuntimePaths`.

Classes:
    NasimController: Orchestrates the client-side toggle.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from nasim.config import Config
from nasim.runtime.paths import RuntimePaths
from nasim.runtime.picker import ModelPicker
from nasim.runtime.settings import ClaudeSettings
from nasim.runtime.state import StateStore
from nasim.runtime.tunnel import SSHTunnel

# Env vars set on start so the CLI talks to the bridge and does not phone home
# while pointed at a local backend (decision AP-10). Names listed once; stop
# unsets exactly these.
_REDIRECT_ENV_NAMES: Tuple[str, ...] = (
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    "DISABLE_TELEMETRY",
    "DISABLE_ERROR_REPORTING",
)


class NasimController:
    """Orchestrate the client-side toggle via the four runtime helpers.

    Attributes:
        _config (Config): Resolved configuration (host, ports, models).
        _paths (RuntimePaths): Resolved runtime file locations.
    """

    def __init__(self, a_config: Config, a_paths: Optional[RuntimePaths] = None) -> None:
        """Compose the helpers from config and runtime paths.

        Args:
            a_config (Config): Resolved Nasim configuration.
            a_paths (Optional[RuntimePaths]): Runtime file layout. Defaults to the
                production layout under the user's home.
        """
        self._config = a_config
        self._paths = a_paths if a_paths is not None else RuntimePaths.default()
        self._logger = logging.getLogger("nasim.controller")
        self._tunnel = SSHTunnel(
            a_local_port=a_config.local_port,
            a_remote_host=a_config.remote_host,
            a_remote_port=a_config.bridge_port,
            a_pid_file=self._paths.pid_file,
            a_connect_timeout=a_config.ssh_connect_timeout,
        )
        self._direct_tunnel = SSHTunnel(
            a_local_port=a_config.direct_local_port,
            a_remote_host=a_config.remote_host,
            a_remote_port=a_config.direct_remote_port,
            a_pid_file=self._paths.direct_pid_file,
            a_connect_timeout=a_config.ssh_connect_timeout,
        )
        self._picker = ModelPicker(self._paths.claude_json)
        self._settings = ClaudeSettings(self._paths.settings_json, self._paths.saved_model_file)
        self._state = StateStore(self._paths.state_file, self._paths.env_file)

    def _get_json(self, a_path: str, a_timeout: float = 4.0) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """GET JSON from the bridge over the localhost tunnel.

        Args:
            a_path (str): Path beginning with ``/`` (e.g. ``/health``).
            a_timeout (float, optional): Socket timeout in seconds. Defaults to 4.

        Returns:
            Tuple[bool, Optional[Dict[str, Any]]]: (success, parsed body or None).
        """
        result: Optional[Dict[str, Any]] = None
        success = False
        url = f"{self._config.base_url}{a_path}"
        try:
            with urllib.request.urlopen(url, timeout=a_timeout) as resp:  # noqa: S310 — localhost tunnel
                result = json.loads(resp.read().decode())
                success = True
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
            self._logger.debug("GET %s failed: %s", url, exc)
            success = False
        return (success, result)

    def _redirect_exports(self) -> Dict[str, str]:
        """Build the environment exports that point the CLI at the bridge."""
        return {
            "ANTHROPIC_BASE_URL": self._config.base_url,
            "ANTHROPIC_AUTH_TOKEN": "nasim",
            "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "128000",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "DISABLE_TELEMETRY": "1",
            "DISABLE_ERROR_REPORTING": "1",
        }

    def start(self) -> Tuple[bool, Dict[str, Any]]:
        """Open the tunnel, verify the bridge, inject models, steer the model.

        Steps: ensure ``~/.nasim`` → start tunnel → health check (abort+rollback
        on failure) → inject picker models → back up and select the recommended
        model → record state → emit env exports for the shim.

        Returns:
            Tuple[bool, Dict[str, Any]]: (success, report). The report carries
            ``base_url``, ``active_model``, ``available_models``,
            ``recommended_model``, and ``warn`` (recommended model not on server),
            or ``error`` on failure.
        """
        result: Dict[str, Any] = {}
        success = False
        self._paths.ensure()

        tunnel_ok, _ = self._tunnel.start(a_raise_on_error=False)
        if not tunnel_ok:
            result = {"error": f"SSH tunnel to {self._config.remote_host} failed"}
        else:
            health_ok, health = self._get_json("/health")
            if not health_ok or not isinstance(health, dict) or health.get("status") != "ok":
                self._tunnel.stop(a_raise_on_error=False)
                result = {"error": "bridge health check failed", "health": health}
            else:
                models_ok, models = self._get_json("/v1/models")
                self._picker.inject(models.get("data", []) if (models_ok and models) else [])
                available = health.get("available_models", [])
                active = health.get("recommended_model") or health.get("default_model") or self._config.default_model
                self._settings.backup_and_set_model(active)
                self._state.set_backend("ollama")
                self._state.write_exports(self._redirect_exports())
                result = {
                    "base_url": self._config.base_url,
                    "active_model": active,
                    "available_models": available,
                    "recommended_model": health.get("recommended_model"),
                    "warn": active not in available if available else False,
                    "vram_warning": health.get("vram_warning"),
                }
                success = True
        return (success, result)

    def stop(self) -> Tuple[bool, Dict[str, Any]]:
        """Full rollback: kill tunnel, eject models, restore model, unset env.

        Idempotent — safe to call when nothing is running (decision T08).

        Returns:
            Tuple[bool, Dict[str, Any]]: (True, empty report).
        """
        self._paths.ensure()
        self._tunnel.stop(a_raise_on_error=False)
        self._picker.eject()
        self._settings.restore_model()
        self._state.set_backend("anthropic")
        self._state.write_unsets(list(_REDIRECT_ENV_NAMES))
        return (True, {})

    def status(self) -> Tuple[bool, Dict[str, Any]]:
        """Report backend, tunnel liveness, bridge health, and active model.

        Returns:
            Tuple[bool, Dict[str, Any]]: (True, status report).
        """
        backend = self._state.get_backend()
        report: Dict[str, Any] = {
            "backend": backend,
            "base_url": self._config.base_url,
            "active_model": self._settings.current_model() or "(default)",
            "tunnel_alive": self._tunnel.is_alive(),
        }
        if backend == "ollama":
            health_ok, health = self._get_json("/health")
            report["bridge"] = health.get("status", "?") if (health_ok and health) else "unreachable"
            if health_ok and health and health.get("vram_warning"):
                report["vram_warning"] = health["vram_warning"]
        return (True, report)

    def models(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """List Ollama models reachable through the bridge, tagged default/fast.

        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (success, entries). Each entry is
            ``{"name": str, "tags": List[str]}``. ``success`` is False only when
            the bridge is unreachable.
        """
        result: List[Dict[str, Any]] = []
        health_ok, health = self._get_json("/health")
        success = bool(health_ok and health and "available_models" in health)
        if success:
            default = health.get("default_model")
            fast = health.get("fast_model")
            recommended = health.get("recommended_model")
            model_sizes = health.get("model_sizes", {})
            for name in health.get("available_models", []):
                tags = []
                if name == default:
                    tags.append("default")
                if name == fast:
                    tags.append("fast")
                if name == recommended:
                    tags.append("recommended")
                size_gb = model_sizes.get(name)
                result.append({"name": name, "tags": tags, "size_gb": size_gb})
        return (success, result)

    # --- Direct native Ollama access (recommended for reliable agentic use) ---

    def _direct_exports(self) -> Dict[str, str]:
        """Env for native Ollama + Anthropic compat (Ollama v0.14+)."""
        base = self._config.direct_base_url
        return {
            "OLLAMA_HOST": base,
            "OLLAMA_API_BASE": base,
            "ANTHROPIC_BASE_URL": base,
            "ANTHROPIC_AUTH_TOKEN": "ollama",
        }

    def direct_start(self) -> Tuple[bool, Dict[str, Any]]:
        """Open direct tunnel to native Ollama (11434), verify reachability, emit env."""
        result: Dict[str, Any] = {}
        self._paths.ensure()
        ok, _ = self._direct_tunnel.start(a_raise_on_error=False)
        if not ok:
            return False, {"error": f"direct tunnel to {self._config.remote_host} failed"}
        # Verify native Ollama
        try:
            import urllib.request, json
            with urllib.request.urlopen(f"{self._config.direct_base_url}/api/tags", timeout=5) as r:
                data = json.loads(r.read())
                models = [m.get("name") for m in data.get("models", [])]
        except Exception as exc:
            self._direct_tunnel.stop(a_raise_on_error=False)
            return False, {"error": f"direct ollama unreachable: {exc}"}
        self._state.set_backend("direct")
        self._state.write_exports(self._direct_exports())
        return True, {"base_url": self._config.direct_base_url, "models": models[:5]}

    def direct_stop(self) -> Tuple[bool, Dict[str, Any]]:
        self._paths.ensure()
        self._direct_tunnel.stop(a_raise_on_error=False)
        self._state.set_backend("none")
        self._state.write_unsets(["OLLAMA_HOST", "OLLAMA_API_BASE", "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN"])
        return True, {}

    def direct_status(self) -> Tuple[bool, Dict[str, Any]]:
        alive = self._direct_tunnel.is_alive()
        backend = self._state.get_backend()
        return True, {
            "backend": backend,
            "direct_tunnel_alive": alive,
            "base_url": self._config.direct_base_url,
        }

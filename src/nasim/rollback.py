"""Environment isolation, backup/restore, and crash-safe cleanup registration.

Because Python launches agents as child processes with a *scoped* environment
(:mod:`nasim.agents`), the parent shell's environment is never modified, so the
classic "ANTHROPIC_* leaked into my shell" problem cannot occur by construction.
What still needs guarding is on-disk state: the Claude ``/model`` picker entries
and the fcc proxy. :class:`EnvGuard` wires the idempotent cleanup
(:meth:`ClaudeSettings.sanitize` + fcc stop) into ``atexit`` and the termination
signals, so a clean exit, Ctrl-C, or a crash all restore Claude Code to defaults.

The env snapshot is retained for parity and the ``nasim env diff`` / ``nasim env
restore`` commands.

Classes:
    EnvGuard: Process-wide guard managing env snapshots and cleanup hooks.

Functions:
    get_guard: Return the shared EnvGuard instance.
"""

from __future__ import annotations

import atexit
import json
import os
import signal
from pathlib import Path
from typing import Optional

from nasim import config
from nasim.util import log

# Environment variables nasim may set for child agents (snapshot scope).
ENV_VARS = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_API_URL",
    "ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL",
    "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW",
    "CLAUDE_CLI_BIN",
    "CLAUDE_WORKSPACE",
    "OPENAI_BASE_URL",
    "OPENAI_API_KEY",
    "OLLAMA_API_BASE",
    "OLLAMA_HOST",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    "AIDER_MODEL",
    "AIDER_API_BASE",
    "DISABLE_TELEMETRY",
    "NASIM_REMOTE_URL",
    "NASIM_MODEL",
    "NASIM_ACTIVE",
]

# Endpoint vars that must be fully *unset* (not left empty) on restore, so plain
# claude only ever talks to official Anthropic afterwards.
_UNSET_ON_RESTORE = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_API_URL",
    "ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL",
    "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW",
    "CLAUDE_CLI_BIN",
    "CLAUDE_WORKSPACE",
]


class EnvGuard:
    """Snapshot/restore env and register crash-safe Claude/fcc cleanup.

    Attributes:
        backup_file (Path): JSON snapshot path for this process.
    """

    def __init__(self, a_backup_file: Optional[Path] = None) -> None:
        """Initialize the guard.

        Args:
            a_backup_file (Optional[Path]): Override snapshot path (tests).
        """
        self.backup_file = a_backup_file or (config.ENV_BACKUP_DIR / f"nasim-env-{os.getpid()}.json")
        self._cleanup_installed = False

    def save_env_state(self) -> None:
        """Snapshot the env vars nasim may touch, once per process.

        A second call is a no-op so re-entry does not overwrite the original
        snapshot.
        """
        if self.backup_file.exists():
            return
        snapshot = {var: os.environ.get(var) for var in ENV_VARS}
        self.backup_file.parent.mkdir(parents=True, exist_ok=True)
        self.backup_file.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    def restore_env_state(self) -> None:
        """Restore env vars from the snapshot and run Claude/fcc cleanup.

        Endpoint vars that were originally unset are deleted (never left empty),
        nasim markers are cleared, the Claude picker is sanitized, and the fcc
        proxy is stopped. The snapshot file is removed afterwards.
        """
        if self.backup_file.exists():
            try:
                snapshot = json.loads(self.backup_file.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                snapshot = {}
            for var, val in snapshot.items():
                if val is None:
                    os.environ.pop(var, None)
                else:
                    os.environ[var] = val
            for var in _UNSET_ON_RESTORE:
                if not os.environ.get(var):
                    os.environ.pop(var, None)
            for var in ("NASIM_ACTIVE", "NASIM_REMOTE_URL", "NASIM_MODEL"):
                os.environ.pop(var, None)
            self.backup_file.unlink(missing_ok=True)

        self.run_cleanup()
        log("env state restored — cloud agents (claude, grok, aider) back to defaults")

    def run_cleanup(self) -> None:
        """Run the idempotent on-disk cleanup: sanitize Claude + stop fcc.

        Safe to call repeatedly and from signal handlers.
        """
        try:
            from nasim.claude_settings import ClaudeSettings

            ClaudeSettings().sanitize()
        except Exception:  # cleanup must never raise during exit
            pass
        try:
            from nasim import fcc

            fcc.stop_proxy()
        except Exception:
            pass

    def install_cleanup(self) -> None:
        """Register atexit + signal handlers so any exit restores Claude defaults.

        Idempotent. Signal handlers chain to the previous handler so default
        termination behaviour is preserved after cleanup.
        """
        if self._cleanup_installed:
            return
        self._cleanup_installed = True

        atexit.register(self.run_cleanup)

        def _handler(a_signum, a_frame):
            self.run_cleanup()
            # Restore default disposition and re-raise so exit code is correct.
            signal.signal(a_signum, signal.SIG_DFL)
            os.kill(os.getpid(), a_signum)

        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            try:
                signal.signal(sig, _handler)
            except (ValueError, OSError):
                pass  # not in main thread / unsupported platform

    def show_env_diff(self) -> None:
        """Print current env values that differ from the snapshot."""
        if not self.backup_file.exists():
            print("No active nasim env backup (nasim not running or no changes made)")
            return
        try:
            snapshot = json.loads(self.backup_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            snapshot = {}
        print("# Current env diffs from nasim backup:")
        for var in ENV_VARS:
            orig = snapshot.get(var)
            curr = os.environ.get(var)
            if orig != curr:
                print(f"  {var}: {orig!r} -> {curr!r}")


_GUARD: Optional[EnvGuard] = None


def get_guard() -> EnvGuard:
    """Return the process-wide :class:`EnvGuard`.

    Returns:
        EnvGuard: The shared guard instance.
    """
    global _GUARD
    if _GUARD is None:
        _GUARD = EnvGuard()
    return _GUARD

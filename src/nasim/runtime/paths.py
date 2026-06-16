"""Runtime path layout — every file the client toggle reads or writes.

All runtime state lives under ``~/.nasim/`` (decision D5); the two Claude Code
files the toggle surgically edits live at their standard locations. Every path
derives from a single ``root`` (the user home), so a test can redirect the whole
layout to a temporary directory by constructing :class:`RuntimePaths` with a
different root — no environment reads, no monkeypatching.

Classes:
    RuntimePaths: Resolved filesystem locations for the client runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    """Filesystem locations for the client toggle, all derived from ``root``.

    Attributes:
        root (Path): Base directory (the user home in production; a temp dir in
            tests). Every other path is derived from it.
    """

    root: Path

    @property
    def nasim_dir(self) -> Path:
        """Directory holding all Nasim runtime state (``~/.nasim``)."""
        return self.root / ".nasim"

    @property
    def state_file(self) -> Path:
        """Backend-state file (``ollama`` vs ``anthropic``)."""
        return self.nasim_dir / "state.json"

    @property
    def pid_file(self) -> Path:
        """SSH tunnel PID file."""
        return self.nasim_dir / "tunnel.pid"

    @property
    def saved_model_file(self) -> Path:
        """Backup of the pre-start ``settings.json`` model selection."""
        return self.nasim_dir / "saved_model.json"

    @property
    def env_file(self) -> Path:
        """Env directives the bash shim sources into the calling shell."""
        return self.nasim_dir / "env.sh"

    @property
    def claude_json(self) -> Path:
        """Claude Code config holding the model-picker cache (``~/.claude.json``)."""
        return self.root / ".claude.json"

    @property
    def settings_json(self) -> Path:
        """Claude Code settings holding the active model (``~/.claude/settings.json``)."""
        return self.root / ".claude" / "settings.json"

    @classmethod
    def default(cls) -> "RuntimePaths":
        """Return the production layout rooted at the user's home directory."""
        return cls(root=Path.home())

    def ensure(self) -> None:
        """Create the ``~/.nasim`` directory if it does not exist."""
        self.nasim_dir.mkdir(parents=True, exist_ok=True)

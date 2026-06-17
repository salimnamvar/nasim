"""Pytest fixtures and path setup for the nasim test suite.

Ensures ``src/`` is importable without installation and provides isolated temp
state so tests never touch the user's real Claude or nasim config.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


@pytest.fixture(autouse=True)
def _dry(monkeypatch):
    """Force dry-run so no test ever opens a real tunnel or execs an agent."""
    monkeypatch.setenv("NASIM_DRY_RUN", "1")


@pytest.fixture
def claude_paths(tmp_path):
    """Return temp settings.json / .claude.json / backup paths for safety tests.

    Args:
        tmp_path: Pytest temp directory.

    Returns:
        dict: ``settings``, ``dot_claude``, ``backup`` Path objects.
    """
    return {
        "settings": tmp_path / ".claude" / "settings.json",
        "dot_claude": tmp_path / ".claude.json",
        "backup": tmp_path / ".nasim" / "claude-backup.json",
    }

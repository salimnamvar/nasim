"""Claude settings surgery — back up and restore the active ``model``.

Claude Code stores the active ``/model`` selection in ``~/.claude/settings.json``
under ``"model"``. On start, the original value is captured **once** (so a
repeated start never overwrites the real backup with an Ollama tag), then the
selection is pointed at a bridge model. On stop, the exact original value is
restored — or the key removed if it was absent — which heals a dangling,
Anthropic-invalid colon-tagged name a user may have picked via ``/model`` while
on Ollama (decision AP-07).

Classes:
    ClaudeSettings: Back up / set / restore the ``model`` field.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class ClaudeSettings:
    """Back up and restore the ``model`` selection in ``settings.json``.

    Attributes:
        _settings_json (Path): Path to ``~/.claude/settings.json``.
        _backup_file (Path): Where the pre-start selection is captured.
    """

    def __init__(self, a_settings_json: Path, a_backup_file: Path) -> None:
        """Initialise the settings editor.

        Args:
            a_settings_json (Path): Path to the Claude Code settings file.
            a_backup_file (Path): Path to persist the pre-start selection.
        """
        self._settings_json = Path(a_settings_json)
        self._backup_file = Path(a_backup_file)
        self._logger = logging.getLogger("nasim.settings")

    def _load(self) -> Dict[str, Any]:
        """Return parsed settings, or ``{}`` if absent or unreadable."""
        result: Dict[str, Any] = {}
        if self._settings_json.is_file():
            try:
                result = json.loads(self._settings_json.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                self._logger.warning("cannot read %s: %s", self._settings_json, exc)
                result = {}
        return result

    def _save(self, a_settings: Dict[str, Any]) -> None:
        """Write settings back, creating the parent directory if needed."""
        self._settings_json.parent.mkdir(parents=True, exist_ok=True)
        self._settings_json.write_text(json.dumps(a_settings, indent=2), encoding="utf-8")

    def current_model(self) -> Optional[str]:
        """Return the currently selected model, or None if unset.

        Returns:
            Optional[str]: The ``model`` value, or None when the key is absent.
        """
        return self._load().get("model")

    def backup_and_set_model(self, a_model: str) -> Tuple[bool, None]:
        """Capture the original selection once, then set ``model`` to ``a_model``.

        The backup records whether the key was present and its value, so restore
        is exact. A second call (repeated start) does not re-capture.

        Args:
            a_model (str): Bridge model to select.

        Returns:
            Tuple[bool, None]: (True, None).
        """
        settings = self._load()
        if not self._backup_file.is_file():
            snapshot = {"present": "model" in settings, "model": settings.get("model")}
            self._backup_file.parent.mkdir(parents=True, exist_ok=True)
            self._backup_file.write_text(json.dumps(snapshot), encoding="utf-8")
        if a_model:
            settings["model"] = a_model
            self._save(settings)
        return (True, None)

    def restore_model(self) -> Tuple[bool, None]:
        """Restore the captured selection and remove the backup. Idempotent.

        If no backup exists (e.g. a second stop), this is a no-op so the user's
        already-restored real selection is left untouched.

        Returns:
            Tuple[bool, None]: (True, None).
        """
        if self._backup_file.is_file():
            try:
                snapshot = json.loads(self._backup_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                snapshot = {}
            settings = self._load()
            if snapshot.get("present"):
                settings["model"] = snapshot.get("model")
            else:
                settings.pop("model", None)
            self._save(settings)
            try:
                self._backup_file.unlink(missing_ok=True)
            except OSError:
                pass
        return (True, None)

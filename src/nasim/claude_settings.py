"""Reversible Claude Code ``/model`` picker injection — the clean-toggle core.

While a nasim session is active we surface the chosen Ollama model inside Claude
Code's ``/model`` picker and (optionally) mark it as the active model. When the
session ends — cleanly, via Ctrl-C, on a crash, or on the next nasim invocation —
every trace is removed and Claude Code returns to its exact prior state.

Two files hold the state that can leak (paths confirmed on disk):
    * ``~/.claude/settings.json`` — top-level ``"model"`` (the active selection).
    * ``~/.claude.json`` — ``additionalModelOptionsCache``: a list of picker
      entries shaped ``{"label","value","description","disabled"}``.

Leakage is prevented by two independent mechanisms:
    1. **Marker-based ejection.** Every injected picker entry is stamped
       ``{"_nasim": true}``. Ejection removes *all* entries carrying the marker —
       never by count or index — so it is idempotent and heals stray entries left
       by a crashed or older session even without a backup.
    2. **Backup/restore of the active model.** The original ``settings.json["model"]``
       is snapshotted once to ``~/.nasim/claude-backup.json`` and restored verbatim
       on ejection (the key is removed if it was originally absent). The backup file
       persists until a successful restore, so a crash cannot strand a dangling
       Ollama model — the next ``sanitize()`` repairs it.

Classes:
    ClaudeSettings: Backup / inject / eject / sanitize over the two config files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from nasim import config
from nasim.util import log

_PICKER_KEY = "additionalModelOptionsCache"
_MARKER = "_nasim"


class ClaudeSettings:
    """Manage reversible Ollama injection into Claude Code's config files.

    Attributes:
        settings_path (Path): Path to ``~/.claude/settings.json``.
        dot_claude_path (Path): Path to ``~/.claude.json``.
        backup_path (Path): Path to the nasim backup of the original active model.

    Example:
        >>> cs = ClaudeSettings()
        >>> cs.inject("deepseek-r1:14b")   # model shows in /model, set active
        >>> cs.eject()                     # original state fully restored
    """

    def __init__(
        self,
        a_settings_path: Optional[Path] = None,
        a_dot_claude_path: Optional[Path] = None,
        a_backup_path: Optional[Path] = None,
    ) -> None:
        """Initialize with overridable paths (tests pass temp paths).

        Args:
            a_settings_path (Optional[Path]): Override for settings.json.
            a_dot_claude_path (Optional[Path]): Override for ~/.claude.json.
            a_backup_path (Optional[Path]): Override for the backup file.
        """
        self.settings_path = a_settings_path or (config.HOME / ".claude" / "settings.json")
        self.dot_claude_path = a_dot_claude_path or (config.HOME / ".claude.json")
        self.backup_path = a_backup_path or config.CLAUDE_BACKUP_FILE

    # --- public API -------------------------------------------------------

    def backup(self) -> None:
        """Snapshot the original active model once, if no backup exists yet.

        The snapshot records whether ``settings.json["model"]`` was present and its
        value, so :meth:`eject` can restore it exactly (including removal when it
        was originally absent). Re-entrant: a second call is a no-op.
        """
        if self.backup_path.exists():
            return
        settings = _read_json(self.settings_path)
        had_model = isinstance(settings, dict) and "model" in settings
        original_model = settings.get("model") if isinstance(settings, dict) else None
        payload = {"had_model": had_model, "original_model": original_model}
        self.backup_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(self.backup_path, payload)

    def inject(self, a_model: str, a_set_active: bool = True) -> None:
        """Add a marked picker entry for ``a_model`` and optionally select it.

        Idempotent: any existing nasim-marked entries are replaced rather than
        duplicated. Always calls :meth:`backup` first so restoration is possible.

        Args:
            a_model (str): The Ollama tag to surface (e.g. ``deepseek-r1:14b``).
            a_set_active (bool): If True, set ``settings.json["model"]`` to the tag.
        """
        self.backup()

        # Picker entries in ~/.claude.json
        data = _read_json(self.dot_claude_path)
        if not isinstance(data, dict):
            data = {}
        entries = data.get(_PICKER_KEY)
        if not isinstance(entries, list):
            entries = []
        entries = [e for e in entries if not _is_marked(e)]
        entries.append(
            {
                "label": f"nasim → {a_model} (black/ollama)",
                "value": a_model,
                "description": "Injected by nasim. Removed automatically when nasim stops.",
                "disabled": False,
                _MARKER: True,
            }
        )
        data[_PICKER_KEY] = entries
        _write_json(self.dot_claude_path, data)

        # Active selection in ~/.claude/settings.json
        if a_set_active:
            settings = _read_json(self.settings_path)
            if not isinstance(settings, dict):
                settings = {}
            settings["model"] = a_model
            _write_json(self.settings_path, settings)

        log(f"claude /model picker now offers '{a_model}' (nasim-marked; auto-removed on stop)")

    def eject(self) -> None:
        """Remove all nasim-marked picker entries and restore the original model.

        Marker-based and idempotent — safe to call any number of times. After a
        successful restore the backup file is deleted so the next session starts
        clean.
        """
        removed = self._strip_marked_entries()
        self._restore_model_from_backup()
        if removed:
            log("removed nasim model entries from claude /model picker")

    def sanitize(self) -> None:
        """Heal stray state even without a backup (called on start and stop).

        Strips any marked picker entries regardless of backup presence, then runs
        :meth:`eject` to also restore the active model when a backup exists. This
        is what guarantees a crashed or older session never leaves Ollama models
        visible in plain Claude Code.
        """
        self.eject()

    def has_nasim_entries(self) -> bool:
        """Return whether any nasim-marked picker entries remain.

        Returns:
            bool: True if ``~/.claude.json`` still holds a marked entry.
        """
        data = _read_json(self.dot_claude_path)
        entries = data.get(_PICKER_KEY) if isinstance(data, dict) else None
        present = isinstance(entries, list) and any(_is_marked(e) for e in entries)
        return present

    # --- internals --------------------------------------------------------

    def _strip_marked_entries(self) -> bool:
        """Drop all marked picker entries from ~/.claude.json.

        Returns:
            bool: True if at least one entry was removed.
        """
        removed = False
        data = _read_json(self.dot_claude_path)
        if isinstance(data, dict) and isinstance(data.get(_PICKER_KEY), list):
            entries = data[_PICKER_KEY]
            kept = [e for e in entries if not _is_marked(e)]
            if len(kept) != len(entries):
                data[_PICKER_KEY] = kept
                _write_json(self.dot_claude_path, data)
                removed = True
        return removed

    def _restore_model_from_backup(self) -> None:
        """Restore ``settings.json["model"]`` from the backup, then drop the backup."""
        if not self.backup_path.exists():
            return
        backup = _read_json(self.backup_path)
        if not isinstance(backup, dict):
            self.backup_path.unlink(missing_ok=True)
            return
        settings = _read_json(self.settings_path)
        if not isinstance(settings, dict):
            settings = {}
        if backup.get("had_model"):
            settings["model"] = backup.get("original_model")
        else:
            settings.pop("model", None)
        _write_json(self.settings_path, settings)
        self.backup_path.unlink(missing_ok=True)


def _is_marked(a_entry: object) -> bool:
    """Return whether a picker entry carries the nasim marker.

    Args:
        a_entry (object): A picker list item.

    Returns:
        bool: True if it is a dict with ``_nasim`` truthy.
    """
    return isinstance(a_entry, dict) and bool(a_entry.get(_MARKER))


def _read_json(a_path: Path) -> object:
    """Read a JSON file, returning an empty dict on any error.

    Args:
        a_path (Path): File to read.

    Returns:
        object: Parsed JSON, or ``{}`` if missing/unreadable/invalid.
    """
    result: object = {}
    try:
        if a_path.exists():
            result = json.loads(a_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        result = {}
    return result


def _write_json(a_path: Path, a_data: object) -> None:
    """Atomically write 2-space JSON (tmp file + os.replace) to avoid corruption.

    Preserves the destination file's existing trailing-newline style so a full
    inject→eject round-trip restores the file byte-for-byte (Claude Code writes
    ``~/.claude.json`` without a trailing newline and ``settings.json`` with one).

    Args:
        a_path (Path): Destination file.
        a_data (object): JSON-serialisable payload.
    """
    a_path.parent.mkdir(parents=True, exist_ok=True)
    trailing = "\n"
    if a_path.exists():
        try:
            trailing = "\n" if a_path.read_text(encoding="utf-8").endswith("\n") else ""
        except OSError:
            trailing = "\n"
    tmp = a_path.with_suffix(a_path.suffix + f".nasim-tmp-{os.getpid()}")
    # ensure_ascii=False matches Claude Code's (Node JSON.stringify) raw-UTF-8 output.
    tmp.write_text(json.dumps(a_data, indent=2, ensure_ascii=False) + trailing, encoding="utf-8")
    os.replace(tmp, a_path)

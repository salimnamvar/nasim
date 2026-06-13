"""Model picker surgery — inject / eject Ollama models in ``~/.claude.json``.

Claude Code caches the ``/model`` picker options in ``~/.claude.json`` under
``additionalModelOptionsCache``. This class adds the bridge's models there so
they appear in the picker, stamping every entry it adds with ``{"_nasim": true}``
so eject is exact and idempotent no matter how many times start runs (decision
AP-08 — never count-based). Only the picker-cache key is touched; the rest of
the file (session history, project data) is read and written back unchanged
(AP-06).

Classes:
    ModelPicker: Marker-based inject/eject of picker-cache entries.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

_CACHE_KEY = "additionalModelOptionsCache"


class ModelPicker:
    """Inject / eject Ollama models in the Claude Code picker cache.

    Attributes:
        _claude_json (Path): Path to ``~/.claude.json``.
        _marker (str): Sentinel field stamped on every injected entry.
    """

    def __init__(self, a_claude_json: Path, a_marker: str = "_nasim") -> None:
        """Initialise the picker editor.

        Args:
            a_claude_json (Path): Path to the Claude Code config JSON.
            a_marker (str, optional): Sentinel key marking injected entries.
                Defaults to ``"_nasim"``.
        """
        self._claude_json = Path(a_claude_json)
        self._marker = a_marker
        self._logger = logging.getLogger("nasim.picker")

    def _load(self) -> Dict[str, Any]:
        """Return the parsed config, or ``{}`` if it is absent or unreadable."""
        result: Dict[str, Any] = {}
        if self._claude_json.is_file():
            try:
                result = json.loads(self._claude_json.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                self._logger.warning("cannot read %s: %s", self._claude_json, exc)
                result = {}
        return result

    def _save(self, a_data: Dict[str, Any]) -> None:
        """Write the config back with stable indentation."""
        self._claude_json.write_text(json.dumps(a_data, indent=2), encoding="utf-8")

    @staticmethod
    def _entry_for(a_model_id: str, a_marker: str) -> Dict[str, Any]:
        """Build one marked picker-cache entry for a model id.

        Args:
            a_model_id (str): Ollama model id, e.g. ``qwen2.5-coder:14b``.
            a_marker (str): Sentinel key to stamp on the entry.

        Returns:
            Dict[str, Any]: The picker-cache entry.
        """
        parts = a_model_id.split(":", 1)
        name = parts[0].replace("-", " ").title()
        tag = parts[1] if len(parts) > 1 else ""
        label = f"{name} {tag}".strip() if tag else name
        return {
            "value": a_model_id,
            "label": label,
            "description": f"{a_model_id} · Local Ollama · nasim",
            a_marker: True,
        }

    def inject(self, a_models: List[Dict[str, Any]]) -> Tuple[bool, int]:
        """Add marked picker entries for each model not already present.

        Idempotent: an id already in the cache (marked or not) is skipped, so a
        second start adds nothing.

        Args:
            a_models (List[Dict[str, Any]]): ``/v1/models`` ``data`` entries,
                each with an ``id``.

        Returns:
            Tuple[bool, int]: (success, number of entries added).
        """
        added = 0
        success = False
        if not self._claude_json.is_file():
            self._logger.warning("%s absent; skipping picker injection", self._claude_json)
        else:
            data = self._load()
            cache = data.get(_CACHE_KEY, [])
            existing = {entry.get("value") for entry in cache}
            for model in a_models:
                model_id = model.get("id", "")
                if model_id and model_id not in existing:
                    cache.append(self._entry_for(model_id, self._marker))
                    existing.add(model_id)
                    added += 1
            data[_CACHE_KEY] = cache
            self._save(data)
            success = True
        return (success, added)

    def eject(self) -> Tuple[bool, int]:
        """Remove every entry stamped with the marker. Idempotent.

        Returns:
            Tuple[bool, int]: (success, number of entries removed).
        """
        removed = 0
        success = False
        if not self._claude_json.is_file():
            success = True  # nothing to clean is still a clean state
        else:
            data = self._load()
            cache = data.get(_CACHE_KEY, [])
            kept = [entry for entry in cache if not entry.get(self._marker)]
            removed = len(cache) - len(kept)
            data[_CACHE_KEY] = kept
            self._save(data)
            success = True
        return (success, removed)

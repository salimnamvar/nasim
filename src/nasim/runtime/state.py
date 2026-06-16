"""Backend state + the env directives the bash shim sources.

Two responsibilities, both file-backed under ``~/.nasim/``:

1. Persist which backend is active (``ollama`` vs ``anthropic``) so ``status``
   and a fresh shell can report it.
2. Emit ``env.sh`` — the ``export`` / ``unset`` lines the thin bash shim sources
   into the *calling* shell. Env mutation must happen in the user's shell, which
   a subprocess cannot do; this file is the hand-off (decision D3).

Classes:
    StateStore: Read/write backend state and the env-directives file.
"""

from __future__ import annotations

import json
import logging
import shlex
from pathlib import Path
from typing import Dict, List, Tuple

_ANTHROPIC = "anthropic"


class StateStore:
    """Persist backend state and emit the shell env-directives file.

    Attributes:
        _state_file (Path): JSON file recording the active backend.
        _env_file (Path): Shell file the bash shim sources then deletes.
    """

    def __init__(self, a_state_file: Path, a_env_file: Path) -> None:
        """Initialise the state store.

        Args:
            a_state_file (Path): Where to persist the backend state.
            a_env_file (Path): Where to write env directives for the shim.
        """
        self._state_file = Path(a_state_file)
        self._env_file = Path(a_env_file)
        self._logger = logging.getLogger("nasim.state")

    def set_backend(self, a_backend: str) -> Tuple[bool, None]:
        """Record the active backend.

        Args:
            a_backend (str): ``"ollama"`` or ``"anthropic"``.

        Returns:
            Tuple[bool, None]: (True, None).
        """
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(json.dumps({"backend": a_backend}), encoding="utf-8")
        return (True, None)

    def get_backend(self) -> str:
        """Return the active backend, defaulting to ``anthropic``.

        Returns:
            str: ``"ollama"`` if a running session was recorded, else ``"anthropic"``.
        """
        result = _ANTHROPIC
        if self._state_file.is_file():
            try:
                result = json.loads(self._state_file.read_text(encoding="utf-8")).get("backend", _ANTHROPIC)
            except (json.JSONDecodeError, OSError):
                result = _ANTHROPIC
        return result

    def write_exports(self, a_exports: Dict[str, str]) -> Tuple[bool, None]:
        """Write ``export NAME='value'`` lines for the shim to source.

        Args:
            a_exports (Dict[str, str]): Environment variables to export.

        Returns:
            Tuple[bool, None]: (True, None).
        """
        lines = [f"export {name}={shlex.quote(value)}" for name, value in a_exports.items()]
        self._env_file.parent.mkdir(parents=True, exist_ok=True)
        self._env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return (True, None)

    def write_unsets(self, a_names: List[str]) -> Tuple[bool, None]:
        """Write ``unset NAME`` lines for the shim to source.

        Args:
            a_names (List[str]): Environment variable names to unset.

        Returns:
            Tuple[bool, None]: (True, None).
        """
        lines = [f"unset {name}" for name in a_names]
        self._env_file.parent.mkdir(parents=True, exist_ok=True)
        self._env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return (True, None)

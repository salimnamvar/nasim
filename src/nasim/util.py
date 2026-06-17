"""Shared utilities: logging, command discovery, dry-run, and subprocess helpers.

These mirror the tiny shell helpers that lived in ``bin/nasim`` (``die``, ``log``,
``have``, ``is_dry``) plus a couple of process helpers used across the package.

Functions:
    log: Print a prefixed progress line to stderr.
    die: Raise NasimError with a prefixed message (fatal setup/transport errors).
    have: True if a command is on PATH.
    is_dry: True under NASIM_DRY_RUN=1 or NASIM_TEST_MODE containing "dry".
    run: Run a command, returning (success, completed_process).
    capture: Run a command and return its stripped stdout (empty on failure).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Optional, Sequence


class NasimError(RuntimeError):
    """Fatal nasim error. Raised by :func:`die`; the CLI maps it to exit code 1."""


def log(a_msg: str) -> None:
    """Print a prefixed progress message to stderr.

    Args:
        a_msg (str): The message to display (without the ``nasim:`` prefix).
    """
    print(f"nasim: {a_msg}", file=sys.stderr, flush=True)


def die(a_msg: str) -> None:
    """Raise a fatal :class:`NasimError` with the standard prefix.

    Args:
        a_msg (str): The error message.

    Raises:
        NasimError: Always.
    """
    raise NasimError(f"nasim: {a_msg}")


def have(a_cmd: str) -> bool:
    """Return whether a command is available on PATH.

    Args:
        a_cmd (str): Command name to look up.

    Returns:
        bool: True if found.
    """
    return shutil.which(a_cmd) is not None


def is_dry() -> bool:
    """Return whether nasim is in dry-run mode.

    True under ``NASIM_DRY_RUN=1`` or when ``NASIM_TEST_MODE`` contains ``dry``.
    Dry-run prevents real ssh, real agent exec, and real proxy starts.

    Returns:
        bool: True if dry-run is active.
    """
    return os.environ.get("NASIM_DRY_RUN") == "1" or "dry" in os.environ.get("NASIM_TEST_MODE", "")


def run(
    a_cmd: Sequence[str],
    a_env: Optional[dict] = None,
    a_check: bool = False,
    a_capture: bool = False,
    a_timeout: Optional[float] = None,
) -> tuple[bool, Optional[subprocess.CompletedProcess]]:
    """Run a command, returning a (success, completed_process) tuple.

    Args:
        a_cmd (Sequence[str]): The argv to execute.
        a_env (Optional[dict]): Full environment to use; defaults to inherited.
        a_check (bool): If True, a non-zero exit counts as failure.
        a_capture (bool): If True, capture stdout/stderr as text.
        a_timeout (Optional[float]): Seconds before the call is abandoned.

    Returns:
        tuple[bool, Optional[subprocess.CompletedProcess]]: success flag and the
            process result (None when the command could not be spawned).
    """
    result: Optional[subprocess.CompletedProcess] = None
    success = False
    try:
        result = subprocess.run(
            list(a_cmd),
            env=a_env,
            capture_output=a_capture,
            text=True,
            timeout=a_timeout,
        )
        success = (result.returncode == 0) if a_check else True
    except (OSError, subprocess.SubprocessError):
        success = False
    return success, result


def capture(a_cmd: Sequence[str], a_timeout: Optional[float] = None) -> str:
    """Run a command and return its stripped stdout, or empty string on failure.

    Args:
        a_cmd (Sequence[str]): The argv to execute.
        a_timeout (Optional[float]): Seconds before the call is abandoned.

    Returns:
        str: Stripped stdout, or "" if the command failed.
    """
    out = ""
    success, result = run(a_cmd, a_check=True, a_capture=True, a_timeout=a_timeout)
    if success and result is not None and result.stdout:
        out = result.stdout.strip()
    return out

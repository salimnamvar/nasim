"""SSH tunnel control — the one access path to the bridge.

Opens, probes, and kills the ``ssh -L`` local forward that connects the client
to the bridge bound on ``127.0.0.1`` on the server. Owns its PID file. The
forward is launched detached (its own session) so it survives the short-lived
``python -m nasim`` process, while its exact PID is captured directly from the
spawned process rather than scraped with ``pgrep``.

Classes:
    SSHTunnel: Lifecycle of the ``-L`` forward and its PID file.
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple


class SSHTunnel:
    """Open / kill / probe the SSH ``-L`` forward; owns the PID file.

    Attributes:
        _local_port (int): Local end of the forward.
        _remote_host (str): SSH host alias / hostname of the server.
        _remote_port (int): Bridge port on the server's loopback.
        _pid_file (Path): File the forwarder PID is written to.
        _connect_timeout (int): SSH ``ConnectTimeout`` in seconds.
    """

    def __init__(
        self,
        a_local_port: int,
        a_remote_host: str,
        a_remote_port: int,
        a_pid_file: Path,
        a_connect_timeout: int = 8,
    ) -> None:
        """Initialise the tunnel controller.

        Args:
            a_local_port (int): Local end of the ``-L`` forward.
            a_remote_host (str): SSH host alias / hostname of the server.
            a_remote_port (int): Bridge port on the server's loopback.
            a_pid_file (Path): Where to persist the forwarder PID.
            a_connect_timeout (int, optional): SSH connect timeout. Defaults to 8.
        """
        self._local_port = a_local_port
        self._remote_host = a_remote_host
        self._remote_port = a_remote_port
        self._pid_file = Path(a_pid_file)
        self._connect_timeout = a_connect_timeout
        self._logger = logging.getLogger("nasim.tunnel")

    @property
    def _forward(self) -> str:
        """The ``local:127.0.0.1:remote`` forward specification."""
        return f"{self._local_port}:127.0.0.1:{self._remote_port}"

    def _read_pid(self) -> Optional[int]:
        """Return the PID recorded in the PID file, or None if absent/invalid."""
        result: Optional[int] = None
        if self._pid_file.is_file():
            try:
                result = int(self._pid_file.read_text(encoding="utf-8").strip())
            except (ValueError, OSError):
                result = None
        return result

    def is_alive(self) -> bool:
        """Report whether the recorded tunnel process is currently running.

        Returns:
            bool: True if a PID is recorded and that process exists.
        """
        result = False
        pid = self._read_pid()
        if pid is not None:
            try:
                os.kill(pid, 0)
                result = True
            except OSError:
                result = False
        return result

    def start(self, a_raise_on_error: bool = True) -> Tuple[bool, Optional[int]]:
        """Open the forward, replacing any existing one. Persist the PID.

        Args:
            a_raise_on_error (bool, optional): Raise on launch failure instead of
                returning ``(False, None)``. Defaults to True.

        Returns:
            Tuple[bool, Optional[int]]: (success, forwarder PID).

        Raises:
            RuntimeError: If ``a_raise_on_error`` and the tunnel fails to launch.
        """
        self.stop(a_raise_on_error=False)
        success = False
        pid: Optional[int] = None
        cmd = [
            "ssh",
            "-N",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={self._connect_timeout}",
            "-L",
            self._forward,
            self._remote_host,
        ]
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            time.sleep(0.5)  # let the forward bind / fail fast on auth error
            if proc.poll() is not None:
                msg = (
                    f"SSH tunnel to {self._remote_host} exited immediately "
                    f"(code {proc.returncode}); check that 'ssh {self._remote_host}' "
                    "works without a passphrase"
                )
                self._logger.error(msg)
                if a_raise_on_error:
                    raise RuntimeError(msg)
            else:
                pid = proc.pid
                self._pid_file.parent.mkdir(parents=True, exist_ok=True)
                self._pid_file.write_text(str(pid), encoding="utf-8")
                success = True
        except OSError as exc:
            msg = f"failed to launch SSH tunnel to {self._remote_host}: {exc}"
            self._logger.error(msg)
            if a_raise_on_error:
                raise RuntimeError(msg) from exc

        return (success, pid)

    def stop(self, a_raise_on_error: bool = True) -> Tuple[bool, None]:
        """Kill the recorded forward (and any stray match) and clear the PID file.

        Idempotent: safe to call when no tunnel is running.

        Args:
            a_raise_on_error (bool, optional): Unused; present for signature
                symmetry with :meth:`start`. Defaults to True.

        Returns:
            Tuple[bool, None]: (True, None) — stop always succeeds.
        """
        pid = self._read_pid()
        if pid is not None:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass  # already gone
        # Fallback: reap any forwarder bound to this exact local:remote pair.
        try:
            subprocess.run(
                ["pkill", "-f", f"ssh.*-L {self._forward} "],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except OSError:
            pass
        try:
            self._pid_file.unlink(missing_ok=True)
        except OSError:
            pass

        return (True, None)

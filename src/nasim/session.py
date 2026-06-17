"""Session history + resume.

Records each agent launch (agent, model, url, project, branch, cwd, timing) as a
JSON file under ``~/.local/share/nasim/sessions/`` so sessions can be listed and
resumed. Uses the standard library ``json`` instead of ``jq``.

Functions:
    session_start: Record a new session, returning its id.
    session_end: Close a session and compute its duration.
    session_list: Print recent sessions.
    session_current: Print the active session.
    session_resume: Reconnect tunnel and relaunch a prior session.
"""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Optional

from nasim import config
from nasim.util import capture, log

CURRENT_FILE = config.STATE_DIR / "current-session"


def _ensure_dir() -> None:
    """Ensure the session directory exists."""
    config.SESSION_DIR.mkdir(parents=True, exist_ok=True)


def session_start(a_agent: str, a_model: str, a_url: str) -> str:
    """Record a session start and mark it current.

    Args:
        a_agent (str): Agent key.
        a_model (str): Model tag.
        a_url (str): Transport URL.

    Returns:
        str: The new session id.
    """
    _ensure_dir()
    session_id = f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
    project = capture(["git", "remote", "get-url", "origin"]) or os.path.basename(os.getcwd())
    branch = capture(["git", "branch", "--show-current"]) or "none"
    record = {
        "id": session_id,
        "start": datetime.datetime.now().astimezone().isoformat(),
        "agent": a_agent,
        "model": a_model,
        "url": a_url,
        "project": project,
        "branch": branch,
        "cwd": os.getcwd(),
        "end": None,
        "duration_sec": None,
    }
    (config.SESSION_DIR / f"{session_id}.json").write_text(json.dumps(record), encoding="utf-8")
    CURRENT_FILE.write_text(session_id, encoding="utf-8")
    return session_id


def session_end(a_session_id: Optional[str] = None) -> None:
    """Close a session and compute its duration.

    Args:
        a_session_id (Optional[str]): Session to close; defaults to current.
    """
    session_id = a_session_id or (CURRENT_FILE.read_text().strip() if CURRENT_FILE.exists() else "")
    if not session_id:
        return
    path = config.SESSION_DIR / f"{session_id}.json"
    if not path.is_file():
        return
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return
    end = datetime.datetime.now().astimezone()
    duration = 0
    try:
        start = datetime.datetime.fromisoformat(record["start"])
        duration = int((end - start).total_seconds())
    except (KeyError, ValueError):
        duration = 0
    record["end"] = end.isoformat()
    record["duration_sec"] = duration
    path.write_text(json.dumps(record), encoding="utf-8")
    CURRENT_FILE.unlink(missing_ok=True)


def _load(a_path: Path) -> dict:
    """Load a session JSON file, returning {} on error.

    Args:
        a_path (Path): Session file.

    Returns:
        dict: Parsed record or empty dict.
    """
    result: dict = {}
    try:
        result = json.loads(a_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        result = {}
    return result


def session_list(a_limit: int = 10) -> None:
    """Print recent sessions, newest first.

    Args:
        a_limit (int): Maximum rows to display.
    """
    _ensure_dir()
    files = sorted(config.SESSION_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:a_limit]
    if not files:
        print("No sessions recorded yet.")
        return
    print(f"Recent nasim sessions (last {a_limit}):\n")
    print(f"{'ID':<20} {'Agent':<10} {'Model':<20} {'Project':<15} {'Duration':<8} Status")
    print("=" * 80)
    for f in files:
        rec = _load(f)
        dur = rec.get("duration_sec")
        if dur in (None, "null"):
            status, dur_s = "running", "-"
        else:
            status, dur_s = "ended", f"{dur}s"
        print(
            f"{rec.get('id', f.stem):<20} {str(rec.get('agent', '?')):<10} "
            f"{str(rec.get('model', '?'))[:20]:<20} {str(rec.get('project', '?'))[:15]:<15} "
            f"{dur_s:<8} {status}"
        )


def session_current() -> None:
    """Print the active session, if any."""
    if not CURRENT_FILE.exists():
        print("No active session.")
        return
    session_id = CURRENT_FILE.read_text().strip()
    path = config.SESSION_DIR / f"{session_id}.json"
    if path.is_file():
        print(f"Active session: {session_id}")
        print(json.dumps(_load(path), indent=2))
    else:
        print(f"Session {session_id} not found (stale current-session marker)")


def session_resume(a_session_id: str) -> int:
    """Reconnect the tunnel and relaunch a previous session.

    Args:
        a_session_id (str): Session id to resume.

    Returns:
        int: The relaunched agent's exit code (1 if not found).
    """
    path = config.SESSION_DIR / f"{a_session_id}.json"
    if not path.is_file():
        log(f"session '{a_session_id}' not found")
        return 1
    rec = _load(path)
    cfg = config.get_config()
    agent = rec.get("agent", "terminal")
    model = rec.get("model", cfg.default_model)
    cwd = rec.get("cwd", "")
    log(f"resuming session {a_session_id}")
    log(f"  agent: {agent}, model: {model}, project: {rec.get('project', '')}")
    if cwd and os.path.isdir(cwd):
        os.chdir(cwd)

    from nasim import daemon
    from nasim.agents import launch_agent

    if not daemon.is_running():
        log("restarting tunnel...")
        daemon.start()
    url = daemon.url()
    log(f"re-launching {agent}...")
    return launch_agent(agent, url, model)

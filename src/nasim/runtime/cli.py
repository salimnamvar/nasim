"""CLI front door for ``python -m nasim`` — parse, orchestrate, print.

This module owns argument parsing and human-readable output only. It calls
:class:`~nasim.runtime.controller.NasimController` and prints what it returns; it
never exports environment variables itself — that is the bash shim's job, fed by
the ``env.sh`` the controller writes (decision D3). The exit code reflects
success so the shim can react.

Functions:
    main: Entry point; returns a process exit code.
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional

from nasim.config import Config
from nasim.runtime.controller import NasimController


def _print_start(a_report: Dict[str, Any]) -> None:
    """Print the outcome of a successful start."""
    print("nasim STARTED — Claude Code → Ollama via bridge")
    print(f"  Bridge  : {a_report['base_url']}")
    available = a_report.get("available_models") or []
    print(f"  Models  : {', '.join(available) if available else '(none reported)'}")
    print(f"  Active  : {a_report.get('active_model', '(bridge default)')}")
    if a_report.get("warn"):
        recommended = a_report.get("recommended_model")
        print(f"  WARNING : recommended model '{recommended}' is not on the server;")
        print(f"            agentic reliability will suffer — pull it: ollama pull {recommended}")
    if a_report.get("vram_warning"):
        print(f"  VRAM    : !! {a_report['vram_warning']}")
        print(f"            Run 'nasim models' to see sizes; use /model to pick a GPU-resident one")
    print("  Tip     : launch 'claude' in THIS shell; use /model to switch")


def _print_status(a_report: Dict[str, Any]) -> None:
    """Print the status report."""
    print(f"Backend : {a_report['backend']}")
    print(f"Base URL: {a_report['base_url']}")
    print(f"Model   : {a_report['active_model']}")
    if a_report["backend"] == "ollama":
        print(f"Tunnel  : {'yes' if a_report['tunnel_alive'] else 'no'}")
        print(f"Bridge  : {a_report.get('bridge', '?')}")
        if a_report.get("vram_warning"):
            print(f"VRAM    : !! {a_report['vram_warning']}")
            print(f"          Use 'nasim models' to see sizes; pick a GPU-resident model")


def _print_models(a_entries: List[Dict[str, Any]]) -> None:
    """Print the model inventory with sizes and default/fast/recommended tags."""
    print("Ollama models (via bridge):")
    for entry in a_entries:
        tags_str = f"  [{', '.join(entry['tags'])}]" if entry["tags"] else ""
        size_str = f"  {entry['size_gb']}GB" if entry.get("size_gb") is not None else ""
        print(f"  {entry['name']}{size_str}{tags_str}")


def main(a_argv: Optional[List[str]] = None) -> int:
    """Parse arguments, run the requested command, print, and return a code.

    Args:
        a_argv (Optional[List[str]]): Argument vector (defaults to ``sys.argv``).

    Returns:
        int: Process exit code — 0 on success, non-zero on failure.
    """
    parser = argparse.ArgumentParser(
        prog="nasim", description="Toggle Claude Code between Anthropic cloud and local Ollama."
    )
    parser.add_argument("command", choices=["start", "stop", "status", "models"], help="action to perform")
    args = parser.parse_args(a_argv)

    controller = NasimController(Config.load())
    code = 0

    if args.command == "start":
        ok, report = controller.start()
        if ok:
            _print_start(report)
        else:
            print(f"nasim start FAILED — {report.get('error', 'unknown error')}")
            code = 1
    elif args.command == "stop":
        controller.stop()
        print("nasim STOPPED — Claude Code → Anthropic cloud (defaults restored)")
    elif args.command == "status":
        _, report = controller.status()
        _print_status(report)
    else:  # models
        ok, entries = controller.models()
        if ok:
            _print_models(entries)
        else:
            print("Bridge not reachable — run: nasim start")
            code = 1

    return code

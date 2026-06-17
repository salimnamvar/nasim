"""Command dispatch + help (the thin controller layer).

Parses ``argv`` and routes to the service/feature modules. Crash-safe cleanup is
installed up front so any exit restores Claude Code defaults.

Functions:
    main: Dispatch a parsed argv list, returning an exit code.
    main_console: Console-script wrapper (reads ``sys.argv``).
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional, Sequence

from nasim import config, daemon, kb, probe, select, session, vram
from nasim.rollback import get_guard
from nasim.util import NasimError, log


def _version() -> str:
    """Return the effective version (override-aware).

    Returns:
        str: Version string.
    """
    from nasim import __version__

    return config.get_config().version_override or __version__


_HELP = """nasim {ver} — remote Ollama on black + frontier agents on laptop.

PRIMARY
  nasim start [ssh|tailscale|litellm]   Start persistent tunnel daemon
  nasim stop                            Stop daemon + RESTORE env/Claude defaults
  nasim status                          Daemon health, models, context
  nasim code [options]                  Smart launch (auto-detect agent)
  nasim select                          Interactive menu (access + agent + model)
  nasim launch --access X --agent Y --model Z

CONTEXT & KNOWLEDGE
  nasim context --refresh|--edit|--show
  nasim kb index <path> [name] | query <name> "q" | list | rm <name>

MODELS
  nasim models [--fit]                  List models on black (via SSH)
  nasim vram fit|recommend|check <model>
  nasim doctor [--url URL]              Health check + model list + ps

SESSIONS
  nasim sessions | session current | session resume <id>

CONFIG
  nasim config show|edit|path
  nasim tunnel ssh|persistent|install-systemd|status
  nasim env diff|restore

LEGACY
  nasim claude|aider|opencode|terminal [args...]

ENVIRONMENT SAFETY
  nasim backs up your ANTHROPIC_*/OPENAI_*/OLLAMA_* and the Claude /model picker on
  start, and RESTORES them on stop/exit/crash. Plain `claude` shows only Anthropic
  models afterwards. Verify with: nasim env diff
"""


def _config_show() -> None:
    """Print the effective configuration."""
    cfg = config.get_config()
    print(f"# Effective nasim configuration (precedence: env > {config.CONFIG_FILE} > defaults)")
    print(f"BLACK_HOST={cfg.black_host}")
    print(f"DEFAULT_MODEL={cfg.default_model}")
    print(f"DEFAULT_LOCAL_PORT={cfg.default_local_port}")
    print(f"LITELLM_PORT={cfg.litellm_port}")
    print(f"ACCESS_ORDER={cfg.access_order}")
    print(f"AGENT_ORDER={cfg.agent_order}")
    print(f"CONFIG_FILE={config.CONFIG_FILE}")


def _config_edit() -> None:
    """Create a default config if missing and open it in the editor."""
    config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not config.CONFIG_FILE.is_file():
        config.CONFIG_FILE.write_text(
            "# nasim user configuration (KEY=val). Env vars and CLI flags override this file.\n"
            "BLACK_HOST=black\n"
            "DEFAULT_MODEL=deepseek-r1:14b\n"
            "# DEFAULT_LOCAL_PORT=11435\n"
            "# LITELLM_PORT=4000\n"
            '# ACCESS_ORDER="ssh-tunnel tailscale litellm"\n'
            '# AGENT_ORDER="claude aider opencode terminal"\n'
            "# NASIM_FCC_SRC_DIR=$HOME/prj/salim/nasim/code/free-claude-code\n"
            "# NASIM_GPU_VRAM_GB=11\n",
            encoding="utf-8",
        )
        print(f"Created default config at {config.CONFIG_FILE}")
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "nano"
    subprocess.run([editor, str(config.CONFIG_FILE)])


def _cmd_context(a_args: list) -> int:
    """Handle ``nasim context`` subcommands.

    Args:
        a_args (list): Args after ``context``.

    Returns:
        int: Exit code.
    """
    from nasim import context

    sub = a_args[0] if a_args else "--show"
    if sub in ("--refresh", "refresh", "generate"):
        context.refresh()
    elif sub in ("--edit", "edit"):
        context.global_edit()
    elif sub in ("--show", "show"):
        cf = context.context_file()
        if cf:
            print(f"=== Context: {cf} ===")
            print(context.read())
        else:
            print("No active context. Run 'nasim context --refresh' in a project directory.")
    else:
        print("nasim context {--refresh|--edit|--show}")
    return 0


def _cmd_kb(a_args: list) -> int:
    """Handle ``nasim kb`` subcommands.

    Args:
        a_args (list): Args after ``kb``.

    Returns:
        int: Exit code.
    """
    sub = a_args[0] if a_args else "list"
    rest = a_args[1:]
    rc = 0
    if sub == "index":
        path = rest[0] if rest else "."
        name = rest[1] if len(rest) > 1 else None
        rc = kb.index(path, name)
    elif sub == "query":
        if len(rest) < 2:
            print("Usage: nasim kb query <name> 'question'")
            rc = 1
        else:
            print(kb.query(rest[0], rest[1]))
    elif sub == "list":
        kb.kb_list()
    elif sub in ("rm", "remove", "delete"):
        rc = kb.rm(rest[0]) if rest else 1
    else:
        print("nasim kb {index <path> [name] | query <name> 'q' | list | rm <name>}")
    return rc


def _cmd_vram(a_args: list) -> int:
    """Handle ``nasim vram`` subcommands.

    Args:
        a_args (list): Args after ``vram``.

    Returns:
        int: Exit code.
    """
    sub = a_args[0] if a_args else "fit"
    rest = a_args[1:]
    if sub == "fit":
        vram.fit(int(rest[0]) if rest else None)
    elif sub == "recommend":
        vram.recommend(rest[0] if rest else "coding")
    elif sub == "check":
        vram.check(rest[0] if rest else "")
    else:
        print("nasim vram {fit [gb] | recommend [workload] | check <model>}")
    return 0


def _cmd_session(a_args: list) -> int:
    """Handle ``nasim session(s)`` subcommands.

    Args:
        a_args (list): Args after ``session``.

    Returns:
        int: Exit code.
    """
    sub = a_args[0] if a_args else "list"
    rest = a_args[1:]
    rc = 0
    if sub in ("list", "ls"):
        session.session_list(int(rest[0]) if rest else 10)
    elif sub == "current":
        session.session_current()
    elif sub == "resume":
        rc = session.session_resume(rest[0]) if rest else 1
    else:
        print("nasim session {list | current | resume <id>}")
    return rc


def _cmd_env(a_args: list) -> int:
    """Handle ``nasim env`` subcommands.

    Args:
        a_args (list): Args after ``env``.

    Returns:
        int: Exit code.
    """
    sub = a_args[0] if a_args else "diff"
    if sub == "diff":
        get_guard().show_env_diff()
    elif sub == "restore":
        get_guard().restore_env_state()
        log("env manually restored")
    else:
        print("nasim env {diff | restore}")
    return 0


def _cmd_tunnel(a_args: list) -> int:
    """Handle ``nasim tunnel`` subcommands.

    Args:
        a_args (list): Args after ``tunnel``.

    Returns:
        int: Exit code.
    """
    cfg = config.get_config()
    sub = a_args[0] if a_args else "help"
    if sub in ("ssh", "start", "adhoc"):
        from nasim.transport import setup_ssh_tunnel

        setup_ssh_tunnel()
        print("Ad-hoc tunnel up. It stays until killed (pkill or 'nasim tunnel status').")
    elif sub in ("persistent", "autossh"):
        print("One-liner for background autossh (reconnects):")
        print(
            f"autossh -M 0 -f -N -o 'ServerAliveInterval 30' "
            f"-L {cfg.default_local_port}:localhost:11434 {cfg.black_host}"
        )
        print(f"Kill: pkill -f 'ssh.*{cfg.default_local_port}.*{cfg.black_host}'")
    elif sub == "install-systemd":
        unit_dir = config.HOME / ".config" / "systemd" / "user"
        unit_dir.mkdir(parents=True, exist_ok=True)
        unit = unit_dir / "nasim-black-tunnel.service"
        unit.write_text(
            "[Unit]\nDescription=Nasim persistent SSH tunnel to black Ollama (11434)\nAfter=network.target\n\n"
            "[Service]\nExecStart=/usr/bin/autossh -M 0 -N -o ServerAliveInterval=30 -o ServerAliveCountMax=3 "
            f"-L {cfg.default_local_port}:localhost:11434 {cfg.black_host}\nRestart=always\nRestartSec=5\n\n"
            "[Install]\nWantedBy=default.target\n",
            encoding="utf-8",
        )
        print(f"Wrote {unit}")
        print("systemctl --user daemon-reload && systemctl --user enable --now nasim-black-tunnel")
    elif sub == "status":
        subprocess.run(["bash", "-c", f"pgrep -af 'ssh.*{cfg.black_host}' | grep -E 'L .*1143' || echo 'no obvious nasim ssh tunnel'"])
    else:
        print("nasim tunnel {ssh|persistent|install-systemd|status}")
    return 0


def _legacy_opencode_or_terminal(a_cmd: str, a_args: list) -> int:
    """Resolve a URL and launch opencode/terminal in legacy mode.

    Args:
        a_cmd (str): ``opencode``/``open`` or ``terminal``/``shell``.
        a_args (list): Extra args.

    Returns:
        int: Exit code.
    """
    from nasim.agents import launch_opencode, launch_terminal
    from nasim.transport import setup_ssh_tunnel

    cfg = config.get_config()
    get_guard().install_cleanup()
    url = os.environ.get("NASIM_REMOTE_URL", "")
    model = os.environ.get("NASIM_MODEL", cfg.default_model)
    if not url and daemon.is_running():
        url = daemon.url()
    if not url:
        url = setup_ssh_tunnel()
    if a_cmd in ("opencode", "open"):
        return launch_opencode(url, model, a_args)
    return launch_terminal(url, model)


def main(a_argv: Optional[Sequence[str]] = None) -> int:
    """Dispatch the CLI.

    Args:
        a_argv (Optional[Sequence[str]]): Args without the program name.

    Returns:
        int: Process exit code.
    """
    argv = list(a_argv if a_argv is not None else sys.argv[1:])
    cmd = argv[0] if argv else "help"
    rest = argv[1:]

    # Crash-safe Claude/fcc cleanup for every invocation.
    get_guard().install_cleanup()

    rc = 0
    try:
        if cmd == "start":
            rc = daemon.start(rest[0] if rest else "ssh-tunnel")
        elif cmd == "stop":
            rc = daemon.stop()
        elif cmd == "status":
            rc = daemon.status()
        elif cmd == "code":
            from nasim.code import cmd_code

            rc = cmd_code(rest)
        elif cmd == "select":
            rc = select.do_select(rest)
        elif cmd == "launch":
            rc = _dispatch_launch(rest)
        elif cmd == "context":
            rc = _cmd_context(rest)
        elif cmd == "kb":
            rc = _cmd_kb(rest)
        elif cmd in ("models", "list-models"):
            if rest and rest[0] == "--fit":
                vram.fit()
            else:
                url = rest[1] if len(rest) >= 2 and rest[0] == "--url" else None
                probe.nasim_models(url)
        elif cmd == "vram":
            rc = _cmd_vram(rest)
        elif cmd in ("doctor", "probe"):
            url = rest[1] if len(rest) >= 2 and rest[0] == "--url" else None
            probe.nasim_doctor(url)
        elif cmd in ("sessions", "session"):
            rc = _cmd_session(rest)
        elif cmd == "config":
            sub = rest[0] if rest else "show"
            if sub == "edit":
                _config_edit()
            elif sub == "path":
                print(config.CONFIG_FILE)
            else:
                _config_show()
        elif cmd == "tunnel":
            rc = _cmd_tunnel(rest)
        elif cmd == "env":
            rc = _cmd_env(rest)
        elif cmd == "claude":
            from nasim.orchestration import legacy_claude

            rc = legacy_claude(rest)
        elif cmd == "aider":
            from nasim.orchestration import legacy_aider

            rc = legacy_aider(rest)
        elif cmd in ("opencode", "open", "terminal", "shell"):
            rc = _legacy_opencode_or_terminal(cmd, rest)
        elif cmd == "version":
            print(_version())
        else:
            print(_HELP.format(ver=_version()))
    except NasimError as exc:
        print(str(exc), file=sys.stderr)
        rc = 1
    except KeyboardInterrupt:
        rc = 130
    return rc


def _dispatch_launch(a_rest: list) -> int:
    """Parse ``nasim launch`` flags and call choose_and_launch.

    Args:
        a_rest (list): Args after ``launch``.

    Returns:
        int: Exit code.
    """
    from nasim.orchestration import choose_and_launch

    cfg = config.get_config()
    access, agent, model = "ssh-tunnel", "claude", cfg.default_model
    extra: list[str] = []
    i = 0
    while i < len(a_rest):
        arg = a_rest[i]
        if arg == "--access":
            access, i = a_rest[i + 1], i + 2
        elif arg == "--agent":
            agent, i = a_rest[i + 1], i + 2
        elif arg == "--model":
            model, i = a_rest[i + 1], i + 2
        elif arg == "--dry-run":
            os.environ["NASIM_DRY_RUN"] = "1"
            i += 1
        else:
            extra = a_rest[i:]
            break
    return choose_and_launch(access, agent, model, extra)


def main_console() -> int:
    """Console-script entry point.

    Returns:
        int: Exit code.
    """
    return main(sys.argv[1:])

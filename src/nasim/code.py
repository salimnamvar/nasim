"""Unified ``nasim code`` entry point — smart launch with context injection.

Auto-starts the daemon, detects the best agent, injects project context (and an
optional KB), then launches with the clean-toggle guarantees of the agent layer.

Functions:
    cmd_code: Parse flags and dispatch to interactive or one-shot launch.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional, Sequence

from nasim import config, context, daemon, kb, session, vram
from nasim.agents import detect_agent, launch_agent, one_shot_claude
from nasim.rollback import get_guard
from nasim.util import have, log

_HELP = """Usage: nasim code [options] [agent-args...]

Smart launch: auto-detects best agent, reuses daemon tunnel, injects context.

Options:
  --agent <name>     Force agent: claude, grok, aider, opencode, terminal
  --model <tag>      Override model (default from config)
  --kb <name>        Inject knowledge base into context
  --context <path>   Use specific context file (default: .nasim/context.md)
  --no-context       Skip project context injection
  --one-shot "..."   Run single prompt and exit (non-interactive)
  --help             Show this help

After exit: all env vars restored, cloud agents work normally.
"""


def cmd_code(a_args: Sequence[str]) -> int:
    """Run the ``nasim code`` command.

    Args:
        a_args (Sequence[str]): Raw CLI args after ``code``.

    Returns:
        int: Exit code.
    """
    cfg = config.get_config()
    agent = ""
    model = cfg.default_model
    kb_name = ""
    context_path = ""
    one_shot = ""
    no_context = False
    extra: list[str] = []

    args = list(a_args)
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--agent":
            agent, i = args[i + 1], i + 2
        elif arg == "--model":
            model, i = args[i + 1], i + 2
        elif arg == "--kb":
            kb_name, i = args[i + 1], i + 2
        elif arg == "--context":
            context_path, i = args[i + 1], i + 2
        elif arg == "--no-context":
            no_context, i = True, i + 1
        elif arg == "--one-shot":
            one_shot, i = args[i + 1], i + 2
        elif arg == "--help":
            print(_HELP)
            return 0
        else:
            extra.append(arg)
            i += 1

    daemon.ensure_running()
    url = daemon.url()

    if not agent:
        agent = detect_agent()
        log(f"auto-detected agent: {agent}")

    if agent in ("claude", "code") and ("qwen2.5" in model or "qwen2" in model):
        log(f"Note: {model} is not recommended for claude-code tool use. Switching to deepseek-r1:14b.")
        model = "deepseek-r1:14b"

    if not vram.check(model):
        try:
            answer = input("Model may not fit GPU. Continue anyway? (y/N): ")
        except EOFError:
            answer = ""
        if not answer.lower().startswith("y"):
            return 1

    get_guard().save_env_state()
    get_guard().install_cleanup()

    context_content = ""
    if not no_context:
        if context_path:
            if Path(context_path).is_file():
                context_content = Path(context_path).read_text(encoding="utf-8")
                log(f"using context: {context_path}")
            else:
                log(f"context file not found: {context_path}")
        elif context.is_active():
            context_content = context.read()
            log(f"project context active ({context.context_file()})")

        if kb_name:
            log(f"injecting KB: {kb_name}")
            results = kb.query(kb_name, one_shot)
            if results:
                context_content += f"\n\n## Relevant Knowledge Base Chunks ({kb_name})\n{results}"

    if one_shot:
        return _one_shot(agent, url, model, context_content, one_shot, extra)
    return _interactive(agent, url, model, context_content, extra)


def _interactive(a_agent: str, a_url: str, a_model: str, a_context: str, a_extra: Sequence[str]) -> int:
    """Launch an agent interactively with context injected per-agent.

    Args:
        a_agent (str): Agent key.
        a_url (str): Transport URL.
        a_model (str): Model tag.
        a_context (str): Context text to inject (may be empty).
        a_extra (Sequence[str]): Extra args.

    Returns:
        int: The agent's exit code.
    """
    session_id = session.session_start(a_agent, a_model, a_url)
    claude_md = Path("./CLAUDE.md")
    backup: Optional[Path] = None
    rc = 0
    try:
        if a_context:
            if a_agent in ("claude", "code"):
                if claude_md.is_file():
                    backup = Path(f"/tmp/nasim-claude-md-backup-{os.getpid()}-{session_id}")
                    backup.write_text(claude_md.read_text(encoding="utf-8"), encoding="utf-8")
                    log(f"backed up existing CLAUDE.md -> {backup}")
                claude_md.write_text(a_context, encoding="utf-8")
                log("injected context via CLAUDE.md (auto-loaded by Claude Code)")
            elif a_agent == "aider":
                ctx_file = f"/tmp/nasim-aider-context-{os.getpid()}-{session_id}.md"
                Path(ctx_file).write_text(a_context, encoding="utf-8")
                os.environ["AIDER_READ"] = ctx_file
                log(f"injected context via AIDER_READ={ctx_file}")
            elif a_agent == "grok":
                os.environ["GROK_CONTEXT"] = a_context
            elif a_agent in ("opencode", "open"):
                os.environ["OPENCODE_SYSTEM_PROMPT"] = a_context
            elif a_agent in ("terminal", "shell"):
                os.environ["NASIM_CONTEXT"] = a_context
        rc = launch_agent(a_agent, a_url, a_model, list(a_extra))
    finally:
        if a_agent in ("claude", "code") and a_context:
            if backup and backup.is_file():
                claude_md.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
                backup.unlink(missing_ok=True)
                log("restored original CLAUDE.md")
            else:
                claude_md.unlink(missing_ok=True)
                log("removed temporary CLAUDE.md")
        session.session_end(session_id)
    return rc


def _one_shot(a_agent: str, a_url: str, a_model: str, a_context: str, a_prompt: str, a_extra: Sequence[str]) -> int:
    """Run a single prompt non-interactively.

    Args:
        a_agent (str): Agent key.
        a_url (str): Transport URL.
        a_model (str): Model tag.
        a_context (str): Context to prepend (may be empty).
        a_prompt (str): User prompt.
        a_extra (Sequence[str]): Extra args.

    Returns:
        int: The agent's exit code.
    """
    log(f"one-shot mode: {a_prompt}")
    full = a_prompt if not a_context else f"{a_context}\n\n--- User Request ---\n{a_prompt}"
    extra = list(a_extra)
    rc = 0
    if a_agent in ("claude", "code"):
        rc = one_shot_claude(a_url, a_model, full, extra)
    elif a_agent == "aider":
        env = dict(os.environ, OLLAMA_API_BASE=a_url)
        rc = subprocess.run(
            ["aider", "--model", f"ollama/{a_model}", "--message", full, "--no-pretty", *extra], env=env
        ).returncode
    elif a_agent == "grok":
        if have("grok"):
            env = dict(os.environ, GROK_API_BASE=f"{a_url.rstrip('/')}/v1", GROK_API_KEY="ollama")
            rc = subprocess.run(["grok", "--model", a_model, "-m", full, *extra], env=env).returncode
        else:
            log("grok not installed, printing prompt")
            print(full)
    elif a_agent in ("opencode", "open"):
        env = dict(os.environ, OPENAI_BASE_URL=f"{a_url.rstrip('/')}/v1", OPENAI_API_KEY="ollama")
        rc = subprocess.run(["opencode", "--model", a_model, "--message", full, *extra], env=env).returncode
    else:
        print(full)
    return rc

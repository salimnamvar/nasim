#!/usr/bin/env bash
# Source this file — do not execute directly.
#
# nasim — toggle Claude Code between the Anthropic cloud and a local Ollama
#         backend (via bridge or direct native). Direct mode recommended for
#         reliable agentic use with local models (Aider, OpenCode, claude via
#         Ollama's native Anthropic compat, etc.).
#
#   nasim start          route Claude Code to Ollama via bridge + picker injection
#   nasim stop           full rollback (bridge mode)
#   nasim status         backend, tunnel, health
#   nasim models         list via bridge
#   nasim direct-start   native Ollama forward (11434); sets OLLAMA_* + ANTHROPIC_* for claude/aider
#   nasim direct-stop    close direct tunnel + clear env
#   nasim direct-status  report direct tunnel liveness
#
# This shim holds NO logic (project rule AP-03). All decisions live in the
# Python package `python -m nasim`. The shim exists for one reason only: env
# vars must be exported into the *calling* shell, which a subprocess cannot do.
# The package writes `~/.nasim/env.sh`; this function sources it, then deletes
# it. Everything else — tunnel, picker surgery, model backup, health — is done
# by the package and is unit-tested.

nasim() {
  # Locate the package: prefer an explicit NASIM_ROOT, else derive from this
  # file's location (…/bin/nasim.sh -> repo root with src/ on the path).
  local _self _root
  _self="${BASH_SOURCE[0]}"
  _root="${NASIM_ROOT:-$(cd "$(dirname "$_self")/.." && pwd)}"
  # env.sh lives under $HOME/.nasim — the same root the Python package uses
  # (RuntimePaths.default() == Path.home()/".nasim"), so the two never disagree.
  local _env_file="$HOME/.nasim/env.sh"

  # Run the package. If installed (`pip install -e`), plain `python -m nasim`
  # works; otherwise fall back to running from the repo's src/ layout.
  if python3 -c "import nasim" >/dev/null 2>&1; then
    python3 -m nasim "$@"
  else
    PYTHONPATH="${_root}/src:${PYTHONPATH:-}" python3 -m nasim "$@"
  fi
  local _rc=$?

  # Apply any env directives the controller emitted, in THIS shell, then clear.
  if [ -f "$_env_file" ]; then
    # shellcheck disable=SC1090
    source "$_env_file"
    rm -f "$_env_file"
  fi

  return $_rc
}

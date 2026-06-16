#!/usr/bin/env bash
# nasim — thin loader + entrypoint (Controller-like dispatch only)
#
# Real implementation lives in lib/nasim/ for modularity, SoC, DRY and scalability (AD-08).
# All hard-coded values moved to config (AD-09).
# Primary validation: real black + agentic self-audit loops (AD-10).
#
# This file must remain small and only do:
#   - early config
#   - sourcing of concerns
#   - call into nasim_main
#
# nasim():
#   Main entry. Resolves lib, sources modules in dependency order, hands off to nasim_main.
#   Supports being sourced (NASIM_INTERNAL=1) for test harness access to internals without exec.
#
#   Globals set:
#     NASIM_VERSION, SCRIPT_DIR, NASIM_LIB_DIR, plus everything from sourced config + modules.
#   Side effects: may exec agent or die on error.

set -euo pipefail

NASIM_VERSION="2026-06-16-v2-litellm-claude-fix+strong-default+docstrings"   # litellm probe/model-name + claude /v1 base + strong DEFAULT_MODEL (deepseek-r1:14b) + early weak-model warnings + Google docstrings via model assistance; full harness re-validated.

# Allow the harness to source us for function access without executing CLI
if [[ "${NASIM_INTERNAL:-}" == "1" && "${BASH_SOURCE[0]}" != "${0}" ]]; then
    :   # just define functions when sourced
fi

# Resolve lib dir relative to this script (works when sourced or exec'd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NASIM_LIB_DIR="$SCRIPT_DIR/../lib/nasim"

# --- Minimal shared utilities (available to all modules) ---
# die(msg):
#   Print to stderr and exit 1. Used for fatal setup / transport / config errors.
die() { echo "nasim: $*" >&2; exit 1; }

# log(msg):
#   Prefix + stderr. All user-facing progress (tunnels, probes, launches).
log() { echo "nasim: $*" >&2; }

# have(cmd):
#   True if command is on PATH. Used for optional (fzf/gum/litellm/tailscale) and ssh/curl.
have() { command -v "$1" >/dev/null 2>&1; }

# is_dry():
#   True under NASIM_DRY_RUN=1 or NASIM_TEST_MODE containing "dry".
#   Prevents real ssh, real exec of agents, real litellm start. Used by all strategies.
is_dry() { [[ "${NASIM_TEST_MODE:-}${1:-}" == *dry* || "${NASIM_DRY_RUN:-}" == "1" ]]; }

# --- Load order (important for dependencies) ---
# 1. Config (provides BLACK_HOST, DEFAULT_*, orders, etc.)
source "$NASIM_LIB_DIR/config.sh"

# 2. Common concerns
source "$NASIM_LIB_DIR/probe.sh"
source "$NASIM_LIB_DIR/transport.sh"
source "$NASIM_LIB_DIR/agent.sh"

# 3. UI + orchestration
source "$NASIM_LIB_DIR/ui.sh"
source "$NASIM_LIB_DIR/orchestration.sh"

# 4. CLI dispatch + help
source "$NASIM_LIB_DIR/cli.sh"

# Hand off to the real command handler
nasim_main "$@"

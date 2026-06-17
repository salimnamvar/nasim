#!/usr/bin/env bash
# lib/nasim/rollback.sh — Environment isolation + rollback on exit (CRITICAL)
#
# save_env_state() / restore_env_state():
#   Before nasim modifies ANY environment variable that could affect
#   Claude Code, Grok Code, Aider, or other frontier CLI agents,
#   we save the original values. On exit (normal or crash), we restore them.
#
#   This guarantees: when nasim closes, your cloud models work exactly
#   as before. No permanent side effects.
#
#   Backups stored in: ~/.local/share/nasim/env-backups/<timestamp>.sh

NASIM_STATE_DIR="${HOME}/.local/share/nasim"
NASIM_ENV_BACKUP_DIR="$NASIM_STATE_DIR/env-backups"

# _rollback_ensure_dirs():
#   Create state directories if missing.
_rollback_ensure_dirs() {
    mkdir -p "$NASIM_ENV_BACKUP_DIR"
}

# _rollback_backup_file():
#   Returns the path to the current backup file for this shell session.
_rollback_backup_file() {
    echo "$NASIM_ENV_BACKUP_DIR/nasim-env-$$.sh"
}

# save_env_state():
#   Save all env vars that nasim might modify, plus a marker.
#   Called once before any env modification.
#   Vars we touch: ANTHROPIC_*, OPENAI_*, OLLAMA_*, CLAUDE_CODE_*, AIDER_*, NASIM_*
save_env_state() {
    _rollback_ensure_dirs
    local bf
    bf="$(_rollback_backup_file)"

    # Only save once per shell session
    [[ -f "$bf" ]] && return 0

    {
        echo "# Nasim env backup for PID $$ — $(date -Iseconds)"
        echo "# DO NOT EDIT — auto-restored on nasim exit"
        echo ""
        # Save values (even if empty — empty means "was unset or was empty")
        for var in ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_API_KEY \
                   ANTHROPIC_DEFAULT_HAIKU_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL \
                   CLAUDE_CODE_SUBAGENT_MODEL \
                   CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY CLAUDE_CODE_AUTO_COMPACT_WINDOW \
                   ANTHROPIC_API_URL \
                   OPENAI_BASE_URL OPENAI_API_KEY \
                   OLLAMA_API_BASE OLLAMA_HOST \
                   CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC \
                   AIDER_MODEL AIDER_API_BASE \
                   DISABLE_TELEMETRY \
                   NASIM_REMOTE_URL NASIM_MODEL NASIM_ACTIVE; do
            # Use printf %q to safely escape values
            printf 'export %s=%q\n' "$var" "${!var:-}"
        done
        echo ""
        echo "# Mark this backup as valid"
        echo "export NASIM_ENV_BACKUP_VALID=1"
    } > "$bf"

    # Register automatic restore on shell exit (if interactive) or explicit call
    # For non-interactive (scripted), caller must call restore_env_state
    if [[ -n "${PS1:-}" || -n "${BASHPID:-}" ]]; then
        # Use trap for shell exit — but only if we're the top-level nasim shell
        if [[ "${NASIM_TOP_LEVEL:-}" == "1" ]]; then
            trap 'restore_env_state' EXIT INT TERM HUP
        fi
    fi
}

# restore_env_state():
#   Restore all backed-up env vars to their original values.
#   Called automatically on exit, or manually via `nasim disconnect` / `nasim stop`.
#   After restore, deletes the backup file to prevent double-restore.
restore_env_state() {
    local bf
    bf="$(_rollback_backup_file)"

    if [[ ! -f "$bf" ]]; then
        # No backup = nothing to restore (or already restored)
        return 0
    fi

    # Source the backup to restore original values
    # shellcheck source=/dev/null
    source "$bf"

    # Clean up: remove the backup file
    rm -f "$bf"

    # CRITICAL for full claude code rollback:
    # If backed-up value for a "custom endpoint" var was empty (i.e. originally unset),
    # we currently have it exported as '' from the source above.
    # Unset it explicitly so claude (and fcc wrappers) see no ANTHROPIC_BASE_URL etc at all.
    # This guarantees: after `nasim stop`, plain `claude` only ever talks to official Anthropic
    # and shows only anthropic models (no ollama leakage from previous nasim session).
    for var in ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_API_KEY \
               ANTHROPIC_DEFAULT_HAIKU_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL \
               CLAUDE_CODE_SUBAGENT_MODEL \
               CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY CLAUDE_CODE_AUTO_COMPACT_WINDOW \
               ANTHROPIC_API_URL ; do
        if [[ -z "${!var:-}" ]]; then
            unset "$var" 2>/dev/null || true
        fi
    done

    # Unset nasim-specific markers
    unset NASIM_ACTIVE NASIM_REMOTE_URL NASIM_MODEL NASIM_ENV_BACKUP_VALID

    # Also stop any fcc sidecar we started for this session (if the function exists)
    if type fcc_cleanup_on_stop >/dev/null 2>&1; then
        fcc_cleanup_on_stop || true
    fi

    log "env state restored — cloud agents (claude, grok, aider) back to defaults"
}

# with_isolated_env(cmd, ...):
#   Run a command in a subshell with nasim env vars set.
#   When the subshell exits, parent env is untouched.
#   This is the SAFEST way to run agents — guarantees zero leakage.
with_isolated_env() {
    (
        # In subshell: all exports are local to this subshell
        export NASIM_ISOLATED=1
        "$@"
    )
    # Parent env is completely untouched
}

# show_env_diff():
#   Print what nasim changed vs original — useful for debugging.
show_env_diff() {
    local bf
    bf="$(_rollback_backup_file)"
    if [[ ! -f "$bf" ]]; then
        echo "No active nasim env backup (nasim not running or no changes made)"
        return 0
    fi

    echo "# Current env diffs from nasim backup:"
    local var
    for var in ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_API_KEY \
               ANTHROPIC_DEFAULT_HAIKU_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL \
               CLAUDE_CODE_SUBAGENT_MODEL \
               CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY CLAUDE_CODE_AUTO_COMPACT_WINDOW \
               ANTHROPIC_API_URL \
               OPENAI_BASE_URL OPENAI_API_KEY \
               OLLAMA_API_BASE OLLAMA_HOST \
               CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC \
               AIDER_MODEL AIDER_API_BASE \
               DISABLE_TELEMETRY \
               NASIM_REMOTE_URL NASIM_MODEL NASIM_ACTIVE; do
        local orig="" curr=""
        # Extract original from backup file
        orig=$(grep "^export $var=" "$bf" | cut -d= -f2- | sed 's/^"//;s/"$//')
        curr="${!var:-}"
        if [[ "$orig" != "$curr" ]]; then
            echo "  $var: '$orig' -> '$curr'"
        fi
    done
}

#!/usr/bin/env bash
# lib/nasim/cli.sh — Full command dispatch, help, tunnel + daemon + context + KB + session (v3.1)
# Fixed: unbound variable errors with set -u, proper shift handling, Claude Code context via ~/.claude/

# nasim_version():
#   Returns effective version (overridable for tests).
nasim_version() {
    echo "${NASIM_VERSION_OVERRIDE:-$NASIM_VERSION}"
}

cmd_help() {
    cat <<EOF
nasim $(nasim_version) — remote Ollama on black + frontier agents on laptop.

═══════════════════════════════════════════════════════════════════════════════
PRIMARY COMMANDS (use these for daily workflow)
═══════════════════════════════════════════════════════════════════════════════

  nasim start [ssh|tailscale|litellm]     Start persistent tunnel daemon
  nasim stop                              Stop daemon + RESTORE env vars
  nasim status                            Show daemon health, models, context
  nasim code [options]                      Smart launch (auto-detects agent)

  nasim select                              Interactive menu (access + agent + model)
  nasim launch --access X --agent Y --model Z   Explicit launch

═══════════════════════════════════════════════════════════════════════════════
CONTEXT & KNOWLEDGE (makes agents understand your project)
═══════════════════════════════════════════════════════════════════════════════

  nasim context --refresh                   Auto-detect project, generate context.md
  nasim context --edit                    Edit global context (applies to all sessions)
  nasim context --show                    Show current context

  nasim kb index <path> [name]            Index docs/code into searchable KB
  nasim kb query <name> "question"        Search KB for relevant chunks
  nasim kb list                           Show all indexed KBs
  nasim kb rm <name>                      Delete a KB

═══════════════════════════════════════════════════════════════════════════════
MODEL MANAGEMENT
═══════════════════════════════════════════════════════════════════════════════

  nasim models                            List models on black (via SSH, no tunnel)
  nasim models --fit                      Show models that fit your 1080Ti (11GB)
  nasim vram recommend [coding|reasoning|chat]   Get model recommendations
  nasim vram check <model>                Check if model fits your GPU

  nasim doctor [--url URL]                Full health check + model list + ps
  nasim probe [--url URL]               Quick endpoint probe

═══════════════════════════════════════════════════════════════════════════════
SESSIONS
═══════════════════════════════════════════════════════════════════════════════

  nasim sessions                          List recent sessions
  nasim session current                   Show active session
  nasim session resume <id>               Reconnect to a previous session

═══════════════════════════════════════════════════════════════════════════════
CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

  nasim config show                       Show effective configuration
  nasim config edit                       Edit ~/.config/nasim/nasim.conf
  nasim config path                       Show config file path

  nasim tunnel {ssh|persistent|install-systemd|status}   Tunnel management

═══════════════════════════════════════════════════════════════════════════════
LEGACY (still work, but prefer 'nasim code')
═══════════════════════════════════════════════════════════════════════════════

  nasim claude [args...]                  Launch Claude Code with Ollama backend
  nasim aider [args...]                   Launch Aider with Ollama backend
  nasim opencode [args...]                Launch OpenCode
  nasim terminal                          Drop into branded shell (manual mode)

═══════════════════════════════════════════════════════════════════════════════
ENVIRONMENT SAFETY GUARANTEE
═══════════════════════════════════════════════════════════════════════════════

  When nasim starts:  it BACKS UP your ANTHROPIC_*, OPENAI_*, OLLAMA_*, etc.
  When nasim stops:   it RESTORES them to original values.

  This means: Claude Code (cloud), Grok (cloud), Aider (cloud) — all work
  normally when nasim is NOT running. Zero permanent side effects.

  To verify:  nasim env diff    (show current env changes vs backup)

═══════════════════════════════════════════════════════════════════════════════
QUICK START
═══════════════════════════════════════════════════════════════════════════════

  1. nasim start                          # Start tunnel to black
  2. cd ~/my-project && git init          # Enter a project
  3. nasim context --refresh              # Index your project
  4. nasim code                           # Launch agent with full context
  5. ... work ...                         # Ask agent to code, review, debug
  6. exit                                 # Agent exits
  7. nasim stop                           # Tear down + restore env

See ~/.local/share/nasim/ for runtime state (sessions, KB indices, contexts).
EOF
}

# Tunnel commands (legacy + daemon integration)
cmd_tunnel() {
    local sub="${1:-help}"
    if [[ $# -gt 0 ]]; then shift; fi
    case "$sub" in
        ssh|start|adhoc)
            setup_ssh_tunnel >/dev/null
            local pidf="/tmp/nasim-ssh-tunnel-$$.pid"
            if [[ -f "$pidf" ]]; then
                trap "cleanup_tunnel '$pidf'" EXIT INT TERM
            fi
            log "ad-hoc tunnel running. Press Ctrl-C or exit this shell to stop."
            echo "Press Ctrl-C or exit to tear down."
            sleep 99999 || true
            ;;
        persistent|autossh)
            log "One-liner for background autossh (reconnects):"
            echo "autossh -M 0 -f -N -o 'ServerAliveInterval 30' -L ${DEFAULT_LOCAL_PORT}:localhost:11434 ${BLACK_HOST}"
            echo "Kill: pkill -f 'ssh.*${DEFAULT_LOCAL_PORT}.*${BLACK_HOST}'"
            ;;
        install-systemd)
            local unit_dir="${HOME}/.config/systemd/user"
            mkdir -p "$unit_dir"
            local unit="$unit_dir/nasim-black-tunnel.service"
            cat > "$unit" <<UNIT
[Unit]
Description=Nasim persistent SSH tunnel to black Ollama (11434)
After=network.target

[Service]
ExecStart=/usr/bin/autossh -M 0 -N -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -L ${DEFAULT_LOCAL_PORT}:localhost:11434 ${BLACK_HOST}
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
UNIT
            log "Wrote $unit"
            echo "systemctl --user daemon-reload && systemctl --user enable --now nasim-black-tunnel"
            echo "journalctl --user -u nasim-black-tunnel -f"
            ;;
        status)
            pgrep -af "ssh.*${BLACK_HOST}" | grep -E 'L .*1143' || echo "no obvious nasim ssh tunnel"
            systemctl --user status nasim-black-tunnel 2>/dev/null || true
            ;;
        *)
            echo "nasim tunnel {ssh|persistent|install-systemd|status}"
            ;;
    esac
}

# Config commands
cmd_config() {
    local sub="${1:-show}"
    if [[ $# -gt 0 ]]; then shift; fi
    case "$sub" in
        edit) nasim_config_edit ;;
        show) nasim_config_show ;;
        path) nasim_config_path ;;
        *)    nasim_config_show ;;
    esac
}

# Context commands
cmd_context() {
    local sub="${1:-show}"
    if [[ $# -gt 0 ]]; then shift; fi
    case "$sub" in
        --refresh|refresh|generate)
            context_refresh ;;
        --edit|edit)
            context_global_edit ;;
        --show|show)
            local cf
            cf=$(context_file)
            if [[ -n "$cf" ]]; then
                echo "=== Context: $cf ==="
                cat "$cf"
            else
                echo "No active context. Run 'nasim context --refresh' in a project directory."
            fi
            ;;
        *)
            echo "nasim context {--refresh|--edit|--show}"
            ;;
    esac
}

# KB commands
cmd_kb() {
    local sub="${1:-list}"
    if [[ $# -gt 0 ]]; then shift; fi
    case "$sub" in
        index)
            local path="${1:-.}"
            local name="${2:-$(basename "$(cd "$path" && pwd)")}"
            kb_index "$path" "$name"
            ;;
        query)
            local name="${1:-}"
            local query="${2:-}"
            if [[ -z "$name" || -z "$query" ]]; then
                echo "Usage: nasim kb query <name> 'question'"
                return 1
            fi
            kb_query "$name" "$query"
            ;;
        list)
            kb_list ;;
        rm|remove|delete)
            kb_rm "${1:-}" ;;
        *)
            echo "nasim kb {index <path> [name] | query <name> 'question' | list | rm <name>}"
            ;;
    esac
}

# VRAM commands
cmd_vram() {
    local sub="${1:-fit}"
    if [[ $# -gt 0 ]]; then shift; fi
    case "$sub" in
        fit)
            vram_fit "$@" ;;
        recommend)
            vram_recommend "$@" ;;
        check)
            vram_check "${1:-}" ;;
        *)
            echo "nasim vram {fit [gb] | recommend [workload] | check <model>}"
            ;;
    esac
}

# Session commands
cmd_session() {
    local sub="${1:-list}"
    if [[ $# -gt 0 ]]; then shift; fi
    case "$sub" in
        list|ls)
            session_list "$@" ;;
        current)
            session_current ;;
        resume)
            session_resume "${1:-}" ;;
        *)
            echo "nasim session {list | current | resume <id>}"
            ;;
    esac
}

# Env commands (for debugging rollback)
cmd_env() {
    local sub="${1:-diff}"
    if [[ $# -gt 0 ]]; then shift; fi
    case "$sub" in
        diff)
            show_env_diff ;;
        restore)
            restore_env_state
            log "env manually restored"
            ;;
        *)
            echo "nasim env {diff | restore}"
            ;;
    esac
}

# Main CLI entry (called after all sourcing)
nasim_main() {
    local cmd="${1:-help}"
    if [[ $# -gt 0 ]]; then shift; fi

    case "$cmd" in
        # === PRIMARY ===
        start)
            daemon_start "$@" ;;
        stop)
            daemon_stop ;;
        status)
            daemon_status ;;
        code)
            cmd_code "$@" ;;
        select)
            do_select "$@" ;;
        launch)
            local access="ssh-tunnel" agent="claude" model="$DEFAULT_MODEL"
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --access) access="$2"; shift 2 ;;
                    --agent)  agent="$2"; shift 2 ;;
                    --model)  model="$2"; shift 2 ;;
                    --dry-run) export NASIM_DRY_RUN=1; shift ;;
                    *) break ;;
                esac
            done
            choose_and_launch "$access" "$agent" "$model" "$@"
            ;;

        # === CONTEXT & KB ===
        context)
            cmd_context "$@" ;;
        kb)
            cmd_kb "$@" ;;

        # === MODEL MANAGEMENT ===
        models|list-models)
            if [[ "${1:-}" == "--fit" ]]; then
                vram_fit
            else
                nasim_models "$@"
            fi
            ;;
        vram)
            cmd_vram "$@" ;;
        doctor|probe|status)
            nasim_doctor "$@" ;;

        # === SESSIONS ===
        sessions|session)
            cmd_session "$@" ;;

        # === CONFIG ===
        config)
            cmd_config "$@" ;;
        tunnel)
            cmd_tunnel "$@" ;;

        # === ENV SAFETY ===
        env)
            cmd_env "$@" ;;

        # === LEGACY ===
        claude|code)
            legacy_claude "$@" ;;
        aider)
            legacy_aider "$@" ;;
        opencode|open)
            # Legacy opencode launch
            local url="${NASIM_REMOTE_URL:-}"
            local model="${NASIM_MODEL:-$DEFAULT_MODEL}"
            if [[ -z "$url" ]]; then
                if type daemon_is_running >/dev/null 2>&1 && daemon_is_running; then
                    url=$(daemon_url)
                fi
            fi
            if [[ -z "$url" ]]; then
                url=$(setup_ssh_tunnel)
            fi
            launch_opencode "$url" "$model" "$@"
            ;;
        terminal|shell)
            local url="${NASIM_REMOTE_URL:-http://127.0.0.1:${DEFAULT_LOCAL_PORT}}"
            local model="${NASIM_MODEL:-$DEFAULT_MODEL}"
            if [[ -z "${NASIM_REMOTE_URL:-}" ]]; then
                url=$(setup_ssh_tunnel)
            fi
            launch_terminal "$url" "$model"
            ;;

        version)
            echo "$(nasim_version)" ;;
        help|*)
            cmd_help ;;
    esac
}

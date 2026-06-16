#!/usr/bin/env bash
# lib/nasim/cli.sh — command dispatch, help, tunnel mgmt (thin controller)

nasim_version() {
    echo "${NASIM_VERSION_OVERRIDE:-$NASIM_VERSION}"
}

cmd_help() {
    cat <<EOF
nasim $(nasim_version) — all solutions for remote Ollama on black + terminal frontier agents on laptop.

Primary (recommended):
  nasim select
  nasim launch --access ssh-tunnel --agent claude --model qwen2.5-coder:14b
                                   Access: ssh-tunnel | tailscale | litellm
                                   Agent:  claude | aider | opencode | terminal

Utility (model discovery is now first-class to fix "models not shown"):
  nasim models [--url URL]         List models available on black (or at URL). No tunnel needed.
  nasim doctor [--url URL]         Probe + full black model list + ps
  nasim status                     Alias for doctor
  nasim config [edit|show|path]    Manage external configuration
  nasim tunnel {ssh|status|...}

Legacy (still work):
  nasim claude [args...]
  nasim aider  [args...]

Env / Config:
  All values (BLACK_HOST, DEFAULT_MODEL, ports, orders) can come from
  $NASIM_CONFIG_FILE or environment. See 'nasim config show'.

See research/ and recipes/ for details. Every combo + real model-powered tests in tests/.
EOF
}

cmd_tunnel() {
    local sub="${1:-help}"; shift || true
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

cmd_config() {
    local sub="${1:-show}"; shift || true
    case "$sub" in
        edit) nasim_config_edit ;;
        show) nasim_config_show ;;
        path) nasim_config_path ;;
        *)    nasim_config_show ;;
    esac
}

# Main CLI entry (called after all sourcing)
nasim_main() {
    local cmd="${1:-help}"
    shift || true

    case "$cmd" in
        select)          do_select "$@" ;;
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
        claude|code)     legacy_claude "$@" ;;
        aider)           legacy_aider "$@" ;;
        doctor|probe|status) nasim_doctor "$@" ;;
        models|list-models) nasim_models "$@" ;;
        tunnel)          cmd_tunnel "$@" ;;
        config)          cmd_config "$@" ;;
        version)         echo "$(nasim_version)" ;;
        help|*)          cmd_help ;;
    esac
}

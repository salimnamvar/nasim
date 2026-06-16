#!/usr/bin/env bash
# lib/nasim/ui.sh — interactive selection (thin controller concerns)
#
# do_select():
#   The interactive "nasim select" flow. Uses bash select + read for zero-dep menus.
#   After choices, does the weak-model guard (new) then delegates to choose_and_launch.
#   All presentation order comes from config (ACCESS_ORDER / AGENT_ORDER).

do_select() {
    log "nasim select — choose access to black + frontier agent (Ctrl-C aborts)"
    echo

    # Access (from config order)
    local -a accesses=() access_keys=()
    local key
    for key in $ACCESS_ORDER; do
        case "$key" in
            ssh-tunnel|ssh) accesses+=("ssh-tunnel (recommended, always works here)"); access_keys+=("ssh-tunnel") ;;
            tailscale|ts)   accesses+=("tailscale (if up)"); access_keys+=("tailscale") ;;
            litellm|llm)    accesses+=("litellm (proxy on top)"); access_keys+=("litellm") ;;
        esac
    done

    PS3="Access method (1-${#accesses[@]}): "
    select a in "${accesses[@]}"; do
        if [[ -n "$a" ]]; then
            ACCESS="${access_keys[$((REPLY-1))]}"
            break
        fi
    done
    echo "Selected access: $ACCESS"
    echo

    # Agents (from config order)
    local -a agents=() agent_keys=()
    for key in $AGENT_ORDER; do
        case "$key" in
            claude|code)     agents+=("claude (native Anthropic compat — full frontier agent)"); agent_keys+=("claude") ;;
            aider)           agents+=("aider (git-centric, excellent local)"); agent_keys+=("aider") ;;
            opencode|open)   agents+=("opencode (open Claude Code alt)"); agent_keys+=("opencode") ;;
            terminal|shell)  agents+=("terminal (branded shell — manual any agent)"); agent_keys+=("terminal") ;;
        esac
    done

    PS3="Agent / terminal (1-${#agents[@]}): "
    select ag in "${agents[@]}"; do
        if [[ -n "$ag" ]]; then
            AGENT="${agent_keys[$((REPLY-1))]}"
            break
        fi
    done
    echo "Selected agent: $AGENT"
    echo

    read -r -p "Model tag on black [${DEFAULT_MODEL}]: " m
    MODEL="${m:-$DEFAULT_MODEL}"

    # Early, visible guard for known-weak models that reliably produce "Workflow" JSON / bad turns with claude-code etc.
    # (The launcher tip is too late; user already picked in the original bug report.)
    if [[ "$MODEL" == *"qwen2.5"* || "$MODEL" == *"qwen2"* ]]; then
        log "WARNING: $MODEL is a weak/older tag for agentic coding (prone to malformed Workflow/JSON turns with claude/opencode)."
        log "Strong recommendations from current black inventory: deepseek-r1:14b, deepseek-r1:32b, qwen3:8b, qwen3.6:latest, gemma4:31b (GPU-resident)."
        read -r -p "Proceed with weak model anyway? (y/N): " yn
        if [[ ! "$yn" =~ ^[Yy] ]]; then
            log "Aborting select. Re-run and choose a strong tag (or edit DEFAULT_MODEL via 'nasim config edit')."
            exit 0
        fi
    fi

    echo
    log "Bringing up $ACCESS + $AGENT + $MODEL ..."
    choose_and_launch "$ACCESS" "$AGENT" "$MODEL"
}

#!/usr/bin/env bash
# lib/nasim/code.sh — Unified "nasim code" entrypoint (Option C)
#
# cmd_code(args...):
#   The main "nasim code" command. Smart dispatch:
#   1. If daemon not running, auto-start it
#   2. Detect best available agent (claude > grok > aider > opencode > terminal)
#   3. Inject project context if available (via agent-specific mechanisms)
#   4. Inject KB if --kb specified
#   5. Launch with isolated env (rollback guaranteed on exit)
#
#   Flags:
#     --agent claude|grok|aider|opencode  Force specific agent
#     --model <tag>                       Override model
#     --kb <name>                         Inject knowledge base
#     --context <path>                    Use specific context file
#     --no-context                        Skip context injection
#     --one-shot "prompt"                 Run single prompt and exit

# cmd_code():
#   Main entry for `nasim code` command.
cmd_code() {
    local agent="" model="$DEFAULT_MODEL" kb="" context="" one_shot="" no_context=0
    local -a extra_args=()

    # Parse flags
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --agent)    agent="$2"; shift 2 ;;
            --model)    model="$2"; shift 2 ;;
            --kb)       kb="$2"; shift 2 ;;
            --context)  context="$2"; shift 2 ;;
            --no-context) no_context=1; shift ;;
            --one-shot) one_shot="$2"; shift 2 ;;
            --help)
                cat <<'EOF'
Usage: nasim code [options] [agent-args...]

Smart launch: auto-detects best agent, reuses daemon tunnel, injects context.

Options:
  --agent <name>     Force agent: claude, grok, aider, opencode, terminal
  --model <tag>      Override model (default: deepseek-r1:14b)
  --kb <name>        Inject knowledge base into context
  --context <path>   Use specific context file (default: .nasim/context.md)
  --no-context       Skip project context injection
  --one-shot "..."   Run single prompt and exit (non-interactive)
  --help             Show this help

Examples:
  nasim code                          # Smart launch with defaults
  nasim code --agent aider            # Force aider
  nasim code --model qwen3:8b         # Use specific model
  nasim code --kb myproject-docs      # Inject KB into prompt
  nasim code --one-shot "fix the bug" # Non-interactive mode

After exit: all env vars restored, cloud agents work normally.
EOF
                return 0
                ;;
            *) extra_args+=("$1"); shift ;;
        esac
    done

    # Auto-start daemon if not running
    daemon_ensure_running
    local url
    url=$(daemon_url)

    # Auto-detect agent if not specified
    if [[ -z "$agent" ]]; then
        agent=$(_code_detect_agent)
        log "auto-detected agent: $agent"
    fi

    # VRAM check before launch
    vram_check "$model" || {
        read -r -p "Model may not fit GPU. Continue anyway? (y/N): " yn
        [[ "$yn" =~ ^[Yy] ]] || return 1
    }

    # Save env state before any modifications
    save_env_state

    # Build context injection
    local context_content=""
    if [[ "$no_context" -eq 0 ]]; then
        # Project context
        if [[ -n "$context" ]]; then
            if [[ -f "$context" ]]; then
                context_content=$(cat "$context")
                log "using context: $context"
            else
                log "context file not found: $context"
            fi
        elif context_is_active; then
            context_content=$(context_read)
            log "project context active ($(context_file))"
        fi

        # KB injection
        if [[ -n "$kb" ]]; then
            log "injecting KB: $kb"
            local kb_results
            kb_results=$(kb_query "$kb" "$one_shot" 2>/dev/null || true)
            if [[ -n "$kb_results" ]]; then
                context_content="${context_content}

## Relevant Knowledge Base Chunks ($kb)
$kb_results"
            fi
        fi
    fi

    # Prepare launch
    log "launching $agent -> $url model=$model"

    # One-shot mode: prepend context to prompt, run once, exit
    if [[ -n "$one_shot" ]]; then
        _code_one_shot "$agent" "$url" "$model" "$context_content" "$one_shot" "${extra_args[@]}"
        return $?
    fi

    # Interactive mode: launch agent with context injection
    _code_interactive "$agent" "$url" "$model" "$context_content" "${extra_args[@]}"
}

# _code_detect_agent():
#   Return first available agent in priority order.
_code_detect_agent() {
    if have claude; then echo "claude"; return 0; fi
    if have grok; then echo "grok"; return 0; fi
    if have aider; then echo "aider"; return 0; fi
    if have opencode; then echo "opencode"; return 0; fi
    echo "terminal"
}

# _code_interactive(agent, url, model, context, extra_args...):
#   Launch agent interactively with context injected.
#   For Claude Code: writes context to CLAUDE.md (project root) so Claude auto-loads it
#   For Aider: uses AIDER_READ env var
#   For others: uses their native mechanisms
_code_interactive() {
    local agent="$1" url="$2" model="$3" context="$4"
    shift 4

    # Start session tracking
    local session_id
    session_id=$(session_start "$agent" "$model" "$url")

    # For terminal agent, we stay in shell so we need special handling
    if [[ "$agent" == "terminal" ]]; then
        # Terminal exports env and execs shell — context goes in env
        if [[ -n "$context" ]]; then
            export NASIM_CONTEXT="$context"
        fi
        launch_terminal "$url" "$model"
        # After terminal exits (exec replaces process, so this only runs if exec fails)
        session_end "$session_id"
        return 0
    fi

    # For other agents, inject context via agent-specific mechanisms
    local -a inject_args=()
    case "$agent" in
        claude|code)
            # Claude Code reads CLAUDE.md from project root automatically
            # We write our context there temporarily, then restore after session
            if [[ -n "$context" ]]; then
                local claude_md="./CLAUDE.md"
                local claude_md_backup=""

                # Backup existing CLAUDE.md if present
                if [[ -f "$claude_md" ]]; then
                    claude_md_backup="/tmp/nasim-claude-md-backup-$$-$session_id"
                    cp "$claude_md" "$claude_md_backup"
                    log "backed up existing CLAUDE.md -> $claude_md_backup"
                fi

                # Write our context as CLAUDE.md
                echo "$context" > "$claude_md"
                log "injected context via CLAUDE.md (auto-loaded by Claude Code)"

                # Register cleanup to restore original CLAUDE.md after session
                trap '_code_cleanup_claude_md "$claude_md" "$claude_md_backup" "$session_id"' EXIT INT TERM
            fi
            ;;
        aider)
            # Aider doesn't have a direct --prompt, but we can set AIDER_READ
            # or use /read in the chat. For now, export env for aider to see.
            if [[ -n "$context" ]]; then
                local aider_ctx="/tmp/nasim-aider-context-$$-$session_id.md"
                echo "$context" > "$aider_ctx"
                export AIDER_READ="$aider_ctx"
                log "injected context via AIDER_READ=$aider_ctx"
            fi
            ;;
        grok)
            if [[ -n "$context" ]]; then
                export GROK_CONTEXT="$context"
                log "injected context via GROK_CONTEXT"
            fi
            ;;
        opencode|open)
            if [[ -n "$context" ]]; then
                export OPENCODE_SYSTEM_PROMPT="$context"
                log "injected context via OPENCODE_SYSTEM_PROMPT"
            fi
            ;;
    esac

    # Launch agent
    launch_agent "$agent" "$url" "$model" "${inject_args[@]}" "$@"

    # After agent exits (if exec fails)
    session_end "$session_id"
}

# _code_cleanup_claude_md(claude_md_path, backup_path, session_id):
#   Restore original CLAUDE.md after session ends.
_code_cleanup_claude_md() {
    local claude_md="$1" backup="$2" session_id="$3"

    if [[ -n "$backup" && -f "$backup" ]]; then
        mv "$backup" "$claude_md"
        log "restored original CLAUDE.md"
    else
        rm -f "$claude_md"
        log "removed temporary CLAUDE.md"
    fi

    session_end "$session_id" 2>/dev/null || true
}

# _code_one_shot(agent, url, model, context, prompt, extra_args...):
#   Run a single prompt and exit. Non-interactive.
_code_one_shot() {
    local agent="$1" url="$2" model="$3" context="$4" prompt="$5"
    shift 5

    log "one-shot mode: $prompt"

    # Combine context + prompt
    local full_prompt="$prompt"
    if [[ -n "$context" ]]; then
        full_prompt="$context

--- User Request ---
$prompt"
    fi

    case "$agent" in
        claude|code)
            # Claude Code one-shot: -m "message" (NOT --prompt)
            # Must map all 4 tiers or Claude falls back to Anthropic model names
            # NOTE: Do NOT append /v1 — Ollama adds it internally for Anthropic compat
            ANTHROPIC_AUTH_TOKEN=ollama \
            ANTHROPIC_BASE_URL="${url%/}" \
            ANTHROPIC_API_KEY="" \
            ANTHROPIC_DEFAULT_HAIKU_MODEL="$model" \
            ANTHROPIC_DEFAULT_SONNET_MODEL="$model" \
            ANTHROPIC_DEFAULT_OPUS_MODEL="$model" \
            CLAUDE_CODE_SUBAGENT_MODEL="$model" \
            DISABLE_TELEMETRY=1 \
            claude --model "$model" -m "$full_prompt" "$@"
            ;;
        aider)
            export OLLAMA_API_BASE="$url"
            aider --model "ollama/${model}" --message "$full_prompt" --no-pretty "$@"
            ;;
        grok)
            if have grok; then
                GROK_API_BASE="${url%/}/v1" \
                GROK_API_KEY=ollama \
                grok --model "$model" -m "$full_prompt" "$@"
            else
                log "grok not installed, falling to terminal mode"
                echo "$full_prompt"
            fi
            ;;
        opencode|open)
            export OPENAI_BASE_URL="${url%/}/v1"
            export OPENAI_API_KEY=ollama
            opencode --model "$model" --message "$full_prompt" "$@"
            ;;
        terminal|shell)
            echo "$full_prompt"
            ;;
    esac
}

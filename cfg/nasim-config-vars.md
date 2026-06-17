# Nasim Configurable Variables

This file lists key configurable variables found in bin/ and lib/nasim/ (and related).

Generated as the result of exercising the prompts from sce1.txt and sce2.txt via `nasim code`.

## Core (config.sh + defaults + conf)
- BLACK_HOST
- DEFAULT_MODEL (e.g. deepseek-r1:14b)
- DEFAULT_LOCAL_PORT (11435)
- LITELLM_PORT (4000)
- ACCESS_ORDER, AGENT_ORDER
- PROBE_TIMEOUT, PROBE_CONNECT_TIMEOUT, SSH_CONNECT_TIMEOUT, SSH_SERVER_ALIVE_INTERVAL
- NASIM_CONFIG_DIR / NASIM_CONFIG_FILE
- NASIM_VERSION_OVERRIDE

## Claude Code specific (for ollama via ANTHROPIC compat or fcc gateway)
- ANTHROPIC_BASE_URL
- ANTHROPIC_API_URL
- ANTHROPIC_AUTH_TOKEN (ollama)
- ANTHROPIC_API_KEY (empty)
- ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS (81920)
- ANTHROPIC_DEFAULT_HAIKU_MODEL / _SONNET_MODEL / _OPUS_MODEL
- CLAUDE_CODE_SUBAGENT_MODEL
- CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY (1)
- CLAUDE_CODE_AUTO_COMPACT_WINDOW (190000)
- CLAUDE_CLI_BIN
- CLAUDE_WORKSPACE (defaults to ~/.fcc/agent_workspace)
- TERM=dumb
- PYTHONIOENCODING=utf-8
- DISABLE_TELEMETRY (1)

All of the above (plus more) are also used inside free-claude-code; nasim now injects the complete relevant set for both direct native-compat and fcc-proxy paths. See lib/nasim/agents/claude.sh and fcc.sh.

## Daemon / State / Rollback
- NASIM_STATE_DIR (~/.local/share/nasim)
- NASIM_ACTIVE_URL_FILE, NASIM_DAEMON_PID_FILE
- NASIM_REMOTE_URL, NASIM_ACTIVE, NASIM_MODEL
- Env backup: ANTHROPIC_*, CLAUDE_CODE_*, OPENAI_*, OLLAMA_*, etc.

## Other modules
- KB: NASIM_KB_DIR, NASIM_KB_EMBED_MODEL, NASIM_KB_CHUNK_SIZE, NASIM_KB_TOP_K
- Session: NASIM_SESSION_DIR, NASIM_CURRENT_SESSION_FILE
- Context: NASIM_CONTEXT_DIR, NASIM_GLOBAL_CONTEXT_DIR
- VRAM, transports (BLACK_HOST used in ssh/tailscale)

## How to configure
- ~/.config/nasim/nasim.conf (KEY=val)
- Env vars (highest precedence)
- CLI flags for launch

See also: nasim config show / edit

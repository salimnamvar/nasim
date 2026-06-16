# C4 Context — Nasim Remote Ollama Selector (v2)

## Context Diagram (Mermaid)

```mermaid
C4Context
    title Nasim: Frontier terminal agents on laptop using Ollama on remote "black"

    Person(user, "User (Salim on salim-hp)", "Wants frontier agentic coding (Claude Code UX or equivalent) powered by strong local models on GPU server without moving files or exposing ports.")

    System_Boundary(laptop, "Laptop (salim-hp)") {
        Container(nasim, "nasim CLI (select / launch / tunnel)", "Bash", "Interactive selector + launcher. Supports all documented transports + agents. Probes, sets envs (ANTHROPIC_BASE_URL / OLLAMA_API_BASE), execs agent or drops configured shell.")
        Container(agents, "Frontier Agents (claude, aider, opencode, ...)", "External binaries", "Run on laptop. Read/write local FS + terminal. Call model via configured base URL.")
    }

    System_Boundary(black, "Remote GPU Server (black)") {
        Container(ollama, "Ollama + Models (GPU resident)", "ollama serve", "Serves /api/* and Anthropic-compatible /v1/messages. Models: qwen2.5-coder, gemma4, deepseek-r1, etc. GPU only for agent loops.")
    }

    System_Ext(tailscale, "Tailscale (optional)", "Mesh VPN")
    System_Ext(litellm, "LiteLLM (optional proxy)", "Unified router + fallbacks")

    Rel(user, nasim, "nasim select\n(picks access + agent + model)", "interactive or flags")
    Rel(nasim, agents, "exec with correct envs (ANTHROPIC_* or OLLAMA_*)", "after transport ready")
    Rel(agents, ollama, "HTTPS? / HTTP over private path\n(tools, streaming, long context)", "via SSH tunnel / Tailscale / LiteLLM")
    Rel(nasim, ollama, "probe reachability\ncurl /api/tags", "before launch")
    Rel(nasim, tailscale, "optional direct MagicDNS", "if up")
    Rel(nasim, litellm, "optional generate config + start proxy", "layer on top of base transport")
    Rel(ollama, black, "runs on", "GPU VRAM fit verified")

    Update: 2026-06-16 (sprint v2). See research and recipes for transport details.
```

**Key notes (C4 context level):**
- Scope: the "Nasim" experience for this user/machine pair.
- External: no public exposure. All model access private.
- Responsibility split: nasim = glue + selection + verification. Agents = the frontier loop. Ollama = inference only.
- Scale: single user, low QPS, long sessions.

See UC for primary flows. SM for states if expanded. Implementation in `bin/nasim`.
# Research: Frontier AI Coding Agents (Claude Code, Grok Code, OpenCode etc.) + Local/Remote Ollama (2026-06-16)

**Goal of this document (and Nasim going forward):**  
Before building anything, deeply search current available solutions. Prefer existing, well-supported, easy-to-install tools and configs. Only code thin glue or knowledge when gaps remain. Never reinvent core wheels (Anthropic-compatible serving, agent loops, tunnels).

**User context:** Laptop (salim-hp) should run the "frontier agent" experience (Claude Code, equivalents for Grok/Open). Heavy inference on remote "black" (Ollama + GPU). Secure, low-friction, persistent access. Maximize benefit of local models without cloud lock-in/cost.

## 1. Major Breakthrough (Jan 2026): Native Anthropic Messages API in Ollama
- Ollama v0.14.0+ directly implements the Anthropic Messages API (`/v1/messages`, streaming, tools, system, vision, extended thinking, etc.).
- This makes the **real Claude Code CLI** (Anthropic's agentic terminal tool) work out-of-the-box with any Ollama model.
- No custom translator/bridge required for the core path. (The previous Nasim v1 wheel — custom FastAPI + schema_coerce + tool_salvage + picker injection — was a pre-native solution and is now obsolete for this use case.)

**Official quick start (same-machine or forwarded):**
```bash
# Install Claude Code (one time)
curl -fsSL https://claude.ai/install.sh | bash

# Point at Ollama (Anthropic format)
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_BASE_URL=http://localhost:11434
export ANTHROPIC_API_KEY=""          # or unset in some shells

claude --model qwen3-coder          # or gemma4:xx, gpt-oss:20b, etc.
# Even simpler on many setups:
ollama launch claude --model qwen3-coder
```

See:
- https://ollama.com/blog/claude (2026-01-16)
- https://docs.ollama.com/integrations/claude-code (recommends >=32k-64k context)

**Claude Code now supports** (via Ollama compat): full tool use (Read/Write/Edit/Bash + MCP, sub-agents, plan mode, hooks, skills), streaming, multi-turn, web search via Ollama capabilities, /loop scheduling, Telegram plugins, headless/CI modes.

**Caveats from field reports:**
- Agentic reliability is still **model-bound** (tool-calling fidelity, long-horizon planning, recovery under the full Claude system prompt + many tools). Strong coder models are required; small/general models often emit malformed calls or loop.
- Large context recommended; set `num_ctx` high in Ollama (or model-specific).
- On GPU-limited hardware (e.g. 11 GB), models that spill to CPU (large dense) become unusably slow for agent loops — choose GPU-resident sizes.

**LM Studio alternative (also native Anthropic compat):**
```bash
lms server start --port 1234
export ANTHROPIC_BASE_URL=http://localhost:1234
export ANTHROPIC_AUTH_TOKEN=lmstudio
claude --model ...
```

## 2. Remote Ollama ("black") from Laptop — Current Best Practices
Do **not** expose Ollama publicly. Options, ranked for this use case (laptop <-> home/lab server):

### A. SSH Local Port Forward (quick, no extra software)
```bash
# One-off (different local port avoids conflict with laptop's own Ollama)
ssh -L 11435:localhost:11434 black

# Then on laptop
export ANTHROPIC_BASE_URL=http://127.0.0.1:11435
export ANTHROPIC_AUTH_TOKEN=ollama
claude --model <tag-on-black>
```

Persistent:
- `autossh` (reconnects on drop).
- systemd `--user` service with `ssh -N -L ...` + `Restart=always`.
- Or a small wrapper script (what Nasim can provide as thin glue).

Many guides (2026) explicitly use this for Claude Code + remote Ollama, including port offset examples (11435).

### B. Tailscale (or WireGuard) — Recommended for "set and forget"
- Install Tailscale on both laptop and black.
- On black: run Ollama bound appropriately (often keep localhost + Tailscale magic, or `OLLAMA_HOST=0.0.0.0` with firewall/Tailscale ACLs restricting to your tailnet only).
- Or use Tailscale Serve to proxy the API with TLS.
- Access via Tailscale MagicDNS IP or name: `http://black:11434` (or custom).
- Zero port-forward hassle, works from anywhere (coffee shop, travel), E2E encrypted, access control.
- Multiple reports and Tailscale's own blog highlight this exact "self-host AI lab + Ollama + remote clients" pattern.

### C. LiteLLM as intermediary (on laptop or black)
Useful when you want:
- Unified endpoint for Claude Code (`ANTHROPIC_BASE_URL` -> LiteLLM :4000).
- Easy remote Ollama config in LiteLLM (`model: ollama/qwen3-coder`, with `api_base` pointing at remote via tunnel/Tailscale).
- Fallbacks (local strong model → weaker local or cheap cloud), logging, load balance, auth.
- Still works post-native (some older LiteLLM bugs with Ollama+Anthropic path were reported; current usage is common).

Example flow (laptop):
- Persistent tunnel or Tailscale to black:11434.
- `litellm --config litellm.yaml` (ollama backend with remote base).
- `export ANTHROPIC_BASE_URL=http://localhost:4000`
- `claude --model my-ollama-qwen`

LiteLLM also lets you put Grok/OpenAI/Gemini etc. behind the same Anthropic-shaped endpoint for Claude Code if desired.

Pre-native proxies (now mostly historical for pure Ollama):
- 1rgs/claude-code-proxy, mattlqx/claude-code-ollama-proxy, UniClaudeProxy, Rust anthropic-proxy, etc. — these translated Anthropic → OpenAI/Gemini/Ollama. Good to know exist if you need non-Ollama backends or extra middleware, but prefer native + simple tunnel first.

Security notes (repeated across sources):
- Never bind Ollama 0.0.0.0 + open firewall to internet.
- Tailscale + localhost (or strict ACLs) is the low-risk pattern.
- SSH tunnels are encrypted and require auth.
- Monitor with `ollama ps`, journal, or LiteLLM observability if used.

## 3. "Grok Code", "Open Code", and Other Frontier Agent Experiences
### Claude Code path (Anthropic binary)
- Now the easiest "frontier-like" agent on local models thanks to native compat.
- For Grok/OpenAI "flavor" inside the same Claude Code UI: use LiteLLM or the older-style proxies to map haiku/sonnet names to Grok/OpenAI/Gemini models.

### OpenCode (opencode / "Open Code")
- Leading **open-source Claude Code alternative**.
- Explicitly designed for multi-provider (75+), first-class Ollama/local support (OpenAI compat or direct), no Anthropic lock-in.
- Terminal agent with similar read/write/execute/tool use.
- Frequently compared favorably for flexibility, cost (free), and local model performance.
- Also supports GitHub Copilot subs, cloud providers, etc.
- Good candidate when you want one agent binary/config that "just works" with remote Ollama via standard OpenAI endpoint.

### Aider (mature, highly recommended for local)
- `pip install aider-chat`
- Native Ollama: `aider --model ollama/qwen3-coder:14b` (or full remote via OpenAI-compat base URL in config/env).
- Excellent git integration, repo map, / commands.
- Often cited as the most practical daily driver for local models in 2026.
- No need for Anthropic format at all.

### IDE / Editor Agents (Continue.dev, Cline, Roo Code, Kilo Code, etc.)
- Continue.dev: Best-in-class Ollama support in VS Code / JetBrains. Set `baseUrl` to remote (via tunnel/Tailscale). Autocomplete + chat + custom agents/commands.
- Cline/Roo/Kilo: Agentic "computer use" style loops inside the editor, full local model support via Ollama/OpenAI providers.
- These give "Claude Code in your IDE" experience against remote black.

### Grok / xAI side specifically
- xAI released **grok-code-fast-1** (and family) — purpose-built fast reasoning model for agentic coding (tool use, planning). Integrated into Cursor, Cline, Roo, opencode, Windsurf, Copilot partners (often with promos).
- Terminal options:
  - grok-cli (multiple projects): open-source agents using xAI Grok API. Some explicitly support Ollama as a provider alternative (`GROKCLI_PROVIDER=ollama` or equivalent).
  - Wrappers that start an Anthropic→Grok proxy + launch the real `claude` binary (so you get the Claude Code UX powered by Grok models via xAI).
- To get "Grok Code" *feel* with **your** Ollama on black: Use one of the open agents above (OpenCode, Aider, Continue, grok-cli variants that accept Ollama) + the strongest local coding model. The model + agent scaffolding matters more than the exact brand name once you are in the tool-calling loop.
- LiteLLM supports xAI provider (for when you want to call real Grok from other tools).

No evidence of a native "Grok speaks Anthropic natively on Ollama" equivalent (unlike Anthropic+Ollama). Use the flexible agents.

### Other mentions
- "ollama launch codex-app" and similar helpers in Ollama ecosystem for launching various coding UIs against models.
- Qwen Code / other vendor "Code" CLIs occasionally surface as direct local alternatives.

## 4. Model Recommendations for Agentic Coding (2026, local via Ollama)
Focus on models proven in real agent loops (tool calling, long context, recovery, multi-file edits) rather than pure HumanEval.

Strong recurring names:
- **Qwen3-Coder / Qwen 3.6 Coder variants (including MoE "Next")**: Frequently top or near-top for local agentic coding. Good tool use, SWE-Bench tuned variants. Size to your GPU (black's 11 GB example in old notes: 7b/14b safe; larger need quantization or more VRAM).
- **GLM-5.1 / GLM cloud via Ollama**: Praised for long-horizon agentic engineering.
- **DeepSeek V4 / Coder V2 (MoE variants)**: Excellent perf/cost, strong on LiveCodeBench etc.
- **Gemma 4 (various sizes, MoE)**: Strong agentic in sub-32B; fast.
- **Kimi K2.x cloud models** (via Ollama cloud if subscribed) or local equivalents.
- Others: Nemotron, MiniMax open weights (newer releases).

**Practical rule:** Pull on black, `ollama ps` or API to check if fully GPU loaded (no heavy CPU offload). For Claude Code / heavy agents, larger context + strong reasoning beats raw size if it fits.

Cloud fallbacks (when local hardware or model ceiling hit): OpenRouter (many of the above), Ollama's own cloud models (glm, kimi, minimax), direct xAI/Grok for grok-code-fast, Anthropic when you want the absolute frontier reference.

## 5. How to Get the Most Benefit (Philosophy for Nasim)
1. **Search current ecosystem first** (this doc is the living record; update via fresh searches before any code).
2. Install the real agent binaries (Claude Code, Aider, Continue, OpenCode, grok-cli variants).
3. Point them at Ollama (native where possible, OpenAI compat otherwise).
4. Secure remote access to black (Tailscale > persistent SSH tunnel > LiteLLM middle).
5. Choose GPU-resident models sized to black.
6. Use the agents' built-in power: permissions, sub-agents, custom skills/prompts, /loop, git workflows.
7. Measure: E2E file-mutating tasks on real repos. Model capability is usually the limiter, not the plumbing.
8. Hybrid: Local fast iteration (small/fast model or laptop) + remote heavy (big model on black) + occasional cloud reference.
9. Thin glue only: persistent tunnel management, env wrappers (`nasim claude`, `nasim aider-remote`), model inventory, one-command status/health.
10. Knowledge lives in `.grok/` (this research + recipes + rules). Sync with global practices. Prefer docs + scripts over heavy packages.

**Anti-patterns to avoid (from history + current reports):**
- Reinventing full API translators when native or LiteLLM exists.
- Exposing Ollama publicly.
- Using models too large for the GPU (CPU split = 10-100x slowdown in agent loops → "nothing happens").
- Blindly assuming "frontier" without verifying tool-use under realistic full system prompt + tools load.
- Forgetting that file ops (Read/Write/etc.) execute on the *client* machine where the agent runs (laptop), model just decides what to do.

## Sources (web results + browsed pages, 2026-06)
- Ollama official blog + docs (claude integration) — primary.
- Multiple Medium/YouTube guides for `ANTHROPIC_BASE_URL` + Ollama (Jan–Jun 2026).
- GitHub: 1rgs/claude-code-proxy (and forks/variants), mattlqx variants — historical proxies.
- LM Studio blog: native Anthropic endpoint.
- Reddit/LocalLLaMA, builder.io comparisons: OpenCode vs Claude Code.
- Aider, Continue.dev ecosystem docs and 2026 roundups ("Best local-first AI coding tools").
- xAI announcements + LiteLLM provider docs for grok-code-fast-1 and grok-cli projects.
- Tailscale blog + community posts on remote Ollama + AI labs.
- Various "best Ollama coding models 2026" roundups (Qwen3-Coder, GLM-5, DeepSeek V4, Gemma 4 dominant for agents).

**Next for Nasim:** Use this as source of truth. Create recipes (Tailscale + Claude Code, Aider remote, Continue remote, thin tunnel helper). Update on every meaningful ecosystem shift. Wipe old custom bridge implementation.

Update date: 2026-06-16. Re-search before major changes.

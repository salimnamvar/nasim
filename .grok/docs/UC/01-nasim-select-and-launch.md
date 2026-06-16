# UC-01: Select remote Ollama on black and launch frontier terminal agent (or configured shell)

**ID:** UC-01  
**Priority:** Primary (the "nasim select" request)  
**Actor:** User on salim-hp laptop  
**Goal:** From one command, choose any supported secure access method to Ollama on black + any supported frontier agent, have the system establish the private path (if needed), verify the endpoint, set correct environment, and hand the user an interactive CLI (the agent REPL or a branded terminal) so they can immediately use it for real work against remote models.

## Preconditions
- SSH key auth to "black" works (or Tailscale up for that option).
- Ollama running on black with at least one model pulled (GPU preferred).
- Desired agent binary installed on laptop (claude, aider, opencode) or user chooses "terminal" fallback.
- nasim script available in PATH or ./bin/nasim.

## Main Success Scenario (SSH tunnel + claude example)
1. User runs `nasim select` (or `nasim select --access ssh-tunnel --agent claude --model qwen3-coder:14b` for non-interactive).
2. nasim presents menu (or uses flags): Access methods (ssh-tunnel [default, always available], tailscale, litellm), Agents (claude, aider, opencode, terminal/shell).
3. User selects "ssh-tunnel" + "claude" + a model known on black (e.g. gemma4 or qwen2.5-coder:14b from `ssh black 'curl .../api/tags'`).
4. nasim:
   - Picks a free local port (e.g. 11435).
   - Launches background `ssh -N -L $port:localhost:11434 black` (with ServerAlive, trap to kill on exit).
   - Probes `curl -sf --max-time 8 http://127.0.0.1:$port/api/tags` → succeeds, shows models.
   - Builds env: ANTHROPIC_AUTH_TOKEN=ollama, ANTHROPIC_BASE_URL=http://127.0.0.1:11435, ANTHROPIC_API_KEY="", CLAUDE_CODE_DISABLE...=1 .
   - Optional: extra NASIM_REMOTE_URL etc for the thin wrapper compatibility.
5. nasim execs `claude --model <chosen>` (or `ollama launch claude ...` path if selected).
6. User is now in the full Claude Code terminal agent, but all model intelligence comes from black's Ollama over the private SSH tunnel. File edits, bash, etc. happen locally on laptop.
7. On agent exit (or Ctrl-D), nasim cleans up tunnel (trap).

## Alternative Flows
- **Tailscale:** If selected and `tailscale status` shows healthy + black in tailnet, use `http://black:11434` (MagicDNS). No local forward. Same probe + launch.
- **LiteLLM:** nasim writes a temp or ~/.config/nasim/litellm.yaml pointing the chosen base (inner ssh/ts) as ollama backend, starts `litellm --config ... --port 4000` (bg, trap kill), sets ANTHROPIC_BASE_URL=http://127.0.0.1:4000 (or equiv for aider). User gets unified endpoint + possible future fallbacks.
- **Aider / opencode:** Different env (OLLAMA_API_BASE or OPENAI_BASE_URL) + `--model ollama/...` or provider flag. Same transport setup underneath.
- **"terminal" choice:** After probe success, export all relevant vars (ANTHROPIC_* + OLLAMA_*), set fancy PS1="nasim[black:${model}] $ ", exec $SHELL -i. User can now type `claude --model X`, `aider ...`, raw `curl $ANTHROPIC_BASE_URL/...`, etc.
- **Persistent tunnel already running:** User can choose "existing" — nasim skips launching forward, just uses the pre-forwarded port (or fixed 11435) and still does probe.
- **Dry / test mode (for CI):** `nasim ... --dry-run` prints the would-be command + effective env without exec or tunnel. Harness asserts the strings.

## Postconditions (Success)
- Private encrypted path established (or confirmed).
- Endpoint reachable and returns expected /api/tags (contains the chosen model).
- Chosen agent (or shell) is running with exactly the env that routes model calls to black.
- No public ports opened. No model weights moved to laptop.
- On cleanup: tunnels killed, no leftover processes from nasim.

## Failure Handling
- Probe fails → clear error + "check black ollama, network, port conflict", offer retry or different access. Never launch agent.
- Agent binary missing → "not found, install via ... or choose different agent / terminal mode".
- User aborts select → clean no-op.

## Non-Functional
- Low latency overhead (SSH forward or Tailscale is fine for token streaming).
- Works in low-dependency envs (pure bash + coreutils + ssh + curl).
- Reproducible: same flags or recorded choices produce identical routing.
- Observable: `nasim status` / `nasim doctor` shows current effective URL + reachability.

## Related
- See C4 context.
- Recipes: remote-claude-code.md, tunnel-setup.md, aider-continue-opencode.md, litellm-for-mixing.md .
- Research 2026-06-16 for why these (native compat, no custom bridge).
- P-Invariants in sprint.md (P01 private, P02 probe-before-launch, P03 laptop execution, P04 CI-per-feature).
- Implementation tested via tests/nasim-features.sh (live on black + matrix in .github/workflows/ci.yml).

## Open (tied to ODs)
- Exact opencode flags (OD-01).
- Auto vs explicit litellm (OD-02).

---

Implementation of this UC is the heart of the sprint. Every access+agent pair must pass the test harness before "done".
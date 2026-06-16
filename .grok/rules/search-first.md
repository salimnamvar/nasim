# Rule: Search Current Solutions First (Never Reinvent the Wheel)

This is the defining discipline of Nasim.

## Mandate
Before designing, coding, or even writing detailed "how to" beyond a pointer:
1. Perform fresh, deep searches (web, GitHub, official docs, X/recent discussions, Reddit/LocalLLaMA, etc.).
2. Open and read the primary sources (Ollama blog/docs, agent project READMEs, Tailscale AI self-host posts, LiteLLM tutorials, Aider/Continue config examples).
3. Document findings (new entry or update under `.grok/research/` with date).
4. Only then decide: "existing solution X does 95% of what we need" → use it + thin documented recipe. Or "real gap after checking Y and Z" → then design minimal addition.

## Examples of What Changed the Game (do not re-solve)
- Ollama native Anthropic Messages API compatibility (v0.14+, Jan 2026) → entire custom bridge/translator layer became unnecessary for Claude Code + Ollama.
- Official `ollama launch claude`, `ANTHROPIC_BASE_URL` support in the real Claude Code binary.
- Tailscale / autossh patterns for remote Ollama (widely documented and used for AI labs).
- Aider native Ollama + Continue first-class ollama provider + OpenCode multi-provider design.
- LiteLLM as the universal proxy/router when you need mixing/auth/observability.
- grok-code-fast-1 landing in multiple agent frontends.

## Anti-Patterns
- "We will build a better proxy/bridge/tunnel manager from scratch" without first proving no current tool (or combo) meets the need.
- Assuming the 2025-era custom Nasim v1 approach is still required.
- Claiming "best model for agents" or "only way to do remote" without dated search evidence + reproduction on the actual hardware (black + laptop).
- Adding features because "it would be nice" instead of because searches showed users hitting a real, unsolved friction.

## In Practice for This Project
- Every significant edit to recipes or research must reference (or update) the latest search-backed findings.
- When user asks for a capability, first response inside the agent loop should be "I searched X Y Z; here is the current best existing path + recipe link. Gap? Then we add the smallest glue."
- Keep a short "last searched" note + key sources in the research file.

This rule keeps Nasim lean, correct, and actually helpful instead of another abandoned custom stack.

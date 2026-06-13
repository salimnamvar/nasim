# Nasim — Audit Report

**Date:** 2026-06-13
**Branch:** feature/implementation
**Scope:** Why `nasim start` did not route Claude Code to Ollama; fix and success criteria.

---

## 1. Problem Statement

After running `nasim start`, Claude Code continued to use Anthropic cloud rather than
the local Ollama instance on `black`. A `qwen3.6:latest` model was manually added via
Claude Code's `/model` interface but also failed to respond.

---

## 2. Root Cause

### RC-01 — Wrong endpoint URL (Critical)

`nasim.sh` set:
```
ANTHROPIC_BASE_URL=http://192.168.70.125:11434
```
Port `11434` is Ollama's native API (`/api/chat`). It does not implement the
Anthropic Messages API (`POST /v1/messages`). Claude Code talks Anthropic protocol,
so every request errored or timed out.

### RC-02 — Bridge bound to localhost only (Contributing)

The `nasim-bridge.service` on `black` listens on `127.0.0.1:8080` — not on the LAN
IP. Even if `nasim.sh` had used port `8080`, the direct network call would have been
refused. The bridge is only reachable via an SSH tunnel.

### RC-03 — Custom model entry not needed (Confusion)

The manually-added `qwen3.6:latest` entry in Claude Code's `/model` interface was
pointing at the wrong URL (Ollama port direct). Even if the URL were correct, this
approach duplicates what `ANTHROPIC_BASE_URL` already does. The env-var redirect
causes the bridge's `/v1/models` endpoint to populate the model list automatically
— no manual entry required.

---

## 3. Fix Applied

`bin/nasim.sh` was rewritten to:

1. **`nasim start`**
   - Kill any existing SSH tunnel on port `18080`
   - Open `ssh -f -N -L 18080:127.0.0.1:8080 black`
   - Set `ANTHROPIC_BASE_URL=http://localhost:18080`
   - Set `ANTHROPIC_AUTH_TOKEN=nasim`
   - Run bridge health check and print available models

2. **`nasim stop`**
   - Kill tunnel by stored PID (fallback: `pkill` pattern)
   - `unset` all four env vars
   - Write `anthropic` to state file

3. **`nasim status`** — shows backend, tunnel liveness, bridge health

4. **`nasim models`** — lists Ollama models without starting/stopping

**No changes** to `nasim-bridge.service` on `black` were required. The bridge is
correct; only the client-side routing was broken.

---

## 4. Architecture

```
salim-hp                          black (192.168.70.125)
─────────────────────             ────────────────────────────
claude (CLI)                      nasim-bridge (port 8080)
  │                                   │
  │ Anthropic API                     │ translates: Anthropic ↔ Ollama
  ▼                                   ▼
localhost:18080 ──SSH tunnel──► 127.0.0.1:8080
                                       │
                               Ollama (:11434)
                                       │
                               qwen3.6:latest / qwen2.5-coder:*
```

When `ANTHROPIC_BASE_URL=http://localhost:18080` is set:
- Claude Code sends all API requests to the bridge
- Claude Code calls `GET /v1/models` on startup → bridge returns Ollama model list → those appear in `/model`
- When user picks a model via `/model`, the model name is sent in the request body → bridge maps it to the correct Ollama tag

When `nasim stop` is called:
- Tunnel is destroyed → bridge is unreachable
- `ANTHROPIC_BASE_URL` is unset → Claude Code reverts to `api.anthropic.com`
- The custom model entry manually added via `/model` remains in Claude Code's config but is harmless (bridge URL is no longer active)

---

## 5. Success Criteria

| # | Criterion | Test |
|---|-----------|------|
| SC-01 | Bridge on black responds to health check via SSH | TC01 |
| SC-02 | `nasim start` opens SSH tunnel on port 18080 | TC02 |
| SC-03 | `ANTHROPIC_BASE_URL` is set to `http://localhost:18080` | TC02 |
| SC-04 | Bridge health check passes through the tunnel | TC03 |
| SC-05 | Bridge returns Ollama model list through tunnel | TC04 |
| SC-06 | A non-streaming message round-trip completes end-to-end | TC05 |
| SC-07 | `nasim status` reports correct state while running | TC06 |
| SC-08 | `nasim stop` kills tunnel process | TC07 |
| SC-09 | `nasim stop` unsets `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` | TC07 |
| SC-10 | Port 18080 is closed after stop | TC08 |
| SC-11 | `nasim status` reports `anthropic` after stop | TC09 |
| SC-12 | Second `nasim start` replaces old tunnel without leaving orphans | TC10 |

All 12 criteria must pass for the fix to be considered complete.

---

## 6. Known Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| Env vars are shell-session-scoped | New terminal windows after `nasim start` will NOT have `ANTHROPIC_BASE_URL` set | Source `~/.bashrc` or run `nasim start` in each new terminal (or use `direnv`) |
| SSH must succeed without passphrase | `nasim start` fails if SSH key agent is not available | Ensure `ssh-agent` is loaded with the key for `black` |
| Tunnel runs per-shell, not as a service | If the shell exits, tunnel dies | For persistent use, run `nasim-bridge-local.service` (future work) |

---

## 7. Removed Approach (Custom Model Entries)

The "Add custom model" feature in Claude Code's `/model` UI stores a model entry with
a fixed base URL in Claude Code's internal settings. This approach has two problems:

1. The URL must be correct at all times (not just when nasim is active)
2. The entry must be manually deleted when nasim is no longer needed

The `ANTHROPIC_BASE_URL` redirect approach is simpler, more reliable, and fully
reversible with `nasim stop`.

If you manually added a qwen entry via `/model`, it will remain in Claude Code's
settings but be harmless after `nasim stop` (the URL is unreachable). You can
remove it by opening Claude Code settings and deleting the custom model entry.

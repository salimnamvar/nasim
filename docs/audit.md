# Nasim — Audit Report

**Date:** 2026-06-13
**Branch:** feature/implementation
**Scope:** Correct, tested start/stop/status/models for routing Claude Code on
`salim-hp` (client) to Ollama on `black` (server) through the Nasim Bridge, with
a guaranteed full rollback to Anthropic defaults on `nasim stop`.

---

## 1. Topology

```
salim-hp (client)                         black (server, 192.168.70.125)
──────────────────────────                ────────────────────────────────────
claude 2.1.177 (real binary)              nasim-bridge.service  (127.0.0.1:8080)
  │  Anthropic Messages API                 │  translator.py: Anthropic <-> Ollama
  ▼                                         ▼
localhost:18080 ──SSH tunnel (-L)──► 127.0.0.1:8080
                                            │
                                    Ollama 0.30.7 (:11434)  — GTX 1080 Ti 11GB
```

The bridge listens on `127.0.0.1` only — it is never exposed on the LAN. The sole
path from the client is the SSH local-forward `nasim start` opens.

---

## 2. Ollama Model Inventory (audited on black, 2026-06-13)

`ollama list` on black, cross-checked against `GET /v1/models` and `/health`:

| Ollama tag          | Size   | Bridge role        | Appears in /model picker |
| ------------------- | ------ | ------------------ | ------------------------ |
| `qwen2.5-coder:14b` | 9.0 GB | **default** (opus/sonnet/fable map here) | yes |
| `qwen2.5-coder:7b`  | 4.7 GB | **fast** (haiku maps here) | yes |
| `gemma4:latest`     | 9.6 GB | extra (selectable)  | yes |

Bridge env (systemd unit): `DEFAULT_MODEL=qwen2.5-coder:14b`,
`FAST_MODEL=qwen2.5-coder:7b`, `BRIDGE_NUM_CTX=32768`.

Model name mapping (`translator.map_model`):

- a name containing `:` is treated as a literal Ollama tag and passed through
  (this is how `/model qwen2.5-coder:7b` hot-swaps inside the CLI);
- a name containing `haiku` → fast model;
- everything else (`opus`, `sonnet`, `fable`, unknown) → default model.

Consequence: even a stale `model: "opus"` in settings still routes to a real
Ollama model, so requests never fail for lack of a perfect model name.

---

## 3. Root Causes Fixed

### RC-01 — Selected model was never rolled back (Critical, new)

Claude Code stores the active `/model` selection in `~/.claude/settings.json`
(`"model": "opus"`). The previous `nasim.sh` managed the tunnel, env vars, and
the picker cache but **never touched the selected model**. So picking an Ollama
model via `/model` (e.g. `gemma4:latest`) wrote a colon-tagged name into
`settings.json` that survived `nasim stop` — leaving a dangling, Anthropic-invalid
model after rollback.

**Fix:** `nasim start` backs up the current `model` value to
`~/.nasim_saved_model` (once per session) and selects the bridge default;
`nasim stop` restores the exact saved value (or removes the key if it was
absent) and deletes the backup.

### RC-02 — Injected-model tracking lost on repeated start (High, new)

The old eject tracked only models added by the *most recent* start. A second
`nasim start` found everything already present, wrote an empty tracking file, and
`nasim stop` then ejected nothing — Ollama entries leaked into the picker after
rollback.

**Fix:** every injected entry is stamped `{"_nasim": true}`. Eject removes all
marked entries regardless of how many times start ran. Injection is idempotent.

### RC-03 — Wrong endpoint / LAN-bound bridge (Critical, prior, confirmed fixed)

Documented in the prior revision: Ollama's native `:11434` does not speak the
Anthropic Messages API, and the bridge binds localhost-only. Both are correctly
handled by routing through `ANTHROPIC_BASE_URL=http://localhost:18080` over the
SSH tunnel. Confirmed still correct.

---

## 4. Rollback Contract (what `nasim stop` guarantees)

| State touched on start            | Restored on stop                          |
| --------------------------------- | ----------------------------------------- |
| SSH tunnel (`-L 18080:…:8080`)    | killed by PID, with `pkill` fallback      |
| `ANTHROPIC_BASE_URL` + auth token | `unset`                                   |
| telemetry/traffic env vars        | `unset`                                   |
| `settings.json` `model`           | restored to pre-start value (or removed)  |
| `~/.claude.json` picker cache     | all `_nasim`-marked entries removed        |
| `~/.nasim_state`                  | set to `anthropic`                        |
| `~/.nasim_saved_model`            | deleted                                   |

`~/.claude.json` is edited surgically (only the marked cache entries) — session
history and project data are never rewritten.

---

## 5. Verification (run on salim-hp ↔ black, 2026-06-13)

### 5.1 Test suite — `bash test/test_nasim.sh`

**43 assertions, 43 passed, 0 failed.** Coverage:

| Area | Tests |
| --- | --- |
| Bridge reachable over SSH; health/ok | TC01 |
| `start` opens tunnel, sets all env vars, writes state + backup | TC02 |
| Health + model list + message round-trip through the tunnel | TC03–TC05 |
| Ollama models injected (marked) into the picker cache | TC06 |
| `start` selects the bridge default model | TC07 |
| `status` reports running state | TC08 |
| Simulated `/model` pick of an Ollama tag | TC09 |
| `stop` full rollback: env unset, tunnel dead, model healed + restored, zero injected left, state files cleared | TC10 |
| Bridge unreachable after stop | TC11 |
| `status` reports `anthropic` after stop | TC12 |
| Double `start` idempotent (no orphan tunnel, no duplicate/lost tracking) | TC13 |
| Double `stop` safe | TC14 |
| Usage on unknown verb | TC15 |
| Baseline `/model` selection intact after the whole run | FINAL |

### 5.2 Real-binary end-to-end

With `nasim start` active, the real `claude` 2.1.177 binary issued a request that
the bridge served (journal on black):

```
messages: model=qwen2.5-coder:7b -> qwen2.5-coder:7b stream=True msgs=2 tools=0
POST /v1/messages?beta=true HTTP/1.1 200 OK
POST http://localhost:11434/api/chat HTTP/1.1 200 OK
```

A direct non-streaming round-trip returns a clean answer in <1s:

```
{"type":"message","content":[{"type":"text","text":"Pong!"}], ...}
```

After `nasim stop`: `ANTHROPIC_BASE_URL` unset and `settings.json` model restored
to `opus`. Rollback verified.

---

## 6. Known Limitations

| Limitation | Impact | Mitigation |
| --- | --- | --- |
| **Small-model agentic reliability** | `qwen2.5-coder:7b` in the full Claude Code agentic loop sometimes emits spurious tool calls (e.g. invoking a Skill) instead of answering, and can loop. Plain single-turn Q&A and direct requests are fine. | Use `qwen2.5-coder:14b` (default) for agentic work; raise VRAM / swap `DEFAULT_MODEL` to a stronger model on the bridge service. The bridge already salvages malformed tool calls. This is a model-capability bound, **not** a nasim plumbing fault. |
| Env vars are shell-session-scoped | A `claude` launched in a *different* terminal than the one that ran `nasim start` will not be redirected | Run `nasim start` then `claude` in the same shell |
| SSH must succeed without a passphrase | `nasim start` fails fast (and tears down) if `ssh black` needs interaction | Load `ssh-agent` with the key for `black` |
| Tunnel is per-shell, not a service | Tunnel dies when the shell exits | Acceptable; `nasim start` re-establishes it |

---

## 7. Success Criteria

| # | Criterion | Test |
|---|-----------|------|
| SC-01 | Bridge on black responds to health check via SSH | TC01 |
| SC-02 | `nasim start` opens SSH tunnel on port 18080 | TC02 |
| SC-03 | All routing/telemetry env vars set on start | TC02 |
| SC-04 | Bridge health passes through the tunnel | TC03 |
| SC-05 | Bridge returns Ollama model list through the tunnel | TC04 |
| SC-06 | Non-streaming message round-trip completes | TC05 |
| SC-07 | Ollama models injected into `/model` picker | TC06 |
| SC-08 | Start selects the bridge default model | TC07 |
| SC-09 | `status` correct while running | TC08 |
| SC-10 | `stop` heals an Ollama `/model` pick and restores the original | TC09–TC10 |
| SC-11 | `stop` unsets env, kills tunnel, clears state | TC10 |
| SC-12 | Port 18080 closed after stop | TC11 |
| SC-13 | `status` reports `anthropic` after stop | TC12 |
| SC-14 | Double start leaves no orphans and no duplicate/lost tracking | TC13 |
| SC-15 | Double stop is safe | TC14 |
| SC-16 | Baseline `/model` selection intact after a full cycle | FINAL |
| SC-17 | Real `claude` binary routes to Ollama through the bridge | §5.2 |

All criteria pass.

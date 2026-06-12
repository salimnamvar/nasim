# Nasim

Nasim is a fully local AI coding agent: the Claude Code CLI, re-identified as
"Naseem" and routed to a self-hosted open model instead of a cloud API.

It keeps Claude Code's complete agent — the same tool loop, permission system,
session history, and project-context handling — and swaps only the model
backend. The agent runs on your workstation with full local filesystem access;
the model runs on a LAN GPU machine through a small translation Bridge.

## What it does

- Runs the unmodified Claude Code agent under the `nasim` command, with a
  separate identity and config root (`~/.nasim`, `NASEEM.md`) so it coexists
  with a real Claude Code install — no shared state.
- Serves all inference from a local Ollama model (`qwen2.5-coder`), reached over
  an on-demand SSH tunnel. No request leaves the LAN; auto-update, telemetry,
  and error reporting are disabled.
- Translates between the Anthropic Messages API and Ollama's chat API in a
  ~250-line Bridge, including streaming SSE and tool calling, with a salvage
  layer that recovers tool calls smaller models emit as plain text.
- Stays current with Claude Code: `sync-from-upstream.sh` downloads the latest
  release binary and re-applies the identity transform in one command.

## Architecture

```
salim-hp (client)                         black (server)
─────────────────────────                 ─────────────────────────
nasim wrapper                             nasim-bridge.service (:8080)
  └─ naseem binary  ── SSH tunnel ──►        FastAPI proxy + translator
     (agent + tools)   :8080→:8080             └─► Ollama (:11434)
     local filesystem                              qwen2.5-coder:14b / :7b
```

The agent loop stays on the client so file and shell tools act on the client's
filesystem. The Bridge is a stateless proxy: no loop logic, no tool execution.
Tunnel latency (~2 ms) is negligible against multi-second local inference.

## How the rename works

Claude Code ships as a bun-compiled binary with its JavaScript bundle embedded
as plain text. `naseem` is the same byte length as `claude`, so
`scripts/patch-binary.py` does an offset-safe in-place replacement
(`claude→naseem`, `Claude→Naseem`, `CLAUDE→NASEEM`) — ~11.5k substitutions —
producing a working binary whose config root, env vars, and branding are all
renamed. No source access or recompilation needed.

## Install

Server (run from the client; acts on the server over SSH):

```bash
./scripts/install-server.sh black
```

Client:

```bash
./scripts/sync-from-upstream.sh      # download + patch latest Claude Code
./scripts/install-client.sh          # install ~/.local/bin/nasim
nasim "say hello"
```

## Update

```bash
./scripts/sync-from-upstream.sh      # re-patch the newest release
./scripts/install-client.sh
```

## Development

```bash
# Bridge unit tests (translator)
python -m pytest bridge/tests -q

# End-to-end tests (requires server live + client installed)
./scripts/integration-test.sh

# Rename audit (no claude identity left in the binary)
./scripts/audit-rename.sh
```

## Layout

| Path | Purpose |
| --- | --- |
| `bridge/server.py` | FastAPI proxy: `/v1/messages`, `/health`, `/v1/models` |
| `bridge/translator.py` | Anthropic ↔ Ollama translation + tool-call salvage |
| `bridge/tests/` | Translator unit tests |
| `scripts/patch-binary.py` | Same-length identity patch of the Claude Code binary |
| `scripts/sync-from-upstream.sh` | Download latest release and re-patch |
| `scripts/install-server.sh` | Deploy Ollama + Bridge to the model server |
| `scripts/install-client.sh` | Install the `nasim` command and seed `~/.nasim` |
| `scripts/integration-test.sh` | End-to-end stack tests |
| `bin/nasim` | Client wrapper: tunnel + env + exec |
| `NASEEM.md` | Seed global context for `~/.nasim/NASEEM.md` |
| `docs/` | Idea, validation, and development blueprints |

## Notes on model choice

The agent loop, tool execution, and translation are validated end-to-end. Raw
agentic reliability depends on the model and GPU: `qwen2.5-coder:14b` on an
11 GB GPU handles single, explicit tool calls well; long multi-tool agentic
chains are slower and less consistent than a frontier cloud model. A larger
model (`qwen2.5-coder:32b`, `qwen3-coder`) on more VRAM closes that gap — set
`DEFAULT_MODEL` on the `nasim-bridge` service to switch, no code change.

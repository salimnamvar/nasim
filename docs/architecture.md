# Architecture

Nasim is a decoupled Python package plus a thin bash shim. A change in one
concern touches one module.

## Topology

```
client                                       server (configurable)
────────────────────────                     ─────────────────────────────────
claude (real binary)                          nasim-bridge (127.0.0.1:8080)
  │  Anthropic Messages API                     │  Anthropic <-> Ollama translation
  ▼                                             ▼
localhost:18080 ──SSH -L──────────────────►  Ollama (:11434)
```

The bridge binds to loopback on the server; the SSH local-forward `nasim start`
opens is the sole access path.

## Layers

```
                       cfg/nasim.toml  ──►  Config (single source)
                                              │
        CLIENT (src/nasim/runtime/)                 SERVER (src/nasim/bridge/)
        ──────────────────────────                  ──────────────────────────
        NasimController                              server.py (thin FastAPI)
          ├─ SSHTunnel                                 └─ translator/ (pure, no I/O)
          ├─ ModelPicker                                    request / response / streaming
          ├─ ClaudeSettings                                 model_map / blocks / content
          └─ StateStore                                     tool_salvage / schema_coerce
        cli.py  ──►  bin/nasim.sh (shim)                    tokens / sse
```

## Module responsibilities (one job each)

### Client — `src/nasim/runtime/`

| Class / module | Single responsibility |
| --- | --- |
| `SSHTunnel` | Open / kill / probe the `-L` forward; owns the PID file. |
| `ModelPicker` | Marker-based inject/eject of Ollama models in the `~/.claude.json` picker cache. |
| `ClaudeSettings` | Back up and restore the active `model` selection. |
| `StateStore` | Persist backend state; emit the env directives the shim sources. |
| `NasimController` | Orchestrate start/stop/status/models from the four helpers. |
| `cli.py` | argparse front door for `python -m nasim`. |
| `RuntimePaths` | Every runtime/Claude path derived from one root (`~/.nasim`, `~/.claude`). |

### Server — `src/nasim/bridge/`

| Module | Single responsibility |
| --- | --- |
| `server.py` | HTTP transport only — routes, request/response shells, streaming wiring. |
| `translator/request` | `anthropic_to_ollama` — build the Ollama chat body. |
| `translator/response` | `ollama_to_anthropic` — non-streaming result. |
| `translator/streaming` | Emit the Anthropic SSE event sequence. |
| `translator/tool_salvage` | Recover tool calls a model emitted as text. |
| `translator/schema_coerce` | Coerce tool-call arguments to the tool's JSON schema. |
| `translator/model_map` | Resolve a requested model name to an Ollama tag. |
| `translator/blocks · content · tokens · sse` | Block builders, content flatteners, token estimate, SSE formatting. |

## Boundary rules

1. **`translator/` performs no I/O** — dict-in / dict-out, so the hard part is
   exhaustively unit-testable without a network or a model.
2. **`server.py` performs no translation** — it awaits Ollama and hands raw dicts
   to the translator.
3. **`bin/nasim.sh` holds no logic** — it runs `python -m nasim`, sources the
   generated `env.sh` (the only thing that must happen in the calling shell), and
   deletes it.
4. **Config is injected, never read ad hoc** — only the config loader reads the
   environment.

## Why a package + bash shim, not pure bash

The toggle must `export` environment variables into the *calling* shell, which
only a sourced shell function can do. Everything else — tunnel control, JSON
surgery on the picker cache, model backup/restore, health checks, translation —
is logic that deserves unit tests and OOP structure. So the shim is ~30 lines
that source a generated `env.sh`; all decisions live in the package.

## Code style

Google Python Style Guide plus project extensions: `a_`-prefixed arguments,
single `return` per function, `(success, result)` tuple returns where a call can
fail, Google docstrings, 120-column lines, `black` + `ruff` + `isort`.

## Protocol references

- Anthropic Messages API: https://docs.anthropic.com/en/api/messages
- Ollama chat API: https://github.com/ollama/ollama/blob/main/docs/api.md

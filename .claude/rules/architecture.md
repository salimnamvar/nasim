# Architecture & Code Design

The design rule for this project: **a change in one concern touches one module.**

## Layered decomposition

```
                       cfg/nasim.toml  ──►  config.Config  (single source)
                                              │
              ┌───────────────────────────────┴───────────────────────────┐
        CLIENT SIDE (runtime/)                              SERVER SIDE (bridge/)
        ────────────────────────                            ────────────────────
        controller.NasimController                          server.py (thin FastAPI)
          ├─ tunnel.SSHTunnel                                 │ delegates to:
          ├─ picker.ModelPicker                               └─ translator/ (pure, no I/O)
          ├─ settings.ClaudeSettings                              ├─ model_map
          └─ state.StateStore                                     ├─ request   (anthropic→ollama)
        cli.py  ──►  bin/nasim.sh (thin shim)                     ├─ response  (ollama→anthropic)
                                                                  ├─ streaming (SSE)
                                                                  ├─ tool_salvage
                                                                  ├─ schema_coerce
                                                                  ├─ tokens
                                                                  └─ sse
```

## Module responsibilities (one job each)

### Client side — `src/nasim/runtime/`

| Class / module | Single responsibility |
| --- | --- |
| `SSHTunnel` | Open / kill / probe the `-L` forward. Owns the PID file. |
| `ModelPicker` | Inject / eject Ollama models in `~/.claude.json` picker cache, marker-based and idempotent. |
| `ClaudeSettings` | Back up and restore the `model` selection in `settings.json`. |
| `StateStore` | Persist backend state + emit the env directives file the shim sources. |
| `NasimController` | Orchestrate start/stop/status/models using the four above. No transport details. |
| `cli.py` | argparse front door for `python -m nasim`. Parses, calls controller, prints. |

### Server side — `src/nasim/bridge/`

| Module | Single responsibility |
| --- | --- |
| `server.py` | HTTP transport only: routes, request/response shells, streaming wiring. No translation logic. |
| `translator/model_map` | Resolve a requested model name → an Ollama tag. |
| `translator/request` | `anthropic_to_ollama(body)` — build the Ollama `/api/chat` body. |
| `translator/response` | `ollama_to_anthropic(resp, …)` — non-streaming result. |
| `translator/streaming` | `stream_ollama_to_anthropic(chunks, …)` — emit Anthropic SSE. |
| `translator/tool_salvage` | Recover tool calls a model emitted as text. |
| `translator/schema_coerce` | Coerce tool-call arguments to the tool's JSON schema. |
| `translator/tokens` | Heuristic token estimate for `count_tokens`. |
| `translator/sse` | Format a single server-sent event. |

## Boundary rules

1. **`translator/` performs no I/O.** No `httpx`, no file reads, no sockets,
   no env reads (config is passed in). Dict-in / dict-out only. This is what
   makes the hard part 100% unit-testable.
2. **`server.py` performs no translation.** It awaits Ollama, hands raw dicts to
   `translator`, and streams the result. If you are writing an `if` about
   message shape in `server.py`, it belongs in `translator`.
3. **`bin/nasim.sh` holds no logic.** It sources the env directives file that
   `python -m nasim` writes, prints nothing it computed itself. Env export must
   happen in the user's shell, which is the *only* reason the shim exists.
4. **Config is injected, never imported ad hoc.** A module that needs a host or
   model receives it from `config.Config`; it does not read `os.environ`
   directly (except `config.py` itself).

## Python style (project standard)

Google Python Style Guide plus these extensions:

- Arguments prefixed `a_` (`a_body`, `a_tool_names`).
- Private attributes `_single_underscore`.
- **Single `return` per function**; declare `result` / `success` at the top,
  assign through `if/elif/else`, return once. Type-guard early returns allowed.
- Methods that can fail return `Tuple[bool, Optional[T]]` — `(success, result)`.
  `success=True` even when the result is empty, as long as the operation ran.
- Google docstrings on every module, class, public function, and `@property`.
- 120-col lines; `black --line-length 120`; `ruff`; `isort` (Google profile).
- Absolute imports only. Specific exception types; log and raise the same string.

## Why a Python package + bash shim (not pure bash)

The toggle must `export` env vars into the *calling* shell, which only a sourced
shell function can do. Everything else — tunnel control, JSON surgery on the
picker cache, model backup/restore, health checks — is logic that deserves unit
tests and OOP structure. So the shim is ~30 lines that source a generated
`env.sh`; all decisions live in the Python package.

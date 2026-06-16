# Nasim — Project Context for Claude Code

Nasim routes the real Claude Code CLI to **local Ollama models on a remote
server** instead of the Anthropic cloud, with a guaranteed one-command rollback.

It does **not** fork or patch the `claude` binary. It drives the real CLI
through environment variables and surgical, fully-reverted edits to its config,
fronted by a translating proxy (the *bridge*) that speaks the Anthropic Messages
API on one side and Ollama's chat API on the other.

## Topology

```
salim-hp (client)                         server (e.g. black)
─────────────────────────                 ───────────────────────────────────
claude 2.1.x (real binary)                nasim-bridge (127.0.0.1:8080)
  │  Anthropic Messages API                 │  Anthropic <-> Ollama translation
  ▼                                         ▼
localhost:18080 ──SSH tunnel (-L)──►  127.0.0.1:bridge_port
                                            │
                                    Ollama (:11434)
```

The bridge binds to `127.0.0.1` on the server only. The SSH local-forward that
`nasim start` opens is the sole access path. The server is **configurable** —
see `cfg/nasim.toml`; point it anywhere.

## Repository layout

```
cfg/        Single source of configuration (TOML). Change the server here.
bin/        nasim.sh (thin sourced shim) + loop.sh (CI/CD loop runner)
src/nasim/  The package — all business logic lives here, fully testable
  config.py         Config loader: cfg/ defaults → env overrides
  runtime/          Client-side toggle (tunnel, picker, settings, state, controller, cli)
  bridge/           Server-side proxy
    server.py       Thin FastAPI app (no business logic)
    translator/     Pure Anthropic<->Ollama translation (no I/O)
    deploy/         systemd unit template + deploy script
test/       unit / integration / capability / e2e / rollback / fixtures
docs/       architecture, methodology, capability-matrix, runbook, model-guidance
.claude/    Knowledge base: project policies (rules/)
```

## Design principles (non-negotiable)

- **Decoupled, OOP, separation of concerns, DRY.** Every module has one job.
- **Pure core.** `bridge/translator/` does dict-in / dict-out translation with
  zero I/O — so it is exhaustively unit-testable without a network or a model.
- **Thin edges.** `bin/nasim.sh` and `bridge/server.py` hold no business logic;
  they wire transport to the package. Logic that can be tested lives in classes.
- **One config source.** `cfg/nasim.toml` → environment-variable overrides.
  Nothing hard-codes a host, port, or model name.
- **Re-provable rollback.** `nasim stop` returns the machine to exactly the
  Claude Code state it had before `nasim start`. This is a tested contract.

## Python style

Follows the Google Python Style Guide plus project extensions: `a_`-prefixed
arguments, single `return` per function, `(success, result)` tuple returns where
a call can fail, Google docstrings, 120-col lines, `black` + `ruff` + `isort`.
See `.claude/rules/architecture.md`.

## Environment

- **Client (salim-hp):** Python 3.12 (miniconda base). Dev deps: `pytest`,
  `httpx`, `fastapi`, `uvicorn` (present). Editable install: `pip install -e ".[dev]"`.
- **Server (black):** the bridge runs from its own venv at
  `/home/salim/nasim-bridge/.venv` under systemd unit `nasim-bridge.service`.
  Redeploy with `make deploy` (rsync `src/` + restart).

## Common commands

```bash
make help            # list targets
make lint            # ruff + black --check
make test            # unit tests (fast, no network)
make deploy          # push bridge to the server and restart the service
make integration     # tests against the live bridge (needs SSH + service up)
make capability      # the full Anthropic-API capability matrix
make e2e             # real claude binary writes/edits files via Ollama
make loop            # full CI/CD loop: lint→unit→deploy→integration→capability→e2e
nasim start          # route Claude Code to Ollama (run, then launch `claude`)
nasim stop           # full rollback to the Anthropic cloud
```

## Project policies (read before changing the matching area)

| Topic | File |
| --- | --- |
| Module boundaries, OOP design, Python style | `.claude/rules/architecture.md` |
| Anthropic↔Ollama translation contract + edge cases | `.claude/rules/bridge-protocol.md` |
| Test taxonomy, capability matrix, exit criteria | `.claude/rules/testing.md` |
| The plan→…→monitor CI/CD loop | `.claude/rules/cicd-loop.md` |
| `cfg/` schema and server reconfiguration | `.claude/rules/config.md` |
| Known traps and what not to do | `.claude/rules/anti-patterns.md` |
| Current state, decisions, matrix progress | `.claude/rules/sprint.md` |

## Critical context (read before changing the bridge)

The bridge plumbing is sound; the failure mode users hit is **model-capability
bound under realistic load** (full system prompt + ~15 tools + multi-step). A
capable coder model (`qwen2.5-coder:14b`) produces correct `tool_use` blocks in
both streaming and non-streaming modes; weak/general models degrade and emit
malformed or missing tool calls under that load. The bridge maximizes robustness
(tool-call salvage + schema-aware coercion) but cannot exceed the local model's
ceiling. See `.claude/rules/anti-patterns.md` and `docs/model-guidance.md`.

Nasim toggles Claude Code between the Anthropic cloud and a local Ollama backend
running on the `black` machine, reached over an SSH tunnel to the Nasim Bridge.

## What it does

- `nasim start` — opens an SSH tunnel to the bridge on `black`, points Claude
  Code at it (`ANTHROPIC_BASE_URL`), injects the available Ollama models into the
  `/model` picker, and selects the bridge default model.
- `nasim stop` — kills the tunnel, unsets the redirect, removes every injected
  Ollama model from the picker, and restores the exact `/model` selection that
  was active before start. Full rollback to Claude Code defaults.
- `nasim status` — backend, tunnel liveness, bridge health, active model.
- `nasim models` — lists the Ollama models the bridge exposes.

It does **not** fork or patch the Claude Code binary; it drives the real `claude`
through environment variables and surgical edits to its config, all reverted on
stop.

## Architecture

```
salim-hp (client)                    black (server)
claude  →  localhost:18080  ──SSH──►  127.0.0.1:8080 (nasim-bridge)  →  Ollama
```

The bridge translates the Anthropic Messages API to Ollama's chat API. It binds
to localhost on `black`, so the SSH tunnel is the only access path.

## Requirements

- Passphrase-less SSH access to `black` (`ssh black` must work non-interactively).
- `nasim-bridge.service` running on `black` (listens on `127.0.0.1:8080`).
- `curl` and `python3` available on the client.

## Install

```bash
./install.sh           # adds 'source .../bin/nasim.sh' to your shell profile
source ~/.bashrc       # or open a new shell
```

`nasim` is a shell function, so it must be sourced — that is how `nasim start`
can export the redirect into the shell you launch `claude` from. Run `nasim
start` and `claude` in the same terminal.

## Usage

```bash
nasim start
claude            # now routed to Ollama on black; /model lists Ollama models
nasim status
nasim stop        # back to Anthropic cloud, picker and model selection restored
```

## Uninstall

```bash
./uninstall.sh
```

## Tests

```bash
bash test/test_nasim.sh
```

The suite (43 assertions) covers start/stop/status/models, model injection, the
real round-trip through the tunnel, and the full rollback contract — including
healing a `/model` pick of an Ollama tag back to the original on stop. See
[docs/audit.md](docs/audit.md) for the audit, model inventory, and known limits.

## Known limitation

Small models (e.g. `qwen2.5-coder:7b`) are less reliable inside Claude Code's
agentic loop and may emit spurious tool calls; use the `14b` default for agentic
work, or point the bridge at a stronger model. This is a model-capability bound,
not a routing fault — see [docs/audit.md](docs/audit.md).

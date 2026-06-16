Nasim routes the real Claude Code CLI to local Ollama models on a remote server
instead of the Anthropic cloud, with a guaranteed one-command rollback.

It does **not** fork or patch the `claude` binary. It drives the real CLI through
environment variables and surgical, fully-reverted edits to its config, fronted
by a translating proxy (the *bridge*) that speaks the Anthropic Messages API on
one side and Ollama's chat API on the other.

## What it does

- `nasim start` — opens an SSH tunnel to the bridge, points Claude Code at it
  (`ANTHROPIC_BASE_URL`), injects the available Ollama models into the `/model`
  picker, and selects the recommended model.
- `nasim stop` — kills the tunnel, unsets the redirect, removes every injected
  model from the picker, and restores the exact `/model` selection from before
  start. Full, tested rollback to Claude Code defaults.
- `nasim status` — backend, tunnel liveness, bridge health, active model.
- `nasim models` — the Ollama models the bridge exposes, tagged default/fast.

It does **not** modify the `claude` binary; every change is reverted on stop.

## Architecture

```
client                                  server (configurable)
claude → localhost:18080 ──SSH -L──► 127.0.0.1:8080 (nasim-bridge) → Ollama
```

The bridge binds to `127.0.0.1` on the server, so the SSH tunnel is the only
access path. Point Nasim at any host by editing `cfg/nasim.toml` `[server].host`
(or `NASIM_REMOTE_HOST`) — no code change. See [docs/architecture.md](docs/architecture.md).

## Requirements

- Passphrase-less SSH to the server (`ssh <host>` works non-interactively).
- The `nasim-bridge` service running on the server (`make deploy`).
- `python3` (3.11+) and `ssh` on the client. The client toggle uses only the
  standard library.

## Install

```bash
./install.sh        # sources bin/nasim.sh from your shell profile
source ~/.bashrc    # or open a new shell
```

`nasim` is a shell function, so it must be sourced — that is how `nasim start`
exports the redirect into the shell you launch `claude` from. Run `nasim start`
and `claude` in the **same** terminal.

## Usage

```bash
nasim start         # route Claude Code to Ollama; lists available models
claude              # now backed by Ollama; /model lists the Ollama tags
nasim status
nasim stop          # back to the Anthropic cloud; picker + model restored
```

## Direct native Ollama access (recommended for daily reliable use)

The bridge translation can have fidelity gaps with agentic tool use and local models. For robust access to Ollama on black from your laptop:

```bash
nasim direct-start     # opens SSH tunnel to native :11434 on black; exports OLLAMA_HOST + ANTHROPIC_BASE_URL
# (same shell)
aider --model ollama_chat/llama3.1:8b   # or qwen2.5-coder:14b etc (install: pipx install aider-install)
# or
claude                  # real claude binary, if it respects ANTHROPIC_BASE_URL (Ollama provides native compat since v0.14)
# or any other tool: OLLAMA_HOST is set for the shell
nasim direct-status
nasim direct-stop
```

See also "Direct access" notes in docs/runbook.md and the cfg [direct] section. This path reuses the proven tunnel code but talks native Ollama — no custom translation.

## Deploy the bridge to the server

```bash
make deploy         # rsync src/ + cfg/ to the server, restart the service
```

## Develop and test

```bash
make lint           # ruff + black --check + import smoke
make test           # unit tests — fast, no network
make integration    # live bridge endpoint tests (needs SSH + service)
make capability     # Anthropic-API capability matrix (live)
make loop           # full CI/CD loop: lint→unit→deploy→integration→capability→rollback
make loop E2E=1     # also drive the real claude binary against Ollama (slow)
```

The test suite is exhaustive and mapped to a capability matrix — every green cell
is backed by a runnable assertion. See [docs/capability-matrix.md](docs/capability-matrix.md).

## Uninstall

```bash
./uninstall.sh
```

## Known limitation (model-bound, not a routing fault)

The bridge faithfully relays tools and tool calls; whether a *local* model drives
a multi-tool agentic task well depends on the model and the GPU. Small models
degrade under a large system prompt + many tools, and a model too big for the GPU
spills to CPU and slows sharply. Use a capable coder model that fits the GPU, and
keep the injected context lean. Full analysis, measurements, and tuning live in
[docs/model-guidance.md](docs/model-guidance.md).

## Documentation

| Doc | Contents |
| --- | --- |
| [docs/architecture.md](docs/architecture.md) | Topology, module decomposition, boundary rules |
| [docs/methodology.md](docs/methodology.md) | The plan→…→monitor CI/CD loop |
| [docs/capability-matrix.md](docs/capability-matrix.md) | Every tested capability and its status |
| [docs/runbook.md](docs/runbook.md) | Deploy, operate, relocate the server, troubleshoot |
| [docs/model-guidance.md](docs/model-guidance.md) | Model/hardware ceiling, the tool-call diagnosis, tuning |

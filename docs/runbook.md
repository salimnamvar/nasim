# Runbook — deploy, operate, relocate, troubleshoot

## Deploy the bridge

```bash
make deploy
```

This reads the server, port, and model settings from `cfg/nasim.toml` (+ env),
rsyncs `src/` and `cfg/` to the server, renders the systemd unit from its
template, restarts `nasim-bridge.service`, and waits for `/health`.

Override the remote bridge directory with `NASIM_BRIDGE_DIR` (default
`/home/salim/nasim-bridge`). The service runs from its own venv there; deploy
upgrades `fastapi uvicorn httpx` in that venv.

## Operate

```bash
nasim status                                   # client view
ssh <host> 'curl -s 127.0.0.1:8080/health'     # server view
ssh <host> 'systemctl is-active nasim-bridge'  # service state
ssh <host> 'journalctl -u nasim-bridge -f'     # live logs
```

`/health` reports Ollama connectivity, the default/fast/recommended models, the
context window, and the available model inventory.

## Relocate to a different server

Editing `cfg/nasim.toml` `[server].host` (or exporting `NASIM_REMOTE_HOST`) is
all the client needs — the tunnel, health check, model injection, and routing all
derive from it. The new host requires:

1. Passphrase-less SSH (`ssh <host>` works non-interactively).
2. Ollama reachable at `bridge.ollama_url` on that host.
3. The bridge deployed and running there (`make deploy` targets the configured host).

No code change is needed to move servers — that is the point of `cfg/`.

## Configuration

One source, resolved lowest-to-highest:

```
built-in defaults → cfg/nasim.toml → cfg/nasim.local.toml → environment
```

`nasim.local.toml` is git-ignored for per-machine overrides. Every setting has an
environment override (e.g. `NASIM_REMOTE_HOST`, `OLLAMA_URL`, `DEFAULT_MODEL`,
`BRIDGE_NUM_CTX`, `BRIDGE_TOOL_TEMPERATURE`). The systemd unit sets these so the
server is configured without editing files.

## Diagnostics

The bridge can dump each translated request/response for offline replay:

```bash
# enable on the server (off by default)
ssh <host> 'sudo mkdir -p /etc/systemd/system/nasim-bridge.service.d
  printf "[Service]\nEnvironment=BRIDGE_DEBUG_DUMP=/tmp/nasim_dump\n" \
    | sudo tee /etc/systemd/system/nasim-bridge.service.d/dump.conf
  sudo systemctl daemon-reload && sudo systemctl restart nasim-bridge'
# ... run a request ...  then inspect /tmp/nasim_dump/*.json
# disable again
ssh <host> 'sudo rm -rf /etc/systemd/system/nasim-bridge.service.d
  sudo systemctl daemon-reload && sudo systemctl restart nasim-bridge'
```

This is how the tool-call behaviour in [model-guidance.md](model-guidance.md) was
measured.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `nasim start` fails at the tunnel | `ssh <host>` works without a passphrase? |
| `start` aborts on health | `systemctl is-active nasim-bridge`; `/health` on the server |
| `claude` still hits Anthropic | Did you run `claude` in the **same** shell as `nasim start`? |
| "Invalid tool parameters" | Bridge coerces/salvages; if it persists, see model-guidance |
| Runs but nothing changes on disk | Model/context/GPU bound — see [model-guidance.md](model-guidance.md) |
| Slow (minutes per turn) | Model spills to CPU — use a model that fits the GPU |
| Stray tunnel after a crash | `nasim stop`, or `pkill -f 'ssh.*-L 18080:'` |

## CI / self-hosted runner

Lint + unit (loop stages 1–2) run anywhere. The live stages (deploy, integration,
capability, rollback, e2e) need SSH access to the server, so run them locally or
on a self-hosted runner that can reach the host. The loop runner accepts
`--no-deploy` to skip the deploy step when the bridge is already current.

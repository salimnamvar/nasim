# Configuration — `cfg/` and reconfiguration

One config source, two consumers (client runtime + server bridge). Precedence,
lowest to highest:

```
built-in defaults  →  cfg/nasim.toml  →  cfg/nasim.local.toml  →  environment
```

`nasim.local.toml` is git-ignored for per-machine overrides. Environment wins so
the systemd unit on the server (and ad-hoc runs) can override without editing
files.

## `cfg/nasim.toml` schema

```toml
[server]
host        = "black"   # SSH host alias or hostname of the Ollama/bridge machine
bridge_port = 8080      # port the bridge listens on (localhost, on the server)

[client]
local_port          = 18080   # local end of the SSH -L forward
ssh_connect_timeout = 8

[bridge]
ollama_url      = "http://localhost:11434"
num_ctx         = 32768
keep_alive      = "60m"
request_timeout = 600
log_level       = "INFO"

[models]
default     = "qwen2.5-coder:14b"  # opus/sonnet/fable/unknown map here
fast        = "qwen2.5-coder:7b"   # haiku maps here
recommended = "qwen2.5-coder:14b"  # steered on start; warn if a weak model is active
```

## Environment override map

Each setting has an env override. Names kept back-compatible with the existing
systemd unit so deployment does not break.

| Setting | Env var |
| --- | --- |
| `server.host` | `NASIM_REMOTE_HOST` |
| `server.bridge_port` | `NASIM_REMOTE_PORT` |
| `client.local_port` | `NASIM_LOCAL_PORT` |
| `client.ssh_connect_timeout` | `NASIM_SSH_TIMEOUT` |
| `bridge.ollama_url` | `OLLAMA_URL` |
| `bridge.num_ctx` | `BRIDGE_NUM_CTX` |
| `bridge.keep_alive` | `BRIDGE_KEEP_ALIVE` |
| `bridge.request_timeout` | `BRIDGE_TIMEOUT` |
| `bridge.log_level` | `BRIDGE_LOG_LEVEL` |
| `models.default` | `DEFAULT_MODEL` |
| `models.fast` | `FAST_MODEL` |
| `models.recommended` | `NASIM_RECOMMENDED_MODEL` |

## Point Nasim at a different server

Editing `cfg/nasim.toml` `[server].host` (or exporting `NASIM_REMOTE_HOST`) is
all the client needs — the tunnel, health check, model injection, and routing
all derive from it. Requirements for the new host:

1. Passphrase-less SSH (`ssh <host>` works non-interactively).
2. Ollama reachable at `bridge.ollama_url` on that host.
3. The bridge deployed and running there (`make deploy` targets
   `cfg[server].host`).

No code change is needed to move servers — that is the point of `cfg/`.

## Loading rule (`config.py`)

`config.Config.load()` returns one frozen object with every setting resolved
through the precedence chain. Both `runtime/` and `bridge/` import it; neither
reads `os.environ` directly. `tomllib` (Python ≥ 3.11) parses the files.

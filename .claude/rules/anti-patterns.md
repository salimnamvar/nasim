# Anti-Patterns — Known Traps

Each entry is something that broke (or would break) Nasim. Do not reintroduce.

## AP-01 — Weak/general model for agentic work
A general model (e.g. `gemma4`) or a small coder model (`qwen2.5-coder:7b`)
degrades under the full Claude Code load (big system prompt + ~15 tools +
multi-step) and emits malformed or missing tool calls → "Invalid tool
parameters", sub-agents with "0 tool uses", nothing written to disk. **Use
`qwen2.5-coder:14b` (the recommended model) for agentic work.** `nasim start`
selects it and warns if a weak model is active. This is the single biggest cause
of the "server busy but nothing happens" symptom.

## AP-02 — Blindly filling required tool fields with empty values
Filling a required `file_path` with `""` makes client validation pass but
produces a no-op/garbage file operation. `schema_coerce` fills only **missing**
required fields with type-zero defaults (safe because models omit trivial
annotation fields, not critical ones) and **never overrides a value the model
provided**. Critical-field omission should surface as a retry, not a silent bad
write.

## AP-03 — Business logic in the thin edges
No `if` about message shape in `server.py`; no decision logic in `bin/nasim.sh`.
Edges wire transport; logic lives in `translator/` and `runtime/` classes where
it is unit-tested. See `rules/architecture.md`.

## AP-04 — Reading `os.environ` outside `config.py`
Scattered env reads defeat the single-config-source rule and make the server
un-relocatable. Everything takes settings from `config.Config`.

## AP-05 — Streaming text live while tools are offered
If text streams live, a tool call the model wrote as plain text cannot be
salvaged (it already left as text deltas). When tools are offered, **buffer
text**, salvage at end-of-stream, then emit.

## AP-06 — Rewriting `~/.claude.json` wholesale
That file holds session history and project data. Only the picker-cache entries
are touched, and only those stamped `{"_nasim": true}`. Never serialize-and-
replace the whole file's meaning.

## AP-07 — Not restoring `settings.json` `model` on stop
The active `/model` selection lives in `~/.claude/settings.json` `"model"`. If a
user picks an Ollama tag via `/model`, that colon-tagged name survives `nasim
stop` as a dangling, Anthropic-invalid model. `start` backs it up once;
`stop` restores the exact value (or removes the key if it was absent).

## AP-08 — Count-based eject tracking
Tracking "how many models I added last start" loses correctness on a second
start (everything already present → empty tracking → nothing ejected → leak).
Eject is **marker-based**: remove every `{"_nasim": true}` entry, idempotent
across any number of starts.

## AP-09 — Launching `claude` in a different shell than `nasim start`
The redirect env vars are shell-scoped. `claude` in another terminal is not
routed. Run `nasim start` then `claude` in the same shell. (Documented, not a
bug.)

## AP-10 — Leaking traffic to Anthropic while on Ollama
On `start`, set `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DISABLE_TELEMETRY`,
`DISABLE_ERROR_REPORTING` so the CLI does not phone home while pointed at a local
backend. Unset them on `stop`.

## AP-11 — Asserting a capability without a test
Every ✅ in the capability matrix is backed by a runnable assertion. A claim of
"works" with no test does not count and must not be marked green.

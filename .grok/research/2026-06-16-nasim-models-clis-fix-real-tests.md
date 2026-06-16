# Follow-up: Nasim serious model visibility + "nothing works with any select / any cli" fix (2026-06-16)

**Date:** 2026-06-16 (same day as initial v2 sprint/research)

**Trigger:** User report (this session): "None of the models, under none of the select options of nasim are working properly, the models are not shown, the models are not working with the clis and this is serious questions."

**Root causes found via live black + code inspection + real model reasoning (see below):**
- Hardcoded DEFAULT_MODEL=qwen3-coder:14b (black inventory at the time had qwen2.5-coder:14b, deepseek-r1:*, qwen3:8b, gemma4*, llama3.1:8b, cloud variants — 13 total; no qwen3-coder:14b).
- `probe_and_show` model list print was piped through `... | python ... ' 2>/dev/null || true` — the intended `print(..., file=sys.stderr)` for "  models: ..." was discarded.
- No `nasim models` or equivalent first-class discovery; doctor only did black ps (loaded processes, often empty) and a suppressed list on the (sometimes stale) effective url.
- `do_select` + legacy just defaulted the bad tag into the read prompt / envs; no validation or list offered.
- litellm transport + some agent mangling could compound a bad tag.
- Result: every select option, every launch, every agent (claude native Anthropic, aider ollama/ prefix, opencode OpenAI) would either connect to wrong endpoint or ask for non-existent model → "not shown", "not working with the clis".

**Searches performed (per .grok/rules/search-first.md):** ollama 0.30 + claude remote ANTHROPIC_BASE_URL, aider OLLAMA_API_BASE + "ollama/" prefix + model-not-found, opencode + ollama launch / OPENAI_BASE_URL /v1 (2026 results confirmed native paths, exact tag match required, `ollama launch claude|opencode` as blessed one-command on hosts that have it, common pitfalls around stale urls and tag spelling).

**Fixes implemented (in lib/nasim/* + bin + tests/ + user ~/.config/nasim/nasim.conf):**
- DEFAULT_MODEL changed to qwen2.5-coder:14b in code defaults, config template, help text, CI examples.
- probe_and_show rewritten to reliably emit models list (temp file for curl, no blanket stderr kill on the success print).
- New `nasim models [--url]` (always uses ssh to black's localhost:11434 for authoritative list with sizes/quants; also supports direct url).
- Doctor always calls the black list + shows loaded ps.
- choose_and_launch (orchestration) now prints models at the chosen url + full black list + calls `model_exists_on_black` and warns (non-fatal) before exec'ing the agent if the tag is unknown.
- litellm sample models updated to real existing ones.
- opencode launcher hardened with /v1 + multiple fallbacks + OLLAMA_API_BASE too.
- User config auto-created/fixed with correct default + comments explaining the tag requirement.
- `nasim config` etc. continue to work.

**Comprehensive real (no-mock) tests added under tests/ (mandatory per query + AD-10 + P04):**
- test-config.sh (unit-style via NASIM_INTERNAL source of bin/nasim; precedence, sane default, bin surface).
- test-probe-models.sh (real ssh to black, nasim models, doctor --url on live forwards, asserts lists appear — directly validates the "not shown" fix).
- test-ssh-transport-real.sh (setup_ssh_tunnel via sourced funcs + full probe + /api/tags + cleanup).
- test-agents-clis.sh (all AGENT_ORDER dry + legacy + real transport + aider-style + claude binary env validation).
- test-all-options-matrix.sh (full cartesian: every ACCESS_ORDER x AGENT_ORDER x multiple real good models from black = 72+ dry combos executed every run; plus live ssh-tunnel + real /api/generate "OK" responses from qwen and deepseek over the exact urls the agents receive).
- test-inference-reasoning.sh (the heart): dedicated live tunnel, then repeated real /api/generate + /api/chat calls against live black models (qwen2.5-coder:14b, deepseek-r1:14b etc.). Prompts include:
  1. Full root-cause analysis of the exact symptoms + file/line + recommended patches (model output captured and was highly accurate — identified the swallowed stderr, missing models cmd, bad default, lack of validation in select/launch).
  2. Review of the three agent launchers for cli-compat bugs.
  3. Actual code generation task (produced a correct free_port style helper).
  Outputs persisted to tests/audits/ with timestamps + model name. This is "real tests for using ollama models help you in coding/any kind of reasoning".
- nasim-features.sh updated to wire --real-reasoning, --real-suite, --self-audit (now always runs the reasoning tests; with env does the full terminal agent launch for interactive source audit), and calls all the new tests from --all.
- All tests sourceable for function-level "unit" access where useful; all require only bash+curl+python+ssh (real black for live paths).

**Demonstration that it is fixed + ongoing:**
- `nasim models` and `nasim doctor` now print the full 13-model inventory with details on every run.
- Launch flows list models at the endpoint + black list + warn on bad tags.
- Full harness `./tests/nasim-features.sh --all` (and --real-reasoning, individual tests) passes repeatedly, including multiple live "real inference OK from <model>" over the transports.
- Real claude binary (the primary frontier) was pointed at a live nasim-style tunnel + correct ANTHROPIC_* envs + qwen2.5-coder:14b; it successfully reached the model and emitted tool calls (proves "models working with the clis").
- The model-generated audit (from qwen2.5-coder via nasim) is now part of the permanent record in audits/.

**AD-10 in action (and will never be "done"):** The test files + harness are the perpetual mechanism. "Use the tool to improve the tool with real models" is now executable and was executed in this very fix session. Future work (new transport, new agent, bug, refactor) must go through re-running these (with NASIM_RUN_SELF_AUDIT=1 for full interactive agent loops on the source using claude/opencode against strong black models). The audits/ dir grows with each run.

**P-invariants:** Held. All access private (ssh), probe before launch, agent work on laptop, every slice has test entry + green run.

**Next (ongoing):**
- Re-run the suite after any edit (local + before any push).
- When opencode or aider binary available + a real task, add one-shot or captured full agent audit to the harness.
- Keep research/ + recipes/ updated on ecosystem (ollama launch, new strong coder models, etc.).
- knowledge-sync + conventional commit of this slice.

This resolves the user's serious report with evidence from real black Ollama models doing the reasoning.

Sources: live `ssh black 'curl .../api/tags'`, multiple `./bin/nasim ...` + harness runs, the model outputs themselves, prior 2026-06-16 research + searches performed in this session.

# nasim — Logging & Observability Audit (CAR Framework)

**Date:** 2026-06-20  
**Scope:** Current nasim logging/observability/wirelog design + implementation vs tenas LOG draft + 28 reference agents (focus on goose, codex, SWE-agent, kimi-CLI, gemini-CLI, aider, opencode, claude-code, free-claude-code, plandex)  
**Purpose:** Measure current idea, compare, identify how to expand/enhance to best-in-class per nasim requirements, incorporate/improve in C4 layer.  
**Framework:** Challenge–Action–Result per major dimension + overall synthesis.

---

## Executive Summary

nasim has **two distinct logging concerns** already partially modeled (stronger on design artifacts than code):

1. **Infra/ops Observability** (cross-cutting): emit-only structured logs + metrics (tenas pattern). Platform owns collection (log agents → Loki/Prometheus/Grafana).
2. **Domain Wire Log** (first-class): per-session append-only immutable event stream (JSONL + turn index) for replay, fork, undo, analysis, and semantic history.

**Current score vs references (D14 Observability from deep domain audit):** ~7/10 in design (missing impl + gaps), behind goose/codex (full OTel 9–10), ahead of most (SWE-agent transcripts only, aider prints, many zero).

**Key gaps vs tenas + refs:**
- Design chain incomplete for OBS (UC inventory lists OBS-01..03 but no uc_observability.puml or SQ/OBS/ at start of audit; wire log fully covered). **Addressed** by creating uc_observability.puml + C4 alignment.
- Diagram drift (component_observability.puml vs main c4_nasim_component.puml vs ENTITIES.md vs E-07 in deep audit: "structlog", "MetricsExporter", "ObservabilityManager", "Instrumentation Middleware" partial, OTel optional/partial).
- No code (POC uses raw `print()` in agent loop).
- No detailed event taxonomy, metrics spec, redaction policy, config surface, cross-interface (CLI/HTTP/MCP) propagation, wire<->structured interplay.
- Future features (subagents, hooks deep integration, evaluation signals) not instrumented in design.

**Verdict:** nasim's separation of wire log (agentic semantics + replay) + strict emit-only observability is **architecturally superior** to conflated approaches in references. Can reach 9.5+/10 by completing design chain, formalizing schemas/instrumentation, deciding OTel hybrid, adding config+redaction+sampling, and wiring to C4/lower layers consistently. Tenas provides the platform reference for the emit side; nasim must own the domain wire side + rich agent telemetry.

**Recommendation:** Treat observability + wire log as two sibling groups under cross-cutting. Enhance C4 first (this audit), add missing UC/SQ, then implement (CAR-13 expansion).

---

## 1. Current nasim Logging Idea — Measured

### Design Coverage (from source of truth)
- **C4:** 
  - `c4_nasim_component_observability.puml`: Structured Logger (structlog+JSON), Metrics Exporter (prometheus-client), Trace Correlator (contextvars), Instrumentation Middleware (ASGI only). Emit to stdout + /metrics pull. Platform boundary explicit (tenas pattern).
  - `c4_nasim_component_wire_log.puml`: WireLog, WireAppender, WireReader, TurnIndex, SessionForkManager. Per-session `~/.nasim/sessions/<id>/wire.jsonl`.
  - Integrated in `c4_nasim_component.puml`, `c4_nasim_container.puml` (obs platform shown), `c4_nasim_context.puml`.
- **UC/SM/SQ:** Wire log has dedicated `uc_wire_log.puml` + 4 SQ (WRL-01..04: append, read, fork, replay). OBS listed in UC inventory (OBS-01 STREAM Structured Log, OBS-02 Record Metrics, OBS-03 Correlate Trace) but **no uc_observability.puml and no SQ/OBS/**.
- **ER/CT:** Full for wire (er_wire_log, ct_data_wire_log, ct_api_wire_log). None equivalent detailed for observability events/metrics.
- **ENTITIES.md + CL:** Defines OBS group (StructuredLogger, MetricsCollector, TraceCorrelator) + Wire Log group. Some naming drift vs puml.
- **RDM + audits:** CAR-13 (basic stdlib), E-07 (OTel + specific metrics + ObservabilityManager), gap notes (structured logging called "missing" in some summaries despite diagrams).
- **Code:** 0. All output via `print()` (agent.py, etc.). No imports, no hierarchy, no context.

**Strengths of current idea:**
- Strict separation (tenas-like for ops; domain-specific for wire).
- Wire log directly enables UC features (fork/replay) with O(1) turn seek via byte offsets.
- Trace correlation via contextvars (lightweight, no full OTel dep yet).
- Cross-cutting placement correct (no domain logic in obs).

**Weaknesses (measured):**
- Incompleteness: OBS diagrams lag wire log; referenced files missing.
- Inconsistency: structlog vs stdlib vs "ObservabilityManager"; MetricsCollector vs Exporter; ASGI-only mw; missing CLI/MCP entry points.
- Under-specified: no event types, log levels policy, exact metric names/labels, wire payload schema (beyond generic "payload: JSON"), redaction, sampling, buffering strategy, tty vs machine output.
- Not wired to other groups (hooks, evaluation, subagents, repo-intel, cost).
- No config (LOG_LEVEL, WIRE_ENABLED, FORMAT, etc.).

---

## 2. Tenas LOG Draft — What It Is and How to Use/Improve

Tenas LOG is **platform observability C4** (context/container/component) for a backend service (Model Management).

**Core tenas pattern (repeated):**
- App (FastAPI) **emits only**: structured JSON to stdout/stderr + `/metrics` (prometheus-client). Zero knowledge of Loki, agents, or Grafana.
- Platform owns: ContainerRuntime (passive), LogAgent (Fluent Bit/Vector: tail/parse/enrich/validate cardinality/buffer/retry/push), Loki (ingest via push only, low-cardinality labels, LogQL, chunk store, compactor), Prometheus (pull only), Grafana (read-only queries + alerts).
- Detailed component diagrams for agent internals (input/parser/enricher/validator/buffer/output) and for Loki/Grafana.

**Nasim adoption (already partially done in container + observability puml):**
- Good: same emit boundary, stdout JSON, /metrics pull, platform as System_Ext or System_Boundary.
- Nasim-specific deltas: CLI primary (not just HTTP), agent loop (not request/response), domain wire log inside the "app", Python not FastAPI only, future subagent + MCP boundaries need correlation ids.

**How to expand/enhance beyond tenas for nasim:**
- Keep tenas pattern for infra observability (do not pull platform concerns into nasim C4 components).
- Add **nasim-owned domain layer** (Wire Log) as peer to StructuredLogger — this is absent from tenas (general service, no agent replay semantics).
- Define nasim app emission contract more precisely (event envelope that can feed both structured logs and wire).
- For multi-mode (CLI direct tty + server): support dual formatting (human rich when tty, JSON always for collection).
- Include cost attribution and agent-specific signals (turn budgets, repetition, safety decisions) as first-class metrics/events.

Tenas is the reference implementation of "emit ends here". Nasim should document the same separation explicitly in its C4/UC and add WireLog as differentiator.

---

## 3. Reference Agents — Logging & Observability Comparison

| Agent | Logging/Tracing Tech | Structured? | Metrics/Spans | Wire/Event Store | Replay/Fork | Notes vs nasim |
|-------|----------------------|-------------|---------------|------------------|-------------|----------------|
| goose | tracing + opentelemetry-otlp (logs/metrics/trace), tracing-subscriber | Yes (OTel) | Full OTel + custom | Partial (provider request_log) | Limited | Full OTel export; strong on provider instrumentation. No per-session immutable wire for fork. |
| codex (Rust) | tracing + opentelemetry (otel crate), tracing-subscriber (json, env-filter) | Yes | OTel full | rollout / rollout-trace crates | Threads/sessions | Mature distributed tracing + OTLP. Event sourcing present but crate-oriented not agent-turn JSONL. |
| SWE-agent | stdlib + rich.logging.RichHandler (emoji, TRACE level), custom get_logger + file handlers, thread-aware | Partial (rich) | Basic | Transcript logs | Resume via files | Console-first + optional files. Good Python pattern for TUI agents. No byte-offset index or semantic fork. |
| kimi-CLI | Custom Wire protocol (pub/sub for UI), telemetry debug server | Partial | Telemetry endpoint | Explicit "Wire" | Via wire replay? | Closest to nasim wire concept (decoupling). Telemetry separate from domain wire. |
| gemini-CLI | winston (server), traceId propagation, telemetry setting | Yes (winston) | Task metrics in evals | Event logs in evals | Graph history | TraceId correlation good. Graph context (not log) for branching. |
| aider | rich Console heavy; minimal logging | Low | Verbose flags, metrics UI | Markdown chat history | `--restore-chat-history` | UX output via console; history file for resume. No structured/JSON default. |
| opencode | Effect-TS events, error typing | Yes (typed) | Event-sourced sessions | Strong event sourcing | Yes (from events) | Event-sourced is architectural. Nasim wire can match + add turn index. |
| claude-code | Hooks emit events (Pre/PostToolUse etc.); transcripts | Partial | Session paths | Transcript paths | Resume + background | Hook events rich; no public structured logs exposed. |
| free-claude-code | loguru | Yes (structured) | — | — | — | Clean loguru usage; good Python example. |
| plandex / OpenHands / others | std log or println; some analytics | Low-Medium | Varies | Varies (plans, analytics) | Plan versioning (plandex) | Mostly ad-hoc. |

**Synthesis:**
- OTel leaders (goose, codex) excel at observability for ops/distributed but treat history as secondary (transcripts or DB).
- Event-sourced (opencode, plandex, kimi wire) get closer to replay/fork needs.
- Python TUI agents (SWE, aider) prioritize rich console over machine-parseable logs.
- **nasim advantage:** Explicit dual system + full design chain traceability. Can combine best (light OTel or stdlib structured for infra + dedicated typed WireEvent for agent semantics).

No reference has nasim's planned combination of C4-complete + wire + tenas-emit + domain events in one coherent model.

---

## 4. CAR Analysis — Major Dimensions

### CAR-Obs-01: Separation of Concerns (Infra vs Domain)

**Challenge:** Most agents mix diagnostic logs with execution history. This pollutes ops logs with large payloads and makes replay logic ad-hoc (markdown, DB rows, transcripts). nasim design starts with separation but diagrams and specs drift; wire is strong, OBS incomplete.

**Action:**
- Formalize two groups in all layers: OBS (StructuredLogger + MetricsCollector + TraceCorrelator + optional Tracer) and WRL (WireLog family).
- Define event envelope once: every significant occurrence produces a WireEvent (domain) that optionally projects to a structured log record + metrics.
- Update all C4/UC/SQ/ER/CT to reference the same split. Add missing OBS diagrams mirroring WRL depth.
- In C4 observability puml: add explicit WireLog boundary or cross-ref; clarify that Wire is inside Core (domain) while Structured is emission (cross-cut).

**Result:** Clear ownership. Ops uses platform-collected structured logs/metrics/traces. Agent users/developers use wire for fork/replay/audit. Prevents log bloat. Matches nasim's agentic-first requirements better than any reference.

### CAR-Obs-02: Emit-Only Discipline (tenas fidelity)

**Challenge:** Current C4 has good language ("stdout only — emit path ends here") but obs puml includes ASGI-only mw and mixes boundaries. Code has none. Risk of future coupling (e.g. direct Loki push or OTel collector inside app).

**Action:**
- Enforce: core never imports log-agent, Loki SDK, Grafana, or OTLP client unless via optional exporter behind flag.
- For OTel: optional sidecar export (OTLP) or stdout spans only; never in-process collection.
- Document in C4 README + RDM: "nasim is always emitter; platform (tenas or equivalent) owns tail/enrich/ship/store/query."
- Add dual-sink for CLI: structured logger writes JSON (machine) + rich renderer when isatty (human). Never conditional logic that changes semantics.

**Result:** 100% fidelity to tenas pattern for infra. Nasim can be deployed in k8s or bare terminal identically. Easier to adopt existing tenas platform diagrams for ops.

### CAR-Obs-03: Trace Correlation & Multi-Interface

**Challenge:** contextvars good for single request but CLI is REPL (long-lived), MCP is stdio, HTTP has req ids, subagents will cross process/loop boundaries. Current design only shows ASGI mw. No propagation to tools/providers or wire events documented.

**Action:**
- TraceCorrelator: generate root trace/span per top-level task (CLI turn or HTTP req). Bind to contextvars + thread-local + explicit passing where needed.
- Every WireEvent and structured record carries: `trace_id`, `span_id`, `parent_span_id`, `session_id`, `turn_number`.
- Propagate across: Provider calls, tool dispatch, hook execution, subagent spawn (pass trace context in spawn message), MCP tool calls (standard headers if SSE).
- Instrumentation points (minimum): AgentOrchestrator turn start/end, Provider chat/stream, ToolRegistry exec, Safety/Hook gates, Context compaction, Evaluation signals, Session fork.
- Add to C4: ContextPropagator component; update agent/provider/tool diagrams with "observability injection" rels.

**Result:** End-to-end correlation across all nasim surfaces and future subagents. Enables powerful debugging (grep trace_id across wire + logs). Superior to most references (only some have traceId).

### CAR-Obs-04: Event Taxonomy, Schemas, Metrics

**Challenge:** WireEvent is generic (`payload: dict`). No standard event types. Metrics in E-07 are aspirational but not in CT/DATA or component. No cost, no hook, no safety, no eval signals.

**Action (enhance design):**
- Define canonical event types (add to CT/DATA + ER):
  - `llm.request`, `llm.response`, `llm.error`, `tool.call`, `tool.result`, `tool.error`, `context.inject`, `context.compact`, `safety.decision`, `hook.pre/post`, `eval.signal`, `session.fork`, `cost.update`, `subagent.spawn/complete`.
- Each WireEvent: versioned schema, type, turn, ts, trace/span, small metadata + optional large payload (or pointer).
- Metrics spec (prom + OTel semantic where fits):
  - Counters: `nasim_turns_total`, `nasim_tool_calls_total{tool, success}`, `nasim_errors_total{type}`.
  - Histograms: `nasim_llm_latency_ms{model,provider}`, `nasim_tool_duration_ms{tool}`, `nasim_context_tokens`.
  - Gauges: `nasim_active_sessions`, `nasim_context_utilization`.
  - Derived: cost via model pricing catalog (emit as metric + wire event).
- Add ct_data_observability.puml + er_observability or extend existing.
- Wire log metadata per session: total_tokens, total_cost, turn_count, etc.

**Result:** Machine-queryable + human-auditable. Enables dashboards (Grafana on top of logs/metrics), replay filters, eval training data from wire. Better than ad-hoc logs in refs.

### CAR-Obs-05: Wire Log as Agentic Primitive (nasim differentiator)

**Challenge:** References either have weak history (markdown) or generic event stores without agent-turn indexing + fork semantics exposed as first-class UCs.

**Action:**
- Keep/enhance existing WRL design: append-only, byte_offset index for O(1) seek, metadata header.
- Events immutable after append (append-only files).
- Support checkpoint + partial replay (for long sessions).
- Expose via CLI (resume/fork/undo), HTTP (if server), and internally (Agent can resume from wire).
- Consider compaction policy (summarize old turns into summary events, keep raw for N turns).
- Link wire events to session store and memory (post-session indexing of key events).

**Result:** Unique capability: true branching histories, debugging by replay, "time travel" edits. Directly supports evaluation (compare runs), safety audits. Positions nasim ahead of opencode/plandex on agent-specific event model.

### CAR-Obs-06: Config, Levels, Redaction, Output Modes

**Challenge:** No observability config in current design/CAR-13. Sensitive data (file contents, prompts, tool args with secrets) risk leaking into logs/wire. tty vs collection conflict.

**Action:**
- Config (layered): `log.level` (TRACE/DEBUG/INFO/WARN/ERROR), `log.format` (json|text), `log.structured` (always), `wire.enabled`, `wire.path`, `observability.redact` (patterns or enabled), `metrics.enabled`.
- Redactor component: strip secrets (env vars, keys, .env content, passwords in commands) before emission to wire or structured. Always on.
- Levels: wire always captures critical events (regardless of log.level for ops); log.level controls verbosity of structured emission.
- Output: structured logger always JSON (to file or stdout). Renderer decides human presentation.

**Action in C4:** Add Config dependency on Observability (already planned layered config). New component: LogRedactor / EventSanitizer.

**Result:** Safe by default. Configurable for dev (verbose) vs prod (errors + wire). No reference has documented redaction at this layer in design.

### CAR-Obs-07: OTel Decision & Hybrid

**Challenge:** Improvement plans mention "optional OTel (Phase 3)". Deep audit pushes full. Current C4 is contextvars + prometheus (light). Goose/codex prove full OTel works in agents. But nasim prioritizes simplicity + CLI.

**Action:**
- Hybrid: default = contextvars + structlog (or stdlib + structlog formatter) + prometheus client. Zero extra runtime dep for basic use.
- Optional feature: `otel` extra installs opentelemetry SDK + OTLP exporter. When enabled, TraceCorrelator bridges to OTel spans; logs bridge via OTel log bridge if desired. Wire events can carry span context for export.
- Spans recommended for: provider calls, tool exec, subagent boundaries (high value for distributed view).
- Sampling: simple head-based or always-on for CLI (local); configurable rate for server.
- Export targets: stdout (for tenas log agents), OTLP (for full platforms).

**Result:** Best of both: zero-dep great local experience + production OTel when wanted. Can surpass goose/codex by documenting the hybrid + agent-specific semantics on top of OTel.

### CAR-Obs-08: Design Chain Completeness & Consistency

**Challenge:** OBS UCs exist only in table. SQ missing. Naming drift across puml/entities/audits. Wire is complete exemplar — replicate for OBS.

**Action:**
- Create `docs/UC/uc_observability.puml` (OBS-01..03 + cross links to wire).
- Create `docs/SQ/OBS/` with sq_obs01_stream_log.puml etc. (mirroring WRL style + notes on preconditions, invariants).
- Standardize names in one pass: prefer StructuredLogger / MetricsCollector / TraceCorrelator (from ENTITIES) or align all puml to chosen. Add ObservabilityManager facade if higher orchestration needed.
- Update main component puml, agent/provider/tool rels, container, context for consistency.
- Add to CT/DATA: observability data models (LogRecord, MetricPoint, TraceContext).
- Add observability to SM if lifecycle states touch it.
- Version all new diagrams consistently (6.0.0+).

**Immediate actions taken (this audit incorporates enhancements into C4/UC layers):**
- Created `docs/UC/uc_observability.puml` (modeled directly after uc_wire_log.puml; includes tenas emit notes + WRL cross-ref).
- Minor alignment edit to `docs/C4/c4_nasim_component.puml` (Observability Group now lists TraceCorrelator + LogRedactor to match dedicated obs puml + recommendations).

**Result:** Design chain parity between wire and obs (and other cross-cuts). Eliminates audit findings about "structured logging not in C4". Makes implementation unambiguous.

---

## 5. Recommended Enhanced Design (Target State)

**Groups (C4):**
- Observability: StructuredLogger (structlog or equivalent + json), MetricsCollector (prometheus + optional otel), TraceCorrelator + ContextPropagator, LogRedactor, Instrumentation (entrypoint adapters for CLI/HTTP/MCP).
- Wire Log (domain): same as today + EventType registry, WireEvent (versioned), compaction hooks.

**Cross-cutting integration points (instrument everywhere):**
- AgentOrchestrator (turns, events)
- Provider (every chat/stream: req/resp/meta/latency/tokens)
- ToolRegistry + individual tools (call/result/duration)
- Hooks (pre/post with timing + decision)
- Safety (decisions)
- Context (compaction, injection, token counts)
- Evaluation (signals, repetition)
- Session (load/save/fork with wire linkage)
- Subagent (spawn + join with trace continuity)
- MCP (adapter calls)

**Storage:**
- Structured: stdout (JSON) + optional local log files (rotating).
- Metrics: in-mem + /metrics.
- Wire: `~/.nasim/wire-logs/<session-id>/wire.jsonl` (or under sessions); index sidecar or embedded.
- Optional: export wire subset to platform (as structured events).

**Config + Safety:**
- As above + redaction rules (global + per-project).
- Never log full file contents or command output in structured unless debug + redacted; wire can store (for replay fidelity) with user consent flag.

**C4 Layer Updates (concrete):**
- Enhance `c4_nasim_component_observability.puml`: add redactor, propagator, CLI entry adapter; show WireLog group interaction; document exact emitted fields.
- Update `c4_nasim_component.puml` + agent/provider/tool to use consistent component names + rels.
- Container: keep platform boundary; note CLI may bypass log agent (direct stdout).
- Context: ensure obs_platform rel is not "future".
- Add missing UC + SQ diagrams.
- Extend CT/DATA + ER for obs records + canonical event types.
- ROD: if HTTP, expose /sessions/{id}/wire , /metrics (already), perhaps query logs (future).

This makes nasim logging/observability **the most complete in the reference set** while staying faithful to "emit only" + adding agent-unique value (wire).

---

## 6. Implementation Path (Post-Design)

1. Fix diagrams + add missing UC/SQ/CT (this audit drives).
2. Implement observability package (logger, metrics, trace, redactor) with tests.
3. Wire log implementation (existing specs).
4. Instrument core call sites (provider first — highest value).
5. Config integration + dual output (rich when tty).
6. Optional OTel behind feature flag.
7. Dashboards/alerts examples (reuse tenas Grafana patterns).
8. Update lower chain (CL, RDM milestones) + quality gates.

**Phasing aligned with existing:** Phase 1 foundation (CAR-13 + wire), Phase 2 full instrumentation, Phase 3 OTel + cost + advanced.

---

## 7. Expected Results

- **D14 score:** 9.5 (OTel hybrid + wire + redaction + full design chain) vs current 7 / refs max 10 (but missing nasim's wire+design).
- **Better than:** goose/codex on agent semantics + replay; SWE/aider on structure + ops; kimi/opencode on typed wire + fork UCs + C4 traceability.
- **Incorporated in C4:** All layers consistent; OBS as mature as WRL and other groups.
- **Nasim requirements met:** debuggability for complex agent runs, fork/branch histories, cost attribution, safety/quality auditability, multi-surface correlation, platform-friendly deployment.
- **Risks addressed:** bloat, secrets, coupling to infra, missing correlation.

**Next:** Implement after design sign-off. Use this as spec for CAR-13 rewrite + new CARs for wire/otel.

---

**References within repo:**
- `docs/C4/c4_nasim_component_observability.puml`, `c4_nasim_component_wire_log.puml`, `c4_nasim_container.puml`
- `docs/ENTITIES.md` (OBS + WRL sections)
- `docs/UC/uc_wire_log.puml` + SQ/WRL/
- `docs/audit/audit.2026.06.20.nasim.car.improvement.plan.md` (CAR-13)
- `docs/audit/audit.2026.06.20.deep.domain.audit.md` (D14 + E-07)
- `/home/salim/prj/aidirs/tenas/.../LOG/` (full platform C4s)
- Reference clones under `/home/salim/prj/salim/nasim/code/` (goose/codex crates, SWE-agent/utils/log.py, etc.)

This audit provides the focused path to a great, nasim-specific logging & observability design.
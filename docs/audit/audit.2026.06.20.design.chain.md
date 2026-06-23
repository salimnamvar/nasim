# nasim — Design Chain Audit

**Date:** 2026-06-20
**Scope:** `docs/` design artifacts (C4, UC, SM, SQ, CL) vs. global software-design rules,
the C4 linter, and the actual `nasim/` source package.
**Method:** `/design audit c4` + manual review against `rules/software-design/*` +
`tools/software-design/c4/c4_lint.py --strict` + code traceability check.

---

## Verdict

The design chain is **incomplete and inconsistent**. The C4 layer is clean (1 high
linter finding), but three structural invariants are broken: SQ count ≠ UC count,
component names diverge across C4 / CL / Code, and there is no canonical entity
registry to anchor them. The diagrams describe an OOP architecture the functional
source code does not implement.

| Severity | Count | Blocks |
| -------- | ----- | ------ |
| Critical | 5 | merge / "design done" |
| Recommended | 9 | should fix before code parity claim |
| Optional | 4 | polish |

---

## Critical findings

### C-1 — SQ count ≠ UC count (chain invariant)
- **Layers:** UC → SQ
- 15 UCs in `docs/UC/README.md`; only **3** SQ diagrams exist
  (`AGT-01`, `LLM-01`, `TL-01`). 12 UCs have no sequence diagram:
  CLI-01..04, AGT-02..04, LLM-02, TL-02..05.
- **Rule:** `cicd.md` — "SQ count ≠ UC count" is a forbidden violation; every UC
  must be designed before implementation.
- **Fix:** author the 12 missing SQ diagrams, or remove the UCs that are not in
  scope for v0.1 (move to a `FUT` group).

### C-2 — Component names diverge across C4 / CL / Code
- **Layers:** C4 → CL → Code
- No layer agrees on the class set:

  | C4 component | CL class | Code reality (`nasim/`) |
  | ------------ | -------- | ----------------------- |
  | `AgentLoop` + `ContextManager` | `Agent` (merged) | `Agent` (single class, holds `messages`) |
  | `ResponseParser` | — (folded into `OllamaClient`) | `OllamaClient._parse_response()` (method) |
  | `ToolExecutor`,`ToolRegistry`,`FileTools`,`ShellTool`,`DirTool` | `ToolRegistry`,`ToolDef` | module-level `TOOL_REGISTRY` dict + `execute_tool()`/`tool()` + free functions |
  | `REPL`,`ArgParser` | — | functions `repl()`, `parse_args()` |

- **Rule:** `design-chain.md` consistency principle — "the same entity name … must
  appear identically across every layer". `cl.md` — class names must match the
  canonical list.
- **Fix:** pick one model. Either (a) collapse C4 to match the functional code
  (`Agent`, `OllamaClient`, tool module), or (b) refactor code to the OOP model.
  Recommend (a) — the code is intentionally functional ("no framework" AD).

### C-3 — No canonical entity registry (`entities.md`)
- **Layers:** all
- There is no `.claude/rules/entities.md`. `c4.md` and `design-chain.md` require
  every component name be registered there before appearing in any diagram. Its
  absence is the root cause of C-2.
- **Fix:** create `.claude/rules/entities.md` listing each component, its Python
  class/module, and owning layer; reconcile C4/CL/Code names against it.

### C-4 — SQ decomposition inlines peer sub-flows (no `ref`)
- **Layer:** SQ
- `sq_agt01` inlines the LLM call (`agent -> llm : chat(...)`) and tool execution
  (`agent -> tool : execute_tool(...)`) instead of `ref`-ing the LLM-01 and
  TL-01/AGT-02 sub-flows. The sub-flow diagrams even declare `Contexts: Called by
  AGT-01`, but AGT-01 never refs them.
- **Rule:** `sq.md` — "Use `ref` blocks to call peer-group sub-flows. Never inline
  sub-flow detail." Anti-patterns AP-01, AP-02.
- **Fix:** replace inline calls in AGT-01 with `ref over` frames to the owning UCs.

### C-5 — Missing failure/`break` paths in SQ
- **Layer:** SQ
- `sq_agt01` and `sq_llm01` declare failures in their notes ("LLM error → ERROR",
  "HTTP error → exception") but contain **no** `break`/error path in the diagram
  body. Only `sq_tl01` models its failure (and uses `alt`, not `break`).
- **Rule:** `sq.md` — "All failure paths use `break` blocks"; AP-06 — design
  failure + happy path together.
- **Fix:** add `break` blocks for the LLM/tool error → ERROR → IDLE path; convert
  TL-01's not-found `alt` to `break`.

---

## Recommended findings

### R-1 — C4 component diagram spans 4 container boundaries (linter HIGH)
- `c4_lint.py --strict` → `C4-C3-001`: a C3 diagram should belong to exactly one
  container; `c4_nasim_component.puml` spans `CLI`, `agent`, `llm`, `tool`.
- **Rule:** `c4.md` — "For each non-trivial layer, author a dedicated component
  diagram … A single monolithic component diagram hides cross-layer boundary
  violations."
- **Fix:** split into `c4_nasim_component_{CLI,agent,llm,tool}.puml`, or accept the
  single overview and document the deviation. (Context + Container pass clean.)

### R-2 — SQ folder names ≠ UC group codes
- SQ dirs are `AGENT/`, `TOOL/`; UC group codes are `AGT`, `TL`. `LLM`/`CLI` match.
- **Rule:** `sq.md` file naming `docs/SQ/{GROUP}/` where GROUP is the UC group code.
- **Fix:** rename `SQ/AGENT` → `SQ/AGT`, `SQ/TOOL` → `SQ/TL` (or standardize the
  group codes to AGENT/TOOL everywhere — pick one and apply in UC, SQ, CL packages).

### R-3 — UC operations use banned/non-standard verbs
- `uc.md` allowed verbs are CRUD/lifecycle (`INSERT, READ, UPDATE, DELETE, VALIDATE,
  …`); `EXECUTE`, `INVOKE`, `RUN`, `TRIGGER` are explicitly banned.
- Violations: "**Execute** User Task", "**Execute** Slash Command", "**Execute**
  Shell Command", "**Invoke** Tool", "**Call** Ollama Chat", "**Manage**
  Conversation", "**Process** User Input", "**Stream** Ollama Chat", "**Display**
  Streaming Output", "**Write** File".
- **Note:** the global verb list is tuned to the OVMS/registry domain and fits a
  CLI agent poorly. **Fix:** either adopt the nearest allowed verbs, or record a
  project-level verb extension in `.claude/rules/entities.md`/project rules and
  reference it (do not silently diverge).

### R-4 — Sub-flow SQ diagrams omit required actor
- `sq_llm01` and `sq_tl01` name a specific UC ID as their primary subject, so by
  `sq.md` classification they are **UC-level sub-flows** → actor + full entry chain
  required. Both omit the actor.
- **Fix:** add the `Developer` actor + entry chain, or reclassify them explicitly as
  "process decomposition" (retitle "Step N of AGT-01") to legitimately drop the actor.

### R-5 — SQ lifeline names don't match CL/Code
- `sq_agt01` lifeline `AgentLoop` ≠ CL `Agent` ≠ code `Agent`. Same `ToolExecutor`
  vs `ToolRegistry`/`execute_tool`. Cascades from C-2/C-3.
- **Fix:** reconcile after entities.md exists.

### R-6 — CL mixes infrastructure/runtime classes with domain
- `cl.md` — "What does NOT belong: C4 architecture components (managers, adapters,
  APIs)". `OllamaClient` (HTTP adapter), `ToolRegistry` (infrastructure), `Agent`
  (orchestrator) are runtime, not domain. Pure value objects here are `LLMResponse`,
  `ToolCall`, `ToolDef`.
- **Fix:** either scope this file as a "runtime/structure" diagram (rename, not
  `cl_domain_model`) or split domain value-objects from runtime classes.

### R-7 — Missing layer READMEs (`SQ`, `CL`)
- `docs/SQ/README.md` and `docs/CL/README.md` are absent. `sq.md`/`cl.md` require a
  catalog README per layer; C4/UC/SM have them.
- **Fix:** add both inventories.

### R-8 — SM has no owning state-gate UC per state
- `sm.md` — "one SMT UC per target state". There is no SMT group and no UC owns the
  IDLE/THINKING/… writes.
- **Note:** states here are transient process states, not a persisted entity
  lifecycle, so the SMT/state-gate machinery applies weakly. **Fix:** document this
  as a deliberate deviation (process FSM, not entity lifecycle) in project rules, or
  drop the SMT expectation for this project.

### R-9 — `docs/README.md` chain text contradicts itself; empty `ER/` dir
- The chain diagram shows `… → SQ → ERD → CL → Code` but the prose says the chain
  "terminates at CL (no ERD needed)". `docs/ER/` exists but is empty.
- **Fix:** remove `ERD` from the chain diagram (and delete the empty `docs/ER/`), or
  keep the dir with a README stating "intentionally empty — no persistent stores".

---

## Optional findings

- **O-1** C4 header comment block sits *after* `!include`/`!theme`/`LAYOUT`; `c4.md`
  wants it as the opening block. Cosmetic.
- **O-2** Component diagram has 5 boundaries + many relations but no
  `skinparam linetype polyline`; `c4.md` recommends polyline for >4 boundaries to
  avoid overprint (default routing is acceptable).
- **O-3** `docs/cli_agents.txt` is a stray reference file in the `docs/` root (paths
  to external agent repos), not a design artifact — move to a `reference/` area.
- **O-4** SQ diagrams use no `box "…" #color` participant grouping (`sq.md` standard).

---

## C4 linter output (verbatim)

```
c4_nasim_context.puml    → 0 violations
c4_nasim_container.puml   → 0 violations
c4_nasim_component.puml   → 1 violation (C4-C3-001, HIGH)
```

`C4-C3-001`: Components span multiple Container boundaries
`['agent_boundary','cli_boundary','llm_boundary','tool_boundary']` — a C3 diagram
should belong to exactly one container. (See R-1.)

---

## Suggested remediation order

1. **C-3** create `entities.md` (canonical names) — unblocks C-2, R-5.
2. **C-2** reconcile C4/CL to the functional code model.
3. **C-1 / C-4 / C-5** complete and properly decompose the SQ layer.
4. **R-1 / R-2 / R-7** split component diagram, align group codes, add READMEs.
5. **R-3 / R-6 / R-8 / R-9** resolve verb policy, CL scope, SM deviation, chain text.
6. Re-run `/design audit all` to confirm green.

> Per session-sync policy, audit files are working papers. Once findings are applied,
> fold resolved decisions into project rules (`entities.md`, `anti-patterns.md`,
> `sprint.md`) and delete this file.

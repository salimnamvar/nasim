# nasim — Model Routing Taxonomy

**Date:** 2026-06-22
**Status:** RESOLVED (DGA-05)
**Owner:** RTG-03 CLASSIFY Task

---

## Task Types

| Task Type | Description | Classification Signals | Default Model Tier |
|-----------|-------------|----------------------|-------------------|
| `COMPLETION` | Autocomplete, single-line fill | Short input (<50 tokens), cursor position context | Cheap (local) |
| `GENERATION` | Create new code from description | "create", "write", "implement" keywords; no existing code context | Mid |
| `REFACTOR` | Restructure existing code | Existing file content in context; "refactor", "restructure", "clean" keywords | Mid |
| `ARCHITECTURE` | Design decisions, system design | "design", "architecture", "pattern", "tradeoff" keywords; multi-file scope | Expensive (reasoning) |
| `DEBUGGING` | Error analysis, fix bugs | Error traceback in context; "fix", "bug", "error", "failing" keywords | Expensive (reasoning) |
| `DOCUMENTATION` | Write docs, comments, README | "document", "explain", "comment", "readme" keywords | Cheap |
| `REVIEW` | Code review, audit | "review", "audit", "check", "evaluate" keywords; read-only context | Mid |

## Routing Rules

1. **Default rule:** If classification confidence < 0.6, use the session's default model.
2. **User override:** `--model <name>` or `/model <name>` forces a specific model for the entire session.
3. **Fallback chain:** If the selected model is unavailable, `FallbackChain` tries the next model in the configured list.
4. **Capability gating:** Before routing, verify `Provider.capabilities.supports_tools` for models that need tool calling.

## Classification Algorithm

`ModelRouter.classify_task(input, context)`:

1. Extract signals from input:
   - Input length (token count)
   - Presence of error traceback → DEBUGGING
   - Presence of file content in context → REFACTOR or REVIEW
   - Keyword matching against task type descriptions
   - Tool call history depth (deeper = more complex)

2. Score each task type:
   ```
   score(type) = keyword_match * 0.4 + context_signal * 0.4 + input_length_signal * 0.2
   ```

3. Select highest-scoring type. If max score < 0.6, return `None` (use default model).

4. Map task type to model via `ModelCatalog`:
   - `COMPLETION` → cheapest local model with tool support
   - `GENERATION`, `REFACTOR`, `REVIEW`, `DOCUMENTATION` → mid-tier model
   - `ARCHITECTURE`, `DEBUGGING` → expensive reasoning model

## Model Tier Configuration

Configured in `~/.nasim/config.yaml`:

```yaml
routing:
  tiers:
    cheap:
      model: "ollama/qwen2.5-coder:7b"
    mid:
      model: "anthropic/claude-sonnet-4-20250514"
    expensive:
      model: "anthropic/claude-opus-4-20250514"
  default_tier: mid
```

## Design Traceability

- UC: RTG-03 CLASSIFY Task
- SQ: `sq_rtg03_classify_task.puml`
- CL: `ModelRouter.classify_task()`, `RoutingStrategy`, `TaskClassifierStrategy`
- C4: `c4_nasim_component.puml` → Service Layer (Provider group)

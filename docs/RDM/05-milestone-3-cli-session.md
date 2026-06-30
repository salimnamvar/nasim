# 05 — Milestone 3: CLI & Session

Back to [docs/rdm/](./README.md).

**Status:** Active · **Prerequisite:** [04-milestone-2-agent-core.md](04-milestone-2-agent-core.md)

Implement the CLI layer: REPL loop, argument parsing, slash commands, and renderer. Wire agent events to terminal output.

---

## Scope

- ArgParser (CLI arguments with layered overrides)
- REPLSession (interactive REPL loop)
- Renderer (all terminal output: colors, diffs, streaming, tool display)
- SlashCommandHandler (/help, /quit, /plan, /approve, /continue, /session)
- Session integration (--continue, --session flags)

## Deliverables

| # | Deliverable | UC Trace | SQ Trace |
| - | --- | --- | --- |
| 1 | `ArgParser` | CLI-04 | sq_cli04 |
| 2 | `REPLSession` input loop | CLI-01 | sq_cli01 |
| 3 | `Renderer` streaming + tool display | CLI-03 | sq_cli03 |
| 4 | `SlashCommandHandler` | CLI-02, CLI-05, CLI-06 | sq_cli02 |
| 5 | Session integration (continue/session flags) | SESSIONSERVICE-01..04 | sq_ssn01..04 |

## Acceptance Criteria

- REPL reads input, dispatches to TaskService, renders AgentEvents
- Streaming text displays token-by-token with Rich formatting
- Tool calls show tool name, parameters, and results
- Slash commands: /help, /quit, /plan, /approve, /continue, /session
- Safety approval prompts user [y/N] for unsafe tools
- Session save/load works end-to-end
- Full integration test: user input → agent → tool → response → session save

# nasim — UC Inventory

**Design chain position:** `C4` → **`UC`** → `SM` → `SQ` → `ERD` → `CL` → `CT/DATA` → `CT/API` → `Code`

**Authoring policy:** `~/.agent-global/shared/rules/software-design/chain/uc.md`

**Source of truth:** `docs/C4/c4_nasim_component.puml` (v13.0.0)

**CSR entry chain:** External Client → Adapter (`cli_adp` / `http_adp` / `mcp_adp`) → `agent_ctrl` → Service → Repository

## UC Groups

| C4 Component ID | Title | UC Diagram | UC ID Prefix | UCs | Description |
|-----------------|-------|------------|--------------|:---:|-------------|
| `agent_ctrl` | Agent Controller | `uc_agent_ctrl.puml` | `AGENTCTRL-` | 5 | Single convergence point. Validate → Adapt → Route → Dispatch to services. |
| `cli_adp` | CLI Adapter | `uc_cli_adp.puml` | `CLIADP-` | 8 | REPL, slash commands, arg parsing. All business via `agent_ctrl`. |
| `http_adp` | HTTP Adapter | `uc_http_adp.puml` | `HTTPADP-` | 11 | REST/SSE API for WebApp, DesktopApp, MobileApp. All via `agent_ctrl`. |
| `mcp_adp` | MCP Adapter | `uc_mcp_adp.puml` | `MCPADP-` | 4 | MCP protocol for external MCP clients. All via `agent_ctrl`. |
| `task_svc` | Task Service | `uc_task_svc.puml` | `TASKSVC-` | 14 | Agentic loop, tool dispatch, subagents, personas, error recovery. |
| `tool_svc` | Tool Service | `uc_tool_svc.puml` | `TOOLSVC-` | 34 | Tool registry, hooks, plugins, execution dispatch. |
| `session_svc` | Session Service | `uc_session_svc.puml` | `SESSIONSVC-` | 9 | Session lifecycle: create, load, save, snapshot, revert. |
| `config_svc` | Config Service | `uc_config_svc.puml` | `CONFIGSVC-` | 3 | Config loading, validation, layered overrides. |
| `safety_svc` | Safety Service | `uc_safety_svc.puml` | `SAFETYSVC-` | 3 | Permission gating, injection scanning, egress inspection. |
| `context_svc` | Context Service | `uc_context_svc.puml` | `CONTEXTSVC-` | 6 | Context pipeline: graph, truncation, distillation, injection, compaction. |
| `eval_svc` | Evaluation Service | `uc_eval_svc.puml` | `EVALSVC-` | 9 | Task evaluation, retries, repetition detection, turn budget. |
| `session_repo` | Session Repository | `uc_session_repo.puml` | `SESSIONREPO-` | 3 | JSONL message persistence, turn management. |
| `history_repo` | History Repository | `uc_history_repo.puml` | `HISTORYREPO-` | 3 | Snapshots, revert index, FTS5 search index. |
| `config_repo` | Config Repository | `uc_config_repo.puml` | `CONFIGREPO-` | 3 | YAML, env vars, CLI flags, project overrides. |
| `memory_repo` | Memory Repository | `uc_memory_repo.puml` | `MEMORYREPOSITORY-` | 4 | Cross-session knowledge persistence. |
| `llm_repo` | LLM Repository | `uc_llm_repo.puml` | `LLMREPOSITORY-` | 8 | LLM API calls + model routing via litellm. |
| `fs_repo` | Filesystem Repository | `uc_fs_repo.puml` | `FSREPO-` | 4 | Host filesystem I/O: read, write, glob, grep. |
| `sandbox_repo` | Sandbox Repository | `uc_sandbox_repo.puml` | `SANDBOXREPOSITORY-` | 4 | Sandboxed command execution: timeout, isolation. |
| `edit_strategy_repo` | Edit Strategy Repository | `uc_edit_strategy_repo.puml` | `EDITSTRATEGYREPOSITORY-` | 10 | Diff staging, computation, safe application. |
| `git_repo` | Git Repository | `uc_git_repo.puml` | `GITREPOSITORY-` | 4 | Git operations: status, diff, commit, branch. |
| `mcp_repo` | MCP Repository | `uc_mcp_repo.puml` | `MCPREPOSITORY-` | 4 | MCP extension tools: discovery, invocation. |
| `repo_intel_repo` | Repo Intelligence Repository | `uc_repo_intel_repo.puml` | `REPOINTELLIGENCEREPOSITORY-` | 6 | AST indexing, symbol graph, embeddings, semantic search. |
| `web_repo` | Web Repository | `uc_web_repo.puml` | `WEBREPO-` | 2 | Web fetch: documentation, search results. |
| `wire_log_repo` | Wire Log Repository | `uc_wire_log_repo.puml` | `WIRELOGREPOSITORY-` | 5 | Append-only event store, fork, checkpoint. |
| **Total** | **24 components** | **24 diagrams** + `uc_overview.puml` | — | **165** | 1:1 C4 component ↔ UC diagram |

---

## C4 → UC Traceability (C4-UC-12)

Every C4 component maps 1:1 to a UC diagram file. This table satisfies C4-UC-12 traceability.

| UC ID | Operation | Component Owner | C4 Group |
|-------|-----------|-----------------|----------|
| AGENTCTRL-01..05 | Process → Validate → Adapt → Route → Dispatch | Agent Controller (`agent_ctrl`) | Controller Layer |
| CLIADP-01..08 | REPL, slash commands, arg parsing, streaming | CLI Adapter (`cli_adp`) | Controller Layer |
| HTTPADP-01..11 | REST session/tool/config CRUD, dispatch | HTTP Adapter (`http_adp`) | Controller Layer |
| MCPADP-01..04 | MCP request, tool listing, invocation, events | MCP Adapter (`mcp_adp`) | Controller Layer |
| TASKSVC-01..15 | Agentic loop, plan, subagent, persona, error recovery | Task Service (`task_svc`) | Service Layer |
| TOOLSVC-01..22, HK, PLG | File/shell/search/web/git/MCP tools, hooks, plugins | Tool Service (`tool_svc`) | Service Layer |
| SESSIONSVC-01..09 | Persist, read, list, restore, snapshot, revert, branch, delete | Session Service (`session_svc`) | Service Layer |
| CONFIGSVC-01..03 | Load, validate, apply layered config | Config Service (`config_svc`) | Service Layer |
| SAFETYSVC-01..03 | Check permission, request approval, apply safety mode | Safety Service (`safety_svc`) | Service Layer |
| CONTEXTSVC-01..06 | Process, truncate, distill, inject, compact, track budget | Context Service (`context_svc`) | Service Layer |
| EVALSVC-01..09 | Evaluate, check completion, retry, quality, turn budget | Evaluation Service (`eval_svc`) | Service Layer |
| SESSIONREPO-01..03 | Append, read, write session files | Session Repository (`session_repo`) | Repository Layer |
| HISTORYREPO-01..03 | Snapshot, index search, revert | History Repository (`history_repo`) | Repository Layer |
| CONFIGREPO-01..03 | Read YAML/env, write config | Config Repository (`config_repo`) | Repository Layer |
| MEMORYREPOSITORY-01..04 | Persist, recall, search, scope knowledge | Memory Repository (`memory_repo`) | Repository Layer |
| LLMREPOSITORY-01..08 | Register provider, request/stream chat, select/fallback/switch | LLM Repository (`llm_repo`) | Repository Layer |
| FSREPO-01..04 | Read, write, list, search files | Filesystem Repository (`fs_repo`) | Repository Layer |
| SANDBOXREPOSITORY-01..04 | Isolate, apply policy, monitor, limit resources | Sandbox Repository (`sandbox_repo`) | Repository Layer |
| EDITSTRATEGYREPOSITORY-01..10 | Select strategy, apply diff types, stage | Edit Strategy Repository (`edit_strategy_repo`) | Repository Layer |
| GITREPOSITORY-01..04 | Read status, commit, diff, auto-commit | Git Repository (`git_repo`) | Repository Layer |
| MCPREPOSITORY-01..04 | Connect, discover, adapt MCP tools, expose nasim tools | MCP Repository (`mcp_repo`) | Repository Layer |
| REPOINTELLIGENCEREPOSITORY-01..06 | Index, build symbol graph, rank, inject repomap, embed, search | Repo Intelligence Repository (`repo_intel_repo`) | Repository Layer |
| WEBREPO-01..02 | Fetch URL, search web | Web Repository (`web_repo`) | Repository Layer |
| WIRELOGREPOSITORY-01..05 | Append, read, seek, fork, checkpoint | Wire Log Repository (`wire_log_repo`) | Repository Layer |

---

## Agent Controller Group (`agent_ctrl`) — Convergence Point

Actor: `Interface Adapter` (cli_adp / http_adp / mcp_adp). End-users never associate directly with this group.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| AGENTCTRL-01 | PROCESS Request | Agent Controller | `sq_agentcontroller01_process_request.puml` | Route incoming request from any interface adapter to services |
| AGENTCTRL-02 | VALIDATE Request | Agent Controller | `sq_agentcontroller02_validate_request.puml` | Validate request format, permissions, and protocol |
| AGENTCTRL-03 | ADAPT Protocol | Agent Controller | `sq_agentcontroller03_adapt_protocol.puml` | Adapt between interface protocols (CLI, HTTP, MCP) |
| AGENTCTRL-04 | DISPATCH to Services | Agent Controller | `sq_agentcontroller04_dispatch_to_services.puml` | Dispatches to TASKSVC-01/07, SESSIONSVC-01..09, CONFIGSVC-01..03, TOOLSVC-14 |
| AGENTCTRL-05 | ROUTE Request | Agent Controller | — | Classifies request type (session/task/config) before dispatch |

---

## HTTP Adapter Group (`http_adp`) — Protocol Adaptation

HTTP endpoints adapt REST/SSE requests to `agent_ctrl` AC01 (PROCESS Request). No business logic lives in this group.
All HTTP operations delegate through Agent Controller (`agent_ctrl`), entering via AC01 for validation and routing.

| UC ID | Operation | HTTP Method | Path | Component Owner | SQ Diagram |
|-------|-----------|-------------|------|-----------------|------------|
| HTTPADP-01 | LIST Sessions | GET | /v1/sessions | HTTP Adapter → AC01 (Validate/Route) → Session Service | `sq_httpadapter01_list_sessions.puml` |
| HTTPADP-02 | CREATE Session | POST | /v1/sessions | HTTP Adapter → AC01 → Session Service | `sq_httpadapter02_create_session.puml` |
| HTTPADP-03 | GET Session | GET | /v1/sessions/{id} | HTTP Adapter → AC01 → Session Service | `sq_httpadapter03_get_session.puml` |
| HTTPADP-04 | UPDATE Session | PATCH | /v1/sessions/{id} | HTTP Adapter → AC01 → Session Service | `sq_httpadapter04_update_session.puml` |
| HTTPADP-05 | DELETE Session | DELETE | /v1/sessions/{id} | HTTP Adapter → AC01 → Session Service | `sq_httpadapter05_delete_session.puml` |
| HTTPADP-06 | DISPATCH Message | POST | /v1/sessions/{id}:dispatch | HTTP Adapter → AC01 → Task Service | `sq_httpadapter06_dispatch_message.puml` |
| HTTPADP-07 | LIST Messages | GET | /v1/sessions/{id}/messages | HTTP Adapter → AC01 → Session Service | `sq_httpadapter07_list_messages.puml` |
| HTTPADP-08 | LIST Tools | GET | /v1/tools | HTTP Adapter → AC01 → Tool Service | `sq_httpadapter08_list_tools.puml` |
| HTTPADP-09 | GET Tool | GET | /v1/tools/{name} | HTTP Adapter → AC01 → Tool Service | `sq_httpadapter09_get_tool.puml` |
| HTTPADP-10 | GET Config | GET | /v1/config | HTTP Adapter → AC01 → Config Service | `sq_httpadapter10_get_config.puml` |
| HTTPADP-11 | UPDATE Config | PATCH | /v1/config | HTTP Adapter → AC01 → Config Service | `sq_httpadapter11_update_config.puml` |

---

## CLI Adapter Group (`cli_adp`)

All business operations MUST delegate through Agent Controller (`agent_ctrl`). No direct calls to core services.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CLIADP-01 | PROCESS User Input | CLI Adapter | `sq_cli01_process_user_input.puml` | REPL loop, input handling. `<<include>>` AGENTCTRL-01, CLIADP-03. `<<extend>>` CLIADP-06 |
| CLIADP-02 | DISPATCH Slash Command | CLI Adapter | `sq_cli02_dispatch_slash_command.puml` | Maps `/cmd` strings to `agent_ctrl`. `<<include>>` AGENTCTRL-01. `<<extend>>` CLIADP-05, 07, 08 |
| CLIADP-03 | STREAM Output | CLI Adapter | `sq_cli03_stream_output.puml` | Renders AgentEvents from SSE stream to terminal |
| CLIADP-04 | READ CLI Arguments | CLI Adapter | `sq_cli04_read_cli_arguments.puml` | Startup argument parsing. `<<include>>` AGENTCTRL-01 |
| CLIADP-05 | ENABLE Plan Mode | CLI Adapter | `sq_cli05_enable_plan_mode.puml` | `/plan` slash command. `<<extend>>` CLIADP-02. `<<include>>` AGENTCTRL-01 → TASKSVC-07 |
| CLIADP-06 | REQUEST Approval | CLI Adapter | `sq_cli06_request_approval.puml` | Safety prompt during task. `<<extend>>` CLIADP-01. No direct actor association — triggered by system during REPL. `<<include>>` AGENTCTRL-01 → SAFETYSVC-02 |
| CLIADP-07 | SWITCH Model | CLI Adapter | `sq_cli07_switch_model.puml` | `/model` slash command. `<<extend>>` CLIADP-02. `<<include>>` AGENTCTRL-01 → LLMREPOSITORY-08 |
| CLIADP-08 | LIST Sessions | CLI Adapter | `sq_cli08_list_sessions.puml` | `/sessions` slash command. `<<extend>>` CLIADP-02. `<<include>>` AGENTCTRL-01 → SESSIONSVC-03 |

---

---

## MCP Adapter Group (`mcp_adp`)

All business operations MUST delegate through Agent Controller (`agent_ctrl`) AC01 (PROCESS Request). No direct calls to core services.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| MCPADP-01 | PROCESS MCP Request | MCP Adapter | `sq_mcp_adapter01_process_mcp_request.puml` | Accept and parse incoming MCP protocol request. `<<include>>` AGENTCTRL-01 |
| MCPADP-02 | LIST nasim Tools | MCP Adapter | `sq_mcp_adapter02_list_nasim_tools.puml` | Expose available tools via MCP tools/list. `<<include>>` AGENTCTRL-01 |
| MCPADP-03 | INVOKE nasim Tool | MCP Adapter | `sq_mcp_adapter03_invoke_nasim_tool.puml` | Execute tool via MCP tools/call. `<<include>>` AGENTCTRL-01, AGENTCTRL-04 |
| MCPADP-04 | STREAM Events | MCP Adapter | `sq_mcp_adapter04_stream_events.puml` | Stream agent events via MCP notification |

---

## Task Service Group (`task_svc`)

Entry: Adapter → `agent_ctrl` → `task_svc`. C4 orchestration: `task_svc` → `tool_svc`, `safety_svc`, `context_svc`, `eval_svc`.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| TASKSVC-01 | PROCESS User Task | Task Service | `sq_taskservice01_process_user_task.puml` | Primary orchestrator. `<<include>>` TASKSVC-02, TASKSVC-03, TASKSVC-15, CONTEXTSVC-01 |
| TASKSVC-02 | DISPATCH Tool Call | Task Service | `sq_taskservice02_dispatch_tool_call.puml` | Routes to `tool_svc`. `<<include>>` TOOLSVC-HK02, SAFETYSVC-01, LLMREPOSITORY-02/03 |
| TASKSVC-03 | UPDATE Conversation | Task Service | `sq_taskservice03_update_conversation.puml` | Appends messages. `<<include>>` SESSIONREPO-01, WIRELOGREPO-01 |
| TASKSVC-04 | DELETE History | Task Service | `sq_taskservice04_delete_history.puml` | Resets conversation history |
| TASKSVC-05 | *(vacant — ID retired per permanence rule)* | — | — | Numbering gap preserved |
| TASKSVC-06 | *(deprecated — moved to CONTEXTSVC-05)* | Context Service | `sq_taskservice06_compact_context.puml` | SQ retained; UC ownership transferred to `context_svc` |
| TASKSVC-07 | QUEUE Plan | Task Service | `sq_taskservice07_queue_plan.puml` | Holds queued tool calls in plan mode |
| TASKSVC-08 | APPROVE Plan | Task Service | `sq_taskservice08_approve_plan.puml` | Drains queued plan calls. `<<include>>` TASKSVC-02 |
| TASKSVC-09 | SPAWN Subagent | Task Service | `sq_taskservice09_spawn_subagent.puml` | Creates child agent with restricted tools |
| TASKSVC-10 | COLLECT Subagent Result | Task Service | `sq_taskservice10_collect_subagent_result.puml` | Gathers results from child agents |
| TASKSVC-11 | DELEGATE to Persona | Task Service | `sq_taskservice11_delegate_to_persona.puml` | Assigns tasks to specialized persona roles |
| TASKSVC-12 | LOAD Persona | Task Service | `sq_taskservice12_load_persona.puml` | Loads persona configuration |
| TASKSVC-13 | SWITCH Persona | Task Service | `sq_taskservice13_switch_persona.puml` | Switches persona at runtime |
| TASKSVC-14 | HANDLE Error | Task Service | `sq_taskservice14_handle_error.puml` | Structured error handling with recovery |
| TASKSVC-15 | DISPATCH Safety Pipeline | Task Service | `sq_taskservice15_dispatch_safety_pipeline.puml` | `<<include>>` SAFETYSVC-01, SAFETYSVC-03 |

---

## LLM Repository Group (LLM) — Provider + Router

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| LLMREPOSITORY-01 | REGISTER Provider | LLM Repository | `sq_llmrepository01_register_provider.puml` |
| LLMREPOSITORY-02 | REQUEST Chat | LLM Repository | `sq_llmrepository02_request_chat.puml` |
| LLMREPOSITORY-03 | STREAM Chat | LLM Repository | `sq_llmrepository03_stream_chat.puml` |
| LLMREPOSITORY-04 | SELECT Provider Backend | LLM Repository | `sq_llmrepository04_select_provider_backend.puml` |
| LLMREPOSITORY-05 | SELECT Model | LLM Repository | `sq_llmrepository05_select_model.puml` |
| LLMREPOSITORY-06 | APPLY Fallback | LLM Repository | `sq_llmrepository06_apply_fallback.puml` |
| LLMREPOSITORY-07 | CLASSIFY Task | LLM Repository | `sq_llmrepository07_classify_task.puml` |
| LLMREPOSITORY-08 | SWITCH Model | LLM Repository | `sq_llmrepository08_switch_model.puml` |

---

## Config Service Group (`config_svc`)

Entry: Adapter → `agent_ctrl` → `config_svc` → `config_repo`.

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| CONFIGSVC-01 | LOAD Config | Config Service | `sq_configservice01_load_config.puml` |
| CONFIGSVC-02 | VALIDATE Config | Config Service | `sq_configservice02_validate_config.puml` |
| CONFIGSVC-03 | APPLY Layered Config | Config Service | `sq_configservice03_apply_layered_config.puml` |

---

## Session Service Group (`session_svc`)

Entry: Adapter → `agent_ctrl` → `session_svc` → `session_repo`, `history_repo`, `wire_log_repo`.

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SESSIONSVC-01 | PERSIST Session | Session Service | `sq_sessionservice01_persist_session.puml` |
| SESSIONSVC-02 | READ Session | Session Service | `sq_sessionservice02_read_session.puml` |
| SESSIONSVC-03 | LIST Sessions | Session Service | `sq_sessionservice03_list_sessions.puml` |
| SESSIONSVC-04 | RESTORE Session | Session Service | `sq_sessionservice04_restore_session.puml` |
| SESSIONSVC-05 | SNAPSHOT Session | Session Service | `sq_sessionservice05_snapshot_session.puml` |
| SESSIONSVC-06 | REVERT Turn | Session Service | `sq_sessionservice06_revert_turn.puml` |
| SESSIONSVC-07 | SEARCH Sessions | Session Service | `sq_sessionservice07_search_sessions.puml` |
| SESSIONSVC-08 | BRANCH Session | Session Service | `sq_sessionservice08_branch_session.puml` |
| SESSIONSVC-09 | DELETE Session | Session Service | `sq_sessionservice09_delete_session.puml` |

---

## Safety Service Group (`safety_svc`)

Entry: Adapter → `agent_ctrl` → `task_svc` → `safety_svc`.

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SAFETYSVC-01 | CHECK Permission | Safety Service | `sq_safetyservice01_check_permission.puml` |
| SAFETYSVC-02 | REQUEST Approval | Safety Service | `sq_safetyservice02_request_approval.puml` |
| SAFETYSVC-03 | APPLY Safety Mode | Safety Service | `sq_safetyservice03_apply_safety_mode.puml` |

---

## Context Service Group (`context_svc`)

Entry: Adapter → `agent_ctrl` → `task_svc` → `context_svc` → `memory_repo`, `repo_intel_repo`.

CONTEXTSVC-02..06 are sub-use-cases of CONTEXTSVC-01.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CONTEXTSVC-01 | PROCESS Context | Context Service | `sq_contextservice01_process_context.puml` | Primary. `<<include>>` CONTEXTSVC-02..06 |
| CONTEXTSVC-02 | TRUNCATE Nodes | Context Service | `sq_contextservice02_truncate_nodes.puml` | Sub-UC of CONTEXTSVC-01 |
| CONTEXTSVC-03 | DISTILL Nodes | Context Service | `sq_contextservice03_distill_nodes.puml` | Sub-UC of CONTEXTSVC-01 |
| CONTEXTSVC-04 | INJECT Context | Context Service | `sq_contextservice04_inject_context.puml` | Sub-UC of CONTEXTSVC-01. `<<include>>` MEMORYREPO-02, REPOINTELREPO-04 |
| CONTEXTSVC-05 | COMPACT Nodes | Context Service | `sq_contextservice05_compact_nodes.puml` | Sub-UC of CONTEXTSVC-01 (absorbed legacy TASKSVC-06) |
| CONTEXTSVC-06 | TRACK Token Budget | Context Service | `sq_contextservice06_track_token_budget.puml` | Sub-UC of CONTEXTSVC-01 |

---

## MCP Repository Group (MCP)

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| MCPREPOSITORY-01 | CONNECT MCP Server | MCP Repository | `sq_mcprepository01_connect_mcp_server.puml` | |
| MCPREPOSITORY-02 | DISCOVER MCP Tools | MCP Repository | `sq_mcprepository02_discover_mcp_tools.puml` | |
| MCPREPOSITORY-03 | ADAPT MCP Tool | MCP Repository | `sq_mcprepository03_adapt_mcp_tool.puml` | |
| MCPREPOSITORY-04 | EXPOSE nasim Tools | MCP Repository | `sq_mcprepository04_expose_nasim_tools.puml` | Internal tool-format bridge only. External MCP exposure is **MCPADP-02** (`mcp_adp`), not this UC. |

> MCPREPOSITORY-05 (REGISTER A2A Task) and MCPREPOSITORY-06 (RECEIVE A2A Result) are planned (A2A agent-to-agent delegation). They are excluded from the current count pending SQ authoring per the design-chain discipline. When implemented, they will use new IDs (MCPREPOSITORY-05 and MCPREPOSITORY-06 remain reserved per UC-02 permanence rule).

> **MCP boundary:** `mcp_adp` (MCPADP-*) handles protocol adaptation for external MCP clients. `mcp_repo` (MCPREPOSITORY-*) handles outbound extension-tool integration invoked by `tool_svc`.

---

## Tool Service Group (`tool_svc`)

Entry: Adapter → `agent_ctrl` → `task_svc` → `tool_svc` → repositories.

| UC ID | Operation | Component Owner | SQ Diagram | Category |
|-------|-----------|-----------------|------------|----------|
| TOOLSVC-01 | READ File | Tool Service | `sq_toolservice01_read_file.puml` | File Operations |
| TOOLSVC-02 | INSERT File | Tool Service | `sq_toolservice02_insert_file.puml` | File Operations |
| TOOLSVC-03 | UPDATE File | Tool Service | `sq_toolservice03_update_file.puml` | File Operations |
| TOOLSVC-04 | LIST Directory | Tool Service | `sq_toolservice04_list_directory.puml` | File Operations |
| TOOLSVC-05 | DISPATCH Shell Command | Tool Service | `sq_toolservice05_dispatch_shell_command.puml` | Execution |
| TOOLSVC-06 | SEARCH Grep | Tool Service | `sq_toolservice06_search_grep.puml` | Search Tools |
| TOOLSVC-07 | SEARCH Glob | Tool Service | `sq_toolservice07_search_glob.puml` | Search Tools |
| TOOLSVC-08 | SEARCH Find | Tool Service | `sq_toolservice08_search_find.puml` | Search Tools |
| TOOLSVC-09 | FETCH Web Content | Tool Service | `sq_toolservice09_fetch_web_content.puml` | Web Tools |
| TOOLSVC-10 | SEARCH Web | Tool Service | `sq_toolservice10_search_web.puml` | Web Tools |
| TOOLSVC-11 | READ Git Status | Tool Service | `sq_toolservice11_read_git_status.puml` | Git Tools |
| TOOLSVC-12 | DISPATCH MCP Extension | Tool Service | `sq_toolservice12_dispatch_mcp_extension.puml` | MCP Dispatch |
| TOOLSVC-13 | READ LSP | Tool Service | `sq_toolservice13_read_lsp.puml` | LSP Tools |
| TOOLSVC-14 | LIST Registered Tools | Tool Service | `sq_toolservice14_list_registered_tools.puml` | Registry |
| TOOLSVC-15 | SPAWN Subagent | Tool Service | `sq_toolservice15_spawn_subagent.puml` | Agent Tools |
| TOOLSVC-16 | INSERT Todo | Tool Service | `sq_toolservice16_insert_todo.puml` | Task Tracking |
| TOOLSVC-17 | UPDATE Todo | Tool Service | `sq_toolservice17_update_todo.puml` | Task Tracking |
| TOOLSVC-18 | READ Todos | Tool Service | `sq_toolservice18_read_todos.puml` | Task Tracking |
| TOOLSVC-19 | PERSIST Memory | Tool Service | `sq_toolservice19_persist_memory.puml` | Memory |
| TOOLSVC-20 | RECALL Memory | Tool Service | `sq_toolservice20_recall_memory.puml` | Memory |
| TOOLSVC-21 | INSERT Plan | Tool Service | `sq_toolservice21_insert_plan.puml` | Planning |
| TOOLSVC-22 | UPDATE Plan | Tool Service | `sq_toolservice22_update_plan.puml` | Planning |
| TOOLSVC-HK01 | REGISTER Hook | Tool Service | `sq_toolservice_hk01_register_hook.puml` | Hooks |
| TOOLSVC-HK02 | DISPATCH Pre-Tool Hook | Tool Service | `sq_toolservice_hk02_dispatch_pre_tool_hook.puml` | Hooks |
| TOOLSVC-HK03 | DISPATCH Post-Tool Hook | Tool Service | `sq_toolservice_hk03_dispatch_post_tool_hook.puml` | Hooks |
| TOOLSVC-HK04 | DISPATCH Pre-LLM Hook | Tool Service | `sq_toolservice_hk04_dispatch_pre_llm_hook.puml` | Hooks |
| TOOLSVC-HK05 | DISPATCH Post-LLM Hook | Tool Service | `sq_toolservice_hk05_dispatch_post_llm_hook.puml` | Hooks |
| TOOLSVC-HK06 | VALIDATE Hook Result | Tool Service | `sq_toolservice_hk06_validate_hook_result.puml` | Hooks |
| TOOLSVC-PLG01 | DISCOVER Plugins | Tool Service | `sq_toolservice_plg01_discover_plugins.puml` | Plugins |
| TOOLSVC-PLG02 | LOAD Manifest | Tool Service | `sq_toolservice_plg02_load_manifest.puml` | Plugins |
| TOOLSVC-PLG03 | REGISTER Plugin Tools | Tool Service | `sq_toolservice_plg03_register_plugin_tools.puml` | Plugins |
| TOOLSVC-PLG04 | REGISTER Plugin Hooks | Tool Service | `sq_toolservice_plg04_register_plugin_hooks.puml` | Plugins |
| TOOLSVC-PLG05 | ENABLE Plugin | Tool Service | `sq_toolservice_plg05_enable_plugin.puml` | Plugins |
| TOOLSVC-PLG06 | DISABLE Plugin | Tool Service | `sq_toolservice_plg06_disable_plugin.puml` | Plugins |

---

## Memory Repository Group (MEM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| MEMORYREPOSITORY-01 | PERSIST Knowledge | Memory Repository | `sq_memoryrepository01_persist_knowledge.puml` |
| MEMORYREPOSITORY-02 | RECALL Knowledge | Memory Repository | `sq_memoryrepository02_recall_knowledge.puml` |
| MEMORYREPOSITORY-03 | SEARCH Knowledge | Memory Repository | `sq_memoryrepository03_search_knowledge.puml` |
| MEMORYREPOSITORY-04 | SCOPE Knowledge | Memory Repository | `sq_memoryrepository04_scope_knowledge.puml` |

---

## Git Repository Group (VCS)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| GITREPOSITORY-01 | READ Git Status | Git Repository | `sq_gitrepository01_read_git_status.puml` |
| GITREPOSITORY-02 | INSERT Commit | Git Repository | `sq_gitrepository02_insert_commit.puml` |
| GITREPOSITORY-03 | READ Diff | Git Repository | `sq_gitrepository03_read_diff.puml` |
| GITREPOSITORY-04 | AUTO-COMMIT | Git Repository | `sq_gitrepository04_auto_commit.puml` |

---

## Sandbox Repository Group (SBX)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SANDBOXREPOSITORY-01 | ISOLATE Command | Sandbox Repository | `sq_sandboxrepository01_isolate_command.puml` |
| SANDBOXREPOSITORY-02 | APPLY Sandbox Policy | Sandbox Repository | `sq_sandboxrepository02_apply_sandbox_policy.puml` |
| SANDBOXREPOSITORY-03 | MONITOR Process | Sandbox Repository | `sq_sandboxrepository03_monitor_process.puml` |
| SANDBOXREPOSITORY-04 | LIMIT Resources | Sandbox Repository | `sq_sandboxrepository04_limit_resources.puml` |

---

## Repo Intelligence Repository Group (RIM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| REPOINTELLIGENCEREPOSITORY-01 | INDEX Codebase | Repo Intelligence Repository | `sq_repointelligencerepository01_index_codebase.puml` |
| REPOINTELLIGENCEREPOSITORY-02 | BUILD Symbol Graph | Repo Intelligence Repository | `sq_repointelligencerepository02_build_symbol_graph.puml` |
| REPOINTELLIGENCEREPOSITORY-03 | RANK Results | Repo Intelligence Repository | `sq_repointelligencerepository03_rank_results.puml` |
| REPOINTELLIGENCEREPOSITORY-04 | INJECT RepoMap | Repo Intelligence Repository | `sq_repointelligencerepository04_inject_repo_map.puml` |
| REPOINTELLIGENCEREPOSITORY-05 | EMBED Code | Repo Intelligence Repository | `sq_repointelligencerepository05_embed_code.puml` |
| REPOINTELLIGENCEREPOSITORY-06 | SEARCH Semantic | Repo Intelligence Repository | `sq_repointelligencerepository06_search_semantic.puml` |

---

## Edit Strategy Repository Group (EDT)

EDITSTRATEGYREPOSITORY-02..10 are sub-use-cases of EDITSTRATEGYREPOSITORY-01. They use `<<include>>` from EDITSTRATEGYREPOSITORY-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EDITSTRATEGYREPOSITORY-01 | SELECT Strategy | Edit Strategy Repository | `sq_editstrategyrepository01_select_strategy.puml` | Primary. `<<include>>` EDITSTRATEGYREPOSITORY-02..10 |
| EDITSTRATEGYREPOSITORY-02 | APPLY Search-Replace | Edit Strategy Repository | `sq_editstrategyrepository02_apply_search_replace.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-03 | APPLY Whole-File | Edit Strategy Repository | `sq_editstrategyrepository03_apply_whole_file.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-04 | APPLY Unified Diff | Edit Strategy Repository | `sq_editstrategyrepository04_apply_unified_diff.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-05 | APPLY Fenced Block | Edit Strategy Repository | `sq_editstrategyrepository05_apply_fenced_block.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-06 | APPLY Function-Level | Edit Strategy Repository | `sq_editstrategyrepository06_apply_function_level.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-07 | APPLY Diff Sandbox | Edit Strategy Repository | `sq_editstrategyrepository07_apply_diff_sandbox.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-08 | APPLY Architect | Edit Strategy Repository | `sq_editstrategyrepository08_apply_architect.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-09 | APPLY Inline Patch | Edit Strategy Repository | `sq_editstrategyrepository09_apply_inline_patch.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-10 | STAGE Diff | Edit Strategy Repository | `sq_editstrategyrepository10_stage_diff.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |

---

## Evaluation Service Group (`eval_svc`)

Entry: Adapter → `agent_ctrl` → `task_svc` → `eval_svc`.

EVALSVC-02..09 are sub-use-cases of EVALSVC-01.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EVALSVC-01 | EVALUATE Task | Evaluation Service | `sq_evaluationservice01_evaluate_task.puml` | Primary. `<<include>>` EVALSVC-02..09 |
| EVALSVC-02 | CHECK Task Completion | Evaluation Service | `sq_evaluationservice02_check_task_completion.puml` | Sub-UC of EVALSVC-01 |
| EVALSVC-03 | CHECK Success | Evaluation Service | `sq_evaluationservice03_check_success.puml` | Sub-UC of EVALSVC-01 |
| EVALSVC-04 | VALIDATE With LLM | Evaluation Service | `sq_evaluationservice04_validate_with_llm.puml` | Sub-UC of EVALSVC-01 |
| EVALSVC-05 | VALIDATE Test Suite | Evaluation Service | `sq_evaluationservice05_validate_test_suite.puml` | Sub-UC of EVALSVC-01 |
| EVALSVC-06 | COORDINATE Retry | Evaluation Service | `sq_evaluationservice06_coordinate_retry.puml` | Sub-UC of EVALSVC-01 |
| EVALSVC-07 | RECORD Quality Signal | Evaluation Service | `sq_evaluationservice07_record_quality_signal.puml` | Sub-UC of EVALSVC-01 |
| EVALSVC-08 | DETECT Repetition | Evaluation Service | `sq_evaluationservice08_detect_repetition.puml` | Sub-UC of EVALSVC-01 |
| EVALSVC-09 | INJECT Turn Budget | Evaluation Service | `sq_evaluationservice09_inject_turn_budget.puml` | Sub-UC of EVALSVC-01 |

---

## Wire Log Repository Group (WRL)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| WIRELOGREPOSITORY-01 | APPEND Event | Wire Log Repository | `sq_wirelogrepository01_append_event.puml` |
| WIRELOGREPOSITORY-02 | READ Log | Wire Log Repository | `sq_wirelogrepository02_read_log.puml` |
| WIRELOGREPOSITORY-03 | SEEK Turn | Wire Log Repository | `sq_wirelogrepository03_seek_turn.puml` |
| WIRELOGREPOSITORY-04 | FORK Session | Wire Log Repository | `sq_wirelogrepository04_fork_session.puml` |
| WIRELOGREPOSITORY-05 | CHECKPOINT Turn | Wire Log Repository | `sq_wirelogrepository05_checkpoint_turn.puml` |

---

## Passive Policies (no behavioral UC)

| Data Structure | Owner Group | Role |
|----------------|-------------|------|
| CompactionPolicy | TASKSERVICE (Task Service) | Compaction rules: token threshold, message age, importance scoring |
| StrategyHeuristics | EDITSTRATEGYREPOSITORY (Edit Strategy Repository) | Rules: edit_size, risk_level, file_type, complexity |

---

## Actor Association Rules

Per the CSR (Controller → Service → Repository) discipline, actor associations follow strict layering:

| Layer | Actor | Rationale |
|-------|-------|-----------|
| **Controller Layer** (adapters) | `User`, `MCP Client` | External clients interact only with adapters |
| **Agent Controller** | `Interface Adapter` | Convergence point — adapters delegate here |
| **Service Layer** (task_svc, session_svc, config_svc) | `Agent Controller` | Services receive requests from AC, never directly from users |
| **Service Layer** (tool_svc, safety_svc, context_svc, eval_svc) | `Task Service` | These are orchestrated by task_svc, not directly by AC |

**Rule:** Only Master UCs at the Controller boundary have direct User/MCP Client associations. All other layers use their upstream component as the actor.

---

## Sub-UC Modeling

Sub-use-cases inherit the Component Owner of their parent UC and are modeled with `<<include>>` relationships in the parent UC diagram:

| Parent UC | Sub-UCs | Pattern |
|-----------|---------|---------|
| AGENTCTRL-01 (PROCESS Request) | AGENTCTRL-02..05 | `AGENTCTRL-01 ..> AGENTCTRL-02 : <<include>>` etc. |
| CONTEXTSVC-01 (PROCESS Context) | CONTEXTSVC-02..06 | `CONTEXTSVC-01 ..> CONTEXTSVC-02 : <<include>>` etc. |
| EDITSTRATEGYREPOSITORY-01 (SELECT Strategy) | EDITSTRATEGYREPOSITORY-02..10 | `EDITSTRATEGYREPOSITORY-01 ..> EDITSTRATEGYREPOSITORY-02 : <<include>>` etc. |
| EVALSVC-01 (EVALUATE Task) | EVALSVC-02..09 | `EVALSVC-01 ..> EVALSVC-02 : <<include>>` etc. |

No sub-UC has its own sub-UCs (no nesting beyond one level).

---

## Traceability Matrix (C4 Component → UC)

Every C4 component maps 1:1 to a UC diagram file.

### UC ID Naming Convention

| Scope | Rule | Example |
|-------|------|---------|
| **Canonical ID** (in UC diagram labels) | Full component name, uppercase, no underscores | `LLMREPOSITORY-02`, `SESSIONREPO-01` |
| **Cross-group extref** (in `<<extref>>` stubs) | Short C4 ID prefix from traceability table | `LLMREPO-02`, `WIRELOGREPO-01` |
| **C4 component ID** | snake_case in diagrams and README tables | `llm_repo`, `agent_ctrl` |

Extref stubs use the short prefix for readability; the owning diagram always uses the canonical ID.

### Primary Traceability Table

| C4 Component ID | UC Diagram Filename | UC ID Prefix | Title |
|-----------------|---------------------|--------------|-------|
| `agent_ctrl` | `uc_agent_ctrl.puml` | `AGENTCTRL-` | Agent Controller Group |
| `cli_adp` | `uc_cli_adp.puml` | `CLIADP-` | CLI Adapter Group |
| `http_adp` | `uc_http_adp.puml` | `HTTPADP-` | HTTP Adapter Group |
| `mcp_adp` | `uc_mcp_adp.puml` | `MCPADP-` | MCP Adapter Group |
| `task_svc` | `uc_task_svc.puml` | `TASKSVC-` | Task Service Group |
| `tool_svc` | `uc_tool_svc.puml` | `TOOLSVC-` | Tool Service Group |
| `session_svc` | `uc_session_svc.puml` | `SESSIONSVC-` | Session Service Group |
| `config_svc` | `uc_config_svc.puml` | `CONFIGSVC-` | Config Service Group |
| `safety_svc` | `uc_safety_svc.puml` | `SAFETYSVC-` | Safety Service Group |
| `context_svc` | `uc_context_svc.puml` | `CONTEXTSVC-` | Context Service Group |
| `eval_svc` | `uc_eval_svc.puml` | `EVALSVC-` | Evaluation Service Group |
| `session_repo` | `uc_session_repo.puml` | `SESSIONREPO-` | Session Repository Group |
| `history_repo` | `uc_history_repo.puml` | `HISTORYREPO-` | History Repository Group |
| `config_repo` | `uc_config_repo.puml` | `CONFIGREPO-` | Config Repository Group |
| `memory_repo` | `uc_memory_repo.puml` | `MEMORYREPOSITORY-` | Memory Repository Group |
| `llm_repo` | `uc_llm_repo.puml` | `LLMREPOSITORY-` | LLM Repository Group |
| `fs_repo` | `uc_fs_repo.puml` | `FSREPO-` | Filesystem Repository Group |
| `sandbox_repo` | `uc_sandbox_repo.puml` | `SANDBOXREPOSITORY-` | Sandbox Repository Group |
| `edit_strategy_repo` | `uc_edit_strategy_repo.puml` | `EDITSTRATEGYREPOSITORY-` | Edit Strategy Repository Group |
| `git_repo` | `uc_git_repo.puml` | `GITREPOSITORY-` | Git Repository Group |
| `mcp_repo` | `uc_mcp_repo.puml` | `MCPREPOSITORY-` | MCP Repository Group |
| `repo_intel_repo` | `uc_repo_intel_repo.puml` | `REPOINTELLIGENCEREPOSITORY-` | Repo Intelligence Repository Group |
| `web_repo` | `uc_web_repo.puml` | `WEBREPO-` | Web Repository Group |
| `wire_log_repo` | `uc_wire_log_repo.puml` | `WIRELOGREPOSITORY-` | Wire Log Repository Group |

### Controller Layer Detail

| C4 Component | C4 ID | UC Diagram | UC IDs | Description |
|--------------|-------|------------|--------|-------------|
| CLI Adapter | `cli_adp` | `uc_cli_adp.puml` | CLIADP-01..08 | CLI-specific interface: REPL, slash commands, rendering. Accessed via `agent_ctrl`. |
| HTTP Adapter | `http_adp` | `uc_http_adp.puml` | HTTPADP-01..11 | Core business operations (HTTP API). Accessed via `agent_ctrl`. |
| MCP Adapter | `mcp_adp` | `uc_mcp_adp.puml` | MCPADP-01..04 | MCP protocol interface: tool exposure, stdio/SSE transport. Accessed via `agent_ctrl`. |
| Agent Controller | `agent_ctrl` | `uc_agent_ctrl.puml` | AGENTCTRL-01..05 | Single convergence point: validates, adapts, routes, and dispatches to services. Actor: `Interface Adapter` (not end-user). |

### Service Layer

| C4 Component | C4 ID | UC Diagram | UC IDs | C4 Entry Chain | UC Actor |
|--------------|-------|------------|--------|----------------|----------|
| Task Service | `task_svc` | `uc_task_svc.puml` | TASKSVC-01..15 | `agent_ctrl` → `task_svc` | Agent Controller |
| Tool Service | `tool_svc` | `uc_tool_svc.puml` | TOOLSVC-01..22, HK, PLG | `agent_ctrl` → `task_svc` → `tool_svc` | Task Service |
| Session Service | `session_svc` | `uc_session_svc.puml` | SESSIONSVC-01..09 | `agent_ctrl` → `session_svc` | Agent Controller |
| Config Service | `config_svc` | `uc_config_svc.puml` | CONFIGSVC-01..03 | `agent_ctrl` → `config_svc` | Agent Controller |
| Safety Service | `safety_svc` | `uc_safety_svc.puml` | SAFETYSVC-01..03 | `agent_ctrl` → `task_svc` → `safety_svc` | Task Service |
| Context Service | `context_svc` | `uc_context_svc.puml` | CONTEXTSVC-01..06 | `agent_ctrl` → `task_svc` → `context_svc` | Task Service |
| Evaluation Service | `eval_svc` | `uc_eval_svc.puml` | EVALSVC-01..09 | `agent_ctrl` → `task_svc` → `eval_svc` | Task Service |

### Repository Layer

| C4 Component | C4 ID | UC Group | UC IDs | SQ Diagrams | Description |
|--------------|-------|----------|--------|-------------|-------------|
| LLM Repository | `llm_repo` | LLM | LLMREPOSITORY-01..08 | `sq_llmrepository01_register_provider.puml` .. `sq_llmrepository08_switch_model.puml` | LLM API calls and model routing |
| Memory Repository | `memory_repo` | MEM | MEMORYREPOSITORY-01..04 | `sq_memoryrepository01_persist_knowledge.puml` .. `sq_memoryrepository04_scope_knowledge.puml` | Cross-session knowledge |
| Sandbox Repository | `sandbox_repo` | SBX | SANDBOXREPOSITORY-01..04 | `sq_sandboxrepository01_isolate_command.puml` .. `sq_sandboxrepository04_limit_resources.puml` | Sandboxed execution |
| Edit Strategy Repository | `edit_strategy_repo` | EDT | EDITSTRATEGYREPOSITORY-01..10 | `sq_editstrategyrepository01_select_strategy.puml` .. `sq_editstrategyrepository10_stage_diff.puml` | Edit strategies |
| Git Repository | `git_repo` | VCS | GITREPOSITORY-01..04 | `sq_gitrepository01_read_git_status.puml` .. `sq_gitrepository04_auto_commit.puml` | Version control |
| MCP Repository | `mcp_repo` | MCP | MCPREPOSITORY-01..04 | `sq_mcprepository01_connect_mcp_server.puml` .. `sq_mcprepository04_expose_nasim_tools.puml` | MCP extension tools |
| Repo Intelligence Repository | `repo_intel_repo` | RIM | REPOINTELLIGENCEREPOSITORY-01..06 | `sq_repointelligencerepository01_index_codebase.puml` .. `sq_repointelligencerepository06_search_semantic.puml` | Codebase intelligence |
| Session Repository | `session_repo` | SSN | SESSIONREPO-01..03 | `sq_sessionrepository01_append_message.puml` .. `sq_sessionrepository03_manage_turns.puml` | JSONL message persistence, turn management |
| History Repository | `history_repo` | HIS | HISTORYREPO-01..03 | `sq_historyrepository01_create_snapshot.puml` .. `sq_historyrepository03_search_history.puml` | Snapshots, revert index, FTS5 search |
| Config Repository | `config_repo` | CFG | CONFIGREPO-01..03 | `sq_configrepository01_load_config.puml` .. `sq_configrepository03_apply_layered_config.puml` | YAML, env vars, CLI flags, project overrides |
| Filesystem Repository | `fs_repo` | FS | FSREPO-01..04 | `sq_filesystemrepository01_read_file.puml` .. `sq_filesystemrepository04_grep_search.puml` | Host filesystem I/O: read, write, glob, grep |
| Web Repository | `web_repo` | WEB | WEBREPO-01..02 | `sq_webrepository01_fetch_content.puml` .. `sq_webrepository02_search_web.puml` | Web fetch: documentation, search results |
| Wire Log Repository | `wire_log_repo` | WRL | WIRELOGREPOSITORY-01..05 | Append-only event store |
| Session Repository | `session_repo` | `uc_session_repo.puml` | SESSIONREPO-01..03 | Data-access: turn persistence, loaded by Session Service |
| History Repository | `history_repo` | `uc_history_repo.puml` | HISTORYREPO-01..03 | Data-access: snapshots, revert index, search |
| Config Repository | `config_repo` | `uc_config_repo.puml` | CONFIGREPO-01..03 | Data-access: YAML/env/CLI reads, loaded by Config Service |
| Filesystem Repository | `fs_repo` | `uc_fs_repo.puml` | FSREPO-01..04 | Data-access: file I/O, used by Tool Service |
| Web Repository | `web_repo` | `uc_web_repo.puml` | WEBREPO-01..02 | Data-access: web fetch, used by Tool Service |

### Data Stores (passive persistence — no behavioral UC)

| C4 Component | C4 ID | Persistence Target | Backed By |
|--------------|-------|-------------------|-----------|
| Session Store | `session_store` | Session data (JSONL) | Session Repository (SSN) |
| Memory Store | `memory_store` | Knowledge (JSON + vectors) | Memory Repository (MEM) |
| Wire Log Store | `wire_log_store` | Event log (JSONL) | Wire Log Repository (WRL) |
| Config Store | `config_store` | Configuration (YAML) | Config Repository (CFG) |

---

## State Machine Layer (SM)

**Source of truth:** Derived from `docs/C4/c4_nasim_component.puml` (v13.0.0) and the UC diagrams in this directory. Existing SM diagrams were **not** used as design input — only as output targets.

**Design chain position:** C4 → UC → **SM** → SQ

**Diagram location:** `docs/SM/` (one `.puml` file per entity lifecycle)

### Stateful Entities (15 State Machines)

| Priority | Entity | C4 Component | Layer | SM File | Type | Justification |
|:--------:|--------|--------------|-------|---------|------|---------------|
| 1 | Session | `session_svc` | Service | `sm_session_svc_session.puml` | Entity | SESSIONSVC-01..09 define create, persist, restore, snapshot, revert, branch, delete — a persisted conversation lifecycle. |
| 1 | Agent Run | `task_svc` | Service | `sm_task_svc_agent.puml` | Process FSM | TASKSVC-01 orchestrates the agentic loop (context → LLM → tools → safety → eval). Transient runtime states, not persisted. |
| 2 | Plan | `task_svc` | Service | `sm_task_svc_plan.puml` | Entity | TASKSVC-07/08 queue and approve tool calls in plan mode (CLIADP-05 `/plan`). Distinct approval-gated lifecycle. |
| 2 | Subagent | `task_svc` | Service | `sm_task_svc_subagent.puml` | Entity | TASKSVC-09/10 spawn and collect child agents with restricted tools. |
| 2 | Persona | `task_svc` | Service | `sm_task_svc_persona.puml` | Entity | TASKSVC-11..13 load, delegate, and switch persona roles at runtime. |
| 2 | Evaluation | `eval_svc` | Service | `sm_eval_svc_evaluation.puml` | Process | EVALSVC-01..09 orchestrate completion checks, LLM review, test validation, scoring, and retry. |
| 3 | Diff Staging | `edit_strategy_repo` | Repository | `sm_edit_strategy_repo_diff.puml` | Entity | EDITSTRATEGYREPOSITORY-10 stages diffs; SAFETYSVC-02 gates user approval before apply. |
| 3 | Sandbox Run | `sandbox_repo` | Repository | `sm_sandbox_repo_sandbox.puml` | Entity | SANDBOXREPOSITORY-01..04 isolate, monitor, and limit subprocess execution. |
| 3 | Safety Mode | `safety_svc` | Service | `sm_safety_svc_safety.puml` | Entity | SAFETYSVC-03 configures permissive/ask/block modes that gate agent transitions. |
| 4 | Plugin | `tool_svc` | Service | `sm_tool_svc_plugin.puml` | Entity | TOOLSVC-PLG01..06 discover, load, register, enable, and disable dynamic plugins. |
| 4 | MCP Client | `mcp_repo` | Repository | `sm_mcp_repo_client.puml` | Entity | MCPREPOSITORY-01/02 connect and discover extension tools from external MCP servers. |
| 4 | MCP Server | `mcp_repo` | Repository | `sm_mcp_repo_server.puml` | Entity | MCPREPOSITORY-04 exposes nasim tools (distinct from `mcp_adp` protocol adaptation). |
| 4 | LLM Router | `llm_repo` | Repository | `sm_llm_repo_router.puml` | Entity | LLMREPOSITORY-05..08 classify, select, fallback, and switch models. |
| 4 | LLM Provider | `llm_repo` | Repository | `sm_llm_repo_provider.puml` | Entity | LLMREPOSITORY-01..04 register providers and select backends for chat. |
| 5 | Repo Index | `repo_intel_repo` | Repository | `sm_repo_intel_repo_index.puml` | Entity | REPOINTELLIGENCEREPOSITORY-01/02/05 index, build symbol graph, embed code; index goes stale on file changes. |

### SM → UC Traceability Matrix

| State Machine | Related UC(s) | Driving Operations |
|---------------|---------------|-------------------|
| Session | SESSIONSVC-01, SESSIONSVC-02, SESSIONSVC-04, SESSIONSVC-08, SESSIONSVC-09 | PERSIST, READ, RESTORE, BRANCH, DELETE (+ HISTORYREPO-01/03, WIRELOGREPO-04/05 via includes) |
| Agent Run | TASKSVC-01..03, TASKSVC-07, TASKSVC-08, TASKSVC-14, TASKSVC-15, HTTPADP-06, CLIADP-01, CONTEXTSVC-05, LLMREPOSITORY-02..05, TOOLSVC-HK02, SAFETYSVC-02, EVALSVC-01..06, EDITSTRATEGYREPOSITORY-10 | PROCESS User Task loop; plan mode; compaction; routing; hooks; approval; evaluation; diff staging |
| Plan | TASKSVC-07, TASKSVC-08, TASKSVC-01, TASKSVC-14, CLIADP-05 | QUEUE Plan, APPROVE Plan, execution drain, error recovery |
| Subagent | TASKSVC-09, TASKSVC-10, TASKSVC-14, TOOLSVC-15 | SPAWN Subagent, COLLECT Subagent Result, HANDLE Error |
| Persona | TASKSVC-11, TASKSVC-12, TASKSVC-13 | DELEGATE to Persona, LOAD Persona, SWITCH Persona |
| Evaluation | EVALSVC-01..09 | EVALUATE Task and all sub-checks (completion, success, LLM review, tests, retry, repetition, turn budget) |
| Diff Staging | EDITSTRATEGYREPOSITORY-10, SAFETYSVC-02 | STAGE Diff, REQUEST Approval |
| Sandbox Run | SANDBOXREPOSITORY-01..04 | ISOLATE Command, APPLY Sandbox Policy, MONITOR Process, LIMIT Resources |
| Safety Mode | SAFETYSVC-01, SAFETYSVC-03, CLIADP-06 | CHECK Permission, APPLY Safety Mode, REQUEST Approval |
| Plugin | TOOLSVC-PLG01..06 | DISCOVER, LOAD Manifest, REGISTER Tools/Hooks, ENABLE, DISABLE |
| MCP Client | MCPREPOSITORY-01, MCPREPOSITORY-02, MCPREPOSITORY-03 | CONNECT MCP Server, DISCOVER MCP Tools, ADAPT MCP Tool |
| MCP Server | MCPREPOSITORY-04, MCPADP-02 | EXPOSE nasim Tools (outbound repo + inbound adapter) |
| LLM Router | LLMREPOSITORY-05..08, CLIADP-07 | SELECT Model, APPLY Fallback, CLASSIFY Task, SWITCH Model |
| LLM Provider | LLMREPOSITORY-01..04 | REGISTER Provider, REQUEST/STREAM Chat, SELECT Provider Backend |
| Repo Index | REPOINTELLIGENCEREPOSITORY-01, REPOINTELLIGENCEREPOSITORY-02, REPOINTELLIGENCEREPOSITORY-05 | INDEX Codebase, BUILD Symbol Graph, EMBED Code |

### Entities Considered — No Dedicated State Machine

| C4 Component | Reason |
|--------------|--------|
| `agent_ctrl`, `cli_adp`, `http_adp`, `mcp_adp` | Controller/adapters: protocol routing and presentation only (CSR rule). Lifecycle is request-scoped, not domain-persisted. |
| `config_svc`, `config_repo` | Load/validate/apply configuration — idempotent reads and writes, no multi-state lifecycle. |
| `context_svc` | CONTEXTSVC-01..06 are synchronous pipeline stages within one invocation. Compaction appears as Agent FSM `COMPACTING` state (CONTEXTSVC-05), not a separate entity. |
| `session_repo`, `history_repo`, `wire_log_repo` | Data-access repositories; lifecycle owned by `session_svc`. Wire log is append-only (no branching SM needed). |
| `memory_repo`, `fs_repo`, `web_repo`, `git_repo` | Stateless I/O or CRUD operations without approval-gated multi-step lifecycles. |
| Data stores (`session_store`, etc.) | Passive persistence — no behavioral UC. |

### Design Decisions (DRY / KISS / SRP / Encapsulation)

| Decision | Rationale |
|----------|-----------|
| **Agent Process FSM** is separate from entity SMs | SRP: `task_svc` runtime loop (THINKING, TOOL_EXEC) is transient; Session/Plan/Subagent have persisted or scoped lifecycles. |
| **Plan, Subagent, Persona** are three SMs under `task_svc` | Encapsulation: each cohesive entity gets one SM; avoids a monolithic task_svc diagram. |
| **LLM Router + Provider** split | SRP: routing (05..08) and provider connection (01..04) are distinct concerns in `uc_llm_repo.puml`. |
| **MCP Client + Server** split | C4 boundary: `mcp_repo` connects outbound (01..03) vs exposes inbound (04); `mcp_adp` handles protocol only. |
| **No Context Pipeline SM** | KISS: pipeline stages complete in one CONTEXTSVC-01 pass; only compaction triggers a visible agent state change. |
| **Diff Staging SM** encapsulates approval | DRY: AWAITING_APPROVAL in Agent FSM delegates to `edit_strategy_repo` + `safety_svc` entity lifecycles. |
| **Guards on transitions** | Used sparingly where UC behavior is conditional (e.g., `TASKSVC-08 / [approved]`, `LLMREPOSITORY-02 / [tool_calls]`). |

Full transition matrices and hex color registry: `docs/SM/README.md`.

---

## Sequence Diagram Layer (SQ)

**Source of truth:** C4 v13.0.0 → UC diagrams → SM diagrams (`docs/SM/`)

**Diagram location:** `docs/SQ/{Group}/sq_{group}{nn}_{description}.puml`

**Shared ref fragments (DRY):** `docs/SQ/common/sq_ref_*.puml`

### SQ Conventions (v10.0.0)

| Rule | Requirement |
|------|-------------|
| CSR layering | External Client → Adapter → `agent_ctrl` → Service → Repository |
| Orchestration | `context_svc`, `safety_svc`, `tool_svc`, `eval_svc` reached **only** via `task_svc` |
| State guards | `alt`/`else` fragments reflect SM transitions; state writes use `ref` blocks |
| Failure paths | `break` for early exits |
| RoD messages | `{UC-ID} camelCaseMethod({params})` e.g. `TASKSVC-01 processUserTask({sessionId})` |
| Intro/Summary | Documented in header comments + `==` section markers (no `note` blocks per linter) |

### Reusable Ref Fragments

| Ref File | Encapsulates | Used By |
|----------|--------------|---------|
| `sq_ref_assemble_context.puml` | CONTEXTSVC-01..06 pipeline + COMPACTING guard | TASKSVC-01 |
| `sq_ref_dispatch_safety_pipeline.puml` | TASKSVC-15 + SAFETYSVC-01/02/03 + ASK approval | TASKSVC-02 |
| `sq_ref_persist_conversation.puml` | TASKSVC-03 + SESSIONREPO-01 + WIRELOGREPO-01 | TASKSVC-01, TASKSVC-02 |
| `sq_ref_handle_error.puml` | TASKSVC-14 ERROR → IDLE recovery | TASKSVC-01 |

### Critical Flows — Updated (2026-07-01)

| SQ File | UC ID | SM Alignment | Status |
|---------|-------|--------------|--------|
| `sq_agentcontroller01_process_request.puml` | AGENTCTRL-01 | RECEIVING | ✅ v10.0.0 |
| `sq_httpadapter06_dispatch_message.puml` | HTTPADP-06 | IDLE → RECEIVING → RESPONDING → IDLE | ✅ v10.0.0 |
| `sq_taskservice01_process_user_task.puml` | TASKSVC-01 | sm_task_svc_agent (full loop) | ✅ v10.0.0 |
| `sq_taskservice02_dispatch_tool_call.puml` | TASKSVC-02 | TOOL_EXEC, AWAITING_APPROVAL, HOOK_RUNNING | ✅ v10.0.0 |
| `sq_taskservice07_queue_plan.puml` | TASKSVC-07 | sm_task_svc_plan + PLANNING | ✅ v10.0.0 |
| `sq_taskservice15_dispatch_safety_pipeline.puml` | TASKSVC-15 | sm_safety_svc_safety | ✅ v10.0.0 |
| `sq_contextservice01_process_context.puml` | CONTEXTSVC-01 | COMPACTING (CONTEXTSVC-05) | ✅ v10.0.0 |
| `sq_evaluationservice01_evaluate_task.puml` | EVALSVC-01 | sm_eval_svc_evaluation | ✅ v10.0.0 |
| `sq_safetyservice02_request_approval.puml` | SAFETYSVC-02 | AWAITING_APPROVAL | ✅ v10.0.0 |

### UC → SQ Traceability (Core Task Flows)

| UC ID | SQ Diagram | SM Diagram |
|-------|------------|------------|
| AGENTCTRL-01 | `sq_agentcontroller01_process_request.puml` | sm_task_svc_agent (RECEIVING) |
| AGENTCTRL-02..04 | included as `ref` in AGENTCTRL-01 | — |
| HTTPADP-06 | `sq_httpadapter06_dispatch_message.puml` | sm_task_svc_agent |
| CLIADP-01, CLIADP-05, CLIADP-06 | `sq_agentcontroller01`, `sq_taskservice07`, `sq_safetyservice02` | sm_task_svc_agent, sm_task_svc_plan |
| TASKSVC-01 | `sq_taskservice01_process_user_task.puml` | sm_task_svc_agent |
| TASKSVC-02 | `sq_taskservice02_dispatch_tool_call.puml` | sm_task_svc_agent |
| TASKSVC-03 | `sq_ref_persist_conversation.puml` | sm_session_svc_session |
| TASKSVC-07 | `sq_taskservice07_queue_plan.puml` | sm_task_svc_plan |
| TASKSVC-08 | `sq_taskservice08_approve_plan.puml` | sm_task_svc_plan |
| TASKSVC-14 | `sq_ref_handle_error.puml` | sm_task_svc_agent (ERROR) |
| TASKSVC-15 | `sq_taskservice15_dispatch_safety_pipeline.puml` | sm_safety_svc_safety |
| CONTEXTSVC-01..06 | `sq_contextservice01_process_context.puml` | sm_task_svc_agent (COMPACTING) |
| EVALSVC-01..09 | `sq_evaluationservice01_evaluate_task.puml` | sm_eval_svc_evaluation |
| SAFETYSVC-01..03 | `sq_taskservice15`, `sq_safetyservice02` | sm_safety_svc_safety |
| EDITSTRATEGYREPOSITORY-10 | `sq_editstrategyrepository10_stage_diff.puml` | sm_edit_strategy_repo_diff |

### SM → SQ State Guard Mapping (Agent Core)

| SM Transition | Guard | SQ Fragment |
|---------------|-------|-------------|
| IDLE → RECEIVING | HTTPADP-06 entry | `sq_httpadapter06`, `sq_taskservice01` |
| THINKING → COMPACTING | `token_count > budget` | `sq_ref_assemble_context`, `sq_contextservice01` |
| THINKING → TOOL_EXEC | `[tool_calls]` | `sq_taskservice01` alt branch |
| THINKING → RESPONDING | `[text_only]` | `sq_taskservice01` alt branch |
| TOOL_EXEC → AWAITING_APPROVAL | safety_mode=ASK | `sq_ref_dispatch_safety_pipeline` |
| PLANNING (agent) | plan_mode_active | `sq_taskservice07` |
| EVALUATING → THINKING | retry with feedback | `sq_evaluationservice01` |

Full SQ inventory: `docs/SQ/README.md` (165+ diagrams + 19 common ref blocks).

---

**Total: 164 UCs** across 24 C4 component groups (+ `uc_overview.puml` navigation map). Excludes overview group nodes and the vacant TASKSVC-05 ID (permanence rule). Repository-layer UCs use canonical `*REPOSITORY-*` IDs; extref stubs use short prefixes per the naming convention above.

### Adapter → Agent Controller → Service Routing

| Adapter UC | HTTP path / trigger | Agent Controller dispatch | Target service UC |
|------------|---------------------|---------------------------|-------------------|
| HTTPADP-01..05, 07 | `/v1/sessions*` | AGENTCTRL-04 | SESSIONSVC-01..09 |
| HTTPADP-06 | `POST ...:dispatch` | AGENTCTRL-04 | TASKSVC-01 |
| HTTPADP-08..09 | `/v1/tools*` | AGENTCTRL-04 | TOOLSVC-14 |
| HTTPADP-10..11 | `/v1/config` | AGENTCTRL-04 | CONFIGSVC-01..03 |
| CLIADP-01 | REPL input | AGENTCTRL-01 | TASKSVC-01 |
| CLIADP-02, 05, 07, 08 | Slash commands | AGENTCTRL-01 | Per-command service UC |
| MCPADP-01, 03 | MCP request / tool invoke | AGENTCTRL-01 | TASKSVC-01 |
| MCPADP-02 | MCP tools/list | AGENTCTRL-04 | TOOLSVC-14 |

---

## Review Checklist

Before finalising any UC diagram (from `chain/uc.md`):

**Naming:**
- [ ] UC titles use allowed verbs and precise entity qualifiers
- [ ] UC IDs follow `{GROUP}-{NN}` format, zero-padded
- [ ] No banned verbs used (`CREATE`, `GET`, `EXECUTE`, `RUN`, `INVOKE`, `PERFORM`, `TRIGGER`, `MANAGE`)
- [ ] Names match ubiquitous language in C4 model

**C4 Traceability:**
- [ ] Every actor traces to a C4 Person, System_Ext, or Component
- [ ] Every UC traces to a C4 component responsibility or container interaction
- [ ] Every C4 component has at least one UC owner (no orphan components)
- [ ] Traceability table (C4-UC-12) in README.md is complete

**Design Chain:**
- [ ] Every UC has a corresponding SQ diagram (or noted as "not yet designed")
- [ ] Every UC has a row in `docs/UC/README.md`
- [ ] Relationships use `<<include>>` downward only, `<<extend>>` for optional paths

**Visual:**
- [ ] One subject boundary per diagram
- [ ] No technology/implementation details inside use cases
- [ ] Diagrams have ≤15 use cases (split if larger)

---

## Scaffold Procedure

From `chain/uc.md` — when adding a new UC:

1. Determine: group, next available UC ID, operation name, C4 component backing, dependencies
2. Add a row to `docs/UC/README.md` with C4 component owner
3. Create a placeholder SQ scaffold file
4. Verify the C4 component has a UC owner (update C4 if orphaned)

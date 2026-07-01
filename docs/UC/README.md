# nasim — UC Inventory

**Source of truth:** `docs/C4/c4_nasim_component.puml` (v13.0.0)

**CSR entry chain:** External Client → Adapter (`cli_adp` / `http_adp` / `mcp_adp`) → `agent_ctrl` → Service → Repository

## UC Groups

| C4 Component ID | Title | UC Diagram | UC ID Prefix | UCs | Description |
|-----------------|-------|------------|--------------|:---:|-------------|
| `agent_ctrl` | Agent Controller | `uc_agent_ctrl.puml` | `AGENTCTRL-` | 4 | Single convergence point. Routes to `task_svc`, `session_svc`, `config_svc`. |
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
| `memory_repo` | Memory Repository | `uc_memory_repo.puml` | `MEMORYREPO-` | 4 | Cross-session knowledge persistence. |
| `llm_repo` | LLM Repository | `uc_llm_repo.puml` | `LLMREPO-` | 8 | LLM API calls + model routing via litellm. |
| `fs_repo` | Filesystem Repository | `uc_fs_repo.puml` | `FSREPO-` | 4 | Host filesystem I/O: read, write, glob, grep. |
| `sandbox_repo` | Sandbox Repository | `uc_sandbox_repo.puml` | `SANDBOXREPO-` | 4 | Sandboxed command execution: timeout, isolation. |
| `edit_strategy_repo` | Edit Strategy Repository | `uc_edit_strategy_repo.puml` | `EDITSTRATEGYREPO-` | 10 | Diff staging, computation, safe application. |
| `git_repo` | Git Repository | `uc_git_repo.puml` | `GITREPO-` | 4 | Git operations: status, diff, commit, branch. |
| `mcp_repo` | MCP Repository | `uc_mcp_repo.puml` | `MCPREPO-` | 4 | MCP extension tools: discovery, invocation. |
| `repo_intel_repo` | Repo Intelligence Repository | `uc_repo_intel_repo.puml` | `REPOINTELREPO-` | 6 | AST indexing, symbol graph, embeddings, semantic search. |
| `web_repo` | Web Repository | `uc_web_repo.puml` | `WEBREPO-` | 2 | Web fetch: documentation, search results. |
| `wire_log_repo` | Wire Log Repository | `uc_wire_log_repo.puml` | `WIRELOGREPO-` | 5 | Append-only event store, fork, checkpoint. |
| **Total** | **24 components** | **24 diagrams** + `uc_overview.puml` | — | **~175** | 1:1 C4 component ↔ UC diagram |

---

## Agent Controller Group (`agent_ctrl`) — Convergence Point

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| AGENTCTRL-01 | PROCESS Request | Agent Controller | `sq_agentcontroller01_process_request.puml` | Route incoming request from any interface adapter to services |
| AGENTCTRL-02 | VALIDATE Request | Agent Controller | `sq_agentcontroller02_validate_request.puml` | Validate request format, permissions, and protocol |
| AGENTCTRL-03 | ADAPT Protocol | Agent Controller | `sq_agentcontroller03_adapt_protocol.puml` | Adapt between interface protocols (CLI, HTTP, MCP) |
| AGENTCTRL-04 | DISPATCH to Services | Agent Controller | `sq_agentcontroller04_dispatch_to_services.puml` | Forward validated request to Task Service, Session Service, Config Service |

---

## HTTP Adapter Group (`http_adp`) — Core Business UCs

All HTTP operations delegate through Agent Controller (`agent_ctrl`) before reaching services.

| UC ID | Operation | HTTP Method | Path | Component Owner | SQ Diagram |
|-------|-----------|-------------|------|-----------------|------------|
| HTTPADP-01 | LIST Sessions | GET | /v1/sessions | HTTP Adapter → Agent Controller → Session Service | `sq_httpadapter01_list_sessions.puml` |
| HTTPADP-02 | CREATE Session | POST | /v1/sessions | HTTP Adapter → Agent Controller → Session Service | `sq_httpadapter02_create_session.puml` |
| HTTPADP-03 | GET Session | GET | /v1/sessions/{id} | HTTP Adapter → Agent Controller → Session Service | `sq_httpadapter03_get_session.puml` |
| HTTPADP-04 | UPDATE Session | PATCH | /v1/sessions/{id} | HTTP Adapter → Agent Controller → Session Service | `sq_httpadapter04_update_session.puml` |
| HTTPADP-05 | DELETE Session | DELETE | /v1/sessions/{id} | HTTP Adapter → Agent Controller → Session Service | `sq_httpadapter05_delete_session.puml` |
| HTTPADP-06 | DISPATCH Message | POST | /v1/sessions/{id}:dispatch | HTTP Adapter → Agent Controller → Task Service | `sq_httpadapter06_dispatch_message.puml` |
| HTTPADP-07 | LIST Messages | GET | /v1/sessions/{id}/messages | HTTP Adapter → Agent Controller → Session Service | `sq_httpadapter07_list_messages.puml` |
| HTTPADP-08 | LIST Tools | GET | /v1/tools | HTTP Adapter → Agent Controller → Tool Service | `sq_httpadapter08_list_tools.puml` |
| HTTPADP-09 | GET Tool | GET | /v1/tools/{name} | HTTP Adapter → Agent Controller → Tool Service | `sq_httpadapter09_get_tool.puml` |
| HTTPADP-10 | GET Config | GET | /v1/config | HTTP Adapter → Agent Controller → Config Service | `sq_httpadapter10_get_config.puml` |
| HTTPADP-11 | UPDATE Config | PATCH | /v1/config | HTTP Adapter → Agent Controller → Config Service | `sq_httpadapter11_update_config.puml` |

---

## CLI Adapter Group (`cli_adp`)

All business operations MUST delegate through Agent Controller (`agent_ctrl`). No direct calls to core services.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CLIADP-01 | PROCESS User Input | CLI Adapter | `sq_cli01_process_user_input.puml` | REPL loop, input handling, slash command dispatch. `<<include>>` AGENTCTRL-01 |
| CLIADP-02 | DISPATCH Slash Command | CLI Adapter | `sq_cli02_dispatch_slash_command.puml` | Maps `/cmd` strings to API calls. `<<include>>` AGENTCTRL-01, HTTPADP-01, HTTPADP-11 |
| CLIADP-03 | STREAM Output | CLI Adapter | `sq_cli03_stream_output.puml` | Renders AgentEvents from API SSE stream to terminal |
| CLIADP-04 | READ CLI Arguments | CLI Adapter | `sq_cli04_read_cli_arguments.puml` | Startup argument parsing. `<<include>>` CONFIGSVC-01 |
| CLIADP-05 | ENABLE Plan Mode | CLI Adapter | `sq_cli05_enable_plan_mode.puml` | `/plan` command. `<<include>>` TASKSVC-07 |
| CLIADP-06 | REQUEST Approval | CLI Adapter | `sq_cli06_request_approval.puml` | Safety prompt. `<<include>>` SAFETYSVC-02 |
| CLIADP-07 | SWITCH Model | CLI Adapter | `sq_cli07_switch_model.puml` | `/model` command. `<<include>>` LLMREPO-08 |
| CLIADP-08 | LIST Sessions | CLI Adapter | `sq_cli08_list_sessions.puml` | `/sessions` command. `<<include>>` HTTPADP-01 |

---

---

## MCP Adapter Group (`mcp_adp`)

All business operations MUST delegate through Agent Controller (`agent_ctrl`). No direct calls to core services.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| MCPADP-01 | PROCESS MCP Request | MCP Adapter | `sq_mcp_adapter01_process_mcp_request.puml` | Accept and parse incoming MCP protocol request. `<<include>>` AGENTCTRL-01 |
| MCPADP-02 | LIST nasim Tools | MCP Adapter | `sq_mcp_adapter02_list_nasim_tools.puml` | Expose available tools via MCP tools/list. `<<include>>` AGENTCTRL-04 |
| MCPADP-03 | INVOKE nasim Tool | MCP Adapter | `sq_mcp_adapter03_invoke_nasim_tool.puml` | Execute tool via MCP tools/call. `<<include>>` AGENTCTRL-01, AGENTCTRL-04 |
| MCPADP-04 | STREAM Events | MCP Adapter | `sq_mcp_adapter04_stream_events.puml` | Stream agent events via MCP notification |

---

## Task Service Group (`task_svc`)

Entry: Adapter → `agent_ctrl` → `task_svc`. C4 orchestration: `task_svc` → `tool_svc`, `safety_svc`, `context_svc`, `eval_svc`.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| TASKSVC-01 | PROCESS User Task | Task Service | `sq_taskservice01_process_user_task.puml` | Primary orchestrator. `<<include>>` TASKSVC-02, TASKSVC-03, TASKSVC-15, CONTEXTSVC-01 |
| TASKSVC-02 | DISPATCH Tool Call | Task Service | `sq_taskservice02_dispatch_tool_call.puml` | Routes to `tool_svc`. `<<include>>` SAFETYSVC-01, LLMREPO-02/03 |
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
| MCPREPOSITORY-04 | EXPOSE nasim Tools | MCP Repository | `sq_mcprepository04_expose_nasim_tools.puml` | |

> MCPREPOSITORY-05 (REGISTER A2A Task) and MCPREPOSITORY-06 (RECEIVE A2A Result) are planned (A2A agent-to-agent delegation). They are excluded from the current count pending SQ authoring per the design-chain discipline. When implemented, they will use new IDs (MCPREPOSITORY-05 and MCPREPOSITORY-06 remain reserved per UC-02 permanence rule).

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

## Sub-UC Modeling

Sub-use-cases inherit the Component Owner of their parent UC and are modeled with `<<include>>` relationships in the parent UC diagram:

| Parent UC | Sub-UCs | Pattern |
|-----------|---------|---------|
| AGENTCTRL-01 (PROCESS Request) | AGENTCTRL-02..04 | `AGENTCTRL-01 ..> AGENTCTRL-02 : <<include>>` etc. |
| CONTEXTSVC-01 (PROCESS Context) | CONTEXTSVC-02..06 | `CONTEXTSVC-01 ..> CONTEXTSVC-02 : <<include>>` etc. |
| EDITSTRATEGYREPO-01 (SELECT Strategy) | EDITSTRATEGYREPO-02..10 | `EDITSTRATEGYREPO-01 ..> EDITSTRATEGYREPO-02 : <<include>>` etc. |
| EVALSVC-01 (EVALUATE Task) | EVALSVC-02..09 | `EVALSVC-01 ..> EVALSVC-02 : <<include>>` etc. |

No sub-UC has its own sub-UCs (no nesting beyond one level).

---

## Traceability Matrix (C4 Component → UC)

Every C4 component maps 1:1 to a UC diagram file. UC ID prefixes are derived from the C4 component ID (remove underscores, uppercase).

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
| `memory_repo` | `uc_memory_repo.puml` | `MEMORYREPO-` | Memory Repository Group |
| `llm_repo` | `uc_llm_repo.puml` | `LLMREPO-` | LLM Repository Group |
| `fs_repo` | `uc_fs_repo.puml` | `FSREPO-` | Filesystem Repository Group |
| `sandbox_repo` | `uc_sandbox_repo.puml` | `SANDBOXREPO-` | Sandbox Repository Group |
| `edit_strategy_repo` | `uc_edit_strategy_repo.puml` | `EDITSTRATEGYREPO-` | Edit Strategy Repository Group |
| `git_repo` | `uc_git_repo.puml` | `GITREPO-` | Git Repository Group |
| `mcp_repo` | `uc_mcp_repo.puml` | `MCPREPO-` | MCP Repository Group |
| `repo_intel_repo` | `uc_repo_intel_repo.puml` | `REPOINTELREPO-` | Repo Intelligence Repository Group |
| `web_repo` | `uc_web_repo.puml` | `WEBREPO-` | Web Repository Group |
| `wire_log_repo` | `uc_wire_log_repo.puml` | `WIRELOGREPO-` | Wire Log Repository Group |

### Controller Layer Detail

| C4 Component | C4 ID | UC Diagram | UC IDs | Description |
|--------------|-------|------------|--------|-------------|
| CLI Adapter | `cli_adp` | `uc_cli_adp.puml` | CLIADP-01..08 | CLI-specific interface: REPL, slash commands, rendering. Accessed via `agent_ctrl`. |
| HTTP Adapter | `http_adp` | `uc_http_adp.puml` | HTTPADP-01..11 | Core business operations (HTTP API). Accessed via `agent_ctrl`. |
| MCP Adapter | `mcp_adp` | `uc_mcp_adp.puml` | MCPADP-01..04 | MCP protocol interface: tool exposure, stdio/SSE transport. Accessed via `agent_ctrl`. |
| Agent Controller | `agent_ctrl` | `uc_agent_ctrl.puml` | AGENTCTRL-01..04 | Single convergence point: routes requests to services |

### Service Layer

| C4 Component | C4 ID | UC Diagram | UC IDs | C4 Entry Chain |
|--------------|-------|------------|--------|----------------|
| Task Service | `task_svc` | `uc_task_svc.puml` | TASKSVC-01..15 | `agent_ctrl` → `task_svc` |
| Tool Service | `tool_svc` | `uc_tool_svc.puml` | TOOLSVC-01..22, HK, PLG | `agent_ctrl` → `task_svc` → `tool_svc` |
| Session Service | `session_svc` | `uc_session_svc.puml` | SESSIONSVC-01..09 | `agent_ctrl` → `session_svc` |
| Config Service | `config_svc` | `uc_config_svc.puml` | CONFIGSVC-01..03 | `agent_ctrl` → `config_svc` |
| Safety Service | `safety_svc` | `uc_safety_svc.puml` | SAFETYSVC-01..03 | `agent_ctrl` → `task_svc` → `safety_svc` |
| Context Service | `context_svc` | `uc_context_svc.puml` | CONTEXTSVC-01..06 | `agent_ctrl` → `task_svc` → `context_svc` |
| Evaluation Service | `eval_svc` | `uc_eval_svc.puml` | EVALSVC-01..09 | `agent_ctrl` → `task_svc` → `eval_svc` |

### Repository Layer

| C4 Component | C4 ID | UC Group | UC IDs | Description |
|--------------|-------|----------|--------|-------------|
| LLM Repository | `llm_repo` | LLM | LLMREPOSITORY-01..08 | LLM API calls and model routing |
| Memory Repository | `memory_repo` | MEM | MEMORYREPOSITORY-01..04 | Cross-session knowledge |
| Sandbox Repository | `sandbox_repo` | SBX | SANDBOXREPOSITORY-01..04 | Sandboxed execution |
| Edit Strategy Repository | `edit_strategy_repo` | EDT | EDITSTRATEGYREPOSITORY-01..10 | Edit strategies |
| Git Repository | `git_repo` | VCS | GITREPOSITORY-01..04 | Version control |
| MCP Repository | `mcp_repo` | MCP | MCPREPOSITORY-01..04 | MCP extension tools |
| Repo Intelligence Repository | `repo_intel_repo` | RIM | REPOINTELLIGENCEREPOSITORY-01..06 | Codebase intelligence |
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

**Total: 150 UCs** across 19 groups (18 original + MCP Adapter) matching 150 SQ diagrams (1:1 mapping, excluding TASKSERVICE-05 which is a vacant ID per permanence rule).

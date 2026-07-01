# nasim — UC Inventory (API-First)

## UC Groups

| Group | C4 Component ID | UC Diagram | UC ID Prefix | SQ Diagrams | Description |
|-------|-----------------|------------|--------------|:-----------:|-------------|
| Agent Controller | `agent_ctrl` | `uc_agent_ctrl.puml` | `AGENTCTRL-` | 4 | Single convergence point for all interface adapters. Routes validated requests to services. |
| HTTP Adapter | `http_adp` | `uc_http_adp.puml` | `HTTPADP-` | 11 | Core business operations exposed via HTTP API (ROD-compliant). Delegates through Agent Controller. |
| CLI Adapter | `cli_adp` | `uc_cli_adp.puml` | `CLIADP-` | 8 | CLI-specific interface UCs: REPL, slash commands, rendering. All business operations delegate through Agent Controller. |
| MCP Adapter | `mcp_adp` | `uc_mcp_adp.puml` | `MCPADP-` | 4 | MCP protocol interface: tool exposure, stdio/SSE transport. External MCP clients discover and invoke nasim tools. |
| AGENT | Task Service | 14 | Core agentic loop, permissions, context, plans, subagents |
| LLM | LLM Repository | 8 | LLM API calls + model routing via litellm |
| CONFIG | Config Service | 3 | Config loading, validation, layered overrides |
| SESSION | Session Service | 9 | Session persistence, versioning, search, fork |
| SAFETY | Safety Service | 3 | Permission gates, injection scanning, egress inspection |
| CONTEXT | Context Service | 6 | Context pipeline: graph construction, truncation, distillation, injection, compaction |
| MCP | MCP Repository | 4 | MCP extension tools: discovery, invocation |
| TOOL | Tool Service | 34 | All tool implementations, hooks, and plugins |
| MEMORY | Memory Repository | 4 | Cross-session knowledge persistence |
| GIT | Git Repository | 4 | Version control integration |
| SANDBOX | Sandbox Repository | 4 | Sandboxed command execution: timeout, isolation |
| REPOINTELLIGENCE | Repo Intelligence Repository | 6 | Codebase intelligence: AST indexing, symbol graph, embedding |
| EDITSTRATEGY | Edit Strategy Repository | 10 | Diff staging, computation, and safe application |
| EVALUATION | Evaluation Service | 9 | Task evaluation and quality checks |
| WIRELOG | Wire Log Repository | 5 | Append-only event store, fork, checkpoint |
| **Total** | **19 groups** | **150** | **1:1 UC↔SQ mapping (100%)** |

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

## Task Service Group (AGT)

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| TASKSERVICE-01 | PROCESS User Task | Task Service | `sq_taskservice01_process_user_task.puml` | Primary orchestrator. `<<include>>` TASKSERVICE-02, TASKSERVICE-03, TASKSERVICE-15 |
| TASKSERVICE-02 | DISPATCH Tool Call | Task Service | `sq_taskservice02_dispatch_tool_call.puml` | Routes to Tool Service. `<<include>>` SAFETYSERVICE-01 |
| TASKSERVICE-03 | UPDATE Conversation | Task Service | `sq_taskservice03_update_conversation.puml` | Appends messages, tracks token count |
| TASKSERVICE-04 | DELETE History | Task Service | `sq_taskservice04_delete_history.puml` | Resets conversation history |
| TASKSERVICE-05 | *(vacant — ID retired per permanence rule)* | — | — | Numbering gap preserved; IDs are permanent. No SQ assigned. |
| TASKSERVICE-06 | COMPACT Context | Context Service | `sq_taskservice06_compact_context.puml` | Summarizes old exchanges via secondary LLM |
| TASKSERVICE-07 | QUEUE Plan | Task Service | `sq_taskservice07_queue_plan.puml` | Holds queued tool calls in plan mode |
| TASKSERVICE-08 | APPROVE Plan | Task Service | `sq_taskservice08_approve_plan.puml` | Drains queued plan calls. `<<include>>` TASKSERVICE-02 |
| TASKSERVICE-09 | SPAWN Subagent | Task Service | `sq_taskservice09_spawn_subagent.puml` | Creates child agent with restricted tools |
| TASKSERVICE-10 | COLLECT Subagent Result | Task Service | `sq_taskservice10_collect_subagent_result.puml` | Gathers results from child agents |
| TASKSERVICE-11 | DELEGATE to Persona | Task Service | `sq_taskservice11_delegate_to_persona.puml` | Assigns tasks to specialized persona roles |
| TASKSERVICE-12 | LOAD Persona | Task Service | `sq_taskservice12_load_persona.puml` | Loads persona configuration |
| TASKSERVICE-13 | SWITCH Persona | Task Service | `sq_taskservice13_switch_persona.puml` | Switches persona at runtime |
| TASKSERVICE-14 | HANDLE Error | Task Service | `sq_taskservice14_handle_error.puml` | Structured error handling with recovery |
| TASKSERVICE-15 | DISPATCH Safety Pipeline | Safety Service | `sq_taskservice15_dispatch_safety_pipeline.puml` | Runs permission, injection, egress checks |

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

## Config Service Group (CFG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| CONFIGSERVICE-01 | LOAD Config | Config Service | `sq_configservice01_load_config.puml` |
| CONFIGSERVICE-02 | VALIDATE Config | Config Service | `sq_configservice02_validate_config.puml` |
| CONFIGSERVICE-03 | APPLY Layered Config | Config Service | `sq_configservice03_apply_layered_config.puml` |

---

## Session Service Group (SSN)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SESSIONSERVICE-01 | PERSIST Session | Session Service | `sq_sessionservice01_persist_session.puml` |
| SESSIONSERVICE-02 | READ Session | Session Service | `sq_sessionservice02_read_session.puml` |
| SESSIONSERVICE-03 | LIST Sessions | Session Service | `sq_sessionservice03_list_sessions.puml` |
| SESSIONSERVICE-04 | RESTORE Session | Session Service | `sq_sessionservice04_restore_session.puml` |
| SESSIONSERVICE-05 | SNAPSHOT Session | Session Service | `sq_sessionservice05_snapshot_session.puml` |
| SESSIONSERVICE-06 | REVERT Turn | Session Service | `sq_sessionservice06_revert_turn.puml` |
| SESSIONSERVICE-07 | SEARCH Sessions | Session Service | `sq_sessionservice07_search_sessions.puml` |
| SESSIONSERVICE-08 | BRANCH Session | Session Service | `sq_sessionservice08_branch_session.puml` |
| SESSIONSERVICE-09 | DELETE Session | Session Service | `sq_sessionservice09_delete_session.puml` |

---

## Safety Service Group (SAF)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SAFETYSERVICE-01 | CHECK Permission | Safety Service | `sq_safetyservice01_check_permission.puml` |
| SAFETYSERVICE-02 | REQUEST Approval | Safety Service | `sq_safetyservice02_request_approval.puml` |
| SAFETYSERVICE-03 | APPLY Safety Mode | Safety Service | `sq_safetyservice03_apply_safety_mode.puml` |

---

## Context Service Group (CTX)

CONTEXTSERVICE-02..06 are sub-use-cases of CONTEXTSERVICE-01. They use `<<include>>` from CONTEXTSERVICE-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CONTEXTSERVICE-01 | PROCESS Context | Context Service | `sq_contextservice01_process_context.puml` | Primary orchestrator. `<<include>>` CONTEXTSERVICE-02..06 |
| CONTEXTSERVICE-02 | TRUNCATE Nodes | Context Service | `sq_contextservice02_truncate_nodes.puml` | Sub-UC of CONTEXTSERVICE-01 |
| CONTEXTSERVICE-03 | DISTILL Nodes | Context Service | `sq_contextservice03_distill_nodes.puml` | Sub-UC of CONTEXTSERVICE-01 |
| CONTEXTSERVICE-04 | INJECT Context | Context Service | `sq_contextservice04_inject_context.puml` | Sub-UC of CONTEXTSERVICE-01 |
| CONTEXTSERVICE-05 | COMPACT Nodes | Context Service | `sq_contextservice05_compact_nodes.puml` | Sub-UC of CONTEXTSERVICE-01 |
| CONTEXTSERVICE-06 | TRACK Token Budget | Context Service | `sq_contextservice06_track_token_budget.puml` | Sub-UC of CONTEXTSERVICE-01 |

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

## Tool Service Group (TL) — Tools + Hooks + Plugins

TOOLSERVICE-01..22 are the current tool set. TOOLSERVICE-23 (QUERY Repo Map), TOOLSERVICE-24 (SEARCH Semantic), and TOOLSERVICE-25 (REVIEW Code) were removed from the top-level list — they lacked corresponding SQ diagrams and were speculative per YAGNI (SE-09). If re-added later, they must first receive SQ diagrams.

| UC ID | Operation | Component Owner | SQ Diagram | Category |
|-------|-----------|-----------------|------------|----------|
| TOOLSERVICE-01 | READ File | Tool Service | `sq_toolservice01_read_file.puml` | File Operations |
| TOOLSERVICE-02 | INSERT File | Tool Service | `sq_toolservice02_insert_file.puml` | File Operations |
| TOOLSERVICE-03 | UPDATE File | Tool Service | `sq_toolservice03_update_file.puml` | File Operations |
| TOOLSERVICE-04 | LIST Directory | Tool Service | `sq_toolservice04_list_directory.puml` | File Operations |
| TOOLSERVICE-05 | DISPATCH Shell Command | Tool Service | `sq_toolservice05_dispatch_shell_command.puml` | Execution |
| TOOLSERVICE-06 | SEARCH Grep | Tool Service | `sq_toolservice06_search_grep.puml` | Search Tools |
| TOOLSERVICE-07 | SEARCH Glob | Tool Service | `sq_toolservice07_search_glob.puml` | Search Tools |
| TOOLSERVICE-08 | SEARCH Find | Tool Service | `sq_toolservice08_search_find.puml` | Search Tools |
| TOOLSERVICE-09 | FETCH Web Content | Tool Service | `sq_toolservice09_fetch_web_content.puml` | Web Tools |
| TOOLSERVICE-10 | SEARCH Web | Tool Service | `sq_toolservice10_search_web.puml` | Web Tools |
| TOOLSERVICE-11 | READ Git Status | Tool Service | `sq_toolservice11_read_git_status.puml` | Git Tools |
| TOOLSERVICE-12 | DISPATCH MCP Extension | Tool Service | `sq_toolservice12_dispatch_mcp_extension.puml` | MCP Dispatch |
| TOOLSERVICE-13 | READ LSP | Tool Service | `sq_toolservice13_read_lsp.puml` | LSP Tools |
| TOOLSERVICE-14 | LIST Registered Tools | Tool Service | `sq_toolservice14_list_registered_tools.puml` | Registry |
| TOOLSERVICE-15 | SPAWN Subagent | Tool Service | `sq_toolservice15_spawn_subagent.puml` | Agent Tools |
| TOOLSERVICE-16 | INSERT Todo | Tool Service | `sq_toolservice16_insert_todo.puml` | Task Tracking |
| TOOLSERVICE-17 | UPDATE Todo | Tool Service | `sq_toolservice17_update_todo.puml` | Task Tracking |
| TOOLSERVICE-18 | READ Todos | Tool Service | `sq_toolservice18_read_todos.puml` | Task Tracking |
| TOOLSERVICE-19 | PERSIST Memory | Tool Service | `sq_toolservice19_persist_memory.puml` | Memory |
| TOOLSERVICE-20 | RECALL Memory | Tool Service | `sq_toolservice20_recall_memory.puml` | Memory |
| TOOLSERVICE-21 | INSERT Plan | Tool Service | `sq_toolservice21_insert_plan.puml` | Planning |
| TOOLSERVICE-22 | UPDATE Plan | Tool Service | `sq_toolservice22_update_plan.puml` | Planning |
| TOOLSERVICE-HK01 | REGISTER Hook | Tool Service | `sq_toolservice_hk01_register_hook.puml` | Hooks |
| TOOLSERVICE-HK02 | DISPATCH Pre-Tool Hook | Tool Service | `sq_toolservice_hk02_dispatch_pre_tool_hook.puml` | Hooks |
| TOOLSERVICE-HK03 | DISPATCH Post-Tool Hook | Tool Service | `sq_toolservice_hk03_dispatch_post_tool_hook.puml` | Hooks |
| TOOLSERVICE-HK04 | DISPATCH Pre-LLM Hook | Tool Service | `sq_toolservice_hk04_dispatch_pre_llm_hook.puml` | Hooks |
| TOOLSERVICE-HK05 | DISPATCH Post-LLM Hook | Tool Service | `sq_toolservice_hk05_dispatch_post_llm_hook.puml` | Hooks |
| TOOLSERVICE-HK06 | VALIDATE Hook Result | Tool Service | `sq_toolservice_hk06_validate_hook_result.puml` | Hooks |
| TOOLSERVICE-PLG01 | DISCOVER Plugins | Tool Service | `sq_toolservice_plg01_discover_plugins.puml` | Plugins |
| TOOLSERVICE-PLG02 | LOAD Manifest | Tool Service | `sq_toolservice_plg02_load_manifest.puml` | Plugins |
| TOOLSERVICE-PLG03 | REGISTER Plugin Tools | Tool Service | `sq_toolservice_plg03_register_plugin_tools.puml` | Plugins |
| TOOLSERVICE-PLG04 | REGISTER Plugin Hooks | Tool Service | `sq_toolservice_plg04_register_plugin_hooks.puml` | Plugins |
| TOOLSERVICE-PLG05 | ENABLE Plugin | Tool Service | `sq_toolservice_plg05_enable_plugin.puml` | Plugins |
| TOOLSERVICE-PLG06 | DISABLE Plugin | Tool Service | `sq_toolservice_plg06_disable_plugin.puml` | Plugins |

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

## Evaluation Service Group (EVL)

EVALUATIONSERVICE-02..09 are sub-use-cases of EVALUATIONSERVICE-01. They use `<<include>>` from EVALUATIONSERVICE-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EVALUATIONSERVICE-01 | EVALUATE Task | Evaluation Service | `sq_evaluationservice01_evaluate_task.puml` | Primary. `<<include>>` EVALUATIONSERVICE-02..09 |
| EVALUATIONSERVICE-02 | CHECK Task Completion | Evaluation Service | `sq_evaluationservice02_check_task_completion.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-03 | CHECK Success | Evaluation Service | `sq_evaluationservice03_check_success.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-04 | VALIDATE With LLM | Evaluation Service | `sq_evaluationservice04_validate_with_llm.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-05 | VALIDATE Test Suite | Evaluation Service | `sq_evaluationservice05_validate_test_suite.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-06 | COORDINATE Retry | Evaluation Service | `sq_evaluationservice06_coordinate_retry.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-07 | RECORD Quality Signal | Evaluation Service | `sq_evaluationservice07_record_quality_signal.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-08 | DETECT Repetition | Evaluation Service | `sq_evaluationservice08_detect_repetition.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-09 | INJECT Turn Budget | Evaluation Service | `sq_evaluationservice09_inject_turn_budget.puml` | Sub-UC of EVALUATIONSERVICE-01 |

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
| CONTEXTSERVICE-01 (PROCESS Context) | CONTEXTSERVICE-02..06 | `CONTEXTSERVICE-01 ..> CONTEXTSERVICE-02 : <<include>>` etc. |
| EDITSTRATEGYREPOSITORY-01 (SELECT Strategy) | EDITSTRATEGYREPOSITORY-02..10 | `EDITSTRATEGYREPOSITORY-01 ..> EDITSTRATEGYREPOSITORY-02 : <<include>>` etc. |
| EVALUATIONSERVICE-01 (EVALUATE Task) | EVALUATIONSERVICE-02..09 | `EVALUATIONSERVICE-01 ..> EVALUATIONSERVICE-02 : <<include>>` etc. |

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

| C4 Component | C4 ID | UC Group | UC IDs | Description |
|--------------|-------|----------|--------|-------------|
| Task Service | `task_svc` | AGT | TASKSERVICE-01..15 | Core agentic loop |
| Tool Service | `tool_svc` | TL | TOOLSERVICE-01..22, HK01..06, PLG01..06 | Tool registry, hooks, plugins |
| Session Service | `session_svc` | SSN | SESSIONSERVICE-01..09 | Session lifecycle |
| Config Service | `config_svc` | CFG | CONFIGSERVICE-01..03 | Config loading and validation |
| Safety Service | `safety_svc` | SAF | SAFETYSERVICE-01..03 | Permission gating, injection scanning |
| Context Service | `context_svc` | CTX | CONTEXTSERVICE-01..06 | Context pipeline |
| Evaluation Service | `eval_svc` | EVL | EVALUATIONSERVICE-01..09 | Task evaluation |

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

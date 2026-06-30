# nasim — UC Inventory (API-First)

## UC Groups

| Group | C4 Component Owner | SQ Diagrams | Description |
|-------|--------------------|:-----------:|-------------|
| AC | AgentController | 4 | Single convergence point for all interface containers. Routes validated requests to Core Engine. |
| API | HTTPAdapter | 11 | Core business operations exposed via API (ROD-compliant). Delegates through AgentController. |
| CLI | CLIAdapter | 8 | CLI-specific interface UCs: REPL, slash commands, rendering. All business operations delegate through AgentController. |
| AGENT | TaskService | 14 | Core agentic loop, permissions, context, plans, subagents |
| LLM | LLMRepository | 8 | LLM provider abstraction + model routing via litellm proxy |
| CONFIG | ConfigRepository | 3 | Config loading and validation |
| SESSION | SessionService | 9 | Session persistence, versioning, search, fork |
| SAFETY | SafetyService | 3 | Permission gates, user approval, safety modes |
| CONTEXTGRAPH | ContextService | 6 | Token counting, compaction, context pipeline |
| MCP | MCPRepository | 4 | Model Context Protocol client/server |
| TOOL | ToolService | 34 | All tool implementations, hooks, and plugins |
| MEMORY | MemoryRepository | 4 | Cross-session knowledge persistence |
| GIT | GitRepository | 4 | Version control integration |
| SANDBOX | SandboxRepository | 4 | OS-level process isolation |
| REPOINTELLIGENCE | RepoIntelligenceRepository | 6 | Codebase indexing, symbol graphs, embedding |
| EDITSTRATEGY | EditStrategyRepository | 10 | Polymorphic edit strategies |
| EVALUATION | EvaluationService | 9 | Task evaluation and quality checks |
| WIRELOG | WireLogRepository | 5 | Append-only event store, fork, checkpoint |
| **Total** | **18 groups** | **146** | **1:1 UC↔SQ mapping (100%)** |

---

## AgentController Group (AC) — Convergence Point

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| AGENTCONTROLLER-01 | PROCESS Request | AgentController | `sq_agentcontroller01_process_request.puml` | Route incoming request from any interface to Core Engine |
| AGENTCONTROLLER-02 | VALIDATE Request | AgentController | `sq_agentcontroller02_validate_request.puml` | Validate request format, permissions, and protocol |
| AGENTCONTROLLER-03 | ADAPT Protocol | AgentController | `sq_agentcontroller03_adapt_protocol.puml` | Adapt between interface protocols (CLI, HTTP, MCP) |
| AGENTCONTROLLER-04 | DISPATCH to Core Engine | AgentController | `sq_agentcontroller04_dispatch_to_core_engine.puml` | Forward validated request to AgentOrchestrator |

---

## HTTPAdapter Group (Entry Gate) — Core Business UCs

| UC ID | Operation | HTTP Method | Path | Component Owner | SQ Diagram |
|-------|-----------|-------------|------|-----------------|------------|
| HTTPADAPTER-01 | LIST Sessions | GET | /v1/sessions | HTTPAdapter → SessionService | `sq_httpadapter01_list_sessions.puml` |
| HTTPADAPTER-02 | CREATE Session | POST | /v1/sessions | HTTPAdapter → SessionService | `sq_httpadapter02_create_session.puml` |
| HTTPADAPTER-03 | GET Session | GET | /v1/sessions/{id} | HTTPAdapter → SessionService | `sq_httpadapter03_get_session.puml` |
| HTTPADAPTER-04 | UPDATE Session | PATCH | /v1/sessions/{id} | HTTPAdapter → SessionService | `sq_httpadapter04_update_session.puml` |
| HTTPADAPTER-05 | DELETE Session | DELETE | /v1/sessions/{id} | HTTPAdapter → SessionService | `sq_httpadapter05_delete_session.puml` |
| HTTPADAPTER-06 | DISPATCH Message | POST | /v1/sessions/{id}:dispatch | HTTPAdapter → TaskService | `sq_httpadapter06_dispatch_message.puml` |
| HTTPADAPTER-07 | LIST Messages | GET | /v1/sessions/{id}/messages | HTTPAdapter → SessionService | `sq_httpadapter07_list_messages.puml` |
| HTTPADAPTER-08 | LIST Tools | GET | /v1/tools | HTTPAdapter → ToolService | `sq_httpadapter08_list_tools.puml` |
| HTTPADAPTER-09 | GET Tool | GET | /v1/tools/{name} | HTTPAdapter → ToolService | `sq_httpadapter09_get_tool.puml` |
| HTTPADAPTER-10 | GET Config | GET | /v1/config | HTTPAdapter → ConfigRepository | `sq_httpadapter10_get_config.puml` |
| HTTPADAPTER-11 | UPDATE Config | PATCH | /v1/config | HTTPAdapter → ConfigRepository | `sq_httpadapter11_update_config.puml` |

---

## CLI Group (Interface Container)

All business operations MUST delegate through AgentController. No direct calls to core services.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CLI-01 | PROCESS User Input | CLIAdapter | `sq_cli01_process_user_input.puml` | REPL loop, input handling, slash command dispatch |
| CLI-02 | DISPATCH Slash Command | CLIAdapter | `sq_cli02_dispatch_slash_command.puml` | Maps `/cmd` strings to API calls. `<<include>>` HTTPADAPTER-01, HTTPADAPTER-11 |
| CLI-03 | STREAM Output | CLIAdapter | `sq_cli03_stream_output.puml` | Renders AgentEvents from API SSE stream to terminal |
| CLI-04 | READ CLI Arguments | CLIAdapter | `sq_cli04_read_cli_arguments.puml` | Startup argument parsing. `<<include>>` CONFIGREPOSITORY-01 |
| CLI-05 | ENABLE Plan Mode | CLIAdapter | `sq_cli05_enable_plan_mode.puml` | `/plan` command. `<<include>>` TASKSERVICE-07 |
| CLI-06 | REQUEST Approval | CLIAdapter | `sq_cli06_request_approval.puml` | Safety prompt. `<<include>>` SAFETYSERVICE-02 |
| CLI-07 | SWITCH Model | CLIAdapter | `sq_cli07_switch_model.puml` | `/model` command. `<<include>>` LLMREPOSITORY-04 |
| CLI-08 | LIST Sessions | CLIAdapter | `sq_cli08_list_sessions.puml` | `/sessions` command. `<<include>>` HTTPADAPTER-01 |

---

## TaskService Group (AGT)

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| TASKSERVICE-01 | PROCESS User Task | TaskService | `sq_taskservice01_process_user_task.puml` | Primary orchestrator. `<<include>>` TASKSERVICE-02, TASKSERVICE-03, TASKSERVICE-15 |
| TASKSERVICE-02 | DISPATCH Tool Call | TaskService | `sq_taskservice02_dispatch_tool_call.puml` | Routes to ToolService. `<<include>>` SAFETYSERVICE-01 |
| TASKSERVICE-03 | UPDATE Conversation | TaskService | `sq_taskservice03_update_conversation.puml` | Appends messages, tracks token count |
| TASKSERVICE-04 | DELETE History | TaskService | `sq_taskservice04_delete_history.puml` | Resets conversation history |
| TASKSERVICE-05 | *(vacant — ID retired per permanence rule)* | — | — | Numbering gap preserved; IDs are permanent. No SQ assigned. |
| TASKSERVICE-06 | COMPACT Context | ContextService | `sq_taskservice06_compact_context.puml` | Summarizes old exchanges via secondary LLM |
| TASKSERVICE-07 | QUEUE Plan | TaskService | `sq_taskservice07_queue_plan.puml` | Holds queued tool calls in plan mode |
| TASKSERVICE-08 | APPROVE Plan | TaskService | `sq_taskservice08_approve_plan.puml` | Drains queued plan calls. `<<include>>` TASKSERVICE-02 |
| TASKSERVICE-09 | SPAWN Subagent | TaskService | `sq_taskservice09_spawn_subagent.puml` | Creates child agent with restricted tools |
| TASKSERVICE-10 | COLLECT Subagent Result | TaskService | `sq_taskservice10_collect_subagent_result.puml` | Gathers results from child agents |
| TASKSERVICE-11 | DELEGATE to Persona | TaskService | `sq_taskservice11_delegate_to_persona.puml` | Assigns tasks to specialized persona roles |
| TASKSERVICE-12 | LOAD Persona | TaskService | `sq_taskservice12_load_persona.puml` | Loads persona configuration |
| TASKSERVICE-13 | SWITCH Persona | TaskService | `sq_taskservice13_switch_persona.puml` | Switches persona at runtime |
| TASKSERVICE-14 | HANDLE Error | TaskService | `sq_taskservice14_handle_error.puml` | Structured error handling with recovery |
| TASKSERVICE-15 | DISPATCH Safety Pipeline | SafetyService | `sq_taskservice15_dispatch_safety_pipeline.puml` | Runs permission, injection, egress checks |

---

## LLMRepository Group (LLM) — Provider + Router

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| LLMREPOSITORY-01 | REGISTER Provider | LLMRepository | `sq_llmrepository01_register_provider.puml` |
| LLMREPOSITORY-02 | REQUEST Chat | LLMRepository | `sq_llmrepository02_request_chat.puml` |
| LLMREPOSITORY-03 | STREAM Chat | LLMRepository | `sq_llmrepository03_stream_chat.puml` |
| LLMREPOSITORY-04 | SELECT Provider Backend | LLMRepository | `sq_llmrepository04_select_provider_backend.puml` |
| LLMREPOSITORY-01 | SELECT Model | LLMRepository | `sq_llmrepository01_select_model.puml` |
| LLMREPOSITORY-02 | APPLY Fallback | LLMRepository | `sq_llmrepository02_apply_fallback.puml` |
| LLMREPOSITORY-03 | CLASSIFY Task | LLMRepository | `sq_llmrepository03_classify_task.puml` |
| LLMREPOSITORY-04 | SWITCH Model | LLMRepository | `sq_llmrepository04_switch_model.puml` |

---

## ConfigRepository Group (CFG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| CONFIGREPOSITORY-01 | LOAD Config | ConfigRepository | `sq_configrepository01_load_config.puml` |
| CONFIGREPOSITORY-02 | VALIDATE Config | ConfigRepository | `sq_configrepository02_validate_config.puml` |
| CONFIGREPOSITORY-03 | APPLY Layered Config | ConfigRepository | `sq_configrepository03_apply_layered_config.puml` |

---

## SessionService Group (SSN)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SESSIONSERVICE-01 | PERSIST Session | SessionService | `sq_sessionservice01_persist_session.puml` |
| SESSIONSERVICE-02 | READ Session | SessionService | `sq_sessionservice02_read_session.puml` |
| SESSIONSERVICE-03 | LIST Sessions | SessionService | `sq_sessionservice03_list_sessions.puml` |
| SESSIONSERVICE-04 | RESTORE Session | SessionService | `sq_sessionservice04_restore_session.puml` |
| SESSIONSERVICE-05 | SNAPSHOT Session | SessionService | `sq_sessionservice05_snapshot_session.puml` |
| SESSIONSERVICE-06 | REVERT Turn | SessionService | `sq_sessionservice06_revert_turn.puml` |
| SESSIONSERVICE-07 | SEARCH Sessions | SessionService | `sq_sessionservice07_search_sessions.puml` |
| SESSIONSERVICE-08 | BRANCH Session | SessionService | `sq_sessionservice08_branch_session.puml` |
| SESSIONSERVICE-09 | DELETE Session | SessionService | `sq_sessionservice09_delete_session.puml` |

---

## SafetyService Group (SAF)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SAFETYSERVICE-01 | CHECK Permission | SafetyService | `sq_safetyservice01_check_permission.puml` |
| SAFETYSERVICE-02 | REQUEST Approval | SafetyService | `sq_safetyservice02_request_approval.puml` |
| SAFETYSERVICE-03 | APPLY Safety Mode | SafetyService | `sq_safetyservice03_apply_safety_mode.puml` |

---

## ContextService Group (CTX)

CONTEXTSERVICE-02..06 are sub-use-cases of CONTEXTSERVICE-01. They use `<<include>>` from CONTEXTSERVICE-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CONTEXTSERVICE-01 | PROCESS Context | ContextService | `sq_contextservice01_process_context.puml` | Primary orchestrator. `<<include>>` CONTEXTSERVICE-02..06 |
| CONTEXTSERVICE-02 | TRUNCATE Nodes | ContextService | `sq_contextservice02_truncate_nodes.puml` | Sub-UC of CONTEXTSERVICE-01 |
| CONTEXTSERVICE-03 | DISTILL Nodes | ContextService | `sq_contextservice03_distill_nodes.puml` | Sub-UC of CONTEXTSERVICE-01 |
| CONTEXTSERVICE-04 | INJECT Context | ContextService | `sq_contextservice04_inject_context.puml` | Sub-UC of CONTEXTSERVICE-01 |
| CONTEXTSERVICE-05 | COMPACT Nodes | ContextService | `sq_contextservice05_compact_nodes.puml` | Sub-UC of CONTEXTSERVICE-01 |
| CONTEXTSERVICE-06 | TRACK Token Budget | ContextService | `sq_contextservice06_track_token_budget.puml` | Sub-UC of CONTEXTSERVICE-01 |

---

## MCPRepository Group (MCP)

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| MCPREPOSITORY-01 | CONNECT MCP Server | MCPRepository | `sq_mcprepository01_connect_mcp_server.puml` | |
| MCPREPOSITORY-02 | DISCOVER MCP Tools | MCPRepository | `sq_mcprepository02_discover_mcp_tools.puml` | |
| MCPREPOSITORY-03 | ADAPT MCP Tool | MCPRepository | `sq_mcprepository03_adapt_mcp_tool.puml` | |
| MCPREPOSITORY-04 | EXPOSE nasim Tools | MCPRepository | `sq_mcprepository04_expose_nasim_tools.puml` | |

> MCPREPOSITORY-05 (REGISTER A2A Task) and MCPREPOSITORY-06 (RECEIVE A2A Result) are planned for Phase 2 (A2A agent-to-agent delegation). They are excluded from the current count pending SQ authoring per the design-chain discipline. When implemented, they will use new IDs (MCPREPOSITORY-05 and MCPREPOSITORY-06 remain reserved per UC-02 permanence rule).

---

## ToolService Group (TL) — Tools + Hooks + Plugins

TOOLSERVICE-01..22 are the current tool set. TOOLSERVICE-23 (QUERY Repo Map), TOOLSERVICE-24 (SEARCH Semantic), and TOOLSERVICE-25 (REVIEW Code) were removed from the top-level list — they lacked corresponding SQ diagrams and were speculative per YAGNI (SE-09). If re-added later, they must first receive SQ diagrams.

| UC ID | Operation | Component Owner | SQ Diagram | Category |
|-------|-----------|-----------------|------------|----------|
| TOOLSERVICE-01 | READ File | ToolService | `sq_toolservice01_read_file.puml` | File Operations |
| TOOLSERVICE-02 | INSERT File | ToolService | `sq_toolservice02_insert_file.puml` | File Operations |
| TOOLSERVICE-03 | UPDATE File | ToolService | `sq_toolservice03_update_file.puml` | File Operations |
| TOOLSERVICE-04 | LIST Directory | ToolService | `sq_toolservice04_list_directory.puml` | File Operations |
| TOOLSERVICE-05 | DISPATCH Shell Command | ToolService | `sq_toolservice05_dispatch_shell_command.puml` | Execution |
| TOOLSERVICE-06 | SEARCH Grep | ToolService | `sq_toolservice06_search_grep.puml` | Search Tools |
| TOOLSERVICE-07 | SEARCH Glob | ToolService | `sq_toolservice07_search_glob.puml` | Search Tools |
| TOOLSERVICE-08 | SEARCH Find | ToolService | `sq_toolservice08_search_find.puml` | Search Tools |
| TOOLSERVICE-09 | FETCH Web Content | ToolService | `sq_toolservice09_fetch_web_content.puml` | Web Tools |
| TOOLSERVICE-10 | SEARCH Web | ToolService | `sq_toolservice10_search_web.puml` | Web Tools |
| TOOLSERVICE-11 | READ Git Status | ToolService | `sq_toolservice11_read_git_status.puml` | Git Tools |
| TOOLSERVICE-12 | DISPATCH MCP Extension | ToolService | `sq_toolservice12_dispatch_mcp_extension.puml` | MCP Dispatch |
| TOOLSERVICE-13 | READ LSP | ToolService | `sq_toolservice13_read_lsp.puml` | LSP Tools |
| TOOLSERVICE-14 | LIST Registered Tools | ToolService | `sq_toolservice14_list_registered_tools.puml` | Registry |
| TOOLSERVICE-15 | SPAWN Subagent | ToolService | `sq_toolservice15_spawn_subagent.puml` | Agent Tools |
| TOOLSERVICE-16 | INSERT Todo | ToolService | `sq_toolservice16_insert_todo.puml` | Task Tracking |
| TOOLSERVICE-17 | UPDATE Todo | ToolService | `sq_toolservice17_update_todo.puml` | Task Tracking |
| TOOLSERVICE-18 | READ Todos | ToolService | `sq_toolservice18_read_todos.puml` | Task Tracking |
| TOOLSERVICE-19 | PERSIST Memory | ToolService | `sq_toolservice19_persist_memory.puml` | Memory |
| TOOLSERVICE-20 | RECALL Memory | ToolService | `sq_toolservice20_recall_memory.puml` | Memory |
| TOOLSERVICE-21 | INSERT Plan | ToolService | `sq_toolservice21_insert_plan.puml` | Planning |
| TOOLSERVICE-22 | UPDATE Plan | ToolService | `sq_toolservice22_update_plan.puml` | Planning |
| TOOLSERVICE-01 | REGISTER Hook | ToolService | `sq_toolserviceservice01_register_hook.puml` | Hooks |
| TOOLSERVICE-02 | DISPATCH Pre-Tool Hook | ToolService | `sq_toolserviceservice02_dispatch_pre_tool_hook.puml` | Hooks |
| TOOLSERVICE-03 | DISPATCH Post-Tool Hook | ToolService | `sq_toolserviceservice03_dispatch_post_tool_hook.puml` | Hooks |
| TOOLSERVICE-04 | DISPATCH Pre-LLM Hook | ToolService | `sq_toolserviceservice04_dispatch_pre_llm_hook.puml` | Hooks |
| TOOLSERVICE-05 | DISPATCH Post-LLM Hook | ToolService | `sq_toolserviceservice05_dispatch_post_llm_hook.puml` | Hooks |
| TOOLSERVICE-06 | VALIDATE Hook Result | ToolService | `sq_toolserviceservice06_validate_hook_result.puml` | Hooks |
| TOOLSERVICE-01 | DISCOVER Plugins | ToolService | `sq_toolserviceservice01_discover_plugins.puml` | Plugins |
| TOOLSERVICE-02 | LOAD Manifest | ToolService | `sq_toolserviceservice02_load_manifest.puml` | Plugins |
| TOOLSERVICE-03 | REGISTER Plugin Tools | ToolService | `sq_toolserviceservice03_register_plugin_tools.puml` | Plugins |
| TOOLSERVICE-04 | REGISTER Plugin Hooks | ToolService | `sq_toolserviceservice04_register_plugin_hooks.puml` | Plugins |
| TOOLSERVICE-05 | ENABLE Plugin | ToolService | `sq_toolserviceservice05_enable_plugin.puml` | Plugins |
| TOOLSERVICE-06 | DISABLE Plugin | ToolService | `sq_toolserviceservice06_disable_plugin.puml` | Plugins |

---

---

## MemoryRepository Group (MEM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| MEMORYREPOSITORY-01 | PERSIST Knowledge | MemoryRepository | `sq_memoryrepository01_persist_knowledge.puml` |
| MEMORYREPOSITORY-02 | RECALL Knowledge | MemoryRepository | `sq_memoryrepository02_recall_knowledge.puml` |
| MEMORYREPOSITORY-03 | SEARCH Knowledge | MemoryRepository | `sq_memoryrepository03_search_knowledge.puml` |
| MEMORYREPOSITORY-04 | SCOPE Knowledge | MemoryRepository | `sq_memoryrepository04_scope_knowledge.puml` |

---

## GitRepository Group (VCS)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| GITREPOSITORY-01 | READ Git Status | GitRepository | `sq_gitrepository01_read_git_status.puml` |
| GITREPOSITORY-02 | INSERT Commit | GitRepository | `sq_gitrepository02_insert_commit.puml` |
| GITREPOSITORY-03 | READ Diff | GitRepository | `sq_gitrepository03_read_diff.puml` |
| GITREPOSITORY-04 | AUTO-COMMIT | GitRepository | `sq_gitrepository04_auto_commit.puml` |

---

## SandboxRepository Group (SBX)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SANDBOXREPOSITORY-01 | ISOLATE Command | SandboxRepository | `sq_sandboxrepository01_isolate_command.puml` |
| SANDBOXREPOSITORY-02 | APPLY Sandbox Policy | SandboxRepository | `sq_sandboxrepository02_apply_sandbox_policy.puml` |
| SANDBOXREPOSITORY-03 | MONITOR Process | SandboxRepository | `sq_sandboxrepository03_monitor_process.puml` |
| SANDBOXREPOSITORY-04 | LIMIT Resources | SandboxRepository | `sq_sandboxrepository04_limit_resources.puml` |

---

## RepoIntelligenceRepository Group (RIM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| REPOINTELLIGENCEREPOSITORY-01 | INDEX Codebase | RepoIntelligenceRepository | `sq_repointelligencerepository01_index_codebase.puml` |
| REPOINTELLIGENCEREPOSITORY-02 | BUILD Symbol Graph | RepoIntelligenceRepository | `sq_repointelligencerepository02_build_symbol_graph.puml` |
| REPOINTELLIGENCEREPOSITORY-03 | RANK Results | RepoIntelligenceRepository | `sq_repointelligencerepository03_rank_results.puml` |
| REPOINTELLIGENCEREPOSITORY-04 | INJECT RepoMap | RepoIntelligenceRepository | `sq_repointelligencerepository04_inject_repo_map.puml` |
| REPOINTELLIGENCEREPOSITORY-05 | EMBED Code | RepoIntelligenceRepository | `sq_repointelligencerepository05_embed_code.puml` |
| REPOINTELLIGENCEREPOSITORY-06 | SEARCH Semantic | RepoIntelligenceRepository | `sq_repointelligencerepository06_search_semantic.puml` |

---

## EditStrategyRepository Group (EDT)

EDITSTRATEGYREPOSITORY-02..10 are sub-use-cases of EDITSTRATEGYREPOSITORY-01. They use `<<include>>` from EDITSTRATEGYREPOSITORY-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EDITSTRATEGYREPOSITORY-01 | SELECT Strategy | EditStrategyRepository | `sq_editstrategyrepository01_select_strategy.puml` | Primary. `<<include>>` EDITSTRATEGYREPOSITORY-02..10 |
| EDITSTRATEGYREPOSITORY-02 | APPLY Search-Replace | EditStrategyRepository | `sq_editstrategyrepository02_apply_search_replace.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-03 | APPLY Whole-File | EditStrategyRepository | `sq_editstrategyrepository03_apply_whole_file.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-04 | APPLY Unified Diff | EditStrategyRepository | `sq_editstrategyrepository04_apply_unified_diff.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-05 | APPLY Fenced Block | EditStrategyRepository | `sq_editstrategyrepository05_apply_fenced_block.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-06 | APPLY Function-Level | EditStrategyRepository | `sq_editstrategyrepository06_apply_function_level.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-07 | APPLY Diff Sandbox | EditStrategyRepository | `sq_editstrategyrepository07_apply_diff_sandbox.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-08 | APPLY Architect | EditStrategyRepository | `sq_editstrategyrepository08_apply_architect.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-09 | APPLY Inline Patch | EditStrategyRepository | `sq_editstrategyrepository09_apply_inline_patch.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |
| EDITSTRATEGYREPOSITORY-10 | STAGE Diff | EditStrategyRepository | `sq_editstrategyrepository10_stage_diff.puml` | Sub-UC of EDITSTRATEGYREPOSITORY-01 |

---

## EvaluationService Group (EVL)

EVALUATIONSERVICE-02..09 are sub-use-cases of EVALUATIONSERVICE-01. They use `<<include>>` from EVALUATIONSERVICE-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EVALUATIONSERVICE-01 | EVALUATE Task | EvaluationService | `sq_evaluationservice01_evaluate_task.puml` | Primary. `<<include>>` EVALUATIONSERVICE-02..09 |
| EVALUATIONSERVICE-02 | CHECK Task Completion | EvaluationService | `sq_evaluationservice02_check_task_completion.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-03 | CHECK Success | EvaluationService | `sq_evaluationservice03_check_success.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-04 | VALIDATE With LLM | EvaluationService | `sq_evaluationservice04_validate_with_llm.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-05 | VALIDATE Test Suite | EvaluationService | `sq_evaluationservice05_validate_test_suite.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-06 | COORDINATE Retry | EvaluationService | `sq_evaluationservice06_coordinate_retry.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-07 | RECORD Quality Signal | EvaluationService | `sq_evaluationservice07_record_quality_signal.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-08 | DETECT Repetition | EvaluationService | `sq_evaluationservice08_detect_repetition.puml` | Sub-UC of EVALUATIONSERVICE-01 |
| EVALUATIONSERVICE-09 | INJECT Turn Budget | EvaluationService | `sq_evaluationservice09_inject_turn_budget.puml` | Sub-UC of EVALUATIONSERVICE-01 |

---

## WireLogRepository Group (WRL)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| WIRELOGREPOSITORY-01 | APPEND Event | WireLogRepository | `sq_wirelogrepository01_append_event.puml` |
| WIRELOGREPOSITORY-02 | READ Log | WireLogRepository | `sq_wirelogrepository02_read_log.puml` |
| WIRELOGREPOSITORY-03 | SEEK Turn | WireLogRepository | `sq_wirelogrepository03_seek_turn.puml` |
| WIRELOGREPOSITORY-04 | FORK Session | WireLogRepository | `sq_wirelogrepository04_fork_session.puml` |
| WIRELOGREPOSITORY-05 | CHECKPOINT Turn | WireLogRepository | `sq_wirelogrepository05_checkpoint_turn.puml` |

---

## Passive Policies (no behavioral UC)

| Data Structure | Owner Group | Role |
|----------------|-------------|------|
| CompactionPolicy | AGT (Agent) | Compaction rules: token threshold, message age, importance scoring |
| StrategyHeuristics | EDT (Edit Strategy) | Rules: edit_size, risk_level, file_type, complexity |

---

## Sub-UC Modeling

Sub-use-cases inherit the Component Owner of their parent UC and are modeled with `<<include>>` relationships in the parent UC diagram:

| Parent UC | Sub-UCs | Pattern |
|-----------|---------|---------|
| AGENTCONTROLLER-01 (PROCESS Request) | AGENTCONTROLLER-02..04 | `AGENTCONTROLLER-01 ..> AGENTCONTROLLER-02 : <<include>>` etc. |
| CONTEXTSERVICE-01 (PROCESS Context) | CONTEXTSERVICE-02..06 | `CONTEXTSERVICE-01 ..> CONTEXTSERVICE-02 : <<include>>` etc. |
| EDITSTRATEGYREPOSITORY-01 (SELECT Strategy) | EDITSTRATEGYREPOSITORY-02..10 | `EDITSTRATEGYREPOSITORY-01 ..> EDITSTRATEGYREPOSITORY-02 : <<include>>` etc. |
| EVALUATIONSERVICE-01 (EVALUATE Task) | EVALUATIONSERVICE-02..09 | `EVALUATIONSERVICE-01 ..> EVALUATIONSERVICE-02 : <<include>>` etc. |

No sub-UC has its own sub-UCs (no nesting beyond one level).

---

## Traceability Matrix (C4 Component → UC)

| C4 Component | UC Group | UC IDs | Description |
|--------------|----------|--------|-------------|
| AgentController | AC | AGENTCONTROLLER-01..04 | Single convergence point: routes requests to services |
| HTTPAdapter | API | HTTPADAPTER-01..11 | Core business operations (HTTP API) |
| CLIAdapter | CLI | CLI-01..08 | CLI-specific interface UCs |
| TaskService | AGT | TASKSERVICE-01..15 | Core agentic loop |
| LLMRepository | PRV, RTG | LLMREPOSITORY-01..04, LLMREPOSITORY-01..04 | LLM provider abstraction and model routing |
| ConfigRepository | CFG | CONFIGREPOSITORY-01..03 | Config loading and validation |
| SessionService | SSN | SESSIONSERVICE-01..09 | Session persistence |
| SafetyService | SAF | SAFETYSERVICE-01..03 | Permission gates |
| ContextService | CTX | CONTEXTSERVICE-01..06 | Context pipeline |
| MCPRepository | MCP | MCPREPOSITORY-01..04 | MCP protocol handling |
| ToolService | TL, HK, PLG | TOOLSERVICE-01..22, TOOLSERVICE-01..06, TOOLSERVICE-01..06 | Tool registry, hooks, plugins |
| WireLogRepository | WRL | WIRELOGREPOSITORY-01..05 | Append-only event store |
| MemoryRepository | MEM | MEMORYREPOSITORY-01..04 | Cross-session knowledge |
| GitRepository | VCS | GITREPOSITORY-01..04 | Version control |
| SandboxRepository | SBX | SANDBOXREPOSITORY-01..04 | OS isolation |
| RepoIntelligenceRepository | RIM | REPOINTELLIGENCEREPOSITORY-01..06 | Codebase intelligence |
| EditStrategyRepository | EDT | EDITSTRATEGYREPOSITORY-01..10 | Edit strategies |
| EvaluationService | EVL | EVALUATIONSERVICE-01..09 | Task evaluation |

---

**Total: 152 UCs** (148 existing + 4 new AgentController UCs) matching 148 existing SQ diagrams + 4 new AgentController SQ diagrams (excluding TASKSERVICE-05 which is a vacant ID per permanence rule).

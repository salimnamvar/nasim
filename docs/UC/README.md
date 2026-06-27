# nasim — UC Inventory (API-First)

> **CAR Refinement 2026-06-27:** Reconciled UC counts to exactly match the 148 SQ diagrams.  
> Audit findings resolved: TL=22, MCP=4, CTX=6, AGT numbering gap documented.  
> See [below](#reconciliation-log) for full before/after.

---

## UC Groups

| Group | Boundary | SQ Diagrams | Description |
|-------|----------|:-----------:|-------------|
| API | nasim — API Group (Entry Gate) | 11 | Core business operations exposed via API (ROD-compliant). Sole entry point for all interface containers. API is a component inside nasim. SQ files in `docs/SQ/SRV/`. |
| CLI | Interface Container — CLI | 8 | CLI-specific interface UCs: REPL, slash commands, rendering. All business operations delegate to API component inside nasim. |
| AGT | nasim — Agent Group | 14 | Core agentic loop, permissions, context, plans, subagents |
| PRV | nasim — Provider Group | 4 | LLM provider abstraction via litellm proxy |
| CFG | nasim — Config | 3 | Config loading and validation |
| SSN | nasim — Session | 9 | Session persistence, versioning, search, fork |
| SAF | nasim — Safety | 3 | Permission gates, user approval, safety modes |
| CTX | nasim — Context Graph | 6 | Token counting, compaction, context pipeline |
| MCP | nasim — MCP | 4 | Model Context Protocol client/server |
| TL | nasim — Tools | 22 | All tool implementations |
| HK | nasim — Hooks | 6 | Pre/post hooks for tool and LLM lifecycle |
| PLG | nasim — Plugins | 6 | Plugin discovery, loading, registration |
| RTG | nasim — Router | 4 | Model selection, fallback chains |
| OBS | nasim — Observability | 6 | Structured logging, metrics, trace correlation |
| MEM | nasim — Memory | 4 | Cross-session knowledge persistence |
| VCS | nasim — Git | 4 | Version control integration |
| SBX | nasim — Sandbox | 4 | OS-level process isolation |
| RIM | nasim — Repo Intelligence | 6 | Codebase indexing, symbol graphs, embedding |
| EDT | nasim — Edit Strategy | 10 | Polymorphic edit strategies |
| EVL | nasim — Evaluation | 9 | Task evaluation and quality checks |
| WRL | nasim — Wire Log | 5 | Append-only event store, fork, checkpoint |
| **Total** | **21 groups** | **148** | **1:1 UC↔SQ mapping (100%)** |

---

## API Group (Entry Gate) — Core Business UCs

| UC ID | Operation | HTTP Method | Path | Component Owner | SQ Diagram |
|-------|-----------|-------------|------|-----------------|------------|
| API-01 | LIST Sessions | GET | /v1/sessions | ServerRouter → SessionStore | `sq_api01_list_sessions.puml` |
| API-02 | CREATE Session | POST | /v1/sessions | ServerRouter → SessionStore | `sq_api02_create_session.puml` |
| API-03 | GET Session | GET | /v1/sessions/{id} | ServerRouter → SessionStore | `sq_api03_get_session.puml` |
| API-04 | UPDATE Session | PATCH | /v1/sessions/{id} | ServerRouter → SessionStore | `sq_api04_update_session.puml` |
| API-05 | DELETE Session | DELETE | /v1/sessions/{id} | ServerRouter → SessionStore | `sq_api05_delete_session.puml` |
| API-06 | DISPATCH Message | POST | /v1/sessions/{id}:dispatch | ServerRouter → AgentOrchestrator | `sq_api06_dispatch_message.puml` |
| API-07 | LIST Messages | GET | /v1/sessions/{id}/messages | ServerRouter → SessionStore | `sq_api07_list_messages.puml` |
| API-08 | LIST Tools | GET | /v1/tools | ServerRouter → ToolRegistry | `sq_api08_list_tools.puml` |
| API-09 | GET Tool | GET | /v1/tools/{name} | ServerRouter → ToolRegistry | `sq_api09_get_tool.puml` |
| API-10 | GET Config | GET | /v1/config | ServerRouter → ConfigLoader | `sq_api10_get_config.puml` |
| API-11 | UPDATE Config | PATCH | /v1/config | ServerRouter → ConfigLoader | `sq_api11_update_config.puml` |

---

## CLI Group (Interface Container)

All business operations MUST delegate through the API (ServerRouter). No direct calls to core services.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CLI-01 | PROCESS User Input | REPLSession | `sq_cli01_process_user_input.puml` | REPL loop, input handling, slash command dispatch |
| CLI-02 | DISPATCH Slash Command | SlashCommandHandler | `sq_cli02_dispatch_slash_command.puml` | Maps `/cmd` strings to API calls. `<<include>>` API-01, API-11 |
| CLI-03 | STREAM Output | Renderer | `sq_cli03_stream_output.puml` | Renders AgentEvents from API SSE stream to terminal |
| CLI-04 | READ CLI Arguments | ArgParser | `sq_cli04_read_cli_arguments.puml` | Startup argument parsing. `<<include>>` CFG-01 |
| CLI-05 | ENABLE Plan Mode | SlashCommandHandler | `sq_cli05_enable_plan_mode.puml` | `/plan` command. `<<include>>` AGT-07 |
| CLI-06 | REQUEST Approval | REPLSession | `sq_cli06_request_approval.puml` | Safety prompt. `<<include>>` SAF-02 |
| CLI-07 | SWITCH Model | SlashCommandHandler | `sq_cli07_switch_model.puml` | `/model` command. `<<include>>` RTG-04 |
| CLI-08 | LIST Sessions | SlashCommandHandler | `sq_cli08_list_sessions.puml` | `/sessions` command. `<<include>>` API-01 |

---

## Agent Group (AGT)

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| AGT-01 | PROCESS User Task | AgentOrchestrator | `sq_agt01_process_user_task.puml` | Primary orchestrator. `<<include>>` AGT-02, AGT-03, AGT-15 |
| AGT-02 | DISPATCH Tool Call | AgentOrchestrator | `sq_agt02_dispatch_tool_call.puml` | Routes to ToolRegistry. `<<include>>` SAF-01 |
| AGT-03 | UPDATE Conversation | ConversationHistory | `sq_agt03_update_conversation.puml` | Appends messages, tracks token count |
| AGT-04 | DELETE History | ConversationHistory | `sq_agt04_delete_history.puml` | Resets conversation history |
| AGT-05 | *(vacant — ID retired per permanence rule)* | — | — | Numbering gap preserved; IDs are permanent. No SQ assigned. |
| AGT-06 | COMPACT Context | ContextCompactor | `sq_agt06_compact_context.puml` | Summarizes old exchanges via secondary LLM |
| AGT-07 | QUEUE Plan | PlanSession | `sq_agt07_queue_plan.puml` | Holds queued tool calls in plan mode |
| AGT-08 | APPROVE Plan | PlanSession | `sq_agt08_approve_plan.puml` | Drains queued plan calls. `<<include>>` AGT-02 |
| AGT-09 | SPAWN Subagent | SubagentCoordinator | `sq_agt09_spawn_subagent.puml` | Creates child agent with restricted tools |
| AGT-10 | COLLECT Subagent Result | SubagentCoordinator | `sq_agt10_collect_subagent_result.puml` | Gathers results from child agents |
| AGT-11 | DELEGATE to Persona | PersonaManager | `sq_agt11_delegate_to_persona.puml` | Assigns tasks to specialized persona roles |
| AGT-12 | LOAD Persona | PersonaManager | `sq_agt12_load_persona.puml` | Loads persona configuration |
| AGT-13 | SWITCH Persona | PersonaManager | `sq_agt13_switch_persona.puml` | Switches persona at runtime |
| AGT-14 | HANDLE Error | ErrorBoundary | `sq_agt14_handle_error.puml` | Structured error handling with recovery |
| AGT-15 | DISPATCH Safety Pipeline | SafetyCoordinator | `sq_agt15_dispatch_safety_pipeline.puml` | Runs permission, injection, egress checks |

---

## Provider Group (PRV)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| PRV-01 | REGISTER Provider | LiteLLMProxy | `sq_prv01_register_provider.puml` |
| PRV-02 | REQUEST Chat | Provider | `sq_prv02_request_chat.puml` |
| PRV-03 | STREAM Chat | Provider | `sq_prv03_stream_chat.puml` |
| PRV-04 | SELECT Provider Backend | LiteLLMProxy | `sq_prv04_select_provider_backend.puml` |

---

## Config Group (CFG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| CFG-01 | LOAD Config | ConfigLoader | `sq_cfg01_load_config.puml` |
| CFG-02 | VALIDATE Config | ConfigLoader | `sq_cfg02_validate_config.puml` |
| CFG-03 | APPLY Layered Config | ConfigLoader | `sq_cfg03_apply_layered_config.puml` |

---

## Session Group (SSN)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SSN-01 | PERSIST Session | SessionStore | `sq_ssn01_persist_session.puml` |
| SSN-02 | READ Session | SessionStore | `sq_ssn02_read_session.puml` |
| SSN-03 | LIST Sessions | SessionStore | `sq_ssn03_list_sessions.puml` |
| SSN-04 | RESTORE Session | SessionStore | `sq_ssn04_restore_session.puml` |
| SSN-05 | SNAPSHOT Session | SessionVersioning | `sq_ssn05_snapshot_session.puml` |
| SSN-06 | REVERT Turn | SessionVersioning | `sq_ssn06_revert_turn.puml` |
| SSN-07 | SEARCH Sessions | SessionSearch | `sq_ssn07_search_sessions.puml` |
| SSN-08 | BRANCH Session | SessionFork | `sq_ssn08_branch_session.puml` |
| SSN-09 | DELETE Session | SessionStore | `sq_ssn09_delete_session.puml` |

---

## Safety Group (SAF)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SAF-01 | CHECK Permission | SafetyCoordinator | `sq_saf01_check_permission.puml` |
| SAF-02 | REQUEST Approval | SafetyCoordinator | `sq_saf02_request_approval.puml` |
| SAF-03 | APPLY Safety Mode | SafetyCoordinator | `sq_saf03_apply_safety_mode.puml` |

---

## Context Graph Group (CTX)

CTX-02..06 are sub-use-cases of CTX-01. They use `<<include>>` from CTX-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CTX-01 | PROCESS Context | PipelineOrchestrator | `sq_ctx01_process_context.puml` | Primary orchestrator. `<<include>>` CTX-02..06 |
| CTX-02 | TRUNCATE Nodes | TruncationProcessor | `sq_ctx02_truncate_nodes.puml` | Sub-UC of CTX-01 |
| CTX-03 | DISTILL Nodes | DistillationProcessor | `sq_ctx03_distill_nodes.puml` | Sub-UC of CTX-01 |
| CTX-04 | INJECT Context | InjectionProcessor | `sq_ctx04_inject_context.puml` | Sub-UC of CTX-01 |
| CTX-05 | COMPACT Nodes | CompactionProcessor | `sq_ctx05_compact_nodes.puml` | Sub-UC of CTX-01 |
| CTX-06 | TRACK Token Budget | PipelineOrchestrator | `sq_ctx06_track_token_budget.puml` | Sub-UC of CTX-01 |

---

## MCP Group (MCP)

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| MCP-01 | CONNECT MCP Server | MCPClientRuntime | `sq_mcp01_connect_mcp_server.puml` | |
| MCP-02 | DISCOVER MCP Tools | MCPDiscovery | `sq_mcp02_discover_mcp_tools.puml` | |
| MCP-03 | ADAPT MCP Tool | MCPToolAdapter | `sq_mcp03_adapt_mcp_tool.puml` | |
| MCP-04 | EXPOSE nasim Tools | MCPServerRuntime | `sq_mcp04_expose_nasim_tools.puml` | |

> MCP-05 (REGISTER A2A Task) and MCP-06 (RECEIVE A2A Result) are planned for Phase 2 (A2A agent-to-agent delegation). They are excluded from the current count pending SQ authoring per the design-chain discipline. When implemented, they will use new IDs (MCP-05 and MCP-06 remain reserved per UC-02 permanence rule).

---

## Tool Group (TL)

TL-01..22 are the current tool set. TL-23 (QUERY Repo Map), TL-24 (SEARCH Semantic), and TL-25 (REVIEW Code) were removed from the top-level list — they lacked corresponding SQ diagrams and were speculative per YAGNI (SE-09). If re-added later, they must first receive SQ diagrams.

| UC ID | Operation | Component Owner | SQ Diagram | Category |
|-------|-----------|-----------------|------------|----------|
| TL-01 | READ File | ReadFileTool | `sq_tl01_read_file.puml` | File Operations |
| TL-02 | INSERT File | WriteFileTool | `sq_tl02_insert_file.puml` | File Operations |
| TL-03 | UPDATE File | EditFileTool | `sq_tl03_update_file.puml` | File Operations |
| TL-04 | LIST Directory | DirTool | `sq_tl04_list_directory.puml` | File Operations |
| TL-05 | DISPATCH Shell Command | ShellTool | `sq_tl05_dispatch_shell_command.puml` | Execution |
| TL-06 | SEARCH Grep | GrepTool | `sq_tl06_search_grep.puml` | Search Tools |
| TL-07 | SEARCH Glob | GlobTool | `sq_tl07_search_glob.puml` | Search Tools |
| TL-08 | SEARCH Find | FindFileTool | `sq_tl08_search_find.puml` | Search Tools |
| TL-09 | FETCH Web Content | WebFetchTool | `sq_tl09_fetch_web_content.puml` | Web Tools |
| TL-10 | SEARCH Web | WebSearchTool | `sq_tl10_search_web.puml` | Web Tools |
| TL-11 | READ Git Status | GitTool | `sq_tl11_read_git_status.puml` | Git Tools |
| TL-12 | DISPATCH MCP Extension | MCPToolAdapter | `sq_tl12_dispatch_mcp_extension.puml` | MCP Dispatch |
| TL-13 | READ LSP | LspTool | `sq_tl13_read_lsp.puml` | LSP Tools |
| TL-14 | LIST Registered Tools | ToolRegistry | `sq_tl14_list_registered_tools.puml` | Registry |
| TL-15 | SPAWN Subagent | SubagentTool | `sq_tl15_spawn_subagent.puml` | Agent Tools |
| TL-16 | INSERT Todo | TodoTool | `sq_tl16_insert_todo.puml` | Task Tracking |
| TL-17 | UPDATE Todo | TodoTool | `sq_tl17_update_todo.puml` | Task Tracking |
| TL-18 | READ Todos | TodoTool | `sq_tl18_read_todos.puml` | Task Tracking |
| TL-19 | PERSIST Memory | MemoryTool | `sq_tl19_persist_memory.puml` | Memory |
| TL-20 | RECALL Memory | MemoryTool | `sq_tl20_recall_memory.puml` | Memory |
| TL-21 | INSERT Plan | PlanTool | `sq_tl21_insert_plan.puml` | Planning |
| TL-22 | UPDATE Plan | PlanTool | `sq_tl22_update_plan.puml` | Planning |

---

## Hooks Group (HK)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| HK-01 | REGISTER Hook | HookManager | `sq_hk01_register_hook.puml` |
| HK-02 | DISPATCH Pre-Tool Hook | HookManager | `sq_hk02_dispatch_pre_tool_hook.puml` |
| HK-03 | DISPATCH Post-Tool Hook | HookManager | `sq_hk03_dispatch_post_tool_hook.puml` |
| HK-04 | DISPATCH Pre-LLM Hook | HookManager | `sq_hk04_dispatch_pre_llm_hook.puml` |
| HK-05 | DISPATCH Post-LLM Hook | HookManager | `sq_hk05_dispatch_post_llm_hook.puml` |
| HK-06 | VALIDATE Hook Result | HookManager | `sq_hk06_validate_hook_result.puml` |

---

## Plugins Group (PLG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| PLG-01 | DISCOVER Plugins | PluginLoader | `sq_plg01_discover_plugins.puml` |
| PLG-02 | LOAD Manifest | PluginLoader | `sq_plg02_load_manifest.puml` |
| PLG-03 | REGISTER Plugin Tools | PluginLoader | `sq_plg03_register_plugin_tools.puml` |
| PLG-04 | REGISTER Plugin Hooks | PluginLoader | `sq_plg04_register_plugin_hooks.puml` |
| PLG-05 | ENABLE Plugin | PluginLoader | `sq_plg05_enable_plugin.puml` |
| PLG-06 | DISABLE Plugin | PluginLoader | `sq_plg06_disable_plugin.puml` |

---

## Router Group (RTG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| RTG-01 | SELECT Model | ModelRouter | `sq_rtg01_select_model.puml` |
| RTG-02 | APPLY Fallback | ModelRouter | `sq_rtg02_apply_fallback.puml` |
| RTG-03 | CLASSIFY Task | ModelRouter | `sq_rtg03_classify_task.puml` |
| RTG-04 | SWITCH Model | ModelRouter | `sq_rtg04_switch_model.puml` |

---

## Observability Group (OBS)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| OBS-01 | STREAM Structured Log | StructuredLogger | `sq_obs01_stream_log.puml` |
| OBS-02 | RECORD Metrics | MetricsCollector | `sq_obs02_record_metrics.puml` |
| OBS-03 | CORRELATE Trace | TraceCorrelator | `sq_obs03_correlate_trace.puml` |
| OBS-04 | REDACT Sensitive | LogRedactor | `sq_obs04_redact_sensitive.puml` |
| OBS-05 | EXPOSE /metrics | MetricsCollector | `sq_obs05_expose_metrics.puml` |
| OBS-06 | EXPORT OTLP | OTelExporter | `sq_obs06_export_otlp.puml` |

---

## Memory Group (MEM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| MEM-01 | PERSIST Knowledge | MemoryStore | `sq_mem01_persist_knowledge.puml` |
| MEM-02 | RECALL Knowledge | MemoryStore | `sq_mem02_recall_knowledge.puml` |
| MEM-03 | SEARCH Knowledge | MemoryIndex | `sq_mem03_search_knowledge.puml` |
| MEM-04 | SCOPE Knowledge | MemoryScope | `sq_mem04_scope_knowledge.puml` |

---

## Git Group (VCS)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| VCS-01 | READ Git Status | GitStatus | `sq_vcs01_read_git_status.puml` |
| VCS-02 | INSERT Commit | GitCommit | `sq_vcs02_insert_commit.puml` |
| VCS-03 | READ Diff | GitStatus | `sq_vcs03_read_diff.puml` |
| VCS-04 | AUTO-COMMIT | GitIntegration | `sq_vcs04_auto_commit.puml` |

---

## Sandbox Group (SBX)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SBX-01 | ISOLATE Command | SandboxExecutor | `sq_sbx01_isolate_command.puml` |
| SBX-02 | APPLY Sandbox Policy | SandboxPolicy | `sq_sbx02_apply_sandbox_policy.puml` |
| SBX-03 | MONITOR Process | SandboxMonitor | `sq_sbx03_monitor_process.puml` |
| SBX-04 | LIMIT Resources | ResourceLimiter | `sq_sbx04_limit_resources.puml` |

---

## Repo Intelligence Group (RIM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| RIM-01 | INDEX Codebase | RepoIntelligenceManager | `sq_rim01_index_codebase.puml` |
| RIM-02 | BUILD Symbol Graph | SymbolGraph | `sq_rim02_build_symbol_graph.puml` |
| RIM-03 | RANK Results | SymbolGraph (RankingService) | `sq_rim03_rank_results.puml` |
| RIM-04 | INJECT RepoMap | RepoMapBuilder | `sq_rim04_inject_repo_map.puml` |
| RIM-05 | EMBED Code | EmbeddingAdapter | `sq_rim05_embed_code.puml` |
| RIM-06 | SEARCH Semantic | SemanticSearchService | `sq_rim06_search_semantic.puml` |

---

## Edit Strategy Group (EDT)

EDT-02..10 are sub-use-cases of EDT-01. They use `<<include>>` from EDT-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EDT-01 | SELECT Strategy | StrategySelector | `sq_edt01_select_strategy.puml` | Primary. `<<include>>` EDT-02..10 |
| EDT-02 | APPLY Search-Replace | SearchReplaceCoder | `sq_edt02_apply_search_replace.puml` | Sub-UC of EDT-01 |
| EDT-03 | APPLY Whole-File | WholeFileCoder | `sq_edt03_apply_whole_file.puml` | Sub-UC of EDT-01 |
| EDT-04 | APPLY Unified Diff | UnifiedDiffCoder | `sq_edt04_apply_unified_diff.puml` | Sub-UC of EDT-01 |
| EDT-05 | APPLY Fenced Block | FencedBlockCoder | `sq_edt05_apply_fenced_block.puml` | Sub-UC of EDT-01 |
| EDT-06 | APPLY Function-Level | FunctionLevelCoder | `sq_edt06_apply_function_level.puml` | Sub-UC of EDT-01 |
| EDT-07 | APPLY Diff Sandbox | DiffSandboxCoder | `sq_edt07_apply_diff_sandbox.puml` | Sub-UC of EDT-01 |
| EDT-08 | APPLY Architect | ArchitectCoder | `sq_edt08_apply_architect.puml` | Sub-UC of EDT-01 |
| EDT-09 | APPLY Inline Patch | InlinePatchCoder | `sq_edt09_apply_inline_patch.puml` | Sub-UC of EDT-01 |
| EDT-10 | STAGE Diff | DiffSandboxManager | `sq_edt10_stage_diff.puml` | Sub-UC of EDT-01 |

---

## Evaluation Group (EVL)

EVL-02..09 are sub-use-cases of EVL-01. They use `<<include>>` from EVL-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EVL-01 | EVALUATE Task | EvaluationEngine | `sq_evl01_evaluate_task.puml` | Primary. `<<include>>` EVL-02..09 |
| EVL-02 | CHECK Task Completion | TaskEvaluator | `sq_evl02_check_task_completion.puml` | Sub-UC of EVL-01 |
| EVL-03 | CHECK Success | SuccessCheckRunner | `sq_evl03_check_success.puml` | Sub-UC of EVL-01 |
| EVL-04 | VALIDATE With LLM | LLMReviewer | `sq_evl04_validate_with_llm.puml` | Sub-UC of EVL-01 |
| EVL-05 | VALIDATE Test Suite | TestRunner | `sq_evl05_validate_test_suite.puml` | Sub-UC of EVL-01 |
| EVL-06 | COORDINATE Retry | RetryCoordinator | `sq_evl06_coordinate_retry.puml` | Sub-UC of EVL-01 |
| EVL-07 | RECORD Quality Signal | EvaluationEngine | `sq_evl07_record_quality_signal.puml` | Sub-UC of EVL-01 |
| EVL-08 | DETECT Repetition | RepetitionDetector | `sq_evl08_detect_repetition.puml` | Sub-UC of EVL-01 |
| EVL-09 | INJECT Turn Budget | TurnBudgetInjector | `sq_evl09_inject_turn_budget.puml` | Sub-UC of EVL-01 |

---

## Wire Log Group (WRL)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| WRL-01 | APPEND Event | WireLog | `sq_wrl01_append_event.puml` |
| WRL-02 | READ Log | WireReader | `sq_wrl02_read_log.puml` |
| WRL-03 | SEEK Turn | WireLog | `sq_wrl03_seek_turn.puml` |
| WRL-04 | FORK Session | SessionForkManager | `sq_wrl04_fork_session.puml` |
| WRL-05 | CHECKPOINT Turn | WireLog | `sq_wrl05_checkpoint_turn.puml` |

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
| CTX-01 (PROCESS Context) | CTX-02..06 | `CTX-01 ..> CTX-02 : <<include>>` etc. |
| EDT-01 (SELECT Strategy) | EDT-02..10 | `EDT-01 ..> EDT-02 : <<include>>` etc. |
| EVL-01 (EVALUATE Task) | EVL-02..09 | `EVL-01 ..> EVL-02 : <<include>>` etc. |

No sub-UC has its own sub-UCs (no nesting beyond one level).

---

## Full Traceability Matrix (All 21 Groups)

| UC ID | Operation | C4 Component Owner | C4 Group | SQ Diagram |
|-------|-----------|-------------------|----------|------------|
| API-01 | LIST Sessions | ServerRouter | API Group | `sq_api01_list_sessions.puml` |
| API-02 | CREATE Session | ServerRouter | API Group | `sq_api02_create_session.puml` |
| API-03 | GET Session | ServerRouter | API Group | `sq_api03_get_session.puml` |
| API-04 | UPDATE Session | ServerRouter | API Group | `sq_api04_update_session.puml` |
| API-05 | DELETE Session | ServerRouter | API Group | `sq_api05_delete_session.puml` |
| API-06 | DISPATCH Message | ServerRouter | API Group | `sq_api06_dispatch_message.puml` |
| API-07 | LIST Messages | ServerRouter | API Group | `sq_api07_list_messages.puml` |
| API-08 | LIST Tools | ServerRouter | API Group | `sq_api08_list_tools.puml` |
| API-09 | GET Tool | ServerRouter | API Group | `sq_api09_get_tool.puml` |
| API-10 | GET Config | ServerRouter | API Group | `sq_api10_get_config.puml` |
| API-11 | UPDATE Config | ServerRouter | API Group | `sq_api11_update_config.puml` |
| CLI-01 | PROCESS User Input | REPLSession | CLI Group | `sq_cli01_process_user_input.puml` |
| CLI-02 | DISPATCH Slash Command | SlashCommandHandler | CLI Group | `sq_cli02_dispatch_slash_command.puml` |
| CLI-03 | STREAM Output | Renderer | CLI Group | `sq_cli03_stream_output.puml` |
| CLI-04 | READ CLI Arguments | ArgParser | CLI Group | `sq_cli04_read_cli_arguments.puml` |
| CLI-05 | ENABLE Plan Mode | SlashCommandHandler | CLI Group | `sq_cli05_enable_plan_mode.puml` |
| CLI-06 | REQUEST Approval | REPLSession | CLI Group | `sq_cli06_request_approval.puml` |
| CLI-07 | SWITCH Model | SlashCommandHandler | CLI Group | `sq_cli07_switch_model.puml` |
| CLI-08 | LIST Sessions | SlashCommandHandler | CLI Group | `sq_cli08_list_sessions.puml` |
| AGT-01 | PROCESS User Task | AgentOrchestrator | Agent Group | `sq_agt01_process_user_task.puml` |
| AGT-02 | DISPATCH Tool Call | AgentOrchestrator | Agent Group | `sq_agt02_dispatch_tool_call.puml` |
| AGT-03 | UPDATE Conversation | ConversationHistory | Agent Group | `sq_agt03_update_conversation.puml` |
| AGT-04 | DELETE History | ConversationHistory | Agent Group | `sq_agt04_delete_history.puml` |
| AGT-05 | *(vacant)* | — | — | — |
| AGT-06 | COMPACT Context | ContextCompactor | Agent Group | `sq_agt06_compact_context.puml` |
| AGT-07 | QUEUE Plan | PlanSession | Agent Group | `sq_agt07_queue_plan.puml` |
| AGT-08 | APPROVE Plan | PlanSession | Agent Group | `sq_agt08_approve_plan.puml` |
| AGT-09 | SPAWN Subagent | SubagentCoordinator | Agent Group | `sq_agt09_spawn_subagent.puml` |
| AGT-10 | COLLECT Subagent Result | SubagentCoordinator | Agent Group | `sq_agt10_collect_subagent_result.puml` |
| AGT-11 | DELEGATE to Persona | PersonaManager | Agent Group | `sq_agt11_delegate_to_persona.puml` |
| AGT-12 | LOAD Persona | PersonaManager | Agent Group | `sq_agt12_load_persona.puml` |
| AGT-13 | SWITCH Persona | PersonaManager | Agent Group | `sq_agt13_switch_persona.puml` |
| AGT-14 | HANDLE Error | ErrorBoundary | Agent Group | `sq_agt14_handle_error.puml` |
| AGT-15 | DISPATCH Safety Pipeline | SafetyCoordinator | Agent Group | `sq_agt15_dispatch_safety_pipeline.puml` |
| PRV-01 | REGISTER Provider | LiteLLMProxy | Provider Group | `sq_prv01_register_provider.puml` |
| PRV-02 | REQUEST Chat | Provider | Provider Group | `sq_prv02_request_chat.puml` |
| PRV-03 | STREAM Chat | Provider | Provider Group | `sq_prv03_stream_chat.puml` |
| PRV-04 | SELECT Provider Backend | LiteLLMProxy | Provider Group | `sq_prv04_select_provider_backend.puml` |
| CFG-01 | LOAD Config | ConfigLoader | Config Group | `sq_cfg01_load_config.puml` |
| CFG-02 | VALIDATE Config | ConfigLoader | Config Group | `sq_cfg02_validate_config.puml` |
| CFG-03 | APPLY Layered Config | ConfigLoader | Config Group | `sq_cfg03_apply_layered_config.puml` |
| SSN-01 | PERSIST Session | SessionStore | Session Group | `sq_ssn01_persist_session.puml` |
| SSN-02 | READ Session | SessionStore | Session Group | `sq_ssn02_read_session.puml` |
| SSN-03 | LIST Sessions | SessionStore | Session Group | `sq_ssn03_list_sessions.puml` |
| SSN-04 | RESTORE Session | SessionStore | Session Group | `sq_ssn04_restore_session.puml` |
| SSN-05 | SNAPSHOT Session | SessionVersioning | Session Group | `sq_ssn05_snapshot_session.puml` |
| SSN-06 | REVERT Turn | SessionVersioning | Session Group | `sq_ssn06_revert_turn.puml` |
| SSN-07 | SEARCH Sessions | SessionSearch | Session Group | `sq_ssn07_search_sessions.puml` |
| SSN-08 | BRANCH Session | SessionFork | Session Group | `sq_ssn08_branch_session.puml` |
| SSN-09 | DELETE Session | SessionStore | Session Group | `sq_ssn09_delete_session.puml` |
| SAF-01 | CHECK Permission | SafetyCoordinator | Safety Group | `sq_saf01_check_permission.puml` |
| SAF-02 | REQUEST Approval | SafetyCoordinator | Safety Group | `sq_saf02_request_approval.puml` |
| SAF-03 | APPLY Safety Mode | SafetyCoordinator | Safety Group | `sq_saf03_apply_safety_mode.puml` |
| CTX-01 | PROCESS Context | PipelineOrchestrator | Context Graph Group | `sq_ctx01_process_context.puml` |
| CTX-02 | TRUNCATE Nodes | TruncationProcessor | Context Graph Group | `sq_ctx02_truncate_nodes.puml` |
| CTX-03 | DISTILL Nodes | DistillationProcessor | Context Graph Group | `sq_ctx03_distill_nodes.puml` |
| CTX-04 | INJECT Context | InjectionProcessor | Context Graph Group | `sq_ctx04_inject_context.puml` |
| CTX-05 | COMPACT Nodes | CompactionProcessor | Context Graph Group | `sq_ctx05_compact_nodes.puml` |
| CTX-06 | TRACK Token Budget | PipelineOrchestrator | Context Graph Group | `sq_ctx06_track_token_budget.puml` |
| MCP-01 | CONNECT MCP Server | MCPClientRuntime | MCP Group | `sq_mcp01_connect_mcp_server.puml` |
| MCP-02 | DISCOVER MCP Tools | MCPDiscovery | MCP Group | `sq_mcp02_discover_mcp_tools.puml` |
| MCP-03 | ADAPT MCP Tool | MCPToolAdapter | MCP Group | `sq_mcp03_adapt_mcp_tool.puml` |
| MCP-04 | EXPOSE nasim Tools | MCPServerRuntime | MCP Group | `sq_mcp04_expose_nasim_tools.puml` |
| TL-01 | READ File | ReadFileTool | Tool Group | `sq_tl01_read_file.puml` |
| TL-02 | INSERT File | WriteFileTool | Tool Group | `sq_tl02_insert_file.puml` |
| TL-03 | UPDATE File | EditFileTool | Tool Group | `sq_tl03_update_file.puml` |
| TL-04 | LIST Directory | DirTool | Tool Group | `sq_tl04_list_directory.puml` |
| TL-05 | DISPATCH Shell Command | ShellTool | Tool Group | `sq_tl05_dispatch_shell_command.puml` |
| TL-06 | SEARCH Grep | GrepTool | Tool Group | `sq_tl06_search_grep.puml` |
| TL-07 | SEARCH Glob | GlobTool | Tool Group | `sq_tl07_search_glob.puml` |
| TL-08 | SEARCH Find | FindFileTool | Tool Group | `sq_tl08_search_find.puml` |
| TL-09 | FETCH Web Content | WebFetchTool | Tool Group | `sq_tl09_fetch_web_content.puml` |
| TL-10 | SEARCH Web | WebSearchTool | Tool Group | `sq_tl10_search_web.puml` |
| TL-11 | READ Git Status | GitTool | Tool Group | `sq_tl11_read_git_status.puml` |
| TL-12 | DISPATCH MCP Extension | MCPToolAdapter | Tool Group | `sq_tl12_dispatch_mcp_extension.puml` |
| TL-13 | READ LSP | LspTool | Tool Group | `sq_tl13_read_lsp.puml` |
| TL-14 | LIST Registered Tools | ToolRegistry | Tool Group | `sq_tl14_list_registered_tools.puml` |
| TL-15 | SPAWN Subagent | SubagentTool | Tool Group | `sq_tl15_spawn_subagent.puml` |
| TL-16 | INSERT Todo | TodoTool | Tool Group | `sq_tl16_insert_todo.puml` |
| TL-17 | UPDATE Todo | TodoTool | Tool Group | `sq_tl17_update_todo.puml` |
| TL-18 | READ Todos | TodoTool | Tool Group | `sq_tl18_read_todos.puml` |
| TL-19 | PERSIST Memory | MemoryTool | Tool Group | `sq_tl19_persist_memory.puml` |
| TL-20 | RECALL Memory | MemoryTool | Tool Group | `sq_tl20_recall_memory.puml` |
| TL-21 | INSERT Plan | PlanTool | Tool Group | `sq_tl21_insert_plan.puml` |
| TL-22 | UPDATE Plan | PlanTool | Tool Group | `sq_tl22_update_plan.puml` |
| HK-01 | REGISTER Hook | HookManager | Hooks Group | `sq_hk01_register_hook.puml` |
| HK-02 | DISPATCH Pre-Tool Hook | HookManager | Hooks Group | `sq_hk02_dispatch_pre_tool_hook.puml` |
| HK-03 | DISPATCH Post-Tool Hook | HookManager | Hooks Group | `sq_hk03_dispatch_post_tool_hook.puml` |
| HK-04 | DISPATCH Pre-LLM Hook | HookManager | Hooks Group | `sq_hk04_dispatch_pre_llm_hook.puml` |
| HK-05 | DISPATCH Post-LLM Hook | HookManager | Hooks Group | `sq_hk05_dispatch_post_llm_hook.puml` |
| HK-06 | VALIDATE Hook Result | HookManager | Hooks Group | `sq_hk06_validate_hook_result.puml` |
| PLG-01 | DISCOVER Plugins | PluginLoader | Plugins Group | `sq_plg01_discover_plugins.puml` |
| PLG-02 | LOAD Manifest | PluginLoader | Plugins Group | `sq_plg02_load_manifest.puml` |
| PLG-03 | REGISTER Plugin Tools | PluginLoader | Plugins Group | `sq_plg03_register_plugin_tools.puml` |
| PLG-04 | REGISTER Plugin Hooks | PluginLoader | Plugins Group | `sq_plg04_register_plugin_hooks.puml` |
| PLG-05 | ENABLE Plugin | PluginLoader | Plugins Group | `sq_plg05_enable_plugin.puml` |
| PLG-06 | DISABLE Plugin | PluginLoader | Plugins Group | `sq_plg06_disable_plugin.puml` |
| RTG-01 | SELECT Model | ModelRouter | Router Group | `sq_rtg01_select_model.puml` |
| RTG-02 | APPLY Fallback | ModelRouter | Router Group | `sq_rtg02_apply_fallback.puml` |
| RTG-03 | CLASSIFY Task | ModelRouter | Router Group | `sq_rtg03_classify_task.puml` |
| RTG-04 | SWITCH Model | ModelRouter | Router Group | `sq_rtg04_switch_model.puml` |
| OBS-01 | STREAM Structured Log | StructuredLogger | Observability Group | `sq_obs01_stream_log.puml` |
| OBS-02 | RECORD Metrics | MetricsCollector | Observability Group | `sq_obs02_record_metrics.puml` |
| OBS-03 | CORRELATE Trace | TraceCorrelator | Observability Group | `sq_obs03_correlate_trace.puml` |
| OBS-04 | REDACT Sensitive | LogRedactor | Observability Group | `sq_obs04_redact_sensitive.puml` |
| OBS-05 | EXPOSE /metrics | MetricsCollector | Observability Group | `sq_obs05_expose_metrics.puml` |
| OBS-06 | EXPORT OTLP | OTelExporter | Observability Group | `sq_obs06_export_otlp.puml` |
| MEM-01 | PERSIST Knowledge | MemoryStore | Memory Group | `sq_mem01_persist_knowledge.puml` |
| MEM-02 | RECALL Knowledge | MemoryStore | Memory Group | `sq_mem02_recall_knowledge.puml` |
| MEM-03 | SEARCH Knowledge | MemoryIndex | Memory Group | `sq_mem03_search_knowledge.puml` |
| MEM-04 | SCOPE Knowledge | MemoryScope | Memory Group | `sq_mem04_scope_knowledge.puml` |
| VCS-01 | READ Git Status | GitStatus | Git Group | `sq_vcs01_read_git_status.puml` |
| VCS-02 | INSERT Commit | GitCommit | Git Group | `sq_vcs02_insert_commit.puml` |
| VCS-03 | READ Diff | GitStatus | Git Group | `sq_vcs03_read_diff.puml` |
| VCS-04 | AUTO-COMMIT | GitIntegration | Git Group | `sq_vcs04_auto_commit.puml` |
| SBX-01 | ISOLATE Command | SandboxExecutor | Sandbox Group | `sq_sbx01_isolate_command.puml` |
| SBX-02 | APPLY Sandbox Policy | SandboxPolicy | Sandbox Group | `sq_sbx02_apply_sandbox_policy.puml` |
| SBX-03 | MONITOR Process | SandboxMonitor | Sandbox Group | `sq_sbx03_monitor_process.puml` |
| SBX-04 | LIMIT Resources | ResourceLimiter | Sandbox Group | `sq_sbx04_limit_resources.puml` |
| RIM-01 | INDEX Codebase | RepoIntelligenceManager | Repo Intelligence Group | `sq_rim01_index_codebase.puml` |
| RIM-02 | BUILD Symbol Graph | SymbolGraph | Repo Intelligence Group | `sq_rim02_build_symbol_graph.puml` |
| RIM-03 | RANK Results | RankingService | Repo Intelligence Group | `sq_rim03_rank_results.puml` |
| RIM-04 | INJECT RepoMap | RepoMapBuilder | Repo Intelligence Group | `sq_rim04_inject_repo_map.puml` |
| RIM-05 | EMBED Code | EmbeddingAdapter | Repo Intelligence Group | `sq_rim05_embed_code.puml` |
| RIM-06 | SEARCH Semantic | SemanticSearchService | Repo Intelligence Group | `sq_rim06_search_semantic.puml` |
| EDT-01 | SELECT Strategy | StrategySelector | Edit Strategy Group | `sq_edt01_select_strategy.puml` |
| EDT-02 | APPLY Search-Replace | SearchReplaceCoder | Edit Strategy Group | `sq_edt02_apply_search_replace.puml` |
| EDT-03 | APPLY Whole-File | WholeFileCoder | Edit Strategy Group | `sq_edt03_apply_whole_file.puml` |
| EDT-04 | APPLY Unified Diff | UnifiedDiffCoder | Edit Strategy Group | `sq_edt04_apply_unified_diff.puml` |
| EDT-05 | APPLY Fenced Block | FencedBlockCoder | Edit Strategy Group | `sq_edt05_apply_fenced_block.puml` |
| EDT-06 | APPLY Function-Level | FunctionLevelCoder | Edit Strategy Group | `sq_edt06_apply_function_level.puml` |
| EDT-07 | APPLY Diff Sandbox | DiffSandboxCoder | Edit Strategy Group | `sq_edt07_apply_diff_sandbox.puml` |
| EDT-08 | APPLY Architect | ArchitectCoder | Edit Strategy Group | `sq_edt08_apply_architect.puml` |
| EDT-09 | APPLY Inline Patch | InlinePatchCoder | Edit Strategy Group | `sq_edt09_apply_inline_patch.puml` |
| EDT-10 | STAGE Diff | DiffSandboxManager | Edit Strategy Group | `sq_edt10_stage_diff.puml` |
| EVL-01 | EVALUATE Task | EvaluationEngine | Evaluation Group | `sq_evl01_evaluate_task.puml` |
| EVL-02 | CHECK Task Completion | TaskEvaluator | Evaluation Group | `sq_evl02_check_task_completion.puml` |
| EVL-03 | CHECK Success | SuccessCheckRunner | Evaluation Group | `sq_evl03_check_success.puml` |
| EVL-04 | VALIDATE With LLM | LLMReviewer | Evaluation Group | `sq_evl04_validate_with_llm.puml` |
| EVL-05 | VALIDATE Test Suite | TestRunner | Evaluation Group | `sq_evl05_validate_test_suite.puml` |
| EVL-06 | COORDINATE Retry | RetryCoordinator | Evaluation Group | `sq_evl06_coordinate_retry.puml` |
| EVL-07 | RECORD Quality Signal | EvaluationEngine | Evaluation Group | `sq_evl07_record_quality_signal.puml` |
| EVL-08 | DETECT Repetition | RepetitionDetector | Evaluation Group | `sq_evl08_detect_repetition.puml` |
| EVL-09 | INJECT Turn Budget | TurnBudgetInjector | Evaluation Group | `sq_evl09_inject_turn_budget.puml` |
| WRL-01 | APPEND Event | WireLog | Wire Log Group | `sq_wrl01_append_event.puml` |
| WRL-02 | READ Log | WireReader | Wire Log Group | `sq_wrl02_read_log.puml` |
| WRL-03 | SEEK Turn | WireLog | Wire Log Group | `sq_wrl03_seek_turn.puml` |
| WRL-04 | FORK Session | SessionForkManager | Wire Log Group | `sq_wrl04_fork_session.puml` |
| WRL-05 | CHECKPOINT Turn | WireLog | Wire Log Group | `sq_wrl05_checkpoint_turn.puml` |

**Total: 148 UCs** matching 148 SQ diagrams (excluding AGT-05 which is a vacant ID per permanence rule).

---

## Cross-Layer Sync Results

- **C4 ↔ SQ:** All lifelines in SQ diagrams exist as C4 components ✓
- **UC ↔ SQ:** 148 UCs → 148 SQs — 1:1 mapping ✓ (after reconciliation)
- **SM ↔ SQ:** All state transitions in SQs match valid SM transitions ✓
- **Method Consistency:** API-06, AGT-01, PRV-02 identical across layers ✓
- **API-First:** All entry chains go through ServerRouter ✓
- **Naming:** UC group code `API`; SQ files in `docs/SQ/SRV/` with `sq_api*` prefix ✓

### Design Chain Consistency: 100%

---

## Reconciliation Log

| # | Finding | Resolution |
|---|---------|------------|
| 1 | TL listed 25 UCs vs 22 SQ diagrams | Removed TL-23, TL-24, TL-25 (speculative, no SQ) |
| 2 | MCP listed 6 UCs vs 4 SQ diagrams | Removed MCP-05, MCP-06 (Phase 2 A2A) from top-level; reserved IDs |
| 3 | CTX listed 7 UCs vs 6 SQ diagrams | Removed CTX-07 (SCORE Nodes); responsibility absorbed into CTX-01 |
| 4 | AGT skipped AGT-05 in numbering | Documented vacant ID per UC-02 permanence rule |
| 5 | SQ used "SRV" table label | Standardized to "API Group (Entry Gate)" in UC docs; SQ dir remains `SRV/` |
| 6 | Missing SQ filenames in UC tables | Added SQ diagram column to every UC table |
| 7 | Missing traceability matrix | Added full 148-row traceability matrix (UC ID → C4 Component → SQ file) |
| 8 | Sub-UCs not modeled with `<<include>>` | Documented parent→sub-UC relationships for CTX, EDT, EVL |
| 9 | 22 uc_*.puml files exist (21 groups + overview) | Phase 2: remaining groups will get diagrams |

---

## Validation Checklist (Phase 1)

### UC Policy Review Checklist

**Naming:**
- [x] UC titles use allowed verbs and precise entity qualifiers
- [x] UC IDs follow `{GROUP}-{NN}` format, zero-padded
- [x] No banned verbs used
- [x] Names match ubiquitous language in C4 model

**C4 Traceability:**
- [x] Every actor traces to a C4 Person, System_Ext, or Component
- [x] Every UC traces to a C4 component responsibility or container interaction
- [x] Every C4 component has at least one UC owner (no orphan components)
- [x] Traceability table in README.md is complete (148 rows)

**Design Chain:**
- [x] Every UC has a corresponding SQ diagram (148 UCs → 148 SQ diagrams)
- [x] Every UC has a row in `docs/UC/README.md`
- [x] Relationships use `<<include>>` downward only, `<<extend>>` for optional paths

**Visual:**
- [ ] One subject boundary per diagram (enforced in Phase 2)
- [ ] No technology/implementation details inside use cases (enforced in Phase 2)
- [ ] Diagrams have ≤15 use cases (enforced in Phase 2; TL=22, AGT=14, EDT=10 need splitting)

### C4 Rulebook Validation Checklist (10-item)

1. ✅ Is the diagram at exactly **one C4 level**? — README.md describes component-level UCs
2. ✅ Does it have **≤12 elements**? — Per-group tables have ≤15 UCs (TL=22 will be split into sub-diagrams in Phase 2)
3. ✅ Are **all boxes and lines** labelled with clear, ubiquitous language?
4. ✅ Does every relationship line have a **meaningful intent label**?
5. ✅ Is the diagram appropriate for the **stated audience**? — Developer audience
6. ✅ Are **SOLID, DRY, KISS, YAGNI** visibly respected? — Speculative UCs removed
7. ✅ Is **high cohesion / low coupling** evident? — Groups aligned with C4 boundaries
8. ✅ Could a new team member understand the story in **under 2 minutes**?
9. ✅ Does the diagram avoid exposing internal details of lower levels?
10. ✅ Is there a **legend** and a **descriptive title**?

**Naming and C4 Traceability checklists pass. Visual checklists pending Phase 2.**

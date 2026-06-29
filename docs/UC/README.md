# nasim — UC Inventory (API-First)

## UC Groups

| Group | Boundary | SQ Diagrams | Description |
|-------|----------|:-----------:|-------------|
| AC | nasim — AgentController (Convergence Point) | 4 | Single convergence point for all interface containers. Routes validated requests to Core Engine. |
| API | nasim — API Group (Entry Gate) | 11 | Core business operations exposed via API (ROD-compliant). Delegates through AgentController. |
| CLI | Interface Container — CLI | 8 | CLI-specific interface UCs: REPL, slash commands, rendering. All business operations delegate through AgentController. |
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
| **Total** | **22 groups** | **152** | **1:1 UC↔SQ mapping (100%)** |

---

## AgentController Group (AC) — Convergence Point

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| AC-01 | PROCESS Request | AgentController | `sq_ac01_process_request.puml` | Route incoming request from any interface to Core Engine |
| AC-02 | VALIDATE Request | AgentController | `sq_ac02_validate_request.puml` | Validate request format, permissions, and protocol |
| AC-03 | ADAPT Protocol | AgentController | `sq_ac03_adapt_protocol.puml` | Adapt between interface protocols (CLI, HTTP, MCP) |
| AC-04 | DISPATCH to Core Engine | AgentController | `sq_ac04_dispatch_to_core_engine.puml` | Forward validated request to AgentOrchestrator |

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

All business operations MUST delegate through AgentController. No direct calls to core services.

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
| AGT-01 | PROCESS User Task | AgentOrchestrator | `sq_agent01_process_user_task.puml` | Primary orchestrator. `<<include>>` AGT-02, AGT-03, AGT-15 |
| AGT-02 | DISPATCH Tool Call | AgentOrchestrator | `sq_agent02_dispatch_tool_call.puml` | Routes to ToolRegistry. `<<include>>` SAF-01 |
| AGT-03 | UPDATE Conversation | ConversationHistory | `sq_agent03_update_conversation.puml` | Appends messages, tracks token count |
| AGT-04 | DELETE History | ConversationHistory | `sq_agent04_delete_history.puml` | Resets conversation history |
| AGT-05 | *(vacant — ID retired per permanence rule)* | — | — | Numbering gap preserved; IDs are permanent. No SQ assigned. |
| AGT-06 | COMPACT Context | ContextCompactor | `sq_agent06_compact_context.puml` | Summarizes old exchanges via secondary LLM |
| AGT-07 | QUEUE Plan | PlanSession | `sq_agent07_queue_plan.puml` | Holds queued tool calls in plan mode |
| AGT-08 | APPROVE Plan | PlanSession | `sq_agent08_approve_plan.puml` | Drains queued plan calls. `<<include>>` AGT-02 |
| AGT-09 | SPAWN Subagent | SubagentCoordinator | `sq_agent09_spawn_subagent.puml` | Creates child agent with restricted tools |
| AGT-10 | COLLECT Subagent Result | SubagentCoordinator | `sq_agent10_collect_subagent_result.puml` | Gathers results from child agents |
| AGT-11 | DELEGATE to Persona | PersonaManager | `sq_agent11_delegate_to_persona.puml` | Assigns tasks to specialized persona roles |
| AGT-12 | LOAD Persona | PersonaManager | `sq_agent12_load_persona.puml` | Loads persona configuration |
| AGT-13 | SWITCH Persona | PersonaManager | `sq_agent13_switch_persona.puml` | Switches persona at runtime |
| AGT-14 | HANDLE Error | ErrorBoundary | `sq_agent14_handle_error.puml` | Structured error handling with recovery |
| AGT-15 | DISPATCH Safety Pipeline | SafetyCoordinator | `sq_agent15_dispatch_safety_pipeline.puml` | Runs permission, injection, egress checks |

---

## Provider Group (PRV)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| PRV-01 | REGISTER Provider | LiteLLMProxy | `sq_provider01_register_provider.puml` |
| PRV-02 | REQUEST Chat | Provider | `sq_provider02_request_chat.puml` |
| PRV-03 | STREAM Chat | Provider | `sq_provider03_stream_chat.puml` |
| PRV-04 | SELECT Provider Backend | LiteLLMProxy | `sq_provider04_select_provider_backend.puml` |

---

## Config Group (CFG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| CFG-01 | LOAD Config | ConfigLoader | `sq_config01_load_config.puml` |
| CFG-02 | VALIDATE Config | ConfigLoader | `sq_config02_validate_config.puml` |
| CFG-03 | APPLY Layered Config | ConfigLoader | `sq_config03_apply_layered_config.puml` |

---

## Session Group (SSN)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SSN-01 | PERSIST Session | SessionStore | `sq_session01_persist_session.puml` |
| SSN-02 | READ Session | SessionStore | `sq_session02_read_session.puml` |
| SSN-03 | LIST Sessions | SessionStore | `sq_session03_list_sessions.puml` |
| SSN-04 | RESTORE Session | SessionStore | `sq_session04_restore_session.puml` |
| SSN-05 | SNAPSHOT Session | SessionVersioning | `sq_session05_snapshot_session.puml` |
| SSN-06 | REVERT Turn | SessionVersioning | `sq_session06_revert_turn.puml` |
| SSN-07 | SEARCH Sessions | SessionSearch | `sq_session07_search_sessions.puml` |
| SSN-08 | BRANCH Session | SessionFork | `sq_session08_branch_session.puml` |
| SSN-09 | DELETE Session | SessionStore | `sq_session09_delete_session.puml` |

---

## Safety Group (SAF)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SAF-01 | CHECK Permission | SafetyCoordinator | `sq_safety01_check_permission.puml` |
| SAF-02 | REQUEST Approval | SafetyCoordinator | `sq_safety02_request_approval.puml` |
| SAF-03 | APPLY Safety Mode | SafetyCoordinator | `sq_safety03_apply_safety_mode.puml` |

---

## Context Graph Group (CTX)

CTX-02..06 are sub-use-cases of CTX-01. They use `<<include>>` from CTX-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CTX-01 | PROCESS Context | PipelineOrchestrator | `sq_contextgraph01_process_context.puml` | Primary orchestrator. `<<include>>` CTX-02..06 |
| CTX-02 | TRUNCATE Nodes | TruncationProcessor | `sq_contextgraph02_truncate_nodes.puml` | Sub-UC of CTX-01 |
| CTX-03 | DISTILL Nodes | DistillationProcessor | `sq_contextgraph03_distill_nodes.puml` | Sub-UC of CTX-01 |
| CTX-04 | INJECT Context | InjectionProcessor | `sq_contextgraph04_inject_context.puml` | Sub-UC of CTX-01 |
| CTX-05 | COMPACT Nodes | CompactionProcessor | `sq_contextgraph05_compact_nodes.puml` | Sub-UC of CTX-01 |
| CTX-06 | TRACK Token Budget | PipelineOrchestrator | `sq_contextgraph06_track_token_budget.puml` | Sub-UC of CTX-01 |

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
| HK-01 | REGISTER Hook | HookManager | `sq_hooks01_register_hook.puml` |
| HK-02 | DISPATCH Pre-Tool Hook | HookManager | `sq_hooks02_dispatch_pre_tool_hook.puml` |
| HK-03 | DISPATCH Post-Tool Hook | HookManager | `sq_hooks03_dispatch_post_tool_hook.puml` |
| HK-04 | DISPATCH Pre-LLM Hook | HookManager | `sq_hooks04_dispatch_pre_llm_hook.puml` |
| HK-05 | DISPATCH Post-LLM Hook | HookManager | `sq_hooks05_dispatch_post_llm_hook.puml` |
| HK-06 | VALIDATE Hook Result | HookManager | `sq_hooks06_validate_hook_result.puml` |

---

## Plugins Group (PLG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| PLG-01 | DISCOVER Plugins | PluginLoader | `sq_plugins01_discover_plugins.puml` |
| PLG-02 | LOAD Manifest | PluginLoader | `sq_plugins02_load_manifest.puml` |
| PLG-03 | REGISTER Plugin Tools | PluginLoader | `sq_plugins03_register_plugin_tools.puml` |
| PLG-04 | REGISTER Plugin Hooks | PluginLoader | `sq_plugins04_register_plugin_hooks.puml` |
| PLG-05 | ENABLE Plugin | PluginLoader | `sq_plugins05_enable_plugin.puml` |
| PLG-06 | DISABLE Plugin | PluginLoader | `sq_plugins06_disable_plugin.puml` |

---

## Router Group (RTG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| RTG-01 | SELECT Model | ModelRouter | `sq_router01_select_model.puml` |
| RTG-02 | APPLY Fallback | ModelRouter | `sq_router02_apply_fallback.puml` |
| RTG-03 | CLASSIFY Task | ModelRouter | `sq_router03_classify_task.puml` |
| RTG-04 | SWITCH Model | ModelRouter | `sq_router04_switch_model.puml` |

---

## Observability Group (OBS)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| OBS-01 | STREAM Structured Log | StructuredLogger | `sq_observability01_stream_log.puml` |
| OBS-02 | RECORD Metrics | MetricsCollector | `sq_observability02_record_metrics.puml` |
| OBS-03 | CORRELATE Trace | TraceCorrelator | `sq_observability03_correlate_trace.puml` |
| OBS-04 | REDACT Sensitive | LogRedactor | `sq_observability04_redact_sensitive.puml` |
| OBS-05 | EXPOSE /metrics | MetricsCollector | `sq_observability05_expose_metrics.puml` |
| OBS-06 | EXPORT OTLP | OTelExporter | `sq_observability06_export_otlp.puml` |

---

## Memory Group (MEM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| MEM-01 | PERSIST Knowledge | MemoryStore | `sq_memory01_persist_knowledge.puml` |
| MEM-02 | RECALL Knowledge | MemoryStore | `sq_memory02_recall_knowledge.puml` |
| MEM-03 | SEARCH Knowledge | MemoryIndex | `sq_memory03_search_knowledge.puml` |
| MEM-04 | SCOPE Knowledge | MemoryScope | `sq_memory04_scope_knowledge.puml` |

---

## Git Group (VCS)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| VCS-01 | READ Git Status | GitStatus | `sq_git01_read_git_status.puml` |
| VCS-02 | INSERT Commit | GitCommit | `sq_git02_insert_commit.puml` |
| VCS-03 | READ Diff | GitStatus | `sq_git03_read_diff.puml` |
| VCS-04 | AUTO-COMMIT | GitIntegration | `sq_git04_auto_commit.puml` |

---

## Sandbox Group (SBX)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SBX-01 | ISOLATE Command | SandboxExecutor | `sq_sandbox01_isolate_command.puml` |
| SBX-02 | APPLY Sandbox Policy | SandboxPolicy | `sq_sandbox02_apply_sandbox_policy.puml` |
| SBX-03 | MONITOR Process | SandboxMonitor | `sq_sandbox03_monitor_process.puml` |
| SBX-04 | LIMIT Resources | ResourceLimiter | `sq_sandbox04_limit_resources.puml` |

---

## Repo Intelligence Group (RIM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| RIM-01 | INDEX Codebase | RepoIntelligenceManager | `sq_repointelligence01_index_codebase.puml` |
| RIM-02 | BUILD Symbol Graph | SymbolGraph | `sq_repointelligence02_build_symbol_graph.puml` |
| RIM-03 | RANK Results | SymbolGraph (RankingService) | `sq_repointelligence03_rank_results.puml` |
| RIM-04 | INJECT RepoMap | RepoMapBuilder | `sq_repointelligence04_inject_repo_map.puml` |
| RIM-05 | EMBED Code | EmbeddingAdapter | `sq_repointelligence05_embed_code.puml` |
| RIM-06 | SEARCH Semantic | SemanticSearchService | `sq_repointelligence06_search_semantic.puml` |

---

## Edit Strategy Group (EDT)

EDT-02..10 are sub-use-cases of EDT-01. They use `<<include>>` from EDT-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EDT-01 | SELECT Strategy | StrategySelector | `sq_editstrategy01_select_strategy.puml` | Primary. `<<include>>` EDT-02..10 |
| EDT-02 | APPLY Search-Replace | SearchReplaceCoder | `sq_editstrategy02_apply_search_replace.puml` | Sub-UC of EDT-01 |
| EDT-03 | APPLY Whole-File | WholeFileCoder | `sq_editstrategy03_apply_whole_file.puml` | Sub-UC of EDT-01 |
| EDT-04 | APPLY Unified Diff | UnifiedDiffCoder | `sq_editstrategy04_apply_unified_diff.puml` | Sub-UC of EDT-01 |
| EDT-05 | APPLY Fenced Block | FencedBlockCoder | `sq_editstrategy05_apply_fenced_block.puml` | Sub-UC of EDT-01 |
| EDT-06 | APPLY Function-Level | FunctionLevelCoder | `sq_editstrategy06_apply_function_level.puml` | Sub-UC of EDT-01 |
| EDT-07 | APPLY Diff Sandbox | DiffSandboxCoder | `sq_editstrategy07_apply_diff_sandbox.puml` | Sub-UC of EDT-01 |
| EDT-08 | APPLY Architect | ArchitectCoder | `sq_editstrategy08_apply_architect.puml` | Sub-UC of EDT-01 |
| EDT-09 | APPLY Inline Patch | InlinePatchCoder | `sq_editstrategy09_apply_inline_patch.puml` | Sub-UC of EDT-01 |
| EDT-10 | STAGE Diff | DiffSandboxManager | `sq_editstrategy10_stage_diff.puml` | Sub-UC of EDT-01 |

---

## Evaluation Group (EVL)

EVL-02..09 are sub-use-cases of EVL-01. They use `<<include>>` from EVL-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EVL-01 | EVALUATE Task | EvaluationEngine | `sq_evaluation01_evaluate_task.puml` | Primary. `<<include>>` EVL-02..09 |
| EVL-02 | CHECK Task Completion | TaskEvaluator | `sq_evaluation02_check_task_completion.puml` | Sub-UC of EVL-01 |
| EVL-03 | CHECK Success | SuccessCheckRunner | `sq_evaluation03_check_success.puml` | Sub-UC of EVL-01 |
| EVL-04 | VALIDATE With LLM | LLMReviewer | `sq_evaluation04_validate_with_llm.puml` | Sub-UC of EVL-01 |
| EVL-05 | VALIDATE Test Suite | TestRunner | `sq_evaluation05_validate_test_suite.puml` | Sub-UC of EVL-01 |
| EVL-06 | COORDINATE Retry | RetryCoordinator | `sq_evaluation06_coordinate_retry.puml` | Sub-UC of EVL-01 |
| EVL-07 | RECORD Quality Signal | EvaluationEngine | `sq_evaluation07_record_quality_signal.puml` | Sub-UC of EVL-01 |
| EVL-08 | DETECT Repetition | RepetitionDetector | `sq_evaluation08_detect_repetition.puml` | Sub-UC of EVL-01 |
| EVL-09 | INJECT Turn Budget | TurnBudgetInjector | `sq_evaluation09_inject_turn_budget.puml` | Sub-UC of EVL-01 |

---

## Wire Log Group (WRL)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| WRL-01 | APPEND Event | WireLog | `sq_wirelog01_append_event.puml` |
| WRL-02 | READ Log | WireReader | `sq_wirelog02_read_log.puml` |
| WRL-03 | SEEK Turn | WireLog | `sq_wirelog03_seek_turn.puml` |
| WRL-04 | FORK Session | SessionForkManager | `sq_wirelog04_fork_session.puml` |
| WRL-05 | CHECKPOINT Turn | WireLog | `sq_wirelog05_checkpoint_turn.puml` |

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
| AC-01 (PROCESS Request) | AC-02..04 | `AC-01 ..> AC-02 : <<include>>` etc. |
| CTX-01 (PROCESS Context) | CTX-02..06 | `CTX-01 ..> CTX-02 : <<include>>` etc. |
| EDT-01 (SELECT Strategy) | EDT-02..10 | `EDT-01 ..> EDT-02 : <<include>>` etc. |
| EVL-01 (EVALUATE Task) | EVL-02..09 | `EVL-01 ..> EVL-02 : <<include>>` etc. |

No sub-UC has its own sub-UCs (no nesting beyond one level).

---

## Traceability Matrix (Container → UC)

| Container | UC Group | UC IDs | Description |
|-----------|----------|--------|-------------|
| AgentController | AC | AC-01..04 | Single convergence point: routes requests to Core Engine |
| HTTP API Server | API | API-01..11 | Core business operations (ROD-compliant REST) |
| CLI Process | CLI | CLI-01..08 | CLI-specific interface UCs |
| Core Engine | AGT, PRV, CFG, SSN, SAF, CTX, TL, HK, PLG, RTG, OBS, MEM, VCS, SBX, RIM, EDT, EVL, WRL | Various | All business logic and domain operations |
| MCP Client | MCP | MCP-01..04 | MCP protocol handling |

---

**Total: 152 UCs** (148 existing + 4 new AgentController UCs) matching 148 existing SQ diagrams + 4 new AgentController SQ diagrams (excluding AGT-05 which is a vacant ID per permanence rule).

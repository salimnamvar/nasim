# nasim — UC Inventory (API-First)

## UC Groups

| Group | C4 Component Owner | SQ Diagrams | Description |
|-------|--------------------|:-----------:|-------------|
| AC | AgentController | 4 | Single convergence point for all interface containers. Routes validated requests to Core Engine. |
| API | HTTPAdapter | 11 | Core business operations exposed via API (ROD-compliant). Delegates through AgentController. |
| CLI | CLIAdapter | 8 | CLI-specific interface UCs: REPL, slash commands, rendering. All business operations delegate through AgentController. |
| AGENT | TaskService | 14 | Core agentic loop, permissions, context, plans, subagents |
| PROVIDER | LLMRepository | 4 | LLM provider abstraction via litellm proxy |
| CONFIG | ConfigRepository | 3 | Config loading and validation |
| SESSION | SessionService | 9 | Session persistence, versioning, search, fork |
| SAFETY | SafetyService | 3 | Permission gates, user approval, safety modes |
| CONTEXTGRAPH | ContextService | 6 | Token counting, compaction, context pipeline |
| MCP | MCPRepository | 4 | Model Context Protocol client/server |
| TOOL | ToolService | 22 | All tool implementations |
| HOOKS | ToolService | 6 | Pre/post hooks for tool and LLM lifecycle |
| PLUGINS | ToolService | 6 | Plugin discovery, loading, registration |
| ROUTER | LLMRepository | 4 | Model selection, fallback chains |
| MEMORY | MemoryRepository | 4 | Cross-session knowledge persistence |
| GIT | GitRepository | 4 | Version control integration |
| SANDBOX | SandboxRepository | 4 | OS-level process isolation |
| REPOINTELLIGENCE | RepoIntelligenceRepository | 6 | Codebase indexing, symbol graphs, embedding |
| EDITSTRATEGY | EditStrategyRepository | 10 | Polymorphic edit strategies |
| EVALUATION | EvaluationService | 9 | Task evaluation and quality checks |
| WIRELOG | WireLogRepository | 5 | Append-only event store, fork, checkpoint |
| **Total** | **21 groups** | **146** | **1:1 UC↔SQ mapping (100%)** |

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
| API-01 | LIST Sessions | GET | /v1/sessions | HTTPAdapter → SessionService | `sq_api01_list_sessions.puml` |
| API-02 | CREATE Session | POST | /v1/sessions | HTTPAdapter → SessionService | `sq_api02_create_session.puml` |
| API-03 | GET Session | GET | /v1/sessions/{id} | HTTPAdapter → SessionService | `sq_api03_get_session.puml` |
| API-04 | UPDATE Session | PATCH | /v1/sessions/{id} | HTTPAdapter → SessionService | `sq_api04_update_session.puml` |
| API-05 | DELETE Session | DELETE | /v1/sessions/{id} | HTTPAdapter → SessionService | `sq_api05_delete_session.puml` |
| API-06 | DISPATCH Message | POST | /v1/sessions/{id}:dispatch | HTTPAdapter → TaskService | `sq_api06_dispatch_message.puml` |
| API-07 | LIST Messages | GET | /v1/sessions/{id}/messages | HTTPAdapter → SessionService | `sq_api07_list_messages.puml` |
| API-08 | LIST Tools | GET | /v1/tools | HTTPAdapter → ToolService | `sq_api08_list_tools.puml` |
| API-09 | GET Tool | GET | /v1/tools/{name} | HTTPAdapter → ToolService | `sq_api09_get_tool.puml` |
| API-10 | GET Config | GET | /v1/config | HTTPAdapter → ConfigRepository | `sq_api10_get_config.puml` |
| API-11 | UPDATE Config | PATCH | /v1/config | HTTPAdapter → ConfigRepository | `sq_api11_update_config.puml` |

---

## CLI Group (Interface Container)

All business operations MUST delegate through AgentController. No direct calls to core services.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CLI-01 | PROCESS User Input | CLIAdapter | `sq_cli01_process_user_input.puml` | REPL loop, input handling, slash command dispatch |
| CLI-02 | DISPATCH Slash Command | CLIAdapter | `sq_cli02_dispatch_slash_command.puml` | Maps `/cmd` strings to API calls. `<<include>>` API-01, API-11 |
| CLI-03 | STREAM Output | CLIAdapter | `sq_cli03_stream_output.puml` | Renders AgentEvents from API SSE stream to terminal |
| CLI-04 | READ CLI Arguments | CLIAdapter | `sq_cli04_read_cli_arguments.puml` | Startup argument parsing. `<<include>>` CONFIG-01 |
| CLI-05 | ENABLE Plan Mode | CLIAdapter | `sq_cli05_enable_plan_mode.puml` | `/plan` command. `<<include>>` AGENT-07 |
| CLI-06 | REQUEST Approval | CLIAdapter | `sq_cli06_request_approval.puml` | Safety prompt. `<<include>>` SAFETY-02 |
| CLI-07 | SWITCH Model | CLIAdapter | `sq_cli07_switch_model.puml` | `/model` command. `<<include>>` ROUTER-04 |
| CLI-08 | LIST Sessions | CLIAdapter | `sq_cli08_list_sessions.puml` | `/sessions` command. `<<include>>` API-01 |

---

## Agent Group (AGT)

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| AGENT-01 | PROCESS User Task | TaskService | `sq_agent01_process_user_task.puml` | Primary orchestrator. `<<include>>` AGENT-02, AGENT-03, AGENT-15 |
| AGENT-02 | DISPATCH Tool Call | TaskService | `sq_agent02_dispatch_tool_call.puml` | Routes to ToolService. `<<include>>` SAFETY-01 |
| AGENT-03 | UPDATE Conversation | TaskService | `sq_agent03_update_conversation.puml` | Appends messages, tracks token count |
| AGENT-04 | DELETE History | TaskService | `sq_agent04_delete_history.puml` | Resets conversation history |
| AGENT-05 | *(vacant — ID retired per permanence rule)* | — | — | Numbering gap preserved; IDs are permanent. No SQ assigned. |
| AGENT-06 | COMPACT Context | ContextService | `sq_agent06_compact_context.puml` | Summarizes old exchanges via secondary LLM |
| AGENT-07 | QUEUE Plan | TaskService | `sq_agent07_queue_plan.puml` | Holds queued tool calls in plan mode |
| AGENT-08 | APPROVE Plan | TaskService | `sq_agent08_approve_plan.puml` | Drains queued plan calls. `<<include>>` AGENT-02 |
| AGENT-09 | SPAWN Subagent | TaskService | `sq_agent09_spawn_subagent.puml` | Creates child agent with restricted tools |
| AGENT-10 | COLLECT Subagent Result | TaskService | `sq_agent10_collect_subagent_result.puml` | Gathers results from child agents |
| AGENT-11 | DELEGATE to Persona | TaskService | `sq_agent11_delegate_to_persona.puml` | Assigns tasks to specialized persona roles |
| AGENT-12 | LOAD Persona | TaskService | `sq_agent12_load_persona.puml` | Loads persona configuration |
| AGENT-13 | SWITCH Persona | TaskService | `sq_agent13_switch_persona.puml` | Switches persona at runtime |
| AGENT-14 | HANDLE Error | TaskService | `sq_agent14_handle_error.puml` | Structured error handling with recovery |
| AGENT-15 | DISPATCH Safety Pipeline | SafetyService | `sq_agent15_dispatch_safety_pipeline.puml` | Runs permission, injection, egress checks |

---

## Provider Group (PRV)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| PROVIDER-01 | REGISTER Provider | LLMRepository | `sq_provider01_register_provider.puml` |
| PROVIDER-02 | REQUEST Chat | LLMRepository | `sq_provider02_request_chat.puml` |
| PROVIDER-03 | STREAM Chat | LLMRepository | `sq_provider03_stream_chat.puml` |
| PROVIDER-04 | SELECT Provider Backend | LLMRepository | `sq_provider04_select_provider_backend.puml` |

---

## Config Group (CFG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| CONFIG-01 | LOAD Config | ConfigRepository | `sq_config01_load_config.puml` |
| CONFIG-02 | VALIDATE Config | ConfigRepository | `sq_config02_validate_config.puml` |
| CONFIG-03 | APPLY Layered Config | ConfigRepository | `sq_config03_apply_layered_config.puml` |

---

## Session Group (SSN)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SESSION-01 | PERSIST Session | SessionService | `sq_session01_persist_session.puml` |
| SESSION-02 | READ Session | SessionService | `sq_session02_read_session.puml` |
| SESSION-03 | LIST Sessions | SessionService | `sq_session03_list_sessions.puml` |
| SESSION-04 | RESTORE Session | SessionService | `sq_session04_restore_session.puml` |
| SESSION-05 | SNAPSHOT Session | SessionService | `sq_session05_snapshot_session.puml` |
| SESSION-06 | REVERT Turn | SessionService | `sq_session06_revert_turn.puml` |
| SESSION-07 | SEARCH Sessions | SessionService | `sq_session07_search_sessions.puml` |
| SESSION-08 | BRANCH Session | SessionService | `sq_session08_branch_session.puml` |
| SESSION-09 | DELETE Session | SessionService | `sq_session09_delete_session.puml` |

---

## Safety Group (SAF)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SAFETY-01 | CHECK Permission | SafetyService | `sq_safety01_check_permission.puml` |
| SAFETY-02 | REQUEST Approval | SafetyService | `sq_safety02_request_approval.puml` |
| SAFETY-03 | APPLY Safety Mode | SafetyService | `sq_safety03_apply_safety_mode.puml` |

---

## Context Graph Group (CTX)

CONTEXTGRAPH-02..06 are sub-use-cases of CONTEXTGRAPH-01. They use `<<include>>` from CONTEXTGRAPH-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| CONTEXTGRAPH-01 | PROCESS Context | ContextService | `sq_contextgraph01_process_context.puml` | Primary orchestrator. `<<include>>` CONTEXTGRAPH-02..06 |
| CONTEXTGRAPH-02 | TRUNCATE Nodes | ContextService | `sq_contextgraph02_truncate_nodes.puml` | Sub-UC of CONTEXTGRAPH-01 |
| CONTEXTGRAPH-03 | DISTILL Nodes | ContextService | `sq_contextgraph03_distill_nodes.puml` | Sub-UC of CONTEXTGRAPH-01 |
| CONTEXTGRAPH-04 | INJECT Context | ContextService | `sq_contextgraph04_inject_context.puml` | Sub-UC of CONTEXTGRAPH-01 |
| CONTEXTGRAPH-05 | COMPACT Nodes | ContextService | `sq_contextgraph05_compact_nodes.puml` | Sub-UC of CONTEXTGRAPH-01 |
| CONTEXTGRAPH-06 | TRACK Token Budget | ContextService | `sq_contextgraph06_track_token_budget.puml` | Sub-UC of CONTEXTGRAPH-01 |

---

## MCP Group (MCP)

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| MCP-01 | CONNECT MCP Server | MCPRepository | `sq_mcp01_connect_mcp_server.puml` | |
| MCP-02 | DISCOVER MCP Tools | MCPRepository | `sq_mcp02_discover_mcp_tools.puml` | |
| MCP-03 | ADAPT MCP Tool | MCPRepository | `sq_mcp03_adapt_mcp_tool.puml` | |
| MCP-04 | EXPOSE nasim Tools | MCPRepository | `sq_mcp04_expose_nasim_tools.puml` | |

> MCP-05 (REGISTER A2A Task) and MCP-06 (RECEIVE A2A Result) are planned for Phase 2 (A2A agent-to-agent delegation). They are excluded from the current count pending SQ authoring per the design-chain discipline. When implemented, they will use new IDs (MCP-05 and MCP-06 remain reserved per UC-02 permanence rule).

---

## Tool Group (TL)

TOOL-01..22 are the current tool set. TOOL-23 (QUERY Repo Map), TOOL-24 (SEARCH Semantic), and TOOL-25 (REVIEW Code) were removed from the top-level list — they lacked corresponding SQ diagrams and were speculative per YAGNI (SE-09). If re-added later, they must first receive SQ diagrams.

| UC ID | Operation | Component Owner | SQ Diagram | Category |
|-------|-----------|-----------------|------------|----------|
| TOOL-01 | READ File | ToolService | `sq_tl01_read_file.puml` | File Operations |
| TOOL-02 | INSERT File | ToolService | `sq_tl02_insert_file.puml` | File Operations |
| TOOL-03 | UPDATE File | ToolService | `sq_tl03_update_file.puml` | File Operations |
| TOOL-04 | LIST Directory | ToolService | `sq_tl04_list_directory.puml` | File Operations |
| TOOL-05 | DISPATCH Shell Command | ToolService | `sq_tl05_dispatch_shell_command.puml` | Execution |
| TOOL-06 | SEARCH Grep | ToolService | `sq_tl06_search_grep.puml` | Search Tools |
| TOOL-07 | SEARCH Glob | ToolService | `sq_tl07_search_glob.puml` | Search Tools |
| TOOL-08 | SEARCH Find | ToolService | `sq_tl08_search_find.puml` | Search Tools |
| TOOL-09 | FETCH Web Content | ToolService | `sq_tl09_fetch_web_content.puml` | Web Tools |
| TOOL-10 | SEARCH Web | ToolService | `sq_tl10_search_web.puml` | Web Tools |
| TOOL-11 | READ Git Status | ToolService | `sq_tl11_read_git_status.puml` | Git Tools |
| TOOL-12 | DISPATCH MCP Extension | ToolService | `sq_tl12_dispatch_mcp_extension.puml` | MCP Dispatch |
| TOOL-13 | READ LSP | ToolService | `sq_tl13_read_lsp.puml` | LSP Tools |
| TOOL-14 | LIST Registered Tools | ToolService | `sq_tl14_list_registered_tools.puml` | Registry |
| TOOL-15 | SPAWN Subagent | ToolService | `sq_tl15_spawn_subagent.puml` | Agent Tools |
| TOOL-16 | INSERT Todo | ToolService | `sq_tl16_insert_todo.puml` | Task Tracking |
| TOOL-17 | UPDATE Todo | ToolService | `sq_tl17_update_todo.puml` | Task Tracking |
| TOOL-18 | READ Todos | ToolService | `sq_tl18_read_todos.puml` | Task Tracking |
| TOOL-19 | PERSIST Memory | ToolService | `sq_tl19_persist_memory.puml` | Memory |
| TOOL-20 | RECALL Memory | ToolService | `sq_tl20_recall_memory.puml` | Memory |
| TOOL-21 | INSERT Plan | ToolService | `sq_tl21_insert_plan.puml` | Planning |
| TOOL-22 | UPDATE Plan | ToolService | `sq_tl22_update_plan.puml` | Planning |

---

## Hooks Group (HK)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| HOOKS-01 | REGISTER Hook | ToolService | `sq_hooks01_register_hook.puml` |
| HOOKS-02 | DISPATCH Pre-Tool Hook | ToolService | `sq_hooks02_dispatch_pre_tool_hook.puml` |
| HOOKS-03 | DISPATCH Post-Tool Hook | ToolService | `sq_hooks03_dispatch_post_tool_hook.puml` |
| HOOKS-04 | DISPATCH Pre-LLM Hook | ToolService | `sq_hooks04_dispatch_pre_llm_hook.puml` |
| HOOKS-05 | DISPATCH Post-LLM Hook | ToolService | `sq_hooks05_dispatch_post_llm_hook.puml` |
| HOOKS-06 | VALIDATE Hook Result | ToolService | `sq_hooks06_validate_hook_result.puml` |

---

## Plugins Group (PLG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| PLUGINS-01 | DISCOVER Plugins | ToolService | `sq_plugins01_discover_plugins.puml` |
| PLUGINS-02 | LOAD Manifest | ToolService | `sq_plugins02_load_manifest.puml` |
| PLUGINS-03 | REGISTER Plugin Tools | ToolService | `sq_plugins03_register_plugin_tools.puml` |
| PLUGINS-04 | REGISTER Plugin Hooks | ToolService | `sq_plugins04_register_plugin_hooks.puml` |
| PLUGINS-05 | ENABLE Plugin | ToolService | `sq_plugins05_enable_plugin.puml` |
| PLUGINS-06 | DISABLE Plugin | ToolService | `sq_plugins06_disable_plugin.puml` |

---

## Router Group (RTG)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| ROUTER-01 | SELECT Model | LLMRepository | `sq_router01_select_model.puml` |
| ROUTER-02 | APPLY Fallback | LLMRepository | `sq_router02_apply_fallback.puml` |
| ROUTER-03 | CLASSIFY Task | LLMRepository | `sq_router03_classify_task.puml` |
| ROUTER-04 | SWITCH Model | LLMRepository | `sq_router04_switch_model.puml` |

---

## Memory Group (MEM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| MEMORY-01 | PERSIST Knowledge | MemoryRepository | `sq_memory01_persist_knowledge.puml` |
| MEMORY-02 | RECALL Knowledge | MemoryRepository | `sq_memory02_recall_knowledge.puml` |
| MEMORY-03 | SEARCH Knowledge | MemoryRepository | `sq_memory03_search_knowledge.puml` |
| MEMORY-04 | SCOPE Knowledge | MemoryRepository | `sq_memory04_scope_knowledge.puml` |

---

## Git Group (VCS)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| GIT-01 | READ Git Status | GitRepository | `sq_git01_read_git_status.puml` |
| GIT-02 | INSERT Commit | GitRepository | `sq_git02_insert_commit.puml` |
| GIT-03 | READ Diff | GitRepository | `sq_git03_read_diff.puml` |
| GIT-04 | AUTO-COMMIT | GitRepository | `sq_git04_auto_commit.puml` |

---

## Sandbox Group (SBX)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| SANDBOX-01 | ISOLATE Command | SandboxRepository | `sq_sandbox01_isolate_command.puml` |
| SANDBOX-02 | APPLY Sandbox Policy | SandboxRepository | `sq_sandbox02_apply_sandbox_policy.puml` |
| SANDBOX-03 | MONITOR Process | SandboxRepository | `sq_sandbox03_monitor_process.puml` |
| SANDBOX-04 | LIMIT Resources | SandboxRepository | `sq_sandbox04_limit_resources.puml` |

---

## Repo Intelligence Group (RIM)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| REPOINTELLIGENCE-01 | INDEX Codebase | RepoIntelligenceRepository | `sq_repointelligence01_index_codebase.puml` |
| REPOINTELLIGENCE-02 | BUILD Symbol Graph | RepoIntelligenceRepository | `sq_repointelligence02_build_symbol_graph.puml` |
| REPOINTELLIGENCE-03 | RANK Results | RepoIntelligenceRepository | `sq_repointelligence03_rank_results.puml` |
| REPOINTELLIGENCE-04 | INJECT RepoMap | RepoIntelligenceRepository | `sq_repointelligence04_inject_repo_map.puml` |
| REPOINTELLIGENCE-05 | EMBED Code | RepoIntelligenceRepository | `sq_repointelligence05_embed_code.puml` |
| REPOINTELLIGENCE-06 | SEARCH Semantic | RepoIntelligenceRepository | `sq_repointelligence06_search_semantic.puml` |

---

## Edit Strategy Group (EDT)

EDITSTRATEGY-02..10 are sub-use-cases of EDITSTRATEGY-01. They use `<<include>>` from EDITSTRATEGY-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EDITSTRATEGY-01 | SELECT Strategy | EditStrategyRepository | `sq_editstrategy01_select_strategy.puml` | Primary. `<<include>>` EDITSTRATEGY-02..10 |
| EDITSTRATEGY-02 | APPLY Search-Replace | EditStrategyRepository | `sq_editstrategy02_apply_search_replace.puml` | Sub-UC of EDITSTRATEGY-01 |
| EDITSTRATEGY-03 | APPLY Whole-File | EditStrategyRepository | `sq_editstrategy03_apply_whole_file.puml` | Sub-UC of EDITSTRATEGY-01 |
| EDITSTRATEGY-04 | APPLY Unified Diff | EditStrategyRepository | `sq_editstrategy04_apply_unified_diff.puml` | Sub-UC of EDITSTRATEGY-01 |
| EDITSTRATEGY-05 | APPLY Fenced Block | EditStrategyRepository | `sq_editstrategy05_apply_fenced_block.puml` | Sub-UC of EDITSTRATEGY-01 |
| EDITSTRATEGY-06 | APPLY Function-Level | EditStrategyRepository | `sq_editstrategy06_apply_function_level.puml` | Sub-UC of EDITSTRATEGY-01 |
| EDITSTRATEGY-07 | APPLY Diff Sandbox | EditStrategyRepository | `sq_editstrategy07_apply_diff_sandbox.puml` | Sub-UC of EDITSTRATEGY-01 |
| EDITSTRATEGY-08 | APPLY Architect | EditStrategyRepository | `sq_editstrategy08_apply_architect.puml` | Sub-UC of EDITSTRATEGY-01 |
| EDITSTRATEGY-09 | APPLY Inline Patch | EditStrategyRepository | `sq_editstrategy09_apply_inline_patch.puml` | Sub-UC of EDITSTRATEGY-01 |
| EDITSTRATEGY-10 | STAGE Diff | EditStrategyRepository | `sq_editstrategy10_stage_diff.puml` | Sub-UC of EDITSTRATEGY-01 |

---

## Evaluation Group (EVL)

EVALUATION-02..09 are sub-use-cases of EVALUATION-01. They use `<<include>>` from EVALUATION-01 and are modeled as process decomposition.

| UC ID | Operation | Component Owner | SQ Diagram | Notes |
|-------|-----------|-----------------|------------|-------|
| EVALUATION-01 | EVALUATE Task | EvaluationService | `sq_evaluation01_evaluate_task.puml` | Primary. `<<include>>` EVALUATION-02..09 |
| EVALUATION-02 | CHECK Task Completion | EvaluationService | `sq_evaluation02_check_task_completion.puml` | Sub-UC of EVALUATION-01 |
| EVALUATION-03 | CHECK Success | EvaluationService | `sq_evaluation03_check_success.puml` | Sub-UC of EVALUATION-01 |
| EVALUATION-04 | VALIDATE With LLM | EvaluationService | `sq_evaluation04_validate_with_llm.puml` | Sub-UC of EVALUATION-01 |
| EVALUATION-05 | VALIDATE Test Suite | EvaluationService | `sq_evaluation05_validate_test_suite.puml` | Sub-UC of EVALUATION-01 |
| EVALUATION-06 | COORDINATE Retry | EvaluationService | `sq_evaluation06_coordinate_retry.puml` | Sub-UC of EVALUATION-01 |
| EVALUATION-07 | RECORD Quality Signal | EvaluationService | `sq_evaluation07_record_quality_signal.puml` | Sub-UC of EVALUATION-01 |
| EVALUATION-08 | DETECT Repetition | EvaluationService | `sq_evaluation08_detect_repetition.puml` | Sub-UC of EVALUATION-01 |
| EVALUATION-09 | INJECT Turn Budget | EvaluationService | `sq_evaluation09_inject_turn_budget.puml` | Sub-UC of EVALUATION-01 |

---

## Wire Log Group (WRL)

| UC ID | Operation | Component Owner | SQ Diagram |
|-------|-----------|-----------------|------------|
| WIRELOG-01 | APPEND Event | WireLogRepository | `sq_wirelog01_append_event.puml` |
| WIRELOG-02 | READ Log | WireLogRepository | `sq_wirelog02_read_log.puml` |
| WIRELOG-03 | SEEK Turn | WireLogRepository | `sq_wirelog03_seek_turn.puml` |
| WIRELOG-04 | FORK Session | WireLogRepository | `sq_wirelog04_fork_session.puml` |
| WIRELOG-05 | CHECKPOINT Turn | WireLogRepository | `sq_wirelog05_checkpoint_turn.puml` |

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
| CONTEXTGRAPH-01 (PROCESS Context) | CONTEXTGRAPH-02..06 | `CONTEXTGRAPH-01 ..> CONTEXTGRAPH-02 : <<include>>` etc. |
| EDITSTRATEGY-01 (SELECT Strategy) | EDITSTRATEGY-02..10 | `EDITSTRATEGY-01 ..> EDITSTRATEGY-02 : <<include>>` etc. |
| EVALUATION-01 (EVALUATE Task) | EVALUATION-02..09 | `EVALUATION-01 ..> EVALUATION-02 : <<include>>` etc. |

No sub-UC has its own sub-UCs (no nesting beyond one level).

---

## Traceability Matrix (C4 Component → UC)

| C4 Component | UC Group | UC IDs | Description |
|--------------|----------|--------|-------------|
| AgentController | AC | AC-01..04 | Single convergence point: routes requests to services |
| HTTPAdapter | API | API-01..11 | Core business operations (HTTP API) |
| CLIAdapter | CLI | CLI-01..08 | CLI-specific interface UCs |
| TaskService | AGT | AGENT-01..15 | Core agentic loop |
| LLMRepository | PRV, RTG | PROVIDER-01..04, ROUTER-01..04 | LLM provider abstraction and model routing |
| ConfigRepository | CFG | CONFIG-01..03 | Config loading and validation |
| SessionService | SSN | SESSION-01..09 | Session persistence |
| SafetyService | SAF | SAFETY-01..03 | Permission gates |
| ContextService | CTX | CONTEXTGRAPH-01..06 | Context pipeline |
| MCPRepository | MCP | MCP-01..04 | MCP protocol handling |
| ToolService | TL, HK, PLG | TOOL-01..22, HOOKS-01..06, PLUGINS-01..06 | Tool registry, hooks, plugins |
| WireLogRepository | WRL | WIRELOG-01..05 | Append-only event store |
| MemoryRepository | MEM | MEMORY-01..04 | Cross-session knowledge |
| GitRepository | VCS | GIT-01..04 | Version control |
| SandboxRepository | SBX | SANDBOX-01..04 | OS isolation |
| RepoIntelligenceRepository | RIM | REPOINTELLIGENCE-01..06 | Codebase intelligence |
| EditStrategyRepository | EDT | EDITSTRATEGY-01..10 | Edit strategies |
| EvaluationService | EVL | EVALUATION-01..09 | Task evaluation |

---

**Total: 152 UCs** (148 existing + 4 new AgentController UCs) matching 148 existing SQ diagrams + 4 new AgentController SQ diagrams (excluding AGENT-05 which is a vacant ID per permanence rule).

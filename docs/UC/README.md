# nasim — UC Inventory (API-First)

## UC Groups

| Group | Boundary | Description |
|-------|----------|-------------|
| API | nasim Backend — API Entry Gate | Core business operations exposed via API (ROD-compliant). Sole entry point for all interface containers. |
| CLI | Interface Container — CLI | CLI-specific interface UCs: REPL, slash commands, rendering. All business operations delegate to API. |
| AGT | Core Library — Agent | Core agentic loop, permissions, context, plans, subagents |
| PRV | Core Library — Provider | LLM provider abstraction via litellm proxy |
| CFG | Core Library — Config | Config loading and validation |
| SSN | Core Library — Session | Session persistence, versioning, search, fork |
| SAF | Core Library — Safety | Permission gates, user approval, safety modes |
| CTX | Core Library — Context Graph | Token counting, compaction, context pipeline |
| MCP | Core Library — MCP | Model Context Protocol client/server |
| TL | Core Library — Tools | All tool implementations |
| HK | Core Library — Hooks | Pre/post hooks for tool and LLM lifecycle |
| PLG | Core Library — Plugins | Plugin discovery, loading, registration |
| RTG | Core Library — Router | Model selection, fallback chains |
| OBS | Core Library — Observability | Structured logging, metrics, trace correlation |
| MEM | Core Library — Memory | Cross-session knowledge persistence |
| VCS | Core Library — Git | Version control integration |
| SBX | Core Library — Sandbox | OS-level process isolation |
| RIM | Core Library — Repo Intelligence | Codebase indexing, symbol graphs, embedding |
| EDT | Core Library — Edit Strategy | Polymorphic edit strategies |
| EVL | Core Library — Evaluation | Task evaluation and quality checks |
| WRL | Core Library — Wire Log | Append-only event store, fork, checkpoint |

## API Group (Entry Gate) — Core Business UCs

| UC ID | Operation | HTTP Method | Path | Component Owner | Notes |
|-------|-----------|-------------|------|-----------------|-------|
| API-01 | LIST Sessions | GET | /v1/sessions | ServerRouter → SessionStore | Paginated (AIP-158) |
| API-02 | CREATE Session | POST | /v1/sessions | ServerRouter → SessionStore | Returns 201 |
| API-03 | GET Session | GET | /v1/sessions/{id} | ServerRouter → SessionStore | Single session |
| API-04 | UPDATE Session | PATCH | /v1/sessions/{id} | ServerRouter → SessionStore | Partial update |
| API-05 | DELETE Session | DELETE | /v1/sessions/{id} | ServerRouter → SessionStore | Hard delete |
| API-06 | DISPATCH Message | POST | /v1/sessions/{id}:dispatch | ServerRouter → AgentOrchestrator | Custom method (AIP-136). Returns SSE stream. |
| API-07 | LIST Messages | GET | /v1/sessions/{id}/messages | ServerRouter → SessionStore | Ordered by sequence |
| API-08 | LIST Tools | GET | /v1/tools | ServerRouter → ToolRegistry | Read-only collection |
| API-09 | GET Tool | GET | /v1/tools/{name} | ServerRouter → ToolRegistry | Single tool definition |
| API-10 | GET Config | GET | /v1/config | ServerRouter → ConfigLoader | Read-only singleton |
| API-11 | UPDATE Config | PATCH | /v1/config | ServerRouter → ConfigLoader | Runtime config patch |

## CLI Group (Interface Container)

| UC ID | Operation | Component Owner | Notes |
|-------|-----------|-----------------|-------|
| CLI-01 | PROCESS User Input | REPLSession | REPL loop, input handling, slash command dispatch. Delegates business ops to API. |
| CLI-02 | DISPATCH Slash Command | SlashCommandHandler | Map /cmd strings to API calls. No direct core access. |
| CLI-03 | STREAM Output | Renderer | Render AgentEvents from API SSE stream to terminal |

> **API-First Rule:** CLI-02 (DISPATCH Slash Command) MUST delegate to the API. For example, `/sessions` calls API-01 (LIST Sessions), `/model` calls API-11 (UPDATE Config). No CLI UC may call AgentOrchestrator, SessionStore, or any core service directly.

## Agent Group (AGT)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| AGT-01 | PROCESS User Task | AgentOrchestrator |
| AGT-02 | DISPATCH Tool Call | AgentOrchestrator |
| AGT-03 | UPDATE Conversation | ConversationHistory |
| AGT-04 | DELETE History | ConversationHistory |
| AGT-06 | COMPACT Context | ContextCompactor |
| AGT-07 | QUEUE Plan | PlanSession |
| AGT-08 | APPROVE Plan | PlanSession |
| AGT-09 | SPAWN Subagent | SubagentCoordinator |
| AGT-10 | COLLECT Subagent Result | SubagentCoordinator |
| AGT-11 | DELEGATE to Persona | PersonaManager |
| AGT-12 | LOAD Persona | PersonaManager |
| AGT-13 | SWITCH Persona | PersonaManager |
| AGT-14 | HANDLE Error | ErrorBoundary |
| AGT-15 | DISPATCH Safety Pipeline | SafetyCoordinator |

## Provider Group (PRV)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| PRV-01 | REGISTER Provider | LiteLLMProxy |
| PRV-02 | REQUEST Chat | Provider |
| PRV-03 | STREAM Chat | Provider |
| PRV-04 | SELECT Provider Backend | LiteLLMProxy |

## Config Group (CFG)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| CFG-01 | LOAD Config | ConfigLoader |
| CFG-02 | VALIDATE Config | ConfigLoader |
| CFG-03 | APPLY Layered Config | ConfigLoader |

## Session Group (SSN)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| SSN-01 | PERSIST Session | SessionStore |
| SSN-02 | READ Session | SessionStore |
| SSN-03 | LIST Sessions | SessionStore |
| SSN-04 | RESTORE Session | SessionStore |
| SSN-05 | SNAPSHOT Session | SessionVersioning |
| SSN-06 | REVERT Turn | SessionVersioning |
| SSN-07 | SEARCH Sessions | SessionSearch |
| SSN-08 | BRANCH Session | SessionFork |
| SSN-09 | DELETE Session | SessionStore |

## Safety Group (SAF)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| SAF-01 | CHECK Permission | SafetyCoordinator |
| SAF-02 | REQUEST Approval | SafetyCoordinator |
| SAF-03 | APPLY Safety Mode | SafetyCoordinator |

## Context Graph Group (CTX)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| CTX-01 | PROCESS Context | PipelineOrchestrator |
| CTX-02 | TRUNCATE Nodes | TruncationProcessor |
| CTX-03 | DISTILL Nodes | DistillationProcessor |
| CTX-04 | INJECT Context | InjectionProcessor |
| CTX-05 | COMPACT Nodes | CompactionProcessor |
| CTX-06 | TRACK Token Budget | TokenBudgetTracker |
| CTX-07 | SCORE Nodes | ContextPrioritizer |

## MCP Group (MCP)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| MCP-01 | CONNECT MCP Server | MCPClientRuntime |
| MCP-02 | DISCOVER MCP Tools | MCPDiscovery |
| MCP-03 | ADAPT MCP Tool | MCPToolAdapter |
| MCP-04 | EXPOSE nasim Tools | MCPServerRuntime |
| MCP-05 | REGISTER A2A Task | MCPServerRuntime |
| MCP-06 | RECEIVE A2A Result | MCPServerRuntime |

## Tool Group (TL)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| TL-01 | READ File | ReadFileTool |
| TL-02 | INSERT File | WriteFileTool |
| TL-03 | UPDATE File | EditFileTool |
| TL-04 | LIST Directory | DirTool |
| TL-05 | DISPATCH Shell Command | ShellTool |
| TL-06 | SEARCH Grep | GrepTool |
| TL-07 | SEARCH Glob | GlobTool |
| TL-08 | SEARCH Find | FindFileTool |
| TL-09 | FETCH Web Content | WebFetchTool |
| TL-10 | SEARCH Web | WebSearchTool |
| TL-11 | READ Git Status | GitTool |
| TL-12 | DISPATCH MCP Extension | MCPToolAdapter |
| TL-13 | READ LSP | LspTool |
| TL-14 | LIST Registered Tools | ToolRegistry |
| TL-15 | SPAWN Subagent | SubagentTool |
| TL-16 | INSERT Todo | TodoTool |
| TL-17 | UPDATE Todo | TodoTool |
| TL-18 | READ Todos | TodoTool |
| TL-19 | PERSIST Memory | MemoryTool |
| TL-20 | RECALL Memory | MemoryTool |
| TL-21 | INSERT Plan | PlanTool |
| TL-22 | UPDATE Plan | PlanTool |

## Hooks Group (HK)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| HK-01 | REGISTER Hook | HookManager |
| HK-02 | DISPATCH Pre-Tool Hook | HookManager |
| HK-03 | DISPATCH Post-Tool Hook | HookManager |
| HK-04 | DISPATCH Pre-LLM Hook | HookManager |
| HK-05 | DISPATCH Post-LLM Hook | HookManager |
| HK-06 | VALIDATE Hook Result | HookManager |

## Plugins Group (PLG)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| PLG-01 | DISCOVER Plugins | PluginLoader |
| PLG-02 | LOAD Manifest | PluginLoader |
| PLG-03 | REGISTER Plugin Tools | PluginLoader |
| PLG-04 | REGISTER Plugin Hooks | PluginLoader |
| PLG-05 | ENABLE Plugin | PluginLoader |
| PLG-06 | DISABLE Plugin | PluginLoader |

## Router Group (RTG)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| RTG-01 | SELECT Model | ModelRouter |
| RTG-02 | APPLY Fallback | ModelRouter |
| RTG-03 | CLASSIFY Task | ModelRouter |
| RTG-04 | SWITCH Model | ModelRouter |

## Observability Group (OBS)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| OBS-01 | STREAM Structured Log | StructuredLogger |
| OBS-02 | RECORD Metrics | MetricsCollector |
| OBS-03 | CORRELATE Trace | TraceCorrelator |
| OBS-04 | REDACT Sensitive | LogRedactor |
| OBS-05 | EXPOSE /metrics | MetricsCollector |
| OBS-06 | EXPORT OTLP | OTelExporter |

## Memory Group (MEM)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| MEM-01 | PERSIST Knowledge | MemoryStore |
| MEM-02 | RECALL Knowledge | MemoryStore |
| MEM-03 | SEARCH Knowledge | MemoryIndex |
| MEM-04 | SCOPE Knowledge | MemoryScope |

## Git Group (VCS)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| VCS-01 | READ Git Status | GitStatus |
| VCS-02 | INSERT Commit | GitCommit |
| VCS-03 | READ Diff | GitStatus |
| VCS-04 | AUTO-COMMIT | GitIntegration |

## Sandbox Group (SBX)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| SBX-01 | ISOLATE Command | SandboxExecutor |
| SBX-02 | APPLY Sandbox Policy | SandboxPolicy |
| SBX-03 | MONITOR Process | SandboxMonitor |
| SBX-04 | LIMIT Resources | ResourceLimiter |

## Repo Intelligence Group (RIM)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| RIM-01 | INDEX Codebase | RepoIntelligenceManager |
| RIM-02 | BUILD Symbol Graph | SymbolGraph |
| RIM-03 | RANK Results | RankingService |
| RIM-04 | INJECT RepoMap | RepoMapBuilder |
| RIM-05 | EMBED Code | EmbeddingAdapter |
| RIM-06 | SEARCH Semantic | SemanticSearchService |

## Edit Strategy Group (EDT)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| EDT-01 | SELECT Strategy | StrategySelector |
| EDT-02 | APPLY Search-Replace | SearchReplaceCoder |
| EDT-03 | APPLY Whole-File | WholeFileCoder |
| EDT-04 | APPLY Unified Diff | UnifiedDiffCoder |
| EDT-05 | APPLY Fenced Block | FencedBlockCoder |
| EDT-06 | APPLY Function-Level | FunctionLevelCoder |
| EDT-07 | APPLY Diff Sandbox | DiffSandboxCoder |
| EDT-08 | APPLY Architect | ArchitectCoder |
| EDT-09 | APPLY Inline Patch | InlinePatchCoder |
| EDT-10 | STAGE Diff | DiffSandboxManager |

## Evaluation Group (EVL)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| EVL-01 | EVALUATE Task | EvaluationEngine |
| EVL-02 | CHECK Task Completion | TaskEvaluator |
| EVL-03 | CHECK Success | SuccessCheckRunner |
| EVL-04 | VALIDATE With LLM | LLMReviewer |
| EVL-05 | VALIDATE Test Suite | TestRunner |
| EVL-06 | COORDINATE Retry | RetryCoordinator |
| EVL-07 | RECORD Quality Signal | EvaluationEngine |
| EVL-08 | DETECT Repetition | RepetitionDetector |
| EVL-09 | INJECT Turn Budget | TurnBudgetInjector |

## Wire Log Group (WRL)

| UC ID | Operation | Component Owner |
|-------|-----------|----------------|
| WRL-01 | APPEND Event | WireLog |
| WRL-02 | READ Log | WireReader |
| WRL-03 | SEEK Turn | WireLog |
| WRL-04 | FORK Session | SessionForkManager |
| WRL-05 | CHECKPOINT Turn | WireLog |

## Passive Policies (no behavioral UC)

| Data Structure | Owner Group | Role |
|----------------|-------------|------|
| CompactionPolicy | AGT (Agent) | Compaction rules: token threshold, message age, importance scoring |
| StrategyHeuristics | EDT (Edit Strategy) | Rules: edit_size, risk_level, file_type, complexity |

**Sub-UCs:** CTX-02..06, EVL-02..09, EDT-02..10 are sub-use-cases of their parent UCs (CTX-01, EVL-01, EDT-01). They inherit the same Component Owner as their parent.

## API↔Core UC Traceability

| API UC | Core UC | Delegation Path |
|--------|---------|-----------------|
| API-01 LIST Sessions | SSN-03 | ServerRouter → SessionStore.list() |
| API-02 CREATE Session | SSN-01 | ServerRouter → SessionStore.create() |
| API-03 GET Session | SSN-02 | ServerRouter → SessionStore.read() |
| API-04 UPDATE Session | SSN-01 | ServerRouter → SessionStore.update() |
| API-05 DELETE Session | SSN-09 | ServerRouter → SessionStore.delete() |
| API-06 DISPATCH Message | AGT-01 | ServerRouter → AgentOrchestrator.process() |
| API-07 LIST Messages | SSN-02 | ServerRouter → SessionStore.read_messages() |
| API-08 LIST Tools | TL-14 | ServerRouter → ToolRegistry.list() |
| API-09 GET Tool | TL-14 | ServerRouter → ToolRegistry.get() |
| API-10 GET Config | CFG-01 | ServerRouter → ConfigLoader.get() |
| API-11 UPDATE Config | CFG-03 | ServerRouter → ConfigLoader.update() |

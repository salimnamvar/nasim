# nasim — UC Inventory

| UC ID | Group | Operation | Component Owner |
|-------|-------|-----------|----------------|
| CLI-01 | CLI | PROCESS User Input | REPLSession |
| CLI-02 | CLI | DISPATCH Slash Command | SlashCommandHandler |
| CLI-03 | CLI | STREAM Output | Renderer |
| CLI-04 | CLI | READ CLI Arguments | ArgParser |
| CLI-05 | CLI | ENABLE Plan Mode | SlashCommandHandler |
| CLI-06 | CLI | REQUEST Approval | Renderer |
| CLI-07 | CLI | SWITCH Model | SlashCommandHandler |
| CLI-08 | CLI | LIST Sessions | SlashCommandHandler |
| AGT-01 | AGT | PROCESS User Task | AgentOrchestrator |
| AGT-02 | AGT | DISPATCH Tool Call | AgentOrchestrator |
| AGT-03 | AGT | UPDATE Conversation | ConversationHistory |
| AGT-04 | AGT | DELETE History | ConversationHistory |
| AGT-06 | AGT | COMPACT Context | ContextCompactor |
| AGT-07 | AGT | QUEUE Plan | PlanSession |
| AGT-08 | AGT | APPROVE Plan | PlanSession |
| AGT-09 | AGT | SPAWN Subagent | SubagentCoordinator |
| AGT-10 | AGT | COLLECT Subagent Result | SubagentCoordinator |
| AGT-11 | AGT | DELEGATE to Persona | PersonaManager |
| AGT-12 | AGT | LOAD Persona | PersonaManager |
| AGT-13 | AGT | SWITCH Persona | PersonaManager |
| AGT-14 | AGT | HANDLE Error | ErrorBoundary |
| AGT-15 | AGT | DISPATCH Safety Pipeline | SafetyCoordinator |
| PRV-01 | PRV | REGISTER Provider | LiteLLMProxy |
| PRV-02 | PRV | REQUEST Chat | Provider |
| PRV-03 | PRV | STREAM Chat | Provider |
| PRV-04 | PRV | SELECT Provider Backend | LiteLLMProxy |
| CFG-01 | CFG | LOAD Config | ConfigLoader |
| CFG-02 | CFG | VALIDATE Config | ConfigLoader |
| CFG-03 | CFG | APPLY Layered Config | ConfigLoader |
| SSN-01 | SSN | PERSIST Session | SessionStore |
| SSN-02 | SSN | READ Session | SessionStore |
| SSN-03 | SSN | LIST Sessions | SessionStore |
| SSN-04 | SSN | RESTORE Session | SessionStore |
| SSN-05 | SSN | SNAPSHOT Session | SessionVersioning |
| SSN-06 | SSN | REVERT Turn | SessionVersioning |
| SSN-07 | SSN | SEARCH Sessions | SessionSearch |
| SSN-08 | SSN | BRANCH Session | SessionFork |
| SSN-09 | SSN | DELETE Session | SessionStore |
| SAF-01 | SAF | CHECK Permission | SafetyCoordinator |
| SAF-02 | SAF | REQUEST Approval | SafetyCoordinator |
| SAF-03 | SAF | APPLY Safety Mode | SafetyCoordinator |
| CTX-01 | CTX | PROCESS Context | PipelineOrchestrator |
| CTX-02 | CTX | TRUNCATE Nodes | TruncationProcessor |
| CTX-03 | CTX | DISTILL Nodes | DistillationProcessor |
| CTX-04 | CTX | INJECT Context | InjectionProcessor |
| CTX-05 | CTX | COMPACT Nodes | CompactionProcessor |
| CTX-06 | CTX | TRACK Token Budget | TokenBudgetTracker |
| MCP-01 | MCP | CONNECT MCP Server | MCPClientRuntime |
| MCP-02 | MCP | DISCOVER MCP Tools | MCPDiscovery |
| MCP-03 | MCP | ADAPT MCP Tool | MCPToolAdapter |
| MCP-04 | MCP | EXPOSE nasim Tools | MCPServerRuntime |
| TL-01 | TL | READ File | ReadFileTool |
| TL-02 | TL | INSERT File | WriteFileTool |
| TL-03 | TL | UPDATE File | EditFileTool |
| TL-04 | TL | LIST Directory | DirTool |
| TL-05 | TL | DISPATCH Shell Command | ShellTool |
| TL-06 | TL | SEARCH Grep | GrepTool |
| TL-07 | TL | SEARCH Glob | GlobTool |
| TL-08 | TL | SEARCH Find | FindFileTool |
| TL-09 | TL | FETCH Web Content | WebFetchTool |
| TL-10 | TL | SEARCH Web | WebSearchTool |
| TL-11 | TL | READ Git Status | GitTool |
| TL-12 | TL | DISPATCH MCP Extension | MCPToolAdapter |
| TL-13 | TL | READ LSP | LspTool |
| TL-14 | TL | LIST Registered Tools | ToolRegistry |
| TL-15 | TL | SPAWN Subagent | SubagentTool |
| TL-16 | TL | INSERT Todo | TodoTool |
| TL-17 | TL | UPDATE Todo | TodoTool |
| TL-18 | TL | READ Todos | TodoTool |
| TL-19 | TL | PERSIST Memory | MemoryTool |
| TL-20 | TL | RECALL Memory | MemoryTool |
| TL-21 | TL | INSERT Plan | PlanTool |
| TL-22 | TL | UPDATE Plan | PlanTool |
| SRV-01 | SRV | LIST Sessions | ServerRouter |
| SRV-02 | SRV | INSERT Session | ServerRouter |
| SRV-03 | SRV | READ Session | ServerRouter |
| SRV-04 | SRV | UPDATE Session | ServerRouter |
| SRV-05 | SRV | DELETE Session | ServerRouter |
| SRV-06 | SRV | DISPATCH Message | ServerRouter |
| SRV-07 | SRV | LIST Messages | ServerRouter |
| SRV-08 | SRV | LIST Tools | ServerRouter |
| SRV-09 | SRV | READ Tool | ServerRouter |
| SRV-10 | SRV | READ Config | ServerRouter |
| SRV-11 | SRV | UPDATE Config | ServerRouter |
| HK-01 | HK | REGISTER Hook | HookManager |
| HK-02 | HK | DISPATCH Pre-Tool Hook | HookManager |
| HK-03 | HK | DISPATCH Post-Tool Hook | HookManager |
| HK-04 | HK | DISPATCH Pre-LLM Hook | HookManager |
| HK-05 | HK | DISPATCH Post-LLM Hook | HookManager |
| HK-06 | HK | VALIDATE Hook Result | HookManager |
| PLG-01 | PLG | DISCOVER Plugins | PluginLoader |
| PLG-02 | PLG | LOAD Manifest | PluginLoader |
| PLG-03 | PLG | REGISTER Plugin Tools | PluginLoader |
| PLG-04 | PLG | REGISTER Plugin Hooks | PluginLoader |
| PLG-05 | PLG | ENABLE Plugin | PluginLoader |
| PLG-06 | PLG | DISABLE Plugin | PluginLoader |
| RTG-01 | RTG | SELECT Model | ModelRouter |
| RTG-02 | RTG | APPLY Fallback | ModelRouter |
| RTG-03 | RTG | CLASSIFY Task | ModelRouter |
| RTG-04 | RTG | SWITCH Model | ModelRouter |
| OBS-01 | OBS | STREAM Structured Log | StructuredLogger |
| OBS-02 | OBS | RECORD Metrics | MetricsCollector |
| OBS-03 | OBS | CORRELATE Trace | TraceCorrelator |
| OBS-04 | OBS | REDACT Sensitive | LogRedactor |
| OBS-05 | OBS | EXPOSE /metrics | MetricsCollector |
| OBS-06 | OBS | EXPORT OTLP | OTelExporter |
| MEM-01 | MEM | PERSIST Knowledge | MemoryStore |
| MEM-02 | MEM | RECALL Knowledge | MemoryStore |
| MEM-03 | MEM | SEARCH Knowledge | MemoryIndex |
| MEM-04 | MEM | SCOPE Knowledge | MemoryScope |
| VCS-01 | VCS | READ Git Status | GitStatus |
| VCS-02 | VCS | INSERT Commit | GitCommit |
| VCS-03 | VCS | READ Diff | GitStatus |
| VCS-04 | VCS | AUTO-COMMIT | GitIntegration |
| SBX-01 | SBX | ISOLATE Command | SandboxExecutor |
| SBX-02 | SBX | APPLY Sandbox Policy | SandboxPolicy |
| SBX-03 | SBX | MONITOR Process | SandboxMonitor |
| SBX-04 | SBX | LIMIT Resources | ResourceLimiter |
| RIM-01 | RIM | INDEX Codebase | RepoIntelligenceManager |
| RIM-02 | RIM | BUILD Symbol Graph | SymbolGraph |
| RIM-03 | RIM | RANK Results | RankingService |
| RIM-04 | RIM | INJECT RepoMap | RepoMapBuilder |
| RIM-05 | RIM | EMBED Code | EmbeddingAdapter |
| RIM-06 | RIM | SEARCH Semantic | SemanticSearchService |
| EDT-01 | EDT | SELECT Strategy | StrategySelector |
| EDT-02 | EDT | APPLY Search-Replace | SearchReplaceCoder |
| EDT-03 | EDT | APPLY Whole-File | WholeFileCoder |
| EDT-04 | EDT | APPLY Unified Diff | UnifiedDiffCoder |
| EDT-05 | EDT | APPLY Fenced Block | FencedBlockCoder |
| EDT-06 | EDT | APPLY Function-Level | FunctionLevelCoder |
| EDT-07 | EDT | APPLY Diff Sandbox | DiffSandboxCoder |
| EDT-08 | EDT | APPLY Architect | ArchitectCoder |
| EDT-09 | EDT | APPLY Inline Patch | InlinePatchCoder |
| EDT-10 | EDT | STAGE Diff | DiffSandboxManager |
| EVL-01 | EVL | EVALUATE Task | EvaluationEngine |
| EVL-02 | EVL | CHECK Task Completion | TaskEvaluator |
| EVL-03 | EVL | CHECK Success | SuccessCheckRunner |
| EVL-04 | EVL | VALIDATE With LLM | LLMReviewer |
| EVL-05 | EVL | VALIDATE Test Suite | TestRunner |
| EVL-06 | EVL | COORDINATE Retry | RetryCoordinator |
| EVL-07 | EVL | RECORD Quality Signal | EvaluationEngine |
| EVL-08 | EVL | DETECT Repetition | RepetitionDetector |
| EVL-09 | EVL | INJECT Turn Budget | TurnBudgetInjector |
| WRL-01 | WRL | APPEND Event | WireLog |
| WRL-02 | WRL | READ Log | WireReader |
| WRL-03 | WRL | SEEK Turn | WireLog |
| WRL-04 | WRL | FORK Session | SessionForkManager |
| WRL-05 | WRL | CHECKPOINT Turn | WireLog |

## Passive Policies (no behavioral UC)

These are configuration/rule objects with no standalone behavioral use cases. They are NOT C4 components (no runtime behavior). They are invoked internally by their owning domain logic.

| Data Structure | Owner Group | Role |
|----------------|-------------|------|
| CompactionPolicy | AGT (Agent) | Compaction rules: token threshold, message age, importance scoring |
| StrategyHeuristics | EDT (Edit Strategy) | Rules: edit_size, risk_level, file_type, complexity |

**Sub-UCs:** CTX-02..06, EVL-02..09, EDT-02..10 are sub-use-cases of their parent UCs (CTX-01, EVL-01, EDT-01). They inherit the same Component Owner as their parent and are not listed separately to avoid inventory duplication.

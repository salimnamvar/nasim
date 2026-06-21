

--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/README.md ---

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
| SRV-02 | SRV | CREATE Session | ServerRouter |
| SRV-03 | SRV | READ Session | ServerRouter |
| SRV-04 | SRV | UPDATE Session | ServerRouter |
| SRV-05 | SRV | DELETE Session | ServerRouter |
| SRV-06 | SRV | SEND Message | ServerRouter |
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

These C4 components are configuration/rule objects with no standalone behavioral use cases. They are invoked internally by their owning domain logic.

| C4 Component | Owner Group | Role |
|--------------|-------------|------|
| CompactionPolicy | AGT (Agent) | Compaction rules: token threshold, message age, importance scoring |
| StrategyHeuristics | EDT (Edit Strategy) | Rules: edit_size, risk_level, file_type, complexity |

**Sub-UCs:** CTX-02..06, EVL-02..09, EDT-02..10 are sub-use-cases of their parent UCs (CTX-01, EVL-01, EDT-01). They inherit the same Component Owner as their parent and are not listed separately to avoid inventory duplication.



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_session.puml ---

@startuml uc_session

' ============================================================
' Title:     nasim — UC: Session Group
' Group:     SSN (Session)
' Boundary:  nasim code agent
' Purpose:   Session persistence, versioning, search, fork
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Session Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Session Group (SSN)" {
    usecase "**SSN-01 PERSIST Session**\n--\nSave session to storage" as SSN01
    usecase "**SSN-02 READ Session**\n--\nLoad session from storage" as SSN02
    usecase "**SSN-03 LIST Sessions**\n--\nList all saved sessions" as SSN03
    usecase "**SSN-04 RESTORE Session**\n--\nResume a previously saved session" as SSN04
    usecase "**SSN-05 SNAPSHOT Session**\n--\nCreate session state snapshot" as SSN05
    usecase "**SSN-06 REVERT Turn**\n--\nUndo last turn in session" as SSN06
    usecase "**SSN-07 SEARCH Sessions**\n--\nCross-session search via FTS5" as SSN07
    usecase "**SSN-08 BRANCH Session**\n--\nFork conversation from any point" as SSN08
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> SSN01
Agent --> SSN02
Agent --> SSN03
Agent --> SSN04
Agent --> SSN05
Agent --> SSN06
Agent --> SSN07
Agent --> SSN08

' ============================================================
' Relationships
' ============================================================

SSN04 ..> SSN02 : <<include>>
SSN05 ..> SSN01 : <<include>>
SSN06 ..> SSN02 : <<include>>
SSN08 ..> SSN01 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_server.puml ---

@startuml uc_server

' ============================================================
' Title:     nasim — UC: Server Group
' Group:     SRV (HTTP Server)
' Boundary:  nasim code agent
' Purpose:   RESTful API + SSE streaming for web/mobile/desktop clients
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Server Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

skinparam usecase<<extref>> {
  BackgroundColor #FFF9C4
  BorderColor #F9A825
  FontColor #5D4037
  BorderStyle dashed
}

' ============================================================
' Actors
' ============================================================

actor "HTTP Client" as HTTPClient <<system>>

' ============================================================
' Cross-Group External References
' ============================================================

usecase "SSN-01\nPERSIST Session\n[uc_session]" as SSN01_ext <<extref>>
usecase "SSN-02\nREAD Session\n[uc_session]" as SSN02_ext <<extref>>
usecase "SSN-03\nLIST Sessions\n[uc_session]" as SSN03_ext <<extref>>
usecase "SSN-09\nDELETE Session\n[uc_session]" as SSN09_ext <<extref>>

usecase "AGT-01\nPROCESS User Task\n[uc_agent]" as AGT01_ext <<extref>>

usecase "CFG-01\nLOAD Config\n[uc_config]" as CFG01_ext <<extref>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Server Group (SRV)" {
    usecase "**SRV-01 LIST Sessions**\n--\nList all sessions with pagination" as SRV01
    usecase "**SRV-02 CREATE Session**\n--\nCreate a new session" as SRV02
    usecase "**SRV-03 READ Session**\n--\nGet session details by ID" as SRV03
    usecase "**SRV-04 UPDATE Session**\n--\nUpdate session metadata" as SRV04
    usecase "**SRV-05 DELETE Session**\n--\nDelete a session" as SRV05
    usecase "**SRV-06 SEND Message**\n--\nSend message and receive SSE stream" as SRV06
    usecase "**SRV-07 LIST Messages**\n--\nList messages in a session" as SRV07
    usecase "**SRV-08 LIST Tools**\n--\nList registered tools" as SRV08
    usecase "**SRV-09 READ Tool**\n--\nGet tool details" as SRV09
    usecase "**SRV-10 READ Config**\n--\nGet current configuration" as SRV10
    usecase "**SRV-11 UPDATE Config**\n--\nUpdate configuration" as SRV11
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

HTTPClient --> SRV01
HTTPClient --> SRV02
HTTPClient --> SRV03
HTTPClient --> SRV04
HTTPClient --> SRV05
HTTPClient --> SRV06
HTTPClient --> SRV07
HTTPClient --> SRV08
HTTPClient --> SRV09
HTTPClient --> SRV10
HTTPClient --> SRV11

' ============================================================
' Relationships (Boundary -> External UC traceability)
' ============================================================

SRV01 ..> SSN03_ext : <<include>>
SRV02 ..> SSN01_ext : <<include>>
SRV03 ..> SSN02_ext : <<include>>
SRV04 ..> SSN01_ext : <<include>>
SRV05 ..> SSN09_ext : <<include>>
SRV06 ..> AGT01_ext : <<include>>
SRV07 ..> SSN02_ext : <<include>>
SRV10 ..> CFG01_ext : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_memory.puml ---

@startuml uc_memory

' ============================================================
' Title:     nasim — UC: Memory Group
' Group:     MEM (Memory)
' Boundary:  nasim code agent
' Purpose:   Cross-session knowledge persistence, retrieval, and RAG adapters
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Memory Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Memory Group (MEM)" {
    usecase "**MEM-01 PERSIST Knowledge**\n--\nStore knowledge entries with scope, key, content" as MEM01
    usecase "**MEM-02 RECALL Knowledge**\n--\nRetrieve knowledge from memory stores" as MEM02
    usecase "**MEM-03 SEARCH Knowledge**\n--\nFTS5 search across stored knowledge" as MEM03
    usecase "**MEM-04 SCOPE Knowledge**\n--\nIsolate knowledge by global, project, session scope" as MEM04
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> MEM01
Agent --> MEM02
Agent --> MEM03
Agent --> MEM04

' ============================================================
' Relationships
' ============================================================

MEM01 ..> MEM04 : <<include>>
MEM02 ..> MEM03 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_router.puml ---

@startuml uc_router

' ============================================================
' Title:     nasim — UC: Router Group
' Group:     RTG (Model Router)
' Boundary:  nasim code agent
' Purpose:   Model selection, fallback chains, task classification
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Router Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Router Group (RTG)" {
    usecase "**RTG-01 SELECT Model**\n--\nSelect optimal model for task" as RTG01
    usecase "**RTG-02 APPLY Fallback**\n--\nTrigger provider failover on error" as RTG02
    usecase "**RTG-03 CLASSIFY Task**\n--\nClassify task type for model selection" as RTG03
    usecase "**RTG-04 SWITCH Model**\n--\nSwitch model at runtime" as RTG04
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> RTG01
Agent --> RTG02
Agent --> RTG03
Agent --> RTG04

' ============================================================
' Relationships
' ============================================================

RTG01 ..> RTG03 : <<include>>
RTG01 ..> RTG02 : <<extend>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_repo_intelligence.puml ---

@startuml uc_repo_intelligence

' ============================================================
' Title:     nasim — UC: Repo Intelligence Group
' Group:     RIM (Repo Intelligence)
' Boundary:  nasim code agent
' Purpose:   Codebase intelligence: AST indexing, symbol graph, semantic search, repo mapping
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Repo Intelligence Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Repo Intelligence Group (RIM)" {
    usecase "**RIM-01 INDEX Codebase**\n--\nAST indexing via tree-sitter" as RIM01
    usecase "**RIM-02 BUILD Symbol Graph**\n--\nCross-file symbol reference graph" as RIM02
    usecase "**RIM-03 RANK Results**\n--\nPageRank ranking of code symbols" as RIM03
    usecase "**RIM-04 INJECT RepoMap**\n--\nGenerate token-budgeted repo-map" as RIM04
    usecase "**RIM-05 EMBED Code**\n--\nGenerate vector embeddings for code" as RIM05
    usecase "**RIM-06 SEARCH Semantic**\n--\nVector similarity search over embeddings" as RIM06
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> RIM01
Agent --> RIM02
Agent --> RIM03
Agent --> RIM04
Agent --> RIM05
Agent --> RIM06

' ============================================================
' Relationships
' ============================================================

RIM01 ..> RIM02 : <<include>>
RIM02 ..> RIM03 : <<include>>
RIM05 ..> RIM06 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_safety.puml ---

@startuml uc_safety

' ============================================================
' Title:     nasim — UC: Safety Group
' Group:     SAF (Safety)
' Boundary:  nasim code agent
' Purpose:   Permission gates, user approval, safety modes
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Safety Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

' ============================================================
' Actors
' ============================================================

actor "Developer" as Developer
actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Safety Group (SAF)" {
    usecase "**SAF-01 CHECK Permission**\n--\nValidate tool permission via PermissionGate" as SAF01
    usecase "**SAF-02 REQUEST Approval**\n--\nPrompt user for safety approval" as SAF02
    usecase "**SAF-03 APPLY Safety Mode**\n--\nApply safety mode: allow, ask, deny" as SAF03
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Developer --> SAF02
Agent --> SAF01
Agent --> SAF03

' ============================================================
' Relationships
' ============================================================

SAF03 ..> SAF01 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_evaluation.puml ---

@startuml uc_evaluation

' ============================================================
' Title:     nasim — UC: Evaluation Group
' Group:     EVL (Evaluation)
' Boundary:  nasim code agent
' Purpose:   Task evaluation: success checks, LLM review, retry coordination
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Evaluation Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Evaluation Group (EVL)" {
    usecase "**EVL-01 EVALUATE Task**\n--\nOrchestrate task evaluation: checks, scores, retries" as EVL01
    usecase "**EVL-02 CHECK Task Completion**\n--\nEvaluate task completion against success criteria" as EVL02
    usecase "**EVL-03 CHECK Success**\n--\nRun user-defined success checks" as EVL03
    usecase "**EVL-04 VALIDATE With LLM**\n--\nLLM-based code review and quality assessment" as EVL04
    usecase "**EVL-05 VALIDATE Test Suite**\n--\nRun project test suites" as EVL05
    usecase "**EVL-06 COORDINATE Retry**\n--\nCoordinate retry with backoff and escalation" as EVL06
    usecase "**EVL-07 RECORD Quality Signal**\n--\nProduce accept/reject with feedback" as EVL07
    usecase "**EVL-08 DETECT Repetition**\n--\nDetect repeated failures or loops" as EVL08
    usecase "**EVL-09 INJECT Turn Budget**\n--\nInject turn budget limits into context" as EVL09
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> EVL01
Agent --> EVL02
Agent --> EVL03
Agent --> EVL04
Agent --> EVL05
Agent --> EVL06
Agent --> EVL07
Agent --> EVL08
Agent --> EVL09

' ============================================================
' Relationships
' ============================================================

EVL01 ..> EVL02 : <<include>>
EVL01 ..> EVL03 : <<include>>
EVL01 ..> EVL04 : <<include>>
EVL01 ..> EVL05 : <<include>>
EVL01 ..> EVL06 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_wire_log.puml ---

@startuml uc_wire_log

' ============================================================
' Title:     nasim — UC: Wire Log Group
' Group:     WRL (Wire Log)
' Boundary:  nasim code agent
' Purpose:   Append-only event log, replay, session fork from wire
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Wire Log Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Wire Log Group (WRL)" {
    usecase "**WRL-01 APPEND Event**\n--\nAppend event to append-only log" as WRL01
    usecase "**WRL-02 READ Log**\n--\nRead and parse wire log entries" as WRL02
    usecase "**WRL-03 SEEK Turn**\n--\nRandom access via TurnIndex" as WRL03
    usecase "**WRL-04 FORK Session**\n--\nFork session from wire log replay" as WRL04
    usecase "**WRL-05 CHECKPOINT Turn**\n--\nIndex wire log entries by turn number" as WRL05
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> WRL01
Agent --> WRL02
Agent --> WRL03
Agent --> WRL04
Agent --> WRL05

' ============================================================
' Relationships
' ============================================================

WRL02 ..> WRL03 : <<include>>
WRL04 ..> WRL02 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_sandbox.puml ---

@startuml uc_sandbox

' ============================================================
' Title:     nasim — UC: Sandbox Group
' Group:     SBX (Sandbox)
' Boundary:  nasim code agent
' Purpose:   OS-level process isolation for shell and edit operations
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Sandbox Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Sandbox Group (SBX)" {
    usecase "**SBX-01 ISOLATE Command**\n--\nExecute command in isolated OS environment" as SBX01
    usecase "**SBX-02 APPLY Sandbox Policy**\n--\nEnforce network, filesystem, exec restrictions" as SBX02
    usecase "**SBX-03 MONITOR Process**\n--\nMonitor process, enforce timeout and resource limits" as SBX03
    usecase "**SBX-04 LIMIT Resources**\n--\nEnforce CPU, memory, and disk quotas" as SBX04
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> SBX01
Agent --> SBX02
Agent --> SBX03
Agent --> SBX04

' ============================================================
' Relationships
' ============================================================

SBX01 ..> SBX02 : <<include>>
SBX01 ..> SBX03 : <<include>>
SBX01 ..> SBX04 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_cli.puml ---

@startuml uc_cli

' ============================================================
' Title:     nasim — UC: CLI Group
' Group:     CLI (CLI Layer)
' Boundary:  nasim code agent
' Purpose:   REPL, argument parsing, slash commands, rich rendering
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — CLI Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam usecase<<extref>> {
  BackgroundColor #FFF9C4
  BorderColor #F9A825
  FontColor #5D4037
  BorderStyle dashed
}

' ============================================================
' Actors
' ============================================================

actor "Developer" as Developer
actor "Agent" as Agent <<system>>

' ============================================================
' Cross-Group External References
' ============================================================

usecase "SSN-03\nLIST Sessions\n[uc_session]" as SSN03_ext <<extref>>
usecase "RTG-04\nSWITCH Model\n[uc_router]" as RTG04_ext <<extref>>
usecase "AGT-07\nQUEUE Plan\n[uc_agent]" as AGT07_ext <<extref>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "CLI Group (CLI)" {
    usecase "**CLI-01 PROCESS User Input**\n--\nREPL loop, input handling, slash command dispatch" as CLI01
    usecase "**CLI-02 DISPATCH Slash Command**\n--\nMap /cmd strings to agent actions" as CLI02
    usecase "**CLI-03 STREAM Output**\n--\nRender AgentEvents to terminal" as CLI03
    usecase "**CLI-04 READ CLI Arguments**\n--\nParse CLI args with layered config overrides" as CLI04
    usecase "**CLI-05 ENABLE Plan Mode**\n--\nToggle plan mode on/off" as CLI05
    usecase "**CLI-06 REQUEST Approval**\n--\nPrompt user for safety approval" as CLI06
    usecase "**CLI-07 SWITCH Model**\n--\nSwitch model at runtime" as CLI07
    usecase "**CLI-08 LIST Sessions**\n--\nList saved sessions" as CLI08
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Developer --> CLI01
Developer --> CLI02
Developer --> CLI05
Developer --> CLI07
Developer --> CLI08
Agent --> CLI03
Agent --> CLI04
Agent --> CLI06

' ============================================================
' Relationships
' ============================================================

CLI01 ..> CLI03 : <<include>>
CLI01 ..> CLI04 : <<include>>
CLI01 ..> CLI06 : <<extend>>
CLI07 ..> RTG04_ext : <<include>>
CLI05 ..> AGT07_ext : <<include>>
CLI08 ..> SSN03_ext : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_agent.puml ---

@startuml uc_agent

' ============================================================
' Title:     nasim — UC: Agent Group
' Group:     AGT (Agent Core)
' Boundary:  nasim code agent
' Purpose:   Core agentic loop, permissions, context, plans, subagents
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Agent Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

skinparam usecase<<extref>> {
  BackgroundColor #FFF9C4
  BorderColor #F9A825
  FontColor #5D4037
  BorderStyle dashed
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' Cross-Group External References
' ============================================================

usecase "SAF-01\nCHECK Permission\n[uc_safety]" as SAF01_ext <<extref>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Agent Group (AGT)" {
    usecase "**AGT-01 PROCESS User Task**\n--\nCore agentic loop: provider call, tool dispatch" as AGT01
    usecase "**AGT-02 DISPATCH Tool Call**\n--\nRoute tool call to registry" as AGT02
    usecase "**AGT-03 UPDATE Conversation**\n--\nManage message list and token count" as AGT03
    usecase "**AGT-04 DELETE History**\n--\nReset conversation history" as AGT04
    usecase "**AGT-06 COMPACT Context**\n--\nSummarize old exchanges via secondary LLM" as AGT06
    usecase "**AGT-07 QUEUE Plan**\n--\nHold queued tool calls in plan mode" as AGT07
    usecase "**AGT-08 APPROVE Plan**\n--\nDrain queued plan calls" as AGT08
    usecase "**AGT-09 SPAWN Subagent**\n--\nCreate child agent with restricted tools" as AGT09
    usecase "**AGT-10 COLLECT Subagent Result**\n--\nGather results from completed child agents" as AGT10
    usecase "**AGT-11 DELEGATE to Persona**\n--\nAssign tasks to specialized persona roles" as AGT11
    usecase "**AGT-12 LOAD Persona**\n--\nLoad persona configuration" as AGT12
    usecase "**AGT-13 SWITCH Persona**\n--\nSwitch to different persona at runtime" as AGT13
    usecase "**AGT-14 HANDLE Error**\n--\nStructured error handling with recovery" as AGT14
    usecase "**AGT-15 DISPATCH Safety Pipeline**\n--\nRun permission, injection, egress checks" as AGT15
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> AGT01
Agent --> AGT04
Agent --> AGT07
Agent --> AGT11
Agent --> AGT12
Agent --> AGT13
Agent --> AGT15
Agent --> SAF01_ext

' ============================================================
' Relationships
' ============================================================

AGT01 ..> AGT02 : <<include>>
AGT01 ..> AGT03 : <<include>>
AGT02 ..> SAF01_ext : <<include>>
AGT15 ..> AGT02 : <<include>>
AGT01 ..> AGT06 : <<extend>>
AGT07 ..> AGT08 : <<extend>>
AGT01 ..> AGT09 : <<extend>>
AGT09 ..> AGT10 : <<include>>
AGT01 ..> AGT14 : <<extend>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_provider.puml ---

@startuml uc_provider

' ============================================================
' Title:     nasim — UC: Provider Group
' Group:     PRV (Provider Abstraction)
' Boundary:  nasim code agent
' Purpose:   LLM provider abstraction via litellm proxy (100+ providers)
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Provider Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Provider Group (PRV)" {
    usecase "**PRV-01 REGISTER Provider**\n--\nInitialize provider from config" as PRV01
    usecase "**PRV-02 REQUEST Chat**\n--\nSend chat request to LLM provider" as PRV02
    usecase "**PRV-03 STREAM Chat**\n--\nStream chat response from LLM provider" as PRV03
    usecase "**PRV-04 SELECT Provider Backend**\n--\nSelect provider backend from config" as PRV04
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> PRV01
Agent --> PRV02
Agent --> PRV03
Agent --> PRV04

' ============================================================
' Relationships
' ============================================================

PRV04 ..> PRV01 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_tools.puml ---

@startuml uc_tools

' ============================================================
' Title:     nasim — UC: Tool Group
' Group:     TL (Tool Layer)
' Boundary:  nasim code agent
' Purpose:   All tool implementations: file, search, shell, web, git, lsp, subagent, memory, plan
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Tool Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Tool Group (TL)" {
    usecase "**TL-01 READ File**\n--\nRead file contents with offset/limit" as TL01
    usecase "**TL-02 INSERT File**\n--\nCreate or overwrite files" as TL02
    usecase "**TL-03 UPDATE File**\n--\nReplace exact strings in files" as TL03
    usecase "**TL-04 LIST Directory**\n--\nList directory contents" as TL04
    usecase "**TL-05 DISPATCH Shell Command**\n--\nExecute shell command via sandbox" as TL05
    usecase "**TL-06 SEARCH Grep**\n--\nSearch file contents by regex" as TL06
    usecase "**TL-07 SEARCH Glob**\n--\nFind files by glob pattern" as TL07
    usecase "**TL-08 SEARCH Find**\n--\nFind files by name pattern" as TL08
    usecase "**TL-09 FETCH Web Content**\n--\nFetch URL content as markdown" as TL09
    usecase "**TL-10 SEARCH Web**\n--\nSearch the web for information" as TL10
    usecase "**TL-11 READ Git Status**\n--\nGit status, diff, commit operations" as TL11
    usecase "**TL-12 DISPATCH MCP Extension**\n--\nInvoke MCP extension tools" as TL12
    usecase "**TL-13 READ LSP**\n--\nLSP operations: hover, definition, references" as TL13
    usecase "**TL-14 LIST Registered Tools**\n--\nList all registered tools" as TL14
    usecase "**TL-15 SPAWN Subagent**\n--\nSpawn child agent via SubagentCoordinator" as TL15
    usecase "**TL-16 INSERT Todo**\n--\nCreate task tracking entry" as TL16
    usecase "**TL-17 UPDATE Todo**\n--\nUpdate task tracking entry" as TL17
    usecase "**TL-18 READ Todos**\n--\nList task tracking entries" as TL18
    usecase "**TL-19 PERSIST Memory**\n--\nStore cross-session knowledge" as TL19
    usecase "**TL-20 RECALL Memory**\n--\nRetrieve cross-session knowledge" as TL20
    usecase "**TL-21 INSERT Plan**\n--\nCreate plan entry" as TL21
    usecase "**TL-22 UPDATE Plan**\n--\nUpdate plan entry" as TL22
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> TL01
Agent --> TL02
Agent --> TL03
Agent --> TL04
Agent --> TL05
Agent --> TL06
Agent --> TL07
Agent --> TL08
Agent --> TL09
Agent --> TL10
Agent --> TL11
Agent --> TL12
Agent --> TL13
Agent --> TL14
Agent --> TL15
Agent --> TL16
Agent --> TL17
Agent --> TL18
Agent --> TL19
Agent --> TL20
Agent --> TL21
Agent --> TL22

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_git.puml ---

@startuml uc_git

' ============================================================
' Title:     nasim — UC: Git Group
' Group:     VCS (Git Integration)
' Boundary:  nasim code agent
' Purpose:   Version control awareness: status, diff, commit
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Git Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Git Group (VCS)" {
    usecase "**VCS-01 READ Git Status**\n--\nRead working tree status and staged changes" as VCS01
    usecase "**VCS-02 INSERT Commit**\n--\nCreate commits with conventional messages" as VCS02
    usecase "**VCS-03 READ Diff**\n--\nRead diff between working tree and HEAD" as VCS03
    usecase "**VCS-04 AUTO-COMMIT**\n--\nAuto-commit after file edits" as VCS04
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> VCS01
Agent --> VCS02
Agent --> VCS03
Agent --> VCS04

' ============================================================
' Relationships
' ============================================================

VCS04 ..> VCS02 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_overview.puml ---

@startuml uc_overview

' ============================================================
' Title:     nasim — UC: Overview
' Group:     ALL (All Groups)
' Boundary:  nasim code agent
' Purpose:   Cross-cutting view of all UC groups and actor interactions
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — UC Overview

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

skinparam usecase<<extref>> {
  BackgroundColor #FFF9C4
  BorderColor #F9A825
  FontColor #5D4037
  BorderStyle dashed
}

' ============================================================
' Actors
' ============================================================

actor "Developer" as Developer
actor "HTTP Client" as HTTPClient <<system>>
actor "MCP Client" as MCPClient <<system>>
actor "Observability Platform" as Platform <<system>>
actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {

  package "CLI (CLI)" {
    usecase "CLI-01\nPROCESS User Input\n[uc_cli]" as UC_CLI <<extref>>
  }

  package "Agent Core (AGT)" {
    usecase "AGT-01\nPROCESS User Task\n[uc_agent]" as UC_AGT <<extref>>
  }

  package "Provider (PRV)" {
    usecase "PRV-01\nREGISTER Provider\n[uc_provider]" as UC_PRV <<extref>>
  }

  package "Tools (TL)" {
    usecase "TL-01\nREAD File\n[uc_tools]" as UC_TL <<extref>>
  }

  package "MCP (MCP)" {
    usecase "MCP-01\nCONNECT MCP Server\n[uc_mcp]" as UC_MCP <<extref>>
  }

  package "Config (CFG)" {
    usecase "CFG-01\nLOAD Config\n[uc_config]" as UC_CFG <<extref>>
  }

  package "Session (SSN)" {
    usecase "SSN-01\nPERSIST Session\n[uc_session]" as UC_SSN <<extref>>
  }

  package "Server (SRV)" {
    usecase "SRV-01\nLIST Sessions\n[uc_server]" as UC_SRV <<extref>>
  }

  package "Hooks (HK)" {
    usecase "HK-01\nREGISTER Hook\n[uc_hooks]" as UC_HK <<extref>>
  }

  package "Plugins (PLG)" {
    usecase "PLG-01\nDISCOVER Plugins\n[uc_plugins]" as UC_PLG <<extref>>
  }

  package "Safety (SAF)" {
    usecase "SAF-01\nCHECK Permission\n[uc_safety]" as UC_SAF <<extref>>
  }

  package "Router (RTG)" {
    usecase "RTG-01\nSELECT Model\n[uc_router]" as UC_RTG <<extref>>
  }

  package "Observability (OBS)" {
    usecase "OBS-01\nSTREAM Structured Log\n[uc_observability]" as UC_OBS <<extref>>
  }

  package "Memory (MEM)" {
    usecase "MEM-01\nPERSIST Knowledge\n[uc_memory]" as UC_MEM <<extref>>
  }

  package "Git (VCS)" {
    usecase "VCS-01\nREAD Git Status\n[uc_git]" as UC_VCS <<extref>>
  }

  package "Sandbox (SBX)" {
    usecase "SBX-01\nISOLATE Command\n[uc_sandbox]" as UC_SBX <<extref>>
  }

  package "Repo Intelligence (RIM)" {
    usecase "RIM-01\nINDEX Codebase\n[uc_repo_intelligence]" as UC_RIM <<extref>>
  }

  package "Edit Strategy (EDT)" {
    usecase "EDT-01\nSELECT Strategy\n[uc_edit_strategy]" as UC_EDT <<extref>>
  }

  package "Evaluation (EVL)" {
    usecase "EVL-01\nEVALUATE Task\n[uc_evaluation]" as UC_EVL <<extref>>
  }

  package "Wire Log (WRL)" {
    usecase "WRL-01\nAPPEND Event\n[uc_wire_log]" as UC_WRL <<extref>>
  }

  package "Context Graph (CTX)" {
    usecase "CTX-01\nPROCESS Context\n[uc_context]" as UC_CTX <<extref>>
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Developer --> UC_CLI
Developer --> UC_SAF

HTTPClient --> UC_SRV
HTTPClient --> UC_OBS

MCPClient --> UC_MCP

Platform --> UC_OBS

Agent --> UC_AGT
Agent --> UC_PRV
Agent --> UC_TL
Agent --> UC_MCP
Agent --> UC_CFG
Agent --> UC_SSN
Agent --> UC_HK
Agent --> UC_PLG
Agent --> UC_SAF
Agent --> UC_RTG
Agent --> UC_OBS
Agent --> UC_MEM
Agent --> UC_VCS
Agent --> UC_SBX
Agent --> UC_RIM
Agent --> UC_EDT
Agent --> UC_EVL
Agent --> UC_WRL
Agent --> UC_CTX

' ============================================================
' Key Relationships
' ============================================================

UC_CLI ..> UC_AGT : <<include>>
UC_AGT ..> UC_RTG : <<include>>
UC_AGT ..> UC_CTX : <<include>>
UC_AGT ..> UC_EDT : <<extend>>
UC_AGT ..> UC_EVL : <<extend>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_hooks.puml ---

@startuml uc_hooks

' ============================================================
' Title:     nasim — UC: Hooks Group
' Group:     HK (Hooks)
' Boundary:  nasim code agent
' Purpose:   Pre/post hooks for tool use and LLM calls
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Hooks Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Hooks Group (HK)" {
    usecase "**HK-01 REGISTER Hook**\n--\nRegister hook with name, event type, handler, priority" as HK01
    usecase "**HK-02 DISPATCH Pre-Tool Hook**\n--\nExecute hook before tool use" as HK02
    usecase "**HK-03 DISPATCH Post-Tool Hook**\n--\nExecute hook after tool use" as HK03
    usecase "**HK-04 DISPATCH Pre-LLM Hook**\n--\nExecute hook before LLM call" as HK04
    usecase "**HK-05 DISPATCH Post-LLM Hook**\n--\nExecute hook after LLM call" as HK05
    usecase "**HK-06 VALIDATE Hook Result**\n--\nValidate hook result: allow, deny, modify" as HK06
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> HK01
Agent --> HK02
Agent --> HK03
Agent --> HK04
Agent --> HK05
Agent --> HK06

' ============================================================
' Relationships
' ============================================================

HK02 ..> HK06 : <<include>>
HK03 ..> HK06 : <<include>>
HK04 ..> HK06 : <<include>>
HK05 ..> HK06 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_config.puml ---

@startuml uc_config

' ============================================================
' Title:     nasim — UC: Config Group
' Group:     CFG (Configuration)
' Boundary:  nasim code agent
' Purpose:   Config loading, validation, and layered overrides
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Config Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Config Group (CFG)" {
    usecase "**CFG-01 LOAD Config**\n--\nLoad global YAML, project YAML, env vars, CLI flags" as CFG01
    usecase "**CFG-02 VALIDATE Config**\n--\nValidate config schema at load time" as CFG02
    usecase "**CFG-03 APPLY Layered Config**\n--\nMerge layered config with precedence rules" as CFG03
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> CFG01
Agent --> CFG02
Agent --> CFG03

' ============================================================
' Relationships
' ============================================================

CFG01 ..> CFG03 : <<include>>
CFG03 ..> CFG02 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_observability.puml ---

@startuml uc_observability

' ============================================================
' Title:     nasim — UC: Observability Group
' Group:     OBS (Observability)
' Boundary:  nasim code agent
' Purpose:   Emit-only structured logging, metrics, trace correlation (tenas pattern)
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Observability Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "HTTP Client" as HTTPClient <<system>>
actor "Observability Platform" as Platform <<system>>
actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Observability Group (OBS)" {
    usecase "**OBS-01 STREAM Structured Log**\n--\nWrite structured JSON records to stdout" as OBS01
    usecase "**OBS-02 RECORD Metrics**\n--\nIncrement counters and observe histograms" as OBS02
    usecase "**OBS-03 CORRELATE Trace**\n--\nGenerate and bind trace/span ids per entrypoint" as OBS03
    usecase "**OBS-04 REDACT Sensitive**\n--\nStrip secrets before any emission" as OBS04
    usecase "**OBS-05 EXPOSE /metrics**\n--\nServe /metrics endpoint for pull scrape" as OBS05
    usecase "**OBS-06 EXPORT OTLP**\n--\nExport traces/metrics via OTLP (optional)" as OBS06
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

HTTPClient --> OBS05
Platform --> OBS05
Agent --> OBS01
Agent --> OBS02
Agent --> OBS03
Agent --> OBS04
Agent --> OBS06

' ============================================================
' Relationships
' ============================================================

OBS02 ..> OBS03 : <<include>>
OBS04 ..> OBS01 : <<extend>>
OBS04 ..> OBS02 : <<extend>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_edit_strategy.puml ---

@startuml uc_edit_strategy

' ============================================================
' Title:     nasim — UC: Edit Strategy Group
' Group:     EDT (Edit Strategy)
' Boundary:  nasim code agent
' Purpose:   Polymorphic edit strategies with sandboxed diff staging
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Edit Strategy Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Edit Strategy Group (EDT)" {
    usecase "**EDT-01 SELECT Strategy**\n--\nSelect optimal edit strategy for model" as EDT01
    usecase "**EDT-02 APPLY Search-Replace**\n--\nSearch-and-replace edit with fuzzy matching" as EDT02
    usecase "**EDT-03 APPLY Whole-File**\n--\nWhole file rewrite strategy" as EDT03
    usecase "**EDT-04 APPLY Unified Diff**\n--\nUnified diff format edit" as EDT04
    usecase "**EDT-05 APPLY Fenced Block**\n--\nFenced code block format edit" as EDT05
    usecase "**EDT-06 APPLY Function-Level**\n--\nAST-targeted function replacement" as EDT06
    usecase "**EDT-07 APPLY Diff Sandbox**\n--\nSandboxed diff with validation" as EDT07
    usecase "**EDT-08 APPLY Architect**\n--\nMulti-file architectural edit" as EDT08
    usecase "**EDT-09 APPLY Inline Patch**\n--\napply-patch format edit" as EDT09
    usecase "**EDT-10 STAGE Diff**\n--\nStage edits for review before apply" as EDT10
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> EDT01

' ============================================================
' Relationships
' ============================================================

EDT01 ..> EDT02 : <<include>>
EDT01 ..> EDT03 : <<include>>
EDT01 ..> EDT04 : <<include>>
EDT01 ..> EDT05 : <<include>>
EDT01 ..> EDT06 : <<include>>
EDT01 ..> EDT07 : <<include>>
EDT01 ..> EDT08 : <<include>>
EDT01 ..> EDT09 : <<include>>
EDT07 ..> EDT10 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_plugins.puml ---

@startuml uc_plugins

' ============================================================
' Title:     nasim — UC: Plugins Group
' Group:     PLG (Plugins)
' Boundary:  nasim code agent
' Purpose:   Plugin discovery, loading, dynamic tool/hook registration
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Plugins Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Plugins Group (PLG)" {
    usecase "**PLG-01 DISCOVER Plugins**\n--\nDiscover plugins from ~/.nasim/plugins/" as PLG01
    usecase "**PLG-02 LOAD Manifest**\n--\nParse plugin manifest metadata" as PLG02
    usecase "**PLG-03 REGISTER Plugin Tools**\n--\nRegister plugin tools with ToolRegistry" as PLG03
    usecase "**PLG-04 REGISTER Plugin Hooks**\n--\nRegister plugin hooks with HookManager" as PLG04
    usecase "**PLG-05 ENABLE Plugin**\n--\nEnable a plugin" as PLG05
    usecase "**PLG-06 DISABLE Plugin**\n--\nDisable a plugin" as PLG06
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> PLG01
Agent --> PLG02
Agent --> PLG03
Agent --> PLG04
Agent --> PLG05
Agent --> PLG06

' ============================================================
' Relationships
' ============================================================

PLG01 ..> PLG02 : <<include>>
PLG02 ..> PLG03 : <<include>>
PLG02 ..> PLG04 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_context.puml ---

@startuml uc_context

' ============================================================
' Title:     nasim — UC: Context Graph Group
' Group:     CTX (Context Management)
' Boundary:  nasim code agent
' Purpose:   Context pipeline: graph construction, truncation, distillation, injection, compaction
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — Context Graph Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "Context Graph Group (CTX)" {
    usecase "**CTX-01 PROCESS Context**\n--\nOrchestrate context pipeline stages" as CTX01
    usecase "**CTX-02 TRUNCATE Nodes**\n--\nTruncate context nodes to fit token budget" as CTX02
    usecase "**CTX-03 DISTILL Nodes**\n--\nSummarize long context nodes via LLM" as CTX03
    usecase "**CTX-04 INJECT Context**\n--\nInject memory and repo-map into graph" as CTX04
    usecase "**CTX-05 COMPACT Nodes**\n--\nMerge redundant context nodes" as CTX05
    usecase "**CTX-06 TRACK Token Budget**\n--\nTrack cumulative token usage" as CTX06
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

Agent --> CTX01

' ============================================================
' Relationships
' ============================================================

CTX01 ..> CTX02 : <<include>>
CTX01 ..> CTX03 : <<include>>
CTX01 ..> CTX04 : <<include>>
CTX01 ..> CTX05 : <<include>>
CTX01 ..> CTX06 : <<include>>

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/UC/uc_mcp.puml ---

@startuml uc_mcp

' ============================================================
' Title:     nasim — UC: MCP Group
' Group:     MCP (Model Context Protocol)
' Boundary:  nasim code agent
' Purpose:   MCP as first-class subsystem: client/server runtime, tool adapter, discovery
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/ENTITIES.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — MCP Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

' ============================================================
' Actors
' ============================================================

actor "MCP Client" as MCPClient <<system>>
actor "Agent" as Agent <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "MCP Group (MCP)" {
    usecase "**MCP-01 CONNECT MCP Server**\n--\nConnect to external MCP server via stdio/SSE" as MCP01
    usecase "**MCP-02 DISCOVER MCP Tools**\n--\nDiscover and register tools from MCP servers" as MCP02
    usecase "**MCP-03 ADAPT MCP Tool**\n--\nWrap MCP tools into nasim Tool ABC format" as MCP03
    usecase "**MCP-04 EXPOSE nasim Tools**\n--\nExpose nasim tools to external MCP clients" as MCP04
  }
}

' ============================================================
' Actor -> Use Case Associations
' ============================================================

MCPClient --> MCP04
Agent --> MCP01
Agent --> MCP02
Agent --> MCP03

' ============================================================
' Relationships
' ============================================================

MCP01 ..> MCP02 : <<include>>
MCP02 ..> MCP03 : <<include>>

@enduml


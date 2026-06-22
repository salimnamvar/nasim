

--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/README.md ---

# nasim — SQ Inventory

Sequence diagrams organised by UC group. 149 diagrams across 21 groups.
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## Groups

| Group | Boundary | Diagrams | Subdirectory |
| ----- | -------- | :------: | ------------ |
| AGT | Agent Core — orchestrator, history, permissions, plans, subagents | 15 | `AGT/` |
| CLI | CLI Layer — REPL, parsing, rendering | 8 | `CLI/` |
| CFG | Configuration — config loading and validation | 3 | `CFG/` |
| CTX | Context Management — token counting and compaction | 6 | `CTX/` |
| EDT | Edit Strategy — polymorphic edit strategies | 10 | `EDT/` |
| EVL | Evaluation — task evaluation and quality checks | 9 | `EVL/` |
| HK | Hooks — pre/post hooks for tool and LLM lifecycle | 6 | `HK/` |
| MCP | Model Context Protocol — client/server extension tools | 4 | `MCP/` |
| MEM | Memory — cross-session knowledge persistence | 4 | `MEM/` |
| OBS | Observability — structured logging, metrics, trace correlation | 6 | `OBS/` |
| PLG | Plugins — plugin discovery, loading, registration | 6 | `PLG/` |
| PRV | Provider Layer — provider abstraction, chat, streaming | 4 | `PRV/` |
| RIM | Repo Intelligence — codebase indexing, symbol graphs, embedding | 6 | `RIM/` |
| RTG | Model Router — model selection, fallback, routing | 4 | `RTG/` |
| SAF | Safety — permission checks and user approval | 3 | `SAF/` |
| SBX | Sandbox — OS-level process isolation | 4 | `SBX/` |
| SRV | HTTP Server — REST API, SSE streaming | 11 | `SRV/` |
| SSN | Session — persistence and resumption | 9 | `SSN/` |
| TL | Tool Layer — all tool implementations | 22 | `TL/` |
| VCS | Version Control — Git status, diff, commit | 4 | `VCS/` |
| WRL | Wire Log — append-only event store, fork, checkpoint | 5 | `WRL/` |

**Total: 149 SQ diagrams across 21 groups**

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version, source, review status
2. **Lifelines** — Actor (Developer/HTTPClient/MCPClientRuntime) + full entry chain + participants grouped by layer (colored boxes)
3. **Intro Note** — Scope, Preconditions, Contexts, Excludes, Rollback, Design, Classification, Returns
4. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks; all messages use RoD method names
5. **Summary Note** — Flow (with UC_ID prefix), State transitions, Success (with HTTP codes), Failure (with HTTP codes and recovery)

### Key Rules (updated 2026-06-22)

- **ALL diagrams must have actors** — even Process Decomposition diagrams show who triggers the sequence
- **Full entry chain required** — Actor → Interface → Core Component → Target
- **RoD method names** — UC_ID METHOD ResourceName(params) format on all messages
- **Returns section** — mandatory in intro note with success/failure response codes
- **Failure propagation** — all failure paths propagate back through entry chain to actor

## Meta-Software Designer Audit (2026-06-21)

Cross-referencing all 6 reference agent prompt outputs (dee.md, mis.md, gro.md, qwe.md, cop.md, gem.md) against the existing 149 SQ diagrams. Key findings and fixes applied:

### Critical Fixes Applied

| Diagram | Violation | Fix |
|---------|-----------|-----|
| SRV-06 | Title "DISPATCH" mismatches UC catalog "SEND"; phantom `AgentService` lifeline | Renamed to SEND; removed AgentService; routes ServerRouter → AgentOrchestrator directly |
| MCP-01 | Missing actor; no ErrorBoundary; no AIP-193 errors | Added Developer actor + CLI entry chain; added ErrorBoundary; added AIP-193 error mapping |
| CLI-01 | Inlined agent loop logic instead of `ref` blocks | Replaced inlined logic with `ref` blocks for AGT-01, CLI-02, OBS-01 |
| AGT-02 | God Object: AgentOrchestrator calls PermissionGate directly | Delegated to SafetyCoordinator (AGT-15) which composes PermissionGate |
| AGT-05 | Orphan SQ with no UC entry | Reclassified as Process Decomposition (internal step of AGT-15) |
| TL-01 | Incorrect "Primary Orchestrator" classification; invalid actor | Changed to Process Decomposition; removed actor and CLI entry chain |
| PRV-02 | Incorrect "Primary Orchestrator" classification; invalid actor | Changed to UC-level Sub-flow; removed actor |

### Standards Enforced

- **CSR Pattern**: Controller (CLI/HTTP) → Service (Agent) → Repository (Tools/Session). No God Objects.
- **ErrorBoundary**: All failure paths terminate at ErrorBoundary (AGT-14). No inline error handling.
- **SafetyCoordinator**: All safety checks delegated to SafetyCoordinator (AGT-15). No direct PermissionGate calls from AgentOrchestrator.
- **SM State Colors**: `hnote` blocks with hex colors at state transition points during diagram flow.
- **ROD AIP-193**: All server-facing failure paths use `{error: {code, message, status}}` format.
- **ref Frames**: Cross-cutting concerns (OBS-01, AGT-15, HK-04/05) use `ref` blocks, never inlined.
- **Actor Rules**: ALL diagrams (including Process Decomposition) require actor + full entry chain. The actor shows who triggers the sequence.
- **RoD Method Names**: All message labels use UC_ID METHOD ResourceName(params) format.
- **Returns Section**: All intro notes include Returns: field with success/failure response codes.
- **Failure Propagation**: All failure paths propagate back through the full entry chain to the actor.

### UC↔SQ Mapping

148 UCs in catalog, 149 SQ diagrams. AGT-05 is an orphan (no UC entry) — reclassified as Process Decomposition.

---

## Design Chain Refinement Audit (2026-06-21)

Full C4 → UC → SM → SQ audit using CAR framework. See `docs/audit/audit.2026.06.21.design-chain.car.md`.

### Fixes Applied in This Audit

| Diagram | Violation | Fix |
|---------|-----------|-----|
| EDT-10 | Actor present in Process Decomposition; participant names mismatch C4; title "Stage Diff" wrong case; note references "edt04" | Removed actor; renamed to DiffSandboxManager/EditStagingArea/DiffComputer; title → "EDT-10 STAGE Diff"; version → 3.0.0 |
| OBS-02 | Classification field merged with Design field on same line | Separated Classification on its own line |
| OBS-03 | Classification field merged with Design field on same line | Separated Classification on its own line |
| OBS-04 | Classification field merged with Design field on same line | Separated Classification on its own line |
| OBS-05 | Classification field merged with Design field on same line | Separated Classification on its own line |

### Cross-Layer Sync Results

- **C4 ↔ SQ:** All lifelines in SQ diagrams exist as C4 components ✓
- **UC ↔ SQ:** 148 UCs → 149 SQs (AGT-05 orphan reclassified) ✓
- **SM ↔ SQ:** All state transitions in SQs match valid SM transitions ✓
- **Method Consistency:** PROCESS, DISPATCH, APPEND, SELECT identical across layers ✓

### Design Chain Consistency: 97.8%



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MCP/sq_mcp02_discover_mcp_tools.puml ---

@startuml sq_mcp02_discover_mcp_tools
' ============================================================
' Title:     MCP-02 — DISCOVER MCP Tools
' Boundary:  nasim code agent
' Purpose:   Discover and register tools from connected MCP server
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — MCP-02 DISCOVER MCP Tools

box "MCP Layer" #EDE7F6
  participant "MCPClientRuntime" as client
  participant "MCPDiscovery" as discovery
  participant "MCPToolAdapter" as adapter
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box
box "External" #F5F5F5
  participant "MCP Server" as server
end box

note over client, server
  Scope:          Tool discovery from connected MCP server
  Preconditions:  MCP server connected (MCP-01 complete)
  Excludes:       Connection management, tool adaptation (MCP-03)
  Contexts:       Agent initialization, server reconnection
  Rollback:       Clear partially discovered tools on failure
  Design:         Lazy discovery with caching
  Classification: Process Decomposition
end note

== MCP-02 DISCOVER MCP Tools ==

client -> discovery : discover_tools(connection)
activate discovery

discovery -> server : list_tools()
activate server
server --> discovery : tool_list (name, description, schema)
deactivate server

loop for each tool in tool_list
    discovery -> adapter : adapt_tool(tool_definition)
    activate adapter
    adapter --> discovery : wrapped_tool
    deactivate adapter

    discovery -> registry : register(wrapped_tool)
    activate registry
    registry --> discovery : registration_confirmed
    deactivate registry
end

discovery --> client : discovery_complete
deactivate discovery

note over client, server
  Flow:    MCPClientRuntime -> MCPDiscovery -> list tools -> wrap each -> register in registry
  State:   No state change
  Failure: Partial discovery -> register available tools, log failures
  Success: All tools available in ToolRegistry
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MCP/sq_mcp01_connect_mcp_server.puml ---

@startuml sq_mcp01_connect_mcp_server
' ============================================================
' Title:     MCP-01 — CONNECT MCP Server
' Boundary:  nasim code agent
' Purpose:   Connect to external MCP server via stdio/SSE
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Meta-Software Designer audit 2026-06-21
' ============================================================

title nasim — MCP-01 CONNECT MCP Server

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ErrorBoundary" as eb
end box
box "MCP Layer" #EDE7F6
  participant "MCPClientRuntime" as client
end box
box "External" #F5F5F5
  participant "MCP Server" as server
end box

note over user, server
  Scope:          Connection establishment to external MCP server
  Preconditions:  MCP server endpoint configured in config
  Excludes:       Tool discovery and adaptation (MCP-02, MCP-03)
  Contexts:       Called by TL-12 (DISPATCH MCP Extension) or agent initialization
  Rollback:       Close socket on failure, map to AIP-193 error
  Design:         Connection pooling and heartbeat monitoring. ErrorBoundary handles all connection failures
  Classification: UC-level Sub-flow
end note

== MCP-01 CONNECT MCP Server ==

user -> repl : invoke MCP connect
repl -> agent : CONNECT_MCP(server_config)
activate agent

hnote over agent #FFF3E0 : **State: THINKING**

agent -> client : connect(server_config)
activate client

client -> server : establish stdio/SSE connection
activate server

break Connection refused / timeout
    server --> client : ConnectionError
    client --> eb : raise MCPConnectionFailed
    activate eb
    eb --> agent : map_to_aip_193(503, "MCP Server Unreachable")
    deactivate eb
    agent --> repl : AIP-193 Error (503)
    deactivate agent
    deactivate client
end

server --> client : connection established
deactivate server

client -> server : send initialize handshake
activate server
server --> client : handshake response (capabilities)
deactivate server

client -> client : store connection state

client --> agent : ConnectionReady
deactivate client

hnote over agent #ECEFF1 : **State: IDLE**

agent --> repl : 200 OK (Connection Active)
deactivate agent

note over user, server
  Flow:    Developer -> REPLSession -> AgentOrchestrator -> MCPClientRuntime -> establish connection -> handshake -> ready
  State:   <back:#ECEFF1>IDLE</back> -> <back:#FFF3E0>THINKING</back> -> <back:#ECEFF1>IDLE</back>
  Failure: Connection refused/timeout -> ErrorBoundary -> 503 UNAVAILABLE
  Success: Agent receives ready connection handle
  ROD errors: 503 UNAVAILABLE {error: {code: "UNAVAILABLE", message: "MCP Server Unreachable", status: "UNAVAILABLE"}}
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MCP/sq_mcp04_expose_nasim_tools.puml ---

@startuml sq_mcp04_expose_nasim_tools
' ============================================================
' Title:     MCP-04 — EXPOSE nasim Tools
' Boundary:  nasim code agent
' Purpose:   Expose nasim tools to external MCP clients
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — MCP-04 EXPOSE nasim Tools

box "MCP Layer" #EDE7F6
  participant "MCPServerRuntime" as server
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box
box "External" #F5F5F5
  participant "MCP Client" as client
end box

note over server, client
  Scope:          Serving nasim tools via MCP server interface
  Preconditions:  MCPServerRuntime initialized, tools registered
  Excludes:       Tool discovery, adaptation (MCP-02, MCP-03)
  Contexts:       External MCP client connection lifecycle
  Rollback:       Disconnect client on tool execution failure
  Design:         Request validation and rate limiting
  Classification: Process Decomposition
end note

== MCP-04 EXPOSE nasim Tools ==

client -> server : list_tools()
activate server

server -> registry : get_all_tools()
activate registry
registry --> server : tool_list
deactivate registry

server --> client : tool_definitions
deactivate server

client -> server : call_tool(name, args)
activate server

break Tool not found
    server --> client : error("tool not found")
end

server -> registry : execute(name, args)
activate registry
registry --> server : result
deactivate registry

break Execution failure
    server --> client : error("execution failed")
end

server --> client : tool_result
deactivate server

note over server, client
  Flow:    MCP Client -> MCPServerRuntime -> ToolRegistry -> execute -> return result
  State:   No state change
  Failure: Tool not found or execution failure -> error response
  Success: Client receives tool execution result
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MCP/sq_mcp03_adapt_mcp_tool.puml ---

@startuml sq_mcp03_adapt_mcp_tool
' ============================================================
' Title:     MCP-03 — ADAPT MCP Tool
' Boundary:  nasim code agent
' Purpose:   Wrap MCP server tool into nasim Tool format
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — MCP-03 ADAPT MCP Tool

box "MCP Layer" #EDE7F6
  participant "MCPToolAdapter" as adapter
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over adapter, registry
  Scope:          Tool format adaptation from MCP to nasim
  Preconditions:  Tool discovered from MCP server (MCP-02)
  Excludes:       Discovery and registration logic
  Contexts:       Called by MCPDiscovery during tool registration
  Rollback:       Reject incompatible tool schemas
  Design:         Schema mapping with type coercion
  Classification: Process Decomposition
end note

== MCP-03 ADAPT MCP Tool ==

adapter -> adapter : parse MCP tool schema

break Incompatible schema
    adapter --> adapter : skip tool, log warning
end

adapter -> adapter : map types to nasim Tool format
adapter -> adapter : create execution wrapper

adapter -> registry : register(adapted_tool)
activate registry
registry --> adapter : tool_registered(name, version)
deactivate registry

note over adapter, registry
  Flow:    MCPToolAdapter -> parse schema -> map types -> create wrapper -> register
  State:   No state change
  Failure: Incompatible schema -> skip tool, log warning
  Success: Tool available in nasim ToolRegistry with MCP backend
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SBX/sq_sbx01_isolate_command.puml ---

@startuml sq_sbx01_isolate_command
' ============================================================
' Title:     SBX-01 — ISOLATE Command
' Boundary:  nasim code agent
' Purpose:   Execute command in OS-level sandbox
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SBX-01 ISOLATE Command

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Sandbox Layer" #F1F8E9
  participant "SandboxExecutor" as executor
  participant "SandboxPolicy" as policy
end box
box "External" #F5F5F5
  participant "Sandbox Runtime" as runtime
end box

note over agent, runtime
  Scope:          Sandboxed command execution
  Preconditions:  SandboxExecutor initialized, policy loaded
  Excludes:       Policy management (SBX-02), monitoring (SBX-03)
  Contexts:       Called by TL-05 (DISPATCH Shell Command)
  Rollback:       Kill sandbox process on timeout or violation
  Design:         Process isolation with namespace and cgroup
  Classification: Process Decomposition
end note

== SBX-01 ISOLATE Command ==

agent -> executor : execute(command, policy)
activate executor

executor -> policy : apply_rules(policy)
activate policy
policy --> executor : rules_applied
deactivate policy

executor -> executor : create sandbox (namespace, cgroup)
executor -> runtime : spawn_process(command)
activate runtime

break Timeout or resource violation
    runtime --> executor : timeout/violation error
    executor --> agent : execution_result(exit_code=124, error="timeout")
end

runtime --> executor : execution_result(output, exit_code)
deactivate runtime

executor --> agent : execution_result(output, exit_code)
deactivate executor

note over agent, runtime
  Flow:    AgentOrchestrator -> SandboxExecutor -> apply policy -> create sandbox -> execute -> return
  State:   <back:#F1F8E9>STAGING</back>
  Failure: Policy violation or timeout -> kill sandbox, return violation error
  Success: Agent receives command output and exit code
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SBX/sq_sbx02_apply_sandbox_policy.puml ---

@startuml sq_sbx02_apply_sandbox_policy
' ============================================================
' Title:     SBX-02 — APPLY Sandbox Policy
' Boundary:  nasim code agent
' Purpose:   Load and apply sandbox security policy
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SBX-02 APPLY Sandbox Policy

box "Sandbox Layer" #F1F8E9
  participant "SandboxExecutor" as executor
  participant "SandboxPolicy" as policy
end box

note over executor, policy
  Scope:          Sandbox policy loading and application
  Preconditions:  Policy file exists, SandboxPolicy initialized
  Excludes:       Command execution (SBX-01), monitoring (SBX-03)
  Contexts:       Called by SBX-01 before command execution
  Rollback:       Revert to default policy on validation failure
  Design:         Declarative policy with rule inheritance
  Classification: Process Decomposition
end note

== SBX-02 APPLY Sandbox Policy ==

executor -> policy : load_policy(policy_path)
activate policy

policy -> policy : read policy file

break Policy file not found
    policy --> executor : default policy applied
end

policy -> policy : validate rules

break Invalid policy rules
    policy --> executor : revert to defaults, log error
end

policy -> policy : apply to sandbox instance

policy --> executor : policy_applied(rules_count)
deactivate policy

note over executor, policy
  Flow:    SandboxExecutor -> SandboxPolicy -> read policy -> validate -> apply -> confirm
  State:   No state change
  Failure: Invalid policy -> revert to defaults, log error
  Success: Executor receives policy application confirmation
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SBX/sq_sbx04_limit_resources.puml ---

@startuml sq_sbx04_limit_resources
' ============================================================
' Title:     SBX-04 — LIMIT Resources
' Boundary:  nasim code agent
' Purpose:   Enforce CPU, memory, and disk quotas per sandbox instance
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SBX-04 LIMIT Resources

box "Sandbox Layer" #F1F8E9
  participant "SandboxExecutor" as executor
  participant "ResourceLimiter" as limiter
end box

note over executor, limiter
  Scope:          Resource quota enforcement via cgroups
  Preconditions:  Sandbox instance created, limits defined
  Excludes:       Process monitoring (SBX-03)
  Contexts:       Called by SandboxExecutor during sandbox creation
  Rollback:       Remove cgroup on setup failure
  Design:         Linux cgroup v2 with CPU, memory, disk I/O limits
  Classification: Process Decomposition
end note

== SBX-04 LIMIT Resources ==

executor -> limiter : set_limits(cgroup_id, quotas)
activate limiter

limiter -> limiter : create cgroup v2 hierarchy

break Cgroup setup fails
    limiter --> executor : CgroupError("setup failed")
end

limiter -> limiter : set cpu.max (CPU quota)
limiter -> limiter : set memory.max (memory limit)
limiter -> limiter : set io.max (disk I/O limit)

limiter --> executor : limits_applied(cgroup_id)
deactivate limiter

note over executor, limiter
  Flow:    SandboxExecutor -> ResourceLimiter -> create cgroup -> set CPU -> set memory -> set I/O -> confirm
  State:   No state change
  Failure: Cgroup setup fails -> remove partial cgroup, return error
  Success: Executor receives cgroup with enforced limits
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SBX/sq_sbx03_monitor_process.puml ---

@startuml sq_sbx03_monitor_process
' ============================================================
' Title:     SBX-03 — MONITOR Process
' Boundary:  nasim code agent
' Purpose:   Monitor sandboxed process for timeout and resource usage
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SBX-03 MONITOR Process

box "Sandbox Layer" #F1F8E9
  participant "SandboxExecutor" as executor
  participant "SandboxMonitor" as monitor
end box

note over executor, monitor
  Scope:          Process monitoring within sandbox
  Preconditions:  Sandbox process running (SBX-01)
  Excludes:       Resource limiting (SBX-04)
  Contexts:       Long-running commands, background processes
  Rollback:       Kill process on timeout, enforce resource limits
  Design:         Watchdog thread with configurable intervals
  Classification: Process Decomposition
end note

== SBX-03 MONITOR Process ==

executor -> monitor : start_watch(process_id, limits)
activate monitor

loop while process running
    monitor -> monitor : poll process status
    monitor -> monitor : check timeout elapsed
    monitor -> monitor : check resource usage (CPU, memory)
end

alt timeout exceeded
    monitor -> executor : kill_process(SIGKILL)
    executor --> monitor : process_killed
else resource limit exceeded
    monitor -> executor : enforce_limit(violation)
    executor --> monitor : limit_enforced
else normal completion
    monitor -> monitor : record final stats
end

monitor --> executor : watch_complete(stats)
deactivate monitor

note over executor, monitor
  Flow:    SandboxExecutor -> SandboxMonitor -> poll -> enforce limits -> complete
  State:   No state change
  Failure: Timeout or resource violation -> kill/enforce
  Success: Executor receives process stats and completion status
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs05_expose_metrics.puml ---

@startuml sq_obs05_expose_metrics
' ============================================================
' Title:     OBS-05 — EXPOSE /metrics
' Boundary:  nasim code agent CLI
' Purpose:   Serve /metrics endpoint for Prometheus pull scrape
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Prometheus" as prom
actor "Developer" as dev

box "Server Layer" #E3F2FD
  participant "ServerApp" as server
end box

box "Observability Layer" #FFF3E0
  participant "MetricsCollector" as metrics
end box

note over prom, metrics
  Scope:
    - obs05 EXPOSE /metrics — serve metrics for pull scrape

  Preconditions:
    - MetricsCollector configured (metrics_enabled)
    - ServerApp running (HTTP mode)

  Contexts:
    - HTTP mode: /metrics served by ServerApp
    - CLI mode: metrics printed on demand or exported to file
    - Prometheus pull-scrapes this endpoint periodically

  Excludes:
    - Metrics recording (OBS-02)
    - Structured logging (OBS-01)
    - OTel export (optional, behind flag)

  Classification: Process Decomposition

  Design:
    - MetricsCollector exposes prometheus-client generate_latest()
    - ServerApp adds /metrics route (GET only)
    - Content-Type: text/plain; version=0.0.4
    - No authentication required (internal network)
    - CLI mode: `nasim metrics` command prints current metrics

  Returns:
    - HTTP 200 with metrics text (Prometheus format)
    - HTTP 503 if metrics disabled

  Invariants:
    - Pull-based only (never pushes to Prometheus)
    - No high-cardinality labels
    - Metric names follow nasim_<metric>[_<unit>]
end note

== obs05 EXPOSE /metrics (HTTP mode) ==

prom -> server : GET /metrics
activate server

server -> metrics : generate_latest()
activate metrics
metrics -> metrics : collect all metric families
metrics --> server : metrics_text (Prometheus format)
deactivate metrics

server --> prom : 200 OK, Content-Type: text/plain
deactivate server

== obs05 EXPOSE /metrics (CLI mode) ==

dev -> server : nasim metrics
activate server

server -> metrics : generate_latest()
activate metrics
metrics --> server : metrics_text
deactivate metrics

server --> dev : formatted metrics output
deactivate server

note over prom, metrics
  Flow:
    - Prometheus → GET /metrics → ServerApp → MetricsCollector → metrics text

  State:
    - <back:#ECEFF1>IDLE</back> → COLLECTING → <back:#E0F2F1>SERVING</back> → DONE

  Failure:
    - Metrics disabled → 503 or empty output

  Success:
    - Prometheus-compatible metrics text

  Key invariants:
    - Pull-based only
    - No authentication required
    - Content-Type: text/plain; version=0.0.4
    - Low-cardinality labels only
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs04_redact_sensitive.puml ---

@startuml sq_obs04_redact_sensitive
' ============================================================
' Title:     OBS-04 — REDACT Sensitive Data
' Boundary:  nasim code agent CLI
' Purpose:   Strip secrets before emission to structured logs or wire
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "StructuredLogger" as logger
actor "WireAppender" as wire

box "Observability Layer" #E3F2FD
  participant "LogRedactor" as redactor
end box

box "Config Layer" #E8F5E9
  participant "Config" as config
end box

note over logger, config
  Scope:
    - obs04 REDACT Sensitive — strip secrets before any emission

  Preconditions:
    - LogRedactor initialized with redaction rules
    - Config loaded (redact_enabled, redact_patterns)

  Contexts:
    - Called before every emission to structured logs (OBS-01)
    - Called before every wire event append (WRL-01)
    - Always on — cannot be disabled

  Excludes:
    - Log emission (OBS-01)
    - Wire append (WRL-01)

  Classification: Process Decomposition

  Design:
    - LogRedactor applies regex patterns to record fields
    - Global rules: env vars, API keys, .env content, passwords
    - Per-project rules: custom patterns from config
    - redacted=true flag on sanitized records
    - Patterns: API_KEY=xxx → API_KEY=[REDACTED]

  Returns:
    - redact(LogRecord) → LogRecord (sanitized)
    - redact_payload(dict) → dict (sanitized)

  Invariants:
    - Always on — cannot be disabled
    - Applied before emission to both structured and wire
    - Original data never reaches stdout or wire file
    - Redaction is lossy (cannot recover originals)
end note

== obs04 REDACT Sensitive (structured log) ==

logger -> redactor : redact(record)
activate redactor

redactor -> config : load_redaction_rules()
activate config
config --> redactor : rules[]
deactivate config

loop for each rule in rules
    redactor -> redactor : apply_pattern(record, rule.pattern, rule.replacement)
end

redactor -> redactor : set_redacted_flag(record)

redactor --> logger : sanitized_record
deactivate redactor

== obs04 REDACT Sensitive (wire event) ==

wire -> redactor : redact_payload(payload)
activate redactor

redactor -> config : load_redaction_rules()
activate config
config --> redactor : rules[]
deactivate config

loop for each rule in rules
    redactor -> redactor : apply_pattern(payload, rule.pattern, rule.replacement)
end

redactor --> wire : sanitized_payload
deactivate redactor

note over logger, config
  Flow:
    - Emitter → LogRedactor → Config (rules) → sanitized record/payload

  State:
    - <back:#ECEFF1>IDLE</back> → LOADING RULES → APPLYING → DONE

  Failure:
    - Rule load failure → default rules only

  Success:
    - Sanitized record with redacted=true flag

  Key invariants:
    - Always applied (never skipped)
    - Applied to both structured and wire emissions
    - Original secrets never reach output
    - Configurable rules (global + per-project)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs02_record_metrics.puml ---

@startuml sq_obs02_record_metrics
' ============================================================
' Title:     OBS-02 — RECORD Metrics
' Boundary:  nasim code agent CLI
' Purpose:   Record metric points for token usage, latency, tool calls
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "AgentOrchestrator" as agent
actor "Provider" as provider
actor "ToolRegistry" as tools

box "Observability Layer" #E3F2FD
  participant "MetricsCollector" as metrics
  participant "TraceCorrelator" as trace
end box

box "External" #F3E5F5
  participant "Prometheus" as prom
end box

note over agent, prom
  Scope:
    - obs02 RECORD Metrics — increment counters, observe histograms

  Preconditions:
    - MetricsCollector configured (enabled)
    - Prometheus scrape endpoint available (HTTP mode)

  Contexts:
    - Called on every LLM request, tool call, error, session event
    - Enables dashboards (Grafana on top of Prometheus)

  Excludes:
    - Structured logging (OBS-01)
    - Trace correlation (OBS-03)
    - Metrics export to OTel (optional, behind flag)

  Classification: Process Decomposition

  Design:
    - MetricsCollector provides counter/gauge/histogram handles
    - Convenience methods instrument key nasim events
    - Labels are low-cardinality (model, provider, tool, success)
    - /metrics endpoint served by ServerApp (HTTP mode)
    - Pull-based only — never pushes to Prometheus

  Returns:
    - Convenience methods: None (fire-and-forget)
    - Handle methods: Counter/Gauge/Histogram for further use

  Invariants:
    - /metrics pull only
    - No high-cardinality labels (no request_id in labels)
    - Metric names follow nasim_<metric>[_<unit>] convention
end note

== obs02 RECORD Metrics ==

agent -> metrics : record_llm_request(model, provider, latency_ms, tokens)
activate metrics

metrics -> metrics : llm_latency_ms.labels(model, provider).observe(latency_ms)
metrics -> metrics : llm_tokens_total.labels(model, provider).inc(tokens)
metrics -> metrics : llm_requests_total.labels(model, provider).inc()

metrics --> agent : None
deactivate metrics

== obs02 RECORD Tool Call ==

tools -> metrics : record_tool_call(tool, success, duration_ms)
activate metrics

metrics -> metrics : tool_duration_ms.labels(tool).observe(duration_ms)
metrics -> metrics : tool_calls_total.labels(tool, success).inc()

metrics --> tools : None
deactivate metrics

== obs02 RECORD Error ==

agent -> metrics : record_error(error_type)
activate metrics

metrics -> metrics : errors_total.labels(type=error_type).inc()

metrics --> agent : None
deactivate metrics

note over agent, prom
  Flow:
    - AgentOrchestrator/Provider/ToolRegistry → MetricsCollector → in-memory metrics → /metrics scrape

  State:
    - <back:#ECEFF1>IDLE</back> → RECORDING → DONE

  Failure:
    - Record failure → silently ignored (never blocks agent)

  Success:
    - Metric point recorded in memory

  Key invariants:
    - Pull-based only (/metrics endpoint)
    - Low-cardinality labels
    - nasim_<metric>[_<unit>] naming convention
    - Fire-and-forget (never raises to caller)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs06_export_otlp.puml ---

@startuml sq_obs06_export_otlp
' ============================================================
' Title:     OBS-06 — EXPORT OTLP
' Boundary:  nasim code agent
' Purpose:   Export traces and metrics to OTel-compatible backend
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — OBS-06 EXPORT OTLP

box "Observability Layer" #E0F2F1
  participant "OTelExporter" as otel
  participant "TraceCorrelator" as trace
  participant "MetricsCollector" as metrics
end box
participant "OTel Backend" as backend

note over otel, backend
  Scope:          Export traces and metrics to OTel-compatible backend
  Preconditions:  OTel feature flag enabled, backend reachable
  Excludes:       Local log emission (OBS-01), redaction (OBS-04)
  Contexts:       Called periodically or on shutdown
  Rollback:       Export failure logged, data buffered for retry
  Design:         Behind otel feature flag. Bridges spans + metrics to OTel SDK.
  Classification: Process Decomposition
end note

== OBS-06 EXPORT OTLP ==

otel -> trace : EXPORT spans
activate trace
trace --> otel : SpanBatch
deactivate trace

otel -> metrics : EXPORT metrics
activate metrics
metrics --> otel : MetricBatch
deactivate metrics

otel -> backend : POST /v1/traces + /v1/metrics
activate backend

break Backend unreachable
  backend --> otel : ConnectionError
  otel -> otel : buffer for retry
end

backend --> otel : 200 OK
deactivate backend

note over otel, backend
  Flow:    OTelExporter -> collect spans + metrics -> POST to backend
  State:   No state change
  Failure: Backend unreachable -> buffer and retry
  Success: Traces and metrics exported to OTel backend
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs03_correlate_trace.puml ---

@startuml sq_obs03_correlate_trace
' ============================================================
' Title:     OBS-03 — CORRELATE Trace
' Boundary:  nasim code agent CLI
' Purpose:   Generate and propagate trace context across nasim surfaces
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "CLI" as cli
actor "ServerApp" as http

box "Observability Layer" #E3F2FD
  participant "TraceCorrelator" as trace
  participant "ContextPropagator" as propagator
end box

box "Agent Layer" #FFF3E0
  participant "AgentOrchestrator" as agent
  participant "Provider" as provider
  participant "ToolRegistry" as tools
end box

box "External" #F3E5F5
  participant "OTelCollector" as otel
end box

note over cli, otel
  Scope:
    - obs03 CORRELATE Trace — generate and propagate trace context

  Preconditions:
    - TraceCorrelator initialized (contextvars available)

  Contexts:
    - Called at entrypoint: CLI turn start or HTTP request
    - Propagated across: Provider calls, tool dispatch, hook execution,
      subagent spawn, MCP tool calls

  Excludes:
    - Structured logging (OBS-01, but consumes trace context)
    - Metrics recording (OBS-02)
    - Wire log (WRL, but receives correlation ids)

  Classification: Process Decomposition

  Design:
    - TraceCorrelator generates root trace/span per entrypoint
    - ContextPropagator ensures trace flows across boundaries
    - Every LogRecord and WireEvent carries: trace_id, span_id, parent_span_id
    - Optional: bridge to OTel SDK when otel feature enabled

  Returns:
    - new_trace: TraceContext (root)
    - child_span: TraceContext (nested)

  Invariants:
    - Every log record has trace_id
    - Every wire event has trace_id
    - Trace flows across all nasim surfaces
end note

== obs03 CORRELATE Trace (CLI turn) ==

cli -> trace : new_trace("cli.turn")
activate trace
trace -> trace : generate trace_id (uuid4)
trace -> trace : generate span_id (uuid4hex)
trace -> trace : bind to contextvars
trace --> cli : TraceContext(trace_id, span_id)
deactivate trace

cli -> agent : execute_turn(user_input, trace_ctx)
activate agent

agent -> propagator : propagate()
activate propagator
propagator --> agent : {trace_id, span_id, parent_span_id}
deactivate propagator

agent -> provider : chat_stream(messages, trace_ctx)
activate provider
provider -> provider : create child_span("llm.chat")
provider --> agent : stream
deactivate provider

agent -> tools : execute(tool_call, trace_ctx)
activate tools
tools -> tools : create child_span("tool.exec")
tools --> agent : result
deactivate tools

agent --> cli : AgentEvent stream
deactivate agent

== obs03 CORRELATE Trace (subagent spawn) ==

agent -> propagator : propagate()
activate propagator
propagator --> agent : trace_context
deactivate propagator

agent -> agent : spawn_subagent(task, trace_context)

note over cli, otel
  Flow:
    - Entry → TraceCorrelator.new_trace → ContextPropagator.propagate
    - → Provider/Tool receives trace context
    - → Every child span links back to root trace_id

  State:
    - <back:#ECEFF1>IDLE</back> → GENERATING → PROPAGATING → DONE

  Failure:
    - Trace generation failure → fallback to random ids

  Success:
    - End-to-end correlation across all surfaces

  Key invariants:
    - Root trace per CLI turn or HTTP request
    - Parent-child span hierarchy
    - trace_id propagated to wire events and structured logs
    - Optional OTel bridge when feature enabled
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs01_stream_log.puml ---

@startuml sq_obs01_stream_log
' ============================================================
' Title:     OBS-01 — STREAM Structured Log
' Boundary:  nasim code agent
' Purpose:   Emit structured JSON log record to stdout
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — OBS-01 STREAM Structured Log

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Observability Layer" #E0F2F1
  participant "StructuredLogger" as logger
  participant "LogRedactor" as redactor
  participant "TraceCorrelator" as trace
  participant "DualOutputAdapter" as adapter
end box
box "External" #F5F5F5
  participant "Stdout" as stdout
end box

note over agent, stdout
  Scope:          Emit structured JSON log record to stdout
  Preconditions:  StructuredLogger configured, LogRedactor available
  Excludes:       Wire log append (WRL-01), Metrics recording (OBS-02)
  Contexts:       Called on every significant agent event (turn, LLM call, tool exec, error)
  Rollback:       Write failure -> stderr warning, never raises to caller
  Design:         StructuredLogger constructs LogRecord with trace context; LogRedactor strips secrets; DualOutputAdapter writes JSON to stdout
  Classification: Process Decomposition
end note

== OBS-01 STREAM Structured Log ==

agent -> logger : emit(msg, level, **extra)
activate logger

logger -> trace : current_span()
activate trace
trace --> logger : TraceContext(trace_id, span_id, parent_span_id)
deactivate trace

logger -> logger : build_record(msg, level, trace_ctx, extra)

logger -> redactor : redact(record)
activate redactor
redactor --> logger : sanitized_record
deactivate redactor

logger -> adapter : emit(sanitized_record)
activate adapter

adapter -> adapter : serialize_json(record)
adapter -> stdout : write_json(record)

adapter --> logger : None
deactivate adapter

deactivate logger

note over agent, stdout
  Flow:    AgentOrchestrator -> StructuredLogger -> TraceCorrelator + LogRedactor -> DualOutputAdapter -> Stdout
  State:   No state change
  Failure: Write failure -> stderr warning, never raises
  Success: JSON line written to stdout
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv06_dispatch_message.puml ---

@startuml sq_srv06_send_message
' ============================================================
' Title:     SRV-06 — SEND Message
' Boundary:  nasim code agent HTTP API
' Purpose:   Dispatch a user message through the agent and stream SSE response
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    Meta-Software Designer audit 2026-06-21
' Pattern:   Controller (ServerRouter) -> Service (AgentOrchestrator) -> Repository (SessionStore)
' ============================================================

title nasim — SRV-06 SEND Message

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "APISchema" as schema
  participant "ServerRouter" as router
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ErrorBoundary" as eb
end box
box "Session Layer" #F3E5F5
  participant "SessionStore" as store
end box
box "Observability Layer" #E0F2F1
  participant "SSEHandler" as sse
  participant "TraceCorrelator" as trace
end box

note over client, trace
  Scope:          Dispatch a user message through the agent and stream SSE response
  Preconditions:  Session exists, ServerRouter initialized
  Excludes:       Session CRUD (SRV-01..05), Tool listing (SRV-08..09)
  Contexts:       Called by HTTPClient via POST /v1/sessions/{id}:dispatch
  Rollback:       404 if session not found, 400 if invalid body, 502 if agent fails
  Design:         CSR: Controller(ServerRouter) -> Service(AgentOrchestrator). No God Object: AgentOrchestrator owns orchestration, delegates tool dispatch to SafetyCoordinator. ROD: custom method :dispatch (AIP-136)
  Classification: Primary Orchestrator
end note

== SRV-06 SEND Message ==

ref over agent, trace
  OBS-03: CORRELATE Trace
end ref

client -> schema : validate(request_body)
schema --> client : ValidatedDispatchRequest

client -> router : POST /v1/sessions/{id}:dispatch
activate router

router -> store : READ session exists
activate store
store --> router : SessionStatus
deactivate store

break Session not found [404]
  router --> client : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

break Invalid request body [400]
  router --> client : 400 INVALID_ARGUMENT {error: {code: "INVALID_ARGUMENT", message: "Invalid request", status: "INVALID_ARGUMENT"}}
end

hnote over agent #FFF3E0 : **State: THINKING**

router -> agent : PROCESS(session_id, message)
activate agent
ref over agent
  AGT-01: PROCESS User Task
end ref

break Agent error [502]
  agent -> eb : handle(AgentError)
  activate eb
  eb --> agent : RecoveryAction(retry/abort)
  deactivate eb
  agent --> router : AgentError
  router --> client : 502 UNAVAILABLE {error: {code: "UNAVAILABLE", message: "Agent error", status: "UNAVAILABLE"}}
end

agent --> router : AgentEventStream
deactivate agent

hnote over sse #E8F5E9 : **State: RESPONDING**

router -> sse : stream(events)
activate sse
sse --> client : Content-Type: text/event-stream
sse --> client : SSE: TextChunk, ToolStart, ToolResult, Done
deactivate sse

router -> store : SAVE session messages
activate store
store --> router : saved
deactivate store

router --> client : 200 OK (stream complete)
deactivate router

note over client, trace
  Flow:    HTTPClient -> APISchema -> ServerRouter -> AgentOrchestrator -> SSE stream -> SessionStore
  State:   <back:#ECEFF1>IDLE</back> -> <back:#E0F7FA>SERVING</back> -> <back:#FFF3E0>THINKING</back> -> <back:#E8F5E9>RESPONDING</back> -> <back:#ECEFF1>IDLE</back>
  Failure: 404 NOT_FOUND, 400 INVALID_ARGUMENT, 502 UNAVAILABLE — all via ErrorBoundary
  Success: 200 OK with SSE event stream
  ROD errors: AIP-193 {error: {code, message, status}} on all failure paths
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv11_update_config.puml ---

@startuml sq_srv11_update_config
' ============================================================
' Title:     SRV-11 — UPDATE Config
' Boundary:  nasim code agent HTTP API
' Purpose:   Update agent configuration at runtime
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-11 UPDATE Config

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "APISchema" as schema
  participant "ServerRouter" as router
end box
box "Config Layer" #FCE4EC
  participant "ConfigLoader" as config
end box

note over client, config
  Scope:          Update agent configuration at runtime
  Preconditions:  ConfigLoader initialized
  Excludes:       Config read, config validation
  Contexts:       Called by HTTPClient via PATCH /v1/config
  Rollback:       400 if invalid config values
  Design:         ROD: standard update. Partial config patch. Triggers CFG-03 APPLY.
  Classification: Primary Orchestrator
end note

== SRV-11 UPDATE Config ==

client -> schema : validate(patch_body)
schema --> client : ValidatedConfigPatch

client -> router : PATCH /v1/config
activate router

router -> config : APPLY config patch
activate config

break Invalid config
  config --> router : ConfigError(invalid_value)
  deactivate config
  router --> client : 400 INVALID_ARGUMENT {error: {code: "INVALID_ARGUMENT", message: "Invalid config", status: "INVALID_ARGUMENT"}}
end

config --> router : applied
deactivate config

router --> client : 200 OK {config: {updated_fields: [...]}}
deactivate router

note over client, config
  Flow:    HTTPClient -> validate -> ServerRouter -> ConfigLoader -> apply -> 200
  State:   No state change
  Failure: 400 invalid config values
  Success: 200 OK with updated config
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv01_list_sessions.puml ---

@startuml sq_srv01_list_sessions
' ============================================================
' Title:     SRV-01 — LIST Sessions
' Boundary:  nasim code agent HTTP API
' Purpose:   List all sessions with pagination
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Prompt audit 2026-06-21 (cop.md: AIP-193 error path added)
' ============================================================

title nasim — SRV-01 LIST Sessions

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "ServerRouter" as router
end box
box "Session Layer" #F3E5F5
  participant "SessionStore" as store
end box

note over client, store
  Scope:          List all sessions with pagination
  Preconditions:  ServerRouter initialized, SessionStore available
  Excludes:       Session CRUD (SRV-02..05), Message operations (SRV-06..07)
  Contexts:       Called by HTTPClient via GET /v1/sessions
  Rollback:       None (read-only operation)
  Design:         CSR: Controller(ServerRouter) -> Repository(SessionStore). ROD: standard list (AIP-136)
  Classification: Primary Orchestrator
end note

== SRV-01 LIST Sessions ==

client -> router : GET /v1/sessions?page_size=10&page_token=abc
activate router

router -> store : LIST sessions(limit=10, cursor="abc")
activate store

break Store read failure [500]
    store --> router : InternalError
    deactivate store
    router --> client : 500 INTERNAL {error: {code: "INTERNAL", message: "Failed to list sessions", status: "INTERNAL"}}
end

alt Sessions exist
    store --> router : sessions, next_page_token
    deactivate store
    router --> client : 200 OK {sessions: [...], next_page_token: "def"}
else No sessions
    store --> router : empty list, no token
    deactivate store
    router --> client : 200 OK {sessions: [], next_page_token: null}
end

deactivate router

note over client, store
  Flow:    HTTPClient -> ServerRouter -> SessionStore
  State:   <back:#2E7D32>ACTIVE</back>
  Failure: 500 INTERNAL on store read failure
  Success: 200 OK with session list and pagination token
  ROD errors: AIP-193 {error: {code, message, status}} on failure paths
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv03_read_session.puml ---

@startuml sq_srv03_read_session
' ============================================================
' Title:     SRV-03 — READ Session
' Boundary:  nasim code agent HTTP API
' Purpose:   Read a session's current state and messages
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-03 READ Session

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "ServerRouter" as router
end box
box "Session Layer" #F3E5F5
  participant "SessionStore" as store
end box

note over client, store
  Scope:          Read a session's current state and messages
  Preconditions:  Session exists on disk
  Excludes:       Session creation (SRV-02), message dispatch (SRV-06)
  Contexts:       Called by HTTPClient via GET /v1/sessions/{id}
  Rollback:       404 if session not found
  Design:         ROD: standard read. Returns full session state.
  Classification: Primary Orchestrator
end note

== SRV-03 READ Session ==

client -> router : GET /v1/sessions/{id}
activate router

router -> store : READ session
activate store

break Session not found
  store --> router : NotFound
  deactivate store
  router --> client : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

store --> router : Session(messages, metadata)
deactivate store

router --> client : 200 OK {session: {id, messages, created_at, updated_at}}
deactivate router

note over client, store
  Flow:    HTTPClient -> ServerRouter -> SessionStore -> return session
  State:   No state change
  Failure: 404 session not found
  Success: 200 OK with session data
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv02_insert_session.puml ---

@startuml sq_srv02_insert_session
' ============================================================
' Title:     SRV-02 — INSERT Session
' Boundary:  nasim code agent HTTP API
' Purpose:   Create and persist a new agent session
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

title nasim — SRV-02 INSERT Session

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "ServerRouter" as router
end box
box "Session Layer" #F3E5F5
  participant "SessionStore" as store
end box

note over client, store
  Scope:          Create and persist a new agent session
  Preconditions:  ServerRouter initialized, SessionStore available
  Excludes:       Session dispatch (SRV-06), Session deletion (SRV-05)
  Contexts:       Called by HTTPClient via POST /v1/sessions
  Rollback:       500 if SessionStore write fails
  Design:         CSR: Controller(ServerRouter) -> Repository(SessionStore). ROD: standard insert (AIP-136)
  Classification: Primary Orchestrator
end note

== SRV-02 INSERT Session ==

client -> router : POST /v1/sessions
activate router

router -> router : Validate request body
break Invalid request [400]
  router --> client : 400 INVALID_ARGUMENT {error: {code: "INVALID_ARGUMENT", message: "Invalid request", status: "INVALID_ARGUMENT"}}
end

router -> router : Generate session UUID

router -> store : INSERT session(session_id, config)
activate store
store --> router : Session
deactivate store

break Store write fails [500]
  router --> client : 500 INTERNAL {error: {code: "INTERNAL", message: "Failed to create session", status: "INTERNAL"}}
end

router --> client : 201 Created {id, created_at, model, state}
deactivate router

note over client, store
  Flow:    HTTPClient -> ServerRouter -> SessionStore
  State:   <back:#E3F2FD>CREATED</back>
  Failure: 400 invalid body, 500 store write failure
  Success: 201 Created with session metadata
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv09_read_tool.puml ---

@startuml sq_srv09_read_tool
' ============================================================
' Title:     SRV-09 — READ Tool
' Boundary:  nasim code agent HTTP API
' Purpose:   Read details of a specific registered tool
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-09 READ Tool

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "ServerRouter" as router
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over client, registry
  Scope:          Read details of a specific registered tool
  Preconditions:  ToolRegistry initialized
  Excludes:       Tool execution, tool listing
  Contexts:       Called by HTTPClient via GET /v1/tools/{name}
  Rollback:       404 if tool not found
  Design:         ROD: standard read. Returns full tool metadata.
  Classification: Primary Orchestrator
end note

== SRV-09 READ Tool ==

client -> router : GET /v1/tools/{name}
activate router

router -> registry : GET tool(name)
activate registry

break Tool not found
  registry --> router : NotFound
  deactivate registry
  router --> client : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Tool not found", status: "NOT_FOUND"}}
end

registry --> router : ToolMetadata
deactivate registry

router --> client : 200 OK {tool: {name, description, safe, parameters}}
deactivate router

note over client, registry
  Flow:    HTTPClient -> ServerRouter -> ToolRegistry -> return tool
  State:   No state change
  Failure: 404 tool not found
  Success: 200 OK with tool metadata
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv08_list_tools.puml ---

@startuml sq_srv08_list_tools
' ============================================================
' Title:     SRV-08 — LIST Tools
' Boundary:  nasim code agent HTTP API
' Purpose:   List all registered tools available to the agent
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Prompt audit 2026-06-21 (cop.md: AIP-193 error path added)
' ============================================================

title nasim — SRV-08 LIST Tools

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "ServerRouter" as router
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over client, registry
  Scope:          List all registered tools available to the agent
  Preconditions:  ToolRegistry initialized
  Excludes:       Tool execution, tool registration
  Contexts:       Called by HTTPClient via GET /v1/tools
  Rollback:       500 if registry read fails
  Design:         CSR: Controller(ServerRouter) -> Repository(ToolRegistry). ROD: standard list (AIP-136)
  Classification: Primary Orchestrator
end note

== SRV-08 LIST Tools ==

client -> router : GET /v1/tools
activate router

router -> registry : LIST tools
activate registry

break Registry read failure [500]
    registry --> router : InternalError
    deactivate registry
    router --> client : 500 INTERNAL {error: {code: "INTERNAL", message: "Failed to list tools", status: "INTERNAL"}}
end

registry --> router : ToolList[name, description, safe]
deactivate registry

router --> client : 200 OK {tools: [...]}
deactivate router

note over client, registry
  Flow:    HTTPClient -> ServerRouter -> ToolRegistry -> return list
  State:   No state change
  Failure: 500 INTERNAL on registry read failure
  Success: 200 OK with tool list
  ROD errors: AIP-193 {error: {code, message, status}} on failure paths
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv05_retire_session.puml ---

@startuml sq_srv05_retire_session
' ============================================================
' Title:     SRV-05 — RETIRE Session
' Boundary:  nasim code agent HTTP API
' Purpose:   Mark a session as retired (soft delete)
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-05 RETIRE Session

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "ServerRouter" as router
end box
box "Session Layer" #F3E5F5
  participant "SessionStore" as store
end box

note over client, store
  Scope:          Mark a session as retired (soft delete)
  Preconditions:  Session exists on disk
  Excludes:       Hard delete, message operations
  Contexts:       Called by HTTPClient via DELETE /v1/sessions/{id}
  Rollback:       404 if session not found
  Design:         ROD: standard delete. Soft delete (retired flag).
  Classification: Primary Orchestrator
end note

== SRV-05 RETIRE Session ==

client -> router : DELETE /v1/sessions/{id}
activate router

router -> store : READ session exists
activate store

break Session not found
  store --> router : NotFound
  deactivate store
  router --> client : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

store --> router : SessionStatus
deactivate store

router -> store : RETIRE session
activate store
store --> router : retired
deactivate store

router --> client : 200 OK {retired: true}
deactivate router

note over client, store
  Flow:    HTTPClient -> ServerRouter -> SessionStore -> retire -> 200
  State:   <back:#2E7D32>ACTIVE</back> -> <back:#757575>CLOSED</back>
  Failure: 404 not found
  Success: 200 OK with retired status
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv04_update_session.puml ---

@startuml sq_srv04_update_session
' ============================================================
' Title:     SRV-04 — UPDATE Session
' Boundary:  nasim code agent HTTP API
' Purpose:   Update session metadata or settings
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-04 UPDATE Session

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "APISchema" as schema
  participant "ServerRouter" as router
end box
box "Session Layer" #F3E5F5
  participant "SessionStore" as store
end box

note over client, store
  Scope:          Update session metadata or settings
  Preconditions:  Session exists on disk
  Excludes:       Message dispatch (SRV-06), session deletion
  Contexts:       Called by HTTPClient via PATCH /v1/sessions/{id}
  Rollback:       404 if not found, 400 if invalid body
  Design:         ROD: standard update. PATCH with partial body.
  Classification: Primary Orchestrator
end note

== SRV-04 UPDATE Session ==

client -> schema : validate(patch_body)
schema --> client : ValidatedPatchRequest

client -> router : PATCH /v1/sessions/{id}
activate router

router -> store : READ session exists
activate store

break Session not found
  store --> router : NotFound
  deactivate store
  router --> client : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

store --> router : SessionStatus
deactivate store

router -> store : UPDATE session patch
activate store
store --> router : updated
deactivate store

router --> client : 200 OK {session: {id, updated_at}}
deactivate router

note over client, store
  Flow:    HTTPClient -> validate -> ServerRouter -> SessionStore -> update -> 200
  State:   No state change
  Failure: 404 not found, 400 invalid body
  Success: 200 OK with updated session metadata
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv07_list_messages.puml ---

@startuml sq_srv07_list_messages
' ============================================================
' Title:     SRV-07 — LIST Messages
' Boundary:  nasim code agent HTTP API
' Purpose:   Retrieve message history for a session
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

title nasim — SRV-07 LIST Messages

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "ServerRouter" as router
end box
box "Session Layer" #F3E5F5
  participant "SessionStore" as store
end box

note over client, store
  Scope:          Retrieve message history for a session
  Preconditions:  Session exists, ServerRouter initialized
  Excludes:       Session CRUD (SRV-01..05), Message dispatch (SRV-06)
  Contexts:       Called by HTTPClient via GET /v1/sessions/{id}/messages
  Rollback:       404 if session not found
  Design:         CSR: Controller(ServerRouter) -> Repository(SessionStore). ROD: standard list (AIP-136)
  Classification: Primary Orchestrator
end note

== SRV-07 LIST Messages ==

client -> router : GET /v1/sessions/{id}/messages
activate router

router -> store : READ session messages
activate store

alt Session exists
    store --> router : Session(messages=[...])
    deactivate store
    router --> client : 200 OK {messages: [...]}
else Session not found
    store --> router : null
    deactivate store
    router --> client : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

deactivate router

note over client, store
  Flow:    HTTPClient -> ServerRouter -> SessionStore
  State:   <back:#2E7D32>ACTIVE</back>
  Failure: 404 session not found
  Success: 200 OK with message list
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv10_read_config.puml ---

@startuml sq_srv10_read_config
' ============================================================
' Title:     SRV-10 — READ Config
' Boundary:  nasim code agent HTTP API
' Purpose:   Read current agent configuration
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Prompt audit 2026-06-21 (cop.md: AIP-193 error path added)
' ============================================================

title nasim — SRV-10 READ Config

actor "HTTPClient" as client

box "Server Layer" #E8EAF6
  participant "ServerRouter" as router
end box
box "Config Layer" #FCE4EC
  participant "ConfigLoader" as config
end box

note over client, config
  Scope:          Read current agent configuration
  Preconditions:  ConfigLoader initialized
  Excludes:       Config update, config validation
  Contexts:       Called by HTTPClient via GET /v1/config
  Rollback:       500 if config read fails
  Design:         CSR: Controller(ServerRouter) -> Repository(ConfigLoader). ROD: standard read (AIP-136). Returns sanitized config (no secrets).
  Classification: Primary Orchestrator
end note

== SRV-10 READ Config ==

client -> router : GET /v1/config
activate router

router -> config : READ config
activate config

break Config read failure [500]
    config --> router : InternalError
    deactivate config
    router --> client : 500 INTERNAL {error: {code: "INTERNAL", message: "Failed to read config", status: "INTERNAL"}}
end

config --> router : Config(provider, model, safety, budget)
deactivate config

router --> client : 200 OK {config: {provider: "...", model: "...", safety_mode: "..."}}
deactivate router

note over client, config
  Flow:    HTTPClient -> ServerRouter -> ConfigLoader -> return config
  State:   No state change
  Failure: 500 INTERNAL on config read failure
  Success: 200 OK with sanitized config
  ROD errors: AIP-193 {error: {code, message, status}} on failure paths
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PRV/sq_prv03_stream_provider_chat.puml ---

@startuml sq_prv03_stream_provider_chat
' ============================================================
' Title:     PRV-03 — STREAM Provider Chat
' Boundary:  nasim code agent CLI
' Purpose:   Streaming LLM chat completion via provider abstraction
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Provider Layer" #FFF3E0
  participant "Provider" as provider
end box
participant "LLM Provider API" as api

note over user, api
  Scope:          Streaming chat completion yielding chunks
  Preconditions:  Provider initialized and reachable
  Contexts:       Called by AGT-01 (Process User Task)
  Excludes:       Sync chat (PRV-02), tool execution
  Rollback:       Connection drop -> ProviderError
  Design:         Yields str | ToolCall chunks from HTTP stream
  Classification: Primary Orchestrator
end note

== PRV-03 STREAM Provider Chat ==

user -> agent : (entry via AGT-01)
agent -> provider : chat_stream(messages, tools)
provider -> api : HTTP POST /api/chat {model, messages, tools, stream:true}

break Connection drops mid-stream
    api --> provider : broken pipe / timeout
    provider --> agent : ProviderError("Stream interrupted")
    agent -> agent : handle error -> ERROR state
end

loop for each chunk
    api --> provider : JSON chunk
    provider -> provider : parse chunk
    alt text content chunk
        provider --> agent : yield str(token)
    else tool_call chunk
        provider -> provider : accumulate ToolCall by index
    end
end

provider -> provider : yield accumulated ToolCalls
provider --> agent : stream complete

note over user, api
  Flow:    Messages -> HTTP stream -> parse chunks -> yield str | ToolCall
  State:   <back:#FFF3E0>THINKING</back> -> <back:#FFF3E0>THINKING</back> (no state change)
  Failure: Connection drop -> ProviderError
  Success: Stream of text tokens and ToolCall objects
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PRV/sq_prv04_select_provider_backend.puml ---

@startuml sq_prv04_select_provider_backend
' ============================================================
' Title:     PRV-04 — Select Provider Backend
' Boundary:  nasim code agent CLI
' Purpose:   Map config.provider string to provider class
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Config Layer" #E0F7FA
  participant "ConfigLoader" as cfg
end box
box "Provider Layer" #FFF3E0
  participant "ProviderFactory" as factory
end box

note over cfg, factory
  Scope:          Provider backend selection from config
  Preconditions:  Config loaded with provider field
  Contexts:       Called by PRV-01 (Initialize Provider)
  Excludes:       Provider instantiation (PRV-01)
  Rollback:       Unknown provider -> ConfigError
  Design:         Registry mapping: str -> class
  Classification: Process Decomposition
end note

== PRV-04 Select Provider Backend ==

cfg -> factory : select_backend(config.provider)
factory -> factory : PROV_REGISTRY lookup

break Provider not in registry
    factory -> factory : raise ConfigError("Unknown provider: X")
    factory --> cfg : ConfigError
end

factory --> cfg : provider_class

note over cfg, factory
  Flow:    config.provider string -> registry lookup -> class
  State:   No state change
  Failure: Unknown provider name -> ConfigError
  Success: Provider class reference for instantiation
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PRV/sq_prv02_request_chat.puml ---

@startuml sq_prv02_request_chat
' ============================================================
' Title:     PRV-02 — Request Chat
' Boundary:  nasim code agent CLI
' Purpose:   Synchronous LLM chat completion via provider abstraction
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Provider Layer" #FFF3E0
  participant "Provider" as provider
end box
participant "LLM Provider API" as api

note over agent, api
  Scope:          Single synchronous chat completion
  Preconditions:  Provider initialized and reachable
  Contexts:       Called by AGT-01 (Process User Task)
  Excludes:       Streaming (PRV-03), tool parsing
  Rollback:       HTTP error raised as ProviderError
  Design:         Uses httpx.AsyncClient with timeout
  Classification: UC-level Sub-flow (called by AGT-01)
end note

== PRV-02 REQUEST Chat ==

hnote over provider #FFF3E0 : **State: THINKING**

agent -> provider : chat(messages, tools)
provider -> api : HTTP POST /api/chat {model, messages, tools, stream:false}

break HTTP error or timeout
    api --> provider : connection error / timeout
    provider --> agent : ProviderError("Connection failed")
    agent -> agent : handle error -> ERROR state
end

api --> provider : JSON response
provider -> provider : parse response -> LLMResponse
provider --> agent : LLMResponse(content, tool_calls)

note over agent, api
  Flow:    AgentOrchestrator -> Provider -> HTTP POST -> JSON parse -> LLMResponse
  State:   <back:#FFF3E0>THINKING</back> -> <back:#FFF3E0>THINKING</back> (no state change)
  Failure: HTTP error or timeout -> ProviderError
  Success: LLMResponse with content and/or tool_calls
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PRV/sq_prv01_register_provider.puml ---

@startuml sq_prv01_register_provider
' ============================================================
' Title:     PRV-01 — Register Provider
' Boundary:  nasim code agent CLI
' Purpose:   Provider instantiation from config
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "ArgParser" as parser
end box
box "Provider Layer" #FFF3E0
  participant "ProviderFactory" as factory
  participant "Provider" as proto
end box

note over user, proto
  Scope:          Provider instantiation from configuration
  Preconditions:  Config loaded with valid provider name
  Contexts:       Called by main() during startup
  Excludes:       Provider chat/stream (PRV-02/03)
  Rollback:       Unknown provider -> ConfigError
  Design:         Factory pattern; one class per backend
  Classification: Primary Orchestrator
end note

== PRV-01 Initialize Provider ==

user -> parser : nasim --provider ollama
parser -> parser : parse args -> Config
parser -> factory : create_provider(config)
factory -> factory : lookup config.provider

alt provider = "ollama"
    factory -> proto : OllamaProvider(url, model, timeout)
else provider = "openai"
    factory -> proto : OpenAIProvider(api_key, model)
else provider = "anthropic"
    factory -> proto : AnthropicProvider(api_key, model)
end

break Unknown provider type
    factory -> factory : raise ConfigError("Unknown provider: X")
    factory --> parser : ConfigError
    parser --> user : error message
end

factory --> parser : Provider instance
parser --> user : Provider ready

note over user, proto
  Flow:    Config -> Factory -> provider class lookup -> instance
  State:   No state change
  Failure: Unknown provider type -> ConfigError
  Success: Provider instance ready for chat/stream
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/WRL/sq_wrl01_append_event.puml ---

@startuml sq_wrl01_append_event
' ============================================================
' Title:     WRL-01 — APPEND Event
' Boundary:  nasim code agent
' Purpose:   Append event to wire log
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — WRL-01 APPEND Event

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Layer" #E0F2F1
  participant "WireLog" as wirelog
  participant "WireAppender" as appender
end box
box "External" #F5F5F5
  participant "Host Filesystem" as fs
end box

note over agent, fs
  Scope:          Append event to wire log
  Preconditions:  Wire log file path configured, write access available
  Excludes:       Log reading (WRL-02), session forking (WRL-04)
  Contexts:       Called on every significant agent event; prerequisite for WRL-02/03/04
  Rollback:       Write failure -> event lost, log warning
  Design:         WireAppender appends serialized events; append-only log; buffered writes with flush on session end
  Classification: Primary Orchestrator
end note

== WRL-01 APPEND Event ==

agent -> wirelog : APPEND_EVENT(event)
activate wirelog

wirelog -> appender : serialize(event)
activate appender
appender --> wirelog : serialized_event
deactivate appender

wirelog -> wirelog : add_metadata(serialized_event, session_id, timestamp)

wirelog -> fs : append_file(log_path, serialized_event)
activate fs

break Write failure
    fs --> wirelog : IOError
    wirelog --> agent : AppendError("write failed")
end

fs --> wirelog : write_result
deactivate fs

wirelog --> agent : AppendResult(event_id, offset)
deactivate wirelog

note over agent, fs
  Flow:    AgentOrchestrator -> WireLog -> WireAppender -> Host Filesystem -> AppendResult
  State:   No state change
  Failure: Write failure -> event lost, warning logged
  Success: AppendResult with event_id and offset
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/WRL/sq_wrl04_fork_session.puml ---

@startuml sq_wrl04_fork_session
' ============================================================
' Title:     WRL-04 — Fork Session
' Boundary:  nasim code agent CLI
' Purpose:   Fork session at any turn
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Layer" #FFF3E0
  participant "WireLogger" as logger
  participant "SessionForker" as forker
end box
box "Session Layer" #E8F5E9
  participant "SessionManager" as session
end box

note over user, session
  Scope:
    - wrl03 FORK Session — fork session at any turn

  Preconditions:
    - Wire log has events for source session
    - SessionManager available for new session creation

  Contexts:
    - Called when user wants to branch from a specific turn
    - Uses WRL-02 (Read Log) to get events up to fork point

  Excludes:
    - Log reading (handled by WRL-02)
    - Session replay (handled by WRL-04)
    - Event writing (handled by WRL-01)

  Rollback:
    - Fork failure → no new session created

  Design:
  Classification: Primary Orchestrator
    - SessionForker reads events up to fork_point from wire log
    - Creates new session with copied event history
    - New session gets unique session_id
    - Fork point marked in wire log for traceability

  Returns:
    - Success: ForkResult with new_session_id and fork_point
    - Failure: ForkError with details
end note

== wrl03 FORK Session ==

agent -> forker : FORK_SESSION(source_session_id, fork_turn)
activate forker

forker -> logger : READ_LOG(source_session_id, up_to_turn=fork_turn)
activate logger
logger --> forker : events[]
deactivate logger

forker -> session : CREATE_SESSION(forked_from=source_session_id)
activate session
session --> forker : new_session_id
deactivate session

forker -> forker : copy_events_to_session(events, new_session_id)

forker -> logger : APPEND_EVENT(ForkEvent(source, fork_point, new_session_id))
activate logger
logger --> forker : append_success
deactivate logger

forker --> agent : ForkResult(new_session_id, fork_turn, event_count)
deactivate forker

note over user, session
  Flow:
    - AgentOrchestrator → SessionForker → WireLogger + SessionManager → ForkResult

  State:
    - <back:#ECEFF1>IDLE</back> → READING → CREATING → COPYING → DONE

  Failure:
    - Fork failure → no session created

  Success:
    - ForkResult with new session ID

  Key invariants:
    - Fork point always recorded in wire log
    - New session gets unique ID
    - Events copied atomically (all or none)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/WRL/sq_wrl02_read_log.puml ---

@startuml sq_wrl02_read_log
' ============================================================
' Title:     WRL-02 — READ Log (Sequential Scan for Replay)
' Boundary:  nasim code agent CLI
' Purpose:   Sequential scan for replay
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Layer" #FFF3E0
  participant "WireLogger" as logger
  participant "EventDeserializer" as deserializer
end box
box "FileSystem Layer" #F3E5F5
  participant "FileSystem" as fs
end box

note over user, fs
  Scope:
    - wrl02 READ Log — sequential scan for replay

  Preconditions:
    - Wire log file exists with events
    - FileSystem read access available

  Contexts:
    - Called by WRL-03 (Fork Session) and WRL-04 (Replay Session)
    - Provides event stream for session reconstruction

  Excludes:
    - Event writing (handled by WRL-01)
    - Session forking (handled by WRL-03)
    - Session replay (handled by WRL-04)

  Rollback:
    - Read failure → return partial events with error

  Design:
  Classification: Primary Orchestrator
    - WireLogger reads log file sequentially
    - EventDeserializer parses each line into Event objects
    - Supports filtering by session_id and event type
    - Streaming read for memory efficiency

  Returns:
    - Success: EventStream with deserialized events
    - Failure: EventStream with partial results and error
end note

== wrl02 READ Log ==

agent -> logger : READ_LOG(session_id, filter)
activate logger

logger -> fs : read_file(log_path)
activate fs
fs --> logger : raw_lines[]
deactivate fs

loop for each raw_line
    logger -> deserializer : deserialize(raw_line)
    activate deserializer
    deserializer --> logger : event
    deactivate deserializer

    logger -> logger : apply_filter(event, session_id, filter)
end

logger -> logger : collect_matching_events()

logger --> agent : EventStream(events[], count, truncated)
deactivate logger

note over user, fs
  Flow:
    - AgentOrchestrator → WireLogger → FileSystem + EventDeserializer → EventStream

  State:
    - <back:#ECEFF1>IDLE</back> → READING → DESERIALIZING → FILTERING → DONE

  Failure:
    - Read failure → partial events + error

  Success:
    - EventStream with matching events

  Key invariants:
    - Sequential read (no random access)
    - Each line deserialized independently
    - Filtering is optional (returns all events if no filter)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/WRL/sq_wrl03_seek_turn.puml ---

@startuml sq_wrl03_seek_turn
' ============================================================
' Title:     WRL-03 — SEEK Turn
' Boundary:  nasim code agent
' Purpose:   Seek to a specific turn in the wire log
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — WRL-03 SEEK Turn

box "Wire Log Group" #FFFDE7
  participant "TurnIndex" as idx
  participant "WireReader" as reader
end box

note over idx, reader
  Scope:          Seek to a specific turn in the wire log
  Preconditions:  Wire log exists, TurnIndex built
  Excludes:       Log append (WRL-01), session fork (WRL-04)
  Contexts:       Called by WRL-04 FORK Session or replay flows
  Rollback:       N/A (read-only)
  Design:         Uses TurnIndex for O(1) random access by turn number
  Classification: Process Decomposition
end note

== WRL-03 SEEK Turn ==

idx -> idx : LOOKUP turn_number
idx -> reader : READ from offset
activate reader

break Turn not found
  reader --> idx : NotFound
  idx --> idx : return error
end

reader --> idx : WireEvents[turn]
deactivate reader

note over idx, reader
  Flow:    TurnIndex -> lookup offset -> WireReader -> read events for turn
  State:   No state change
  Failure: Turn not found in index
  Success: Wire events for the requested turn
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/WRL/sq_wrl05_checkpoint_turn.puml ---

@startuml sq_wrl05_checkpoint_turn
' ============================================================
' Title:     WRL-05 — CHECKPOINT Turn
' Boundary:  nasim code agent
' Purpose:   Index current turn and persist checkpoint for resumption
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — WRL-05 CHECKPOINT Turn

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Layer" #FFFDE7
  participant "WireLog" as wl
  participant "TurnIndex" as ti
end box
box "FileSystem Layer" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Index current conversation turn and persist checkpoint for session resumption
  Preconditions:  Turn data available, wire log initialized
  Excludes:       Event appending (WRL-01), log reading (WRL-02), session forking (WRL-04)
  Contexts:       Called at turn boundaries or on-demand for persistence
  Rollback:       Write failure → checkpoint not persisted, warning logged
  Design:         TurnIndex extracts turn metadata, builds checkpoint, persists to filesystem
  Classification: Process Decomposition
end note

== WRL-05 CHECKPOINT Turn ==

agent -> wl : CHECKPOINT_TURN(turn_data)
activate wl

wl -> ti : index_turn(turn_data)
activate ti

ti -> ti : extract_turn_metadata(turn_data)

ti -> ti : build_checkpoint_index(metadata)

ti -> fs : persist_checkpoint(checkpoint_index)
activate fs
fs --> ti : persist_result
deactivate fs

ti --> wl : CheckpointResult(turn_id, offset)
deactivate ti

wl --> agent : CheckpointResult
deactivate wl

note over participants
  Flow:    WireLog -> TurnIndex -> index current turn -> persist checkpoint
  State:   <back:#ECEFF1>IDLE</back> → INDEXING → PERSISTING → DONE
  Failure: Write failure → checkpoint not persisted, warning logged
  Success: CheckpointResult with turn_id and file offset
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn02_read_session.puml ---

@startuml sq_ssn02_read_session
' ============================================================
' Title:     SSN-02 — Read Session
' Boundary:  nasim code agent CLI
' Purpose:   Load conversation history from disk
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Layer" #F1F8E9
  participant "SessionStore" as store
end box
database "Session Directory" as dir

note over agent, dir
  Scope:          Load session messages from JSON Lines file
  Preconditions:  Session ID provided (--continue or --session)
  Contexts:       Called by CLI-04 or SSN-04 (Resume Session)
  Excludes:       Session saving (SSN-01)
  Rollback:       Not found -> start fresh session
  Design:         Deserialize JSON Lines back to message list
  Classification: Process Decomposition
end note

== SSN-02 Load Session ==

agent -> store : load(session_id)
store -> dir : read session.jsonl

break Session file not found
    dir --> store : FileNotFoundError
    store --> agent : FileNotFoundError
    agent -> agent : start fresh session
end

store -> store : deserialize JSON Lines -> messages
store --> agent : Session(id, created_at, messages)

note over agent, dir
  Flow:    session_id -> read file -> deserialize -> Session
  State:   No state change
  Failure: File not found -> start fresh
  Success: Session with restored messages
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn07_search_sessions.puml ---

@startuml sq_ssn07_search_sessions
' ============================================================
' Title:     SSN-07 — Search Sessions
' Boundary:  nasim code agent CLI
' Purpose:   Full-text search across session history
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-07 Search Sessions

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Layer" #F1F8E9
  participant "SessionSearch" as search
end box
database "FTS5 Index" as fts

note over agent, fts
  Scope:          Full-text search across all session history
  Preconditions:  FTS5 index built on session messages
  Excludes:       Session read (SSN-02), session persist (SSN-01)
  Contexts:       Called when user searches past conversations
  Rollback:       Index missing → fallback to linear scan
  Design:         FTS5 for fast search; results ranked by relevance
  Classification: Process Decomposition
end note

== SSN-07 Search Sessions ==

agent -> search : search(query, limit)
activate search

search -> fts : FTS5 query(query)
activate fts
fts --> search : raw_results [session_id, turn_id, snippet, rank]
deactivate fts

search -> search : rank results by relevance
search -> search : format snippets

search --> agent : SearchResult[session_id, turn_id, snippet, score]
deactivate search

break Index not available
    fts --> search : IndexError
    search -> search : fallback: linear scan
    search --> agent : SearchResult[linear_scan_results]
end

note over agent, fts
  Flow:    AgentOrchestrator → SessionSearch → FTS5 query → rank → return
  State:   No state change (read-only query)
  Failure: Index missing → linear scan fallback
  Success: Ranked search results returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn03_list_sessions.puml ---

@startuml sq_ssn03_list_sessions
' ============================================================
' Title:     SSN-03 — List Sessions
' Boundary:  nasim code agent CLI
' Purpose:   List available saved sessions
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Session Layer" #F1F8E9
  participant "SessionStore" as store
end box
database "Session Directory" as dir

note over user, dir
  Scope:          List all saved sessions with metadata
  Preconditions:  /sessions command entered
  Contexts:       Called by CLI-02 (Execute Slash Command)
  Excludes:       Session save/load
  Rollback:       No sessions -> empty list
  Design:         Scans ~/.nasim/sessions/ for session dirs
  Classification: Primary Orchestrator
end note

== SSN-03 List Sessions ==

repl -> store : list_sessions()
store -> dir : scan ~/.nasim/sessions/

break No sessions directory
    dir --> store : FileNotFoundError
    store --> repl : [] (empty list)
end

store -> store : read metadata from each session
store --> repl : [(id, created_at, message_count), ...]
repl -> repl : format session table
repl --> user : session list display

note over user, dir
  Flow:    scan directory -> read metadata -> list
  State:   No state change
  Failure: No directory -> empty list
  Success: Formatted list of sessions
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn06_revert_turn.puml ---

@startuml sq_ssn06_revert_turn
' ============================================================
' Title:     SSN-06 — Revert Turn
' Boundary:  nasim code agent CLI
' Purpose:   Restore session to a previous snapshot or turn
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-06 Revert Turn

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Layer" #F1F8E9
  participant "SessionVersioning" as ver
end box
database "Snapshot Store" as snap

note over agent, snap
  Scope:          Restore session to a previous snapshot or specific turn
  Preconditions:  Snapshot exists (created via SSN-05)
  Excludes:       Snapshot creation (SSN-05), session persistence (SSN-01)
  Contexts:       Called when user requests undo or revert
  Rollback:       Snapshot not found → display error, retain current state
  Design:         Revert replaces current messages with snapshot copy
  Classification: Process Decomposition
end note

== SSN-06 Revert Turn ==

agent -> ver : revert(session_id, snapshot_id)
activate ver

ver -> snap : load snapshot(snapshot_id)
activate snap
alt snapshot found
    snap --> ver : snapshot_messages
    deactivate snap
else snapshot not found
    snap --> ver : NotFound
    deactivate snap
    ver --> agent : RevertError("snapshot not found")
end

ver -> ver : replace current messages with snapshot
ver -> ver : truncate messages after snapshot point

ver --> agent : Reverted(snapshot_id, turn_count)
deactivate ver

break Snapshot load error
    snap --> ver : IOError
    ver --> agent : RevertError("snapshot unreadable")
end

note over agent, snap
  Flow:    AgentOrchestrator → SessionVersioning → find snapshot → restore to turn
  State:   <back:#2E7D32>ACTIVE</back> → REVERTING → <back:#2E7D32>ACTIVE</back>
  Failure: Snapshot not found → error, retain current
  Success: Session restored to snapshot point
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn01_persist_session.puml ---

@startuml sq_ssn01_persist_session
' ============================================================
' Title:     SSN-01 — Persist Session
' Boundary:  nasim code agent CLI
' Purpose:   Persist conversation history to disk
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Layer" #F1F8E9
  participant "SessionStore" as store
end box
database "Session Directory" as dir

note over agent, dir
  Scope:          Save session messages to JSON Lines file
  Preconditions:  AgentOrchestrator has messages to save
  Contexts:       Called by AGT-01 after each task turn
  Excludes:       Session loading (SSN-02)
  Rollback:       Write error -> log warning, session lost
  Design:         One file per session: ~/.nasim/sessions/<id>/session.jsonl
  Classification: Process Decomposition
end note

== SSN-01 Save Session ==

agent -> store : save(session_id, messages)
store -> store : serialize messages to JSON Lines
store -> dir : write session.jsonl

break Disk write error
    dir --> store : IOError
    store -> agent : log warning("Session save failed")
end

store --> agent : save complete

note over agent, dir
  Flow:    messages -> serialize -> write JSON Lines
  State:   No state change
  Failure: Disk error -> log warning, continue
  Success: Session persisted to disk
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn08_branch_session.puml ---

@startuml sq_ssn08_branch_session
' ============================================================
' Title:     SSN-08 — Branch Session
' Boundary:  nasim code agent CLI
' Purpose:   Fork session into a new branch for parallel exploration
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-08 Branch Session

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Layer" #F1F8E9
  participant "SessionFork" as fork
end box
database "Session Store" as store

note over agent, store
  Scope:          Fork current session into a new branch
  Preconditions:  Active session with message history
  Excludes:       Session revert (SSN-06), session search (SSN-07)
  Contexts:       Called when user requests to explore alternative path
  Rollback:       Fork failure → display error, retain current session
  Design:         Branch copies messages up to fork point; new session gets unique ID
  Classification: Process Decomposition
end note

== SSN-08 Branch Session ==

agent -> fork : branch(session_id, from_turn)
activate fork

fork -> store : load messages up to from_turn
activate store
store --> fork : messages_subset
deactivate store

fork -> fork : generate new session_id
fork -> store : create branch session
activate store
store --> fork : branch_session_id
deactivate store

fork -> fork : copy messages to branch
fork -> fork : create parent-child link

fork --> agent : BranchCreated(branch_session_id, parent_id)
deactivate fork

break Copy failure
    store --> fork : IOError
    fork --> agent : BranchError
    agent -> agent : log error, retain current session
end

note over agent, store
  Flow:    AgentOrchestrator → SessionFork → copy session → create branch
  State:   <back:#2E7D32>ACTIVE</back> → BRANCHING → <back:#2E7D32>ACTIVE</back> (parent + child)
  Failure: Copy error → display error, retain current
  Success: Branch session created, new session_id returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn09_delete_session.puml ---

@startuml sq_ssn09_delete_session
' ============================================================
' Title:     SSN-09 — DELETE Session
' Boundary:  nasim code agent
' Purpose:   Permanently delete a session and its associated data
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-09 DELETE Session

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Layer" #F3E5F5
  participant "SessionStore" as store
end box
box "External" #F5F5F5
  participant "Host Filesystem" as fs
end box

note over agent, fs
  Scope:          Permanently delete a session and its associated data
  Preconditions:  Session exists on disk
  Excludes:       Soft delete/retire (SRV-05), session read (SSN-02)
  Contexts:       Called by SRV-05 (RETIRE Session) for hard delete
  Rollback:       Deletion is irreversible; backup recommended
  Design:         Removes session directory and all associated files
  Classification: Process Decomposition
end note

== SSN-09 DELETE Session ==

agent -> store : DELETE(session_id)
activate store

store -> store : validate_session_exists(session_id)

break Session not found
    store --> agent : DeleteError("session not found")
end

store -> fs : remove_directory(session_path)
activate fs

break Permission denied
    fs --> store : PermissionError
    store --> agent : DeleteError("permission denied")
end

fs --> store : removed
deactivate fs

store -> store : clear_session_index(session_id)

store --> agent : delete_confirmed(session_id)
deactivate store

note over agent, fs
  Flow:    AgentOrchestrator -> SessionStore -> validate -> remove directory -> clear index -> confirm
  State:   <back:#757575>CLOSED</back>
  Failure: Session not found or permission denied -> DeleteError
  Success: Session permanently deleted
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn05_snapshot_session.puml ---

@startuml sq_ssn05_snapshot_session
' ============================================================
' Title:     SSN-05 — Snapshot Session
' Boundary:  nasim code agent CLI
' Purpose:   Create a point-in-time snapshot of session state
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-05 Snapshot Session

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Layer" #F1F8E9
  participant "SessionVersioning" as ver
end box
database "Snapshot Store" as snap

note over agent, snap
  Scope:          Create a point-in-time snapshot of session messages
  Preconditions:  Active session with messages
  Excludes:       Session read (SSN-02), revert (SSN-06)
  Contexts:       Called before risky operations or on explicit request
  Rollback:       Snapshot failure → log warning, continue without snapshot
  Design:         Snapshot stored as immutable copy; supports revert via SSN-06
  Classification: Process Decomposition
end note

== SSN-05 Snapshot Session ==

agent -> ver : snapshot(session_id)
activate ver

ver -> ver : serialize current messages
ver -> snap : write snapshot (immutable copy)
activate snap
snap --> ver : snapshot_id
deactivate snap

ver --> agent : SnapshotCreated(snapshot_id)
deactivate ver

break Disk write error
    snap --> ver : IOError
    ver --> agent : SnapshotError
    agent -> agent : log warning, continue without snapshot
end

note over agent, snap
  Flow:    AgentOrchestrator → SessionVersioning → create snapshot → store
  State:   No state change (snapshot is side-effect)
  Failure: Disk error → log warning, continue
  Success: Snapshot ID returned for future revert (SSN-06)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn04_restore_session.puml ---

@startuml sq_ssn04_restore_session
' ============================================================
' Title:     SSN-04 — Restore Session
' Boundary:  nasim code agent CLI
' Purpose:   Resume a previous session by loading its history
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Session Layer" #F1F8E9
  participant "SessionStore" as store
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box

note over user, agent
  Scope:          Resume session from --continue or --session flag
  Preconditions:  CLI invoked with --continue or --session <id>
  Contexts:       Called by CLI-04 (Parse CLI Arguments)
  Excludes:       New session creation
  Rollback:       No session found -> start fresh
  Design:         --continue loads latest; --session loads by ID
  Classification: Primary Orchestrator
end note

== SSN-04 Resume Session ==

user -> repl : nasim --continue (or --session <id>)
repl -> store : load_latest() or load(session_id)
ref over store
  SSN-02: Load Session
end ref

alt Session found
    store --> repl : Session(id, messages)
    repl -> agent : restore messages
    agent -> agent : set self.messages = session.messages
    repl --> user : "Resumed session <id> (<N> messages)"
else Session not found
    store --> repl : FileNotFoundError
    repl -> agent : start fresh
    repl --> user : "No session found, starting fresh"
end

note over user, agent
  Flow:    --continue -> load_latest -> restore messages -> continue
  State:   No state change
  Failure: No session -> start fresh
  Success: Conversation restored, ready for input
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg04_register_plugin_hooks.puml ---

@startuml sq_plg04_register_plugin_hooks
' ============================================================
' Title:     PLG-04 — Register Plugin Hooks
' Boundary:  nasim code agent
' Purpose:   Register all hooks declared in a plugin manifest
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PLG-04 Register Plugin Hooks

box "Tool Layer" #F3E5F5
  participant "PluginLoader" as loader
end box
box "Hooks Layer" #FFFDE7
  participant "HookManager" as hm
end box

note over participants
  Scope:          Register plugin-declared hooks into HookManager
  Preconditions:  Valid PluginManifest loaded (PLG-02)
  Excludes:       Tool registration, plugin activation
  Contexts:       Called during plugin enable (PLG-05)
  Rollback:       Registration failure logged; other hooks still registered
  Design:         Plugin hooks prefixed with plugin name
  Classification: Process Decomposition
end note

== PLG-04 Register Plugin Hooks ==

loader -> loader : enumerate hooks from PluginManifest

loop for each hook in manifest
    loader -> hm : register(event, handler, priority)

    break Registration failure
        hm --> loader : RegistrationError
        loader --> loader : log warning, skip hook
    end

    hm --> loader : registered
end

loader --> loader : all hooks registered

note over participants
  Flow:    PluginLoader -> enumerate plugin hooks -> register in HookManager
  State:   Hooks added to HookManager
  Failure: Registration failure -> hook skipped with warning
  Success: All plugin hooks registered
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg06_disable_plugin.puml ---

@startuml sq_plg06_disable_plugin
' ============================================================
' Title:     PLG-06 — Disable Plugin
' Boundary:  nasim code agent
' Purpose:   Deactivate plugin tools and hooks, set state DISABLED
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PLG-06 Disable Plugin

box "Tool Layer" #F3E5F5
  participant "PluginLoader" as loader
  participant "ToolRegistry" as registry
end box
box "Hooks Layer" #FFFDE7
  participant "HookManager" as hm
end box

note over participants
  Scope:          Deactivate plugin tools and hooks, set state DISABLED
  Preconditions:  Plugin is currently ENABLED
  Excludes:       Plugin enable, discovery, removal
  Contexts:       Called by CLI or PluginLoader
  Rollback:       Partial disable logged; state set to ERROR
  Design:         Reverse of PLG-05; unregister tools then hooks
  Classification: Process Decomposition
end note

== PLG-06 Disable Plugin ==

loader -> registry : unregister plugin tools
loader -> hm : unregister plugin hooks
loader -> loader : set state DISABLED

break Unregister failure
    loader -> loader : set state ERROR, log failure
end

loader --> loader : plugin disabled

note over participants
  Flow:    PluginLoader -> deactivate tools + hooks -> set state DISABLED
  State:   Plugin state: ENABLED -> DISABLED (or ERROR)
  Failure: Unregister failure -> state ERROR, partial disable logged
  Success: Plugin disabled with tools and hooks removed
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg02_load_manifest.puml ---

@startuml sq_plg02_load_manifest
' ============================================================
' Title:     PLG-02 — Load Manifest
' Boundary:  nasim code agent
' Purpose:   Read and parse a plugin's manifest.yaml file
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PLG-02 Load Manifest

box "Plugins Layer" #EDE7F6
  participant "PluginLoader" as loader
end box
participant "Host Filesystem" as fs

note over participants
  Scope:          Read manifest.yaml and parse plugin metadata
  Preconditions:  Plugin directory exists
  Excludes:       Tool/hook registration, plugin activation
  Contexts:       Called during plugin discovery (PLG-01)
  Rollback:       Plugin skipped with warning
  Design:         Strict schema validation; fail-fast on malformed YAML
  Classification: Process Decomposition
end note

== PLG-02 Load Manifest ==

loader -> fs : read(manifest.yaml)

break File not found
    fs --> loader : FileNotFoundError
    loader --> loader : skip plugin, log warning
end

break YAML parse error
    fs --> loader : valid YAML
    loader -> loader : validate schema
    loader --> loader : skip plugin, log error
end

fs --> loader : raw YAML content
loader -> loader : parse metadata (name, version, tools, hooks)
loader --> loader : return PluginManifest

note over participants
  Flow:    PluginLoader -> read manifest.yaml -> parse metadata -> return PluginManifest
  State:   No state change
  Failure: File not found or malformed YAML -> plugin skipped
  Success: Validated PluginManifest returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg03_register_plugin_tools.puml ---

@startuml sq_plg03_register_plugin_tools
' ============================================================
' Title:     PLG-03 — Register Plugin Tools
' Boundary:  nasim code agent
' Purpose:   Register all tools declared in a plugin manifest
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PLG-03 Register Plugin Tools

box "Tool Layer" #F3E5F5
  participant "PluginLoader" as loader
  participant "ToolRegistry" as registry
end box

note over participants
  Scope:          Register plugin-declared tools into ToolRegistry
  Preconditions:  Valid PluginManifest loaded (PLG-02)
  Excludes:       Hook registration, plugin activation
  Contexts:       Called during plugin enable (PLG-05)
  Rollback:       Registration failure logged; other tools still registered
  Design:         Namespaced tool names to avoid collisions
  Classification: Process Decomposition
end note

== PLG-03 Register Plugin Tools ==

loader -> loader : enumerate tools from PluginManifest

loop for each tool in manifest
    loader -> registry : register(plugin::tool_name, handler)

    break Name collision
        registry --> loader : CollisionError
        loader --> loader : log warning, skip tool
    end

    registry --> loader : registered
end

loader --> loader : all tools registered

note over participants
  Flow:    PluginLoader -> enumerate plugin tools -> register in ToolRegistry
  State:   Tools added to registry
  Failure: Name collision -> tool skipped with warning
  Success: All plugin tools registered
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg05_enable_plugin.puml ---

@startuml sq_plg05_enable_plugin
' ============================================================
' Title:     PLG-05 — Enable Plugin
' Boundary:  nasim code agent
' Purpose:   Load plugin and activate its tools and hooks
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PLG-05 Enable Plugin

box "Tool Layer" #F3E5F5
  participant "PluginLoader" as loader
  participant "ToolRegistry" as registry
end box
box "Hooks Layer" #FFFDE7
  participant "HookManager" as hm
end box

note over participants
  Scope:          Load plugin, register tools and hooks, set state ENABLED
  Preconditions:  Valid PluginManifest loaded (PLG-02)
  Excludes:       Plugin discovery, disable
  Contexts:       Called by CLI or PluginLoader
  Rollback:       Partial enable logged; state set to ERROR
  Design:         Atomic enable: tools + hooks + state
  Classification: Process Decomposition
end note

== PLG-05 Enable Plugin ==

loader -> loader : PLG-03 register_plugin_tools()
loader -> loader : PLG-04 register_plugin_hooks()
loader -> loader : set state ENABLED

break Tool or hook registration fails
    loader -> loader : set state ERROR, log failure
end

loader --> loader : plugin enabled

note over participants
  Flow:    PluginLoader -> load plugin -> activate tools + hooks -> set state ENABLED
  State:   Plugin state: DISABLED -> ENABLED (or ERROR)
  Failure: Registration failure -> state ERROR, partial enable logged
  Success: Plugin enabled with tools and hooks active
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg01_discover_plugins.puml ---

@startuml sq_plg01_discover_plugins
' ============================================================
' Title:     PLG-01 — DISCOVER Plugins
' Boundary:  nasim code agent
' Purpose:   Discover plugins from plugin directory
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PLG-01 DISCOVER Plugins

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Plugins Layer" #EDE7F6
  participant "PluginLoader" as loader
end box
participant "Host Filesystem" as fs

note over agent, fs
  Scope:          Discover plugins from plugin directory
  Preconditions:  Plugin directory configured (~/.nasim/plugins/)
  Excludes:       Tool/hook registration (PLG-03/04), activation (PLG-05)
  Contexts:       Called during agent initialization
  Rollback:       Malformed plugins skipped with warning
  Design:         Scan plugin directory for manifest.yaml files
  Classification: Primary Orchestrator
end note

== PLG-01 DISCOVER Plugins ==

agent -> loader : discover(plugin_dir)
activate loader

loader -> fs : scan(plugin_dir)
activate fs
fs --> loader : plugin_directories[]
deactivate fs

loop for each plugin directory
    loader -> loader : PLG-02 load_manifest()

    break Manifest load fails
        loader --> loader : skip plugin, log warning
    end

    loader --> loader : append to discovered list
end

loader --> agent : list[PluginManifest]
deactivate loader

note over agent, fs
  Flow:    AgentOrchestrator -> PluginLoader -> scan directory -> load manifests -> return list
  State:   <back:#ECEFF1>DISCOVERED</back>
  Failure: Malformed plugin skipped with warning
  Success: List of discovered PluginManifests returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SAF/sq_saf01_check_permission.puml ---

@startuml sq_saf01_check_permission
' ============================================================
' Title:     SAF-01 — CHECK Permission
' Boundary:  nasim code agent
' Purpose:   Per-tool safety check before execution (internal step of AGT-15)
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Prompt audit 2026-06-21 (gro.md: God Object residual fixed)
' Note:      Process decomposition — internal step of AGT-15. No actor per sq.md rules.
' ============================================================

title nasim — SAF-01 CHECK Permission

box "Agent Layer" #E3F2FD
  participant "SafetyCoordinator" as safety
  participant "PermissionGate" as gate
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over safety, registry
  Scope:          Check tool permission before execution
  Preconditions:  Tool call received from LLM, SafetyCoordinator initialized
  Contexts:       Called by AGT-15 (DISPATCH Safety Pipeline)
  Excludes:       User approval prompt (SAF-02), injection/egress checks
  Rollback:       Rejected -> SafetyViolation returned to caller
  Design:         SafetyCoordinator delegates to PermissionGate for safe-flag check
  Classification: Process Decomposition
end note

== SAF-01 CHECK Permission ==

safety -> gate : check(tool_name, safety_mode)
activate gate

gate -> registry : get_tool(tool_name)
activate registry
registry --> gate : Tool(safe=True/False)
deactivate registry

gate -> gate : check tool.safe against safety_mode

alt tool.safe = True
    gate --> safety : SafetyPassed
else tool.safe = False AND safety_mode = "auto"
    gate --> safety : SafetyPassed
else tool.safe = False AND safety_mode = "ask"
    gate --> safety : SafetyViolation(permission_denied)
else safety_mode = "off"
    gate --> safety : SafetyPassed
end

deactivate gate

note over safety, registry
  Flow:    SafetyCoordinator -> PermissionGate -> ToolRegistry.get_tool() -> check safe flag -> return
  State:   No state change (delegated by AGT-15)
  Failure: Unsafe tool in ask/off mode -> SafetyViolation
  Success: SafetyPassed -> proceed to next pipeline stage
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SAF/sq_saf03_apply_safety_mode.puml ---

@startuml sq_saf03_apply_safety_mode
' ============================================================
' Title:     SAF-03 — Apply Safety Mode
' Boundary:  nasim code agent CLI
' Purpose:   Configure safety mode from config
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Config Layer" #E0F7FA
  participant "ConfigLoader" as cfg
end box
box "Agent Layer" #E3F2FD
  participant "PermissionGate" as gate
end box

note over cfg, gate
  Scope:          Apply safety mode from config to PermissionGate
  Preconditions:  Config loaded with safety_mode field
  Contexts:       Called during AgentOrchestrator initialization
  Excludes:       Runtime permission checks (SAF-01)
  Rollback:       N/A — mode is always set
  Design:         ask | auto | off — set once at startup
  Classification: Process Decomposition
end note

== SAF-03 Apply Safety Mode ==

cfg -> gate : apply_mode(config.safety_mode)
gate -> gate : self.mode = config.safety_mode

note over cfg, gate
  Flow:    config.safety_mode -> PermissionGate.mode
  State:   No state change
  Failure: N/A
  Success: Safety mode configured
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SAF/sq_saf02_prompt_user_approval.puml ---

@startuml sq_saf02_prompt_user_approval
' ============================================================
' Title:     SAF-02 — Prompt User Approval
' Boundary:  nasim code agent CLI
' Purpose:   Display approval prompt for unsafe tool execution
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "PermissionGate" as gate
end box
box "CLI Layer" #E8F5E9
  participant "Renderer" as renderer
end box

note over user, gate
  Scope:          Prompt user for approval of unsafe tool
  Preconditions:  safety_mode=ask AND tool.safe=False
  Contexts:       Called by SAF-01 (CHECK Tool Permission)
  Excludes:       Permission check logic (SAF-01)
  Rollback:       User rejects -> tool skipped
  Design:         Shows tool name + args, prompts [y/N]
  Classification: Primary Orchestrator
end note

== SAF-02 Prompt User Approval ==

gate -> renderer : display_approval(tool_name, args)
renderer --> user : "Allow <tool_name>(<args>)? [y/N]"

user -> renderer : y or N
renderer --> gate : choice (bool)

alt user = y
    renderer --> gate : approved
else user = N
    renderer --> gate : rejected
end

note over user, gate
  Flow:    gate -> Renderer -> user prompt -> choice -> gate
  State:   <back:#F3E5F5>TOOL_EXEC</back> -> <back:#FFF9C4>AWAITING_APPROVAL</back> -> <back:#F3E5F5>TOOL_EXEC</back> or <back:#ECEFF1>IDLE</back>
  Failure: User rejects -> tool skipped
  Success: User approves -> tool executes
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MEM/sq_mem03_search_knowledge.puml ---

@startuml sq_mem03_search_knowledge
' ============================================================
' Title:     MEM-03 — SEARCH Knowledge
' Boundary:  nasim code agent
' Purpose:   Full-text search across knowledge store
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — MEM-03 SEARCH Knowledge

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Memory Layer" #E0F2F1
  participant "MemoryIndex" as index
end box

note over agent, index
  Scope:          Full-text search across all knowledge
  Preconditions:  MemoryIndex populated with entries
  Excludes:       Direct key recall (MEM-02)
  Contexts:       Called by TL-20 (RECALL Memory), cross-project discovery
  Rollback:       No rollback needed (read-only operation)
  Design:         BM25 ranking with relevance scoring
  Classification: Process Decomposition
end note

== MEM-03 SEARCH Knowledge ==

agent -> index : search(query, filters)
activate index

index -> index : tokenize query
index -> index : FTS5 query with BM25 ranking
index -> index : rank results by relevance

break No results found
    index --> agent : empty list
end

index --> agent : ranked_results
deactivate index

note over agent, index
  Flow:    AgentOrchestrator -> MemoryIndex -> tokenize -> FTS5 query -> rank -> return
  State:   No state change
  Failure: No results -> return empty list, log query
  Success: Agent receives ranked search results
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MEM/sq_mem01_persist_knowledge.puml ---

@startuml sq_mem01_persist_knowledge
' ============================================================
' Title:     MEM-01 — PERSIST Knowledge
' Boundary:  nasim code agent
' Purpose:   Store cross-session knowledge entries
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — MEM-01 PERSIST Knowledge

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Memory Layer" #E0F2F1
  participant "MemoryStore" as store
  participant "MemoryScope" as scope
  participant "MemoryIndex" as index
end box

note over agent, index
  Scope:          Store cross-session knowledge entries
  Preconditions:  MemoryStore initialized, scope valid
  Excludes:       Search and recall (MEM-02, MEM-03)
  Contexts:       Called by TL-19 (PERSIST Memory), session checkpoint
  Rollback:       Transactional write with rollback on index failure
  Design:         Append-only store with index synchronization
  Classification: Process Decomposition
end note

== MEM-01 PERSIST Knowledge ==

agent -> store : persist(key, value, scope)
activate store

store -> scope : validate_scope(scope)
activate scope
scope --> store : scope_valid
deactivate scope

store -> store : write_to_disk(key, value)

break Disk write fails
    store --> agent : PersistError("write failed")
end

store -> index : index_entry(key, value, metadata)
activate index
index --> store : indexed
deactivate index

store --> agent : persist_confirmed(key)
deactivate store

note over agent, index
  Flow:    AgentOrchestrator -> MemoryStore -> validate scope -> write disk -> index -> confirm
  State:   No state change
  Failure: Disk write fails -> rollback, no index update
  Success: Entry persisted and indexed for search
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MEM/sq_mem04_scope_knowledge.puml ---

@startuml sq_mem04_scope_knowledge
' ============================================================
' Title:     MEM-04 — SCOPE Knowledge
' Boundary:  nasim code agent
' Purpose:   Filter knowledge by scope (global, project, session)
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — MEM-04 SCOPE Knowledge

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Memory Layer" #E0F2F1
  participant "MemoryScope" as scope
  participant "MemoryStore" as store
end box

note over agent, store
  Scope:          Scope-based filtering of knowledge entries
  Preconditions:  MemoryStore with multi-scope entries
  Excludes:       Search and recall (MEM-02, MEM-03)
  Contexts:       Called by MEM-01 and MEM-02 for scope validation
  Rollback:       No rollback needed (read-only operation)
  Design:         Three-level scope hierarchy: global > project > session
  Classification: Process Decomposition
end note

== MEM-04 SCOPE Knowledge ==

agent -> scope : filter(query, scope)
activate scope

scope -> scope : resolve_scope_hierarchy(scope)

scope -> store : get_entries_in_scope(scope)
activate store
store --> scope : entries
deactivate store

scope -> scope : apply scope mask

break Invalid scope
    scope --> agent : global scope entries (fallback)
end

scope --> agent : scoped_entries
deactivate scope

note over agent, store
  Flow:    AgentOrchestrator -> MemoryScope -> resolve hierarchy -> fetch entries -> apply mask -> return
  State:   No state change
  Failure: Invalid scope -> return global scope entries
  Success: Agent receives scope-filtered entries
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MEM/sq_mem02_recall_knowledge.puml ---

@startuml sq_mem02_recall_knowledge
' ============================================================
' Title:     MEM-02 — RECALL Knowledge
' Boundary:  nasim code agent
' Purpose:   Retrieve previously stored knowledge
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — MEM-02 RECALL Knowledge

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Memory Layer" #E0F2F1
  participant "MemoryStore" as store
  participant "MemoryScope" as scope
  participant "MemoryIndex" as index
end box

note over agent, index
  Scope:          Knowledge retrieval by key or pattern
  Preconditions:  Knowledge entries exist in store
  Excludes:       Full-text search (MEM-03), scope filtering (MEM-04)
  Contexts:       Called by TL-20 (RECALL Memory), session rebuild
  Rollback:       No rollback needed (read-only operation)
  Design:         Key-based lookup with scope filtering
  Classification: Process Decomposition
end note

== MEM-02 RECALL Knowledge ==

agent -> store : recall(key, scope)
activate store

store -> scope : filter_by_scope(key, scope)
activate scope
scope --> store : scoped_results
deactivate scope

store -> index : lookup(key)
activate index
index --> store : entry_data
deactivate index

break Key not found
    store --> agent : null
end

store --> agent : recalled_entry
deactivate store

note over agent, index
  Flow:    AgentOrchestrator -> MemoryStore -> filter by scope -> lookup key -> return entry
  State:   No state change
  Failure: Key not found -> return null, log miss
  Success: Agent receives knowledge entry
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/VCS/sq_vcs03_read_diff.puml ---

@startuml sq_vcs03_read_diff
' ============================================================
' Title:     VCS-03 — READ Diff
' Boundary:  nasim code agent
' Purpose:   Read diff of staged or unstaged changes
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — VCS-03 READ Diff

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Git Layer" #E8EAF6
  participant "GitStatus" as status
end box
box "External" #F5F5F5
  participant "Git Repository" as git
end box

note over agent, git
  Scope:          Diff inspection for staged/unstaged changes
  Preconditions:  Git repository with changes
  Excludes:       Commit operations (VCS-02)
  Contexts:       Pre-commit review, change inspection
  Rollback:       No rollback needed (read-only operation)
  Design:         Unified diff format with context lines
  Classification: Process Decomposition
end note

== VCS-03 READ Diff ==

agent -> status : get_diff(scope)
activate status

status -> git : git diff --cached (staged) or git diff (unstaged)
activate git
git --> status : raw_diff
deactivate git

status -> status : parse diff output

break No changes detected
    status --> agent : empty_diff
end

status --> agent : diff_content(files, hunks)
deactivate status

note over agent, git
  Flow:    AgentOrchestrator -> GitStatus -> determine scope -> execute git diff -> parse -> return
  State:   No state change
  Failure: No changes -> return empty diff
  Success: Agent receives diff content with file/hunk structure
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/VCS/sq_vcs02_insert_commit.puml ---

@startuml sq_vcs02_insert_commit
' ============================================================
' Title:     VCS-02 — INSERT Commit
' Boundary:  nasim code agent
' Purpose:   Create a commit with conventional message
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — VCS-02 INSERT Commit

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Git Layer" #E8EAF6
  participant "GitCommit" as commit
  participant "GitStatus" as status
end box
box "External" #F5F5F5
  participant "Git Repository" as git
end box

note over agent, git
  Scope:          Git commit creation with conventional format
  Preconditions:  Files staged, commit message valid
  Excludes:       Status checking (VCS-01), diff (VCS-03)
  Contexts:       Called by VCS-04 (AUTO-COMMIT), manual commit requests
  Rollback:       Reset HEAD if commit fails mid-operation
  Design:         Atomic commit with pre-commit hook validation
  Classification: Process Decomposition
end note

== VCS-02 INSERT Commit ==

agent -> commit : commit(message, files)
activate commit

commit -> status : check_staged()
activate status
status --> commit : staged_files
deactivate status

break No staged files
    commit --> agent : error("no staged files")
end

commit -> commit : validate_message(message)

break Invalid message format
    commit --> agent : error("invalid commit message")
end

commit -> git : git commit -m message
activate git
git --> commit : commit_output
deactivate git

commit --> agent : commit_result(hash, files)
deactivate commit

note over agent, git
  Flow:    AgentOrchestrator -> GitCommit -> check staged -> validate message -> commit -> return hash
  State:   No state change
  Failure: Pre-commit hook fails -> abort, return error
  Success: Agent receives commit hash and file list
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/VCS/sq_vcs01_read_git_status.puml ---

@startuml sq_vcs01_read_git_status
' ============================================================
' Title:     VCS-01 — READ Git Status
' Boundary:  nasim code agent
' Purpose:   Read working tree status and staged changes
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — VCS-01 READ Git Status

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Git Layer" #E8EAF6
  participant "GitStatus" as status
end box
box "External" #F5F5F5
  participant "Git Repository" as git
end box

note over agent, git
  Scope:          Git working tree status inspection
  Preconditions:  Git repository initialized
  Excludes:       Commit operations (VCS-02), diff (VCS-03)
  Contexts:       Called by TL-11 (READ Git Status), pre-commit validation
  Rollback:       No rollback needed (read-only operation)
  Design:         Cached status with file system watch invalidation
  Classification: Process Decomposition
end note

== VCS-01 READ Git Status ==

agent -> status : get_status()
activate status

status -> git : git status --porcelain
activate git
git --> status : raw_output
deactivate git

status -> status : parse status output

break Not a git repo
    status --> agent : error_status("not a git repository")
end

status --> agent : status_summary(staged, modified, untracked)
deactivate status

note over agent, git
  Flow:    AgentOrchestrator -> GitStatus -> execute git status -> parse -> return summary
  State:   No state change
  Failure: Not a git repo -> return error status
  Success: Agent receives staged/modified/untracked file lists
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/VCS/sq_vcs04_auto_commit.puml ---

@startuml sq_vcs04_auto_commit
' ============================================================
' Title:     VCS-04 — AUTO-COMMIT
' Boundary:  nasim code agent
' Purpose:   Automatically commit changes after edit operations
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — VCS-04 AUTO-COMMIT

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Git Layer" #E8EAF6
  participant "GitIntegration" as integration
  participant "GitStatus" as status
  participant "GitCommit" as commit
end box

note over agent, commit
  Scope:          Automatic commit after file edits
  Preconditions:  File edits completed, working tree dirty
  Excludes:       Manual commit (VCS-02)
  Contexts:       Post-edit hook, batch operation cleanup
  Rollback:       Skip commit if no changes detected
  Design:         Debounced auto-commit with conventional message generation
  Classification: Process Decomposition
end note

== VCS-04 AUTO-COMMIT ==

agent -> integration : auto_commit(edit_context)
activate integration

integration -> status : check_dirty()
activate status
status --> integration : is_dirty
deactivate status

break No changes detected
    integration --> agent : auto_commit_complete(noop)
end

integration -> commit : commit(generated_message, files)
activate commit
commit --> integration : commit_result(hash)
deactivate commit

integration --> agent : auto_commit_complete(hash)
deactivate integration

note over agent, commit
  Flow:    AgentOrchestrator -> GitIntegration -> check dirty -> generate message -> commit -> return
  State:   No state change
  Failure: No changes -> skip commit, return noop
  Success: Agent receives commit hash from auto-commit
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl07_record_quality_signal.puml ---

@startuml sq_evl07_record_quality_signal
' ============================================================
' Title:     EVL-07 — RECORD Quality Signal
' Boundary:  nasim code agent
' Purpose:   Record accept/reject quality signal with feedback
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EVL-07 RECORD Quality Signal

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #F9FBE7
  participant "EvaluationEngine" as engine
  participant "QualitySignal" as signal
end box
box "Storage Layer" #F3E5F5
  participant "SignalStore" as store
end box

note over participants
  Scope:          Record accept/reject quality signal with feedback for future reference
  Preconditions:  Evaluation completed, decision made (accept or reject)
  Excludes:       Evaluation logic, retry coordination
  Contexts:       Called after EVL-01..06 evaluation completes
  Rollback:       Storage failure → signal lost, warning logged
  Design:         QualitySignal persists accept/reject decision with contextual feedback
  Classification: Process Decomposition
end note

== EVL-07 RECORD Quality Signal ==

agent -> engine : RECORD_SIGNAL(task_id, decision, feedback?)
activate engine

engine -> signal : record_quality_signal(task_id, decision, feedback)
activate signal

signal -> signal : build_signal_record(task_id, decision, feedback, timestamp)

signal -> store : persist_signal(signal_record)
activate store
store --> signal : persist_result
deactivate store

signal --> engine : SignalRecorded(signal_id)
deactivate signal

engine --> agent : SignalRecorded
deactivate engine

note over participants
  Flow:    EvaluationEngine -> QualitySignal -> record accept/reject + feedback
  State:   <back:#ECEFF1>IDLE</back> → RECORDING → PERSISTED → DONE
  Failure: Storage failure → signal lost, warning logged
  Success: SignalRecorded with signal_id for future reference
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl04_validate_with_llm.puml ---

@startuml sq_evl04_validate_with_llm
' ============================================================
' Title:     EVL-04 — Validate With LLM
' Boundary:  nasim code agent CLI
' Purpose:   LLM-as-judge scoring for edit quality
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #FFF3E0
  participant "LLMReviewer" as reviewer
end box
box "Provider Layer" #E3F2FD
  participant "Provider" as provider
end box
box "Edit Layer" #FFF3E0
  participant "FileSystem" as fs
end box

note over user, fs
  Scope:
    - evl02 INVOKE LLM Reviewer — LLM-as-judge scoring for edit quality

  Preconditions:
    - Edit applied to file system
    - Provider available for LLM calls
    - Review prompt template configured

  Contexts:
    - Called after EVL-01 (Run Success Checks) as complementary evaluation
    - Provides semantic quality assessment beyond exit codes

  Excludes:
    - Shell-based checks (handled by EVL-01)
    - Retry coordination (handled by EVL-03)

  Rollback:
    - LLM call failure → skip review, proceed with exit code results only

  Design:
  Classification: Primary Orchestrator
    - LLMReviewer sends original + edited file to Provider
    - Prompt asks for quality score (1-10) and feedback
    - Score below threshold triggers retry via EVL-03
    - Review is non-blocking (failure doesn't block flow)

  Returns:
    - Success: ReviewResult with score and feedback
    - Failure: ReviewResult with skip flag
end note

== evl02 INVOKE LLM Reviewer ==

agent -> reviewer : REVIEW_EDIT(original_file, edited_file)
activate reviewer

reviewer -> fs : read_file(original_file)
activate fs
fs --> reviewer : original_content
deactivate fs

reviewer -> fs : read_file(edited_file)
activate fs
fs --> reviewer : edited_content
deactivate fs

reviewer -> reviewer : format_review_prompt(original_content, edited_content)

reviewer -> provider : chat(review_prompt)
activate provider
provider --> reviewer : review_response
deactivate provider

reviewer -> reviewer : parse_score_and_feedback(review_response)

reviewer -> reviewer : validate_score(score, min=1, max=10)

reviewer --> agent : ReviewResult(score, feedback, passed)
deactivate reviewer

note over user, fs
  Flow:
    - AgentOrchestrator → LLMReviewer → FileSystem + Provider → ReviewResult

  State:
    - <back:#ECEFF1>IDLE</back> → READING → PROMPTING → SCORING → DONE

  Failure:
    - LLM call failure → skip review
    - Parse failure → skip review

  Success:
    - ReviewResult with score and feedback

  Key invariants:
    - Review is non-blocking (failure doesn't stop flow)
    - Score always in range 1-10
    - Feedback always provided regardless of score
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl03_check_success.puml ---

@startuml sq_evl03_check_success
' ============================================================
' Title:     EVL-03 — CHECK Success
' Boundary:  nasim code agent
' Purpose:   Run user-defined success checks and return pass/fail
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EVL-03 CHECK Success

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #F9FBE7
  participant "EvaluationEngine" as engine
  participant "SuccessCheckRunner" as runner
end box
box "Tool Layer" #F3E5F5
  participant "ShellRunner" as shell
end box

note over participants
  Scope:          Run user-defined success checks and aggregate pass/fail
  Preconditions:  Success check commands configured, shell environment available
  Excludes:       Task completion evaluation (EVL-02), retry coordination (EVL-04)
  Contexts:       EVL-01 EVALUATE Task delegates success checks here
  Rollback:       No state change — read-only execution
  Design:         SuccessCheckRunner executes each check, captures exit codes and output
  Classification: Process Decomposition
end note

== EVL-03 CHECK Success ==

agent -> engine : CHECK_SUCCESS(check_commands[])
activate engine

engine -> runner : run_checks(check_commands)
activate runner

loop for each check_command
    runner -> shell : execute(check_command, timeout=30s)
    activate shell
    alt exit_code == 0
        shell --> runner : CheckOutput(exit_code=0, stdout)
    else exit_code != 0
        shell --> runner : CheckOutput(exit_code, stderr)
    end
    deactivate shell

    runner -> runner : record_result(check_command, output)
end

runner -> runner : aggregate_results()

runner --> engine : SuccessCheckResult(passed, results[])
deactivate runner

engine --> agent : SuccessCheckResult
deactivate engine

note over participants
  Flow:    EvaluationEngine -> SuccessCheckRunner -> run user-defined checks -> return pass/fail
  State:   <back:#ECEFF1>IDLE</back> → RUNNING → AGGREGATING → DONE
  Failure: Any check fails → SuccessCheckResult(passed=false)
  Success: All checks pass → SuccessCheckResult(passed=true)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl09_inject_turn_budget.puml ---

@startuml sq_evl09_inject_turn_budget
' ============================================================
' Title:     EVL-09 — Inject Turn Budget
' Boundary:  nasim code agent CLI
' Purpose:   Turn budget injection per-turn
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #FFF3E0
  participant "TurnBudgetInjector" as injector
  participant "TurnBudget" as budget
end box
box "Context Layer" #E8F5E9
  participant "ConversationHistory" as history
end box

note over user, history
  Scope:
    - evl05 INJECT Turn Budget — turn budget injection per-turn

  Preconditions:
    - TurnBudget initialized with max_turns
    - ConversationHistory tracks turn count

  Contexts:
    - Called at start of each agentic turn
    - Injects budget status into context for LLM awareness

  Excludes:
    - Repetition detection (handled by EVL-04)
    - Edit evaluation (handled by EVL-01/02)

  Rollback:
    - Budget exceeded → force task completion

  Design:
  Classification: Primary Orchestrator
    - TurnBudgetInjector computes remaining budget
    - Injects formatted status into system message
    - Warns when budget drops below threshold (20%)
    - Forces completion at zero budget

  Returns:
    - Success: BudgetStatus with remaining turns and warning flag
    - Failure: BudgetExhausted error
end note

== evl05 INJECT Turn Budget ==

agent -> injector : INJECT_BUDGET(current_turn)
activate injector

injector -> budget : get_max_turns()
activate budget
budget --> injector : max_turns
deactivate budget

injector -> injector : compute_remaining(current_turn, max_turns)

injector -> injector : check_warning_threshold(remaining, threshold=0.2)

alt remaining > 0
    injector -> injector : format_budget_message(remaining, warning)

    injector -> history : prepend_system_message(budget_message)
    activate history
    history --> injector : message_injected
    deactivate history

    injector --> agent : BudgetStatus(remaining, warning, continue=true)
else remaining <= 0
    injector --> agent : BudgetExhausted(current_turn, max_turns)
end

deactivate injector

note over user, history
  Flow:
    - AgentOrchestrator → TurnBudgetInjector → TurnBudget + ConversationHistory → BudgetStatus

  State:
    - <back:#ECEFF1>IDLE</back> → COMPUTING → CHECKING → INJECTING → DONE

  Failure:
    - Budget exhausted → BudgetExhausted error

  Success:
    - BudgetStatus with remaining turns

  Key invariants:
    - Budget message always injected before LLM call
    - Warning triggered at 20% remaining
    - Zero budget forces immediate completion
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl06_coordinate_retry.puml ---

@startuml sq_evl06_coordinate_retry
' ============================================================
' Title:     EVL-06 — Coordinate Retry
' Boundary:  nasim code agent CLI
' Purpose:   Retry with feedback on failure
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #FFF3E0
  participant "RetryCoordinator" as retry
  participant "FeedbackInjector" as feedback
  participant "TurnBudgetInjector" as budget
end box
box "Sandbox Layer" #F1F8E9
  participant "FileSystem" as fs
end box

note over user, budget
  Scope:
    - evl03 COORDINATE Retry — retry with feedback on failure

  Preconditions:
    - EVL-01 or EVL-02 identified failure
    - Backup file available for revert
    - Turn budget not exhausted

  Contexts:
    - Called after evaluation failure (EVL-01 or EVL-02)
    - Triggers new EDT cycle with injected feedback

  Excludes:
    - Evaluation logic (handled by EVL-01/02)
    - Turn budget management (handled by EVL-05)

  Rollback:
    - Max retries exceeded → abort, report to user
    - Turn budget exhausted → abort, report to user

  Design:
  Classification: Primary Orchestrator
    - RetryCoordinator manages retry count and limits
    - FeedbackInjector formats failure details for next LLM call
    - Backup restored before retry attempt
    - Max 3 retries per edit before escalating

  Returns:
    - Success: RetryResult with retry_count and next_action
    - Failure: RetryExhausted error
end note

== evl03 COORDINATE Retry ==

agent -> retry : COORDINATE_RETRY(edit_result, check_result, review_result)
activate retry

retry -> retry : increment_retry_count()

retry -> retry : check_retry_limit(max=3)

alt retry_count <= max_retries
    retry -> fs : restore_backup(edit_result.backup_path)
    activate fs
    fs --> retry : restore_success
    deactivate fs

    retry -> feedback : INJECT_FEEDBACK(check_result, review_result)
    activate feedback
    feedback --> retry : feedback_context
    deactivate feedback

    retry --> agent : RetryResult(retry_count, feedback_context, continue=true)
else retry_count > max_retries
    retry --> agent : RetryExhausted(retry_count, final_error)
end

deactivate retry

note over user, budget
  Flow:
    - AgentOrchestrator → RetryCoordinator → FileSystem + FeedbackInjector → RetryResult

  State:
    - <back:#ECEFF1>IDLE</back> → CHECKING_LIMIT → RESTORING → INJECTING → DONE

  Failure:
    - Max retries exceeded → RetryExhausted error

  Success:
    - RetryResult with feedback for next attempt

  Key invariants:
    - Backup always restored before retry
    - Retry count never exceeds max_retries
    - Feedback always includes specific failure reasons
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl08_detect_repetition.puml ---

@startuml sq_evl08_detect_repetition
' ============================================================
' Title:     EVL-08 — DETECT Repetition
' Boundary:  nasim code agent
' Purpose:   Tool-call loop detection
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Prompt audit 2026-06-21 (gro.md: extraneous PermissionGate removed)
' Note:      Process decomposition — internal step of EVL-01. No actor per sq.md rules.
' ============================================================

title nasim — EVL-08 DETECT Repetition

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #FFF3E0
  participant "RepetitionDetector" as detector
  participant "ToolCallHistory" as history
end box

note over agent, history
  Scope:          Detect tool-call loops and repeated patterns
  Preconditions:  Tool call history available, RepetitionDetector initialized
  Contexts:       Called on each tool dispatch to detect loops
  Excludes:       Turn budget management (EVL-09), edit evaluation (EVL-01/02)
  Rollback:       Loop detected -> force abort, notify agent
  Design:         RepetitionDetector tracks tool call patterns. Detects same tool+args repeated N times, oscillating patterns. Configurable window and threshold.
  Classification: Process Decomposition
end note

== EVL-08 DETECT Repetition ==

agent -> detector : CHECK_REPETITION(tool_call, call_history)
activate detector

detector -> history : get_recent_calls(window=5)
activate history
history --> detector : recent_calls[]
deactivate history

detector -> detector : analyze_pattern(recent_calls)

detector -> detector : check_same_tool_repeat(tool_call, recent_calls, threshold=3)

detector -> detector : check_oscillation_pattern(recent_calls)

detector -> detector : check_stuck_pattern(recent_calls)

alt loop_detected
    detector --> agent : LoopDetected(pattern, repeat_count)
else no_loop
    detector --> agent : RepetitionResult(detected=false, confidence)
end

deactivate detector

note over agent, history
  Flow:    AgentOrchestrator -> RepetitionDetector -> ToolCallHistory -> RepetitionResult
  State:   No state change
  Failure: Loop detected -> LoopDetected error
  Success: RepetitionResult with detected=false
  Key invariants:
    - Detection is non-blocking until threshold
    - Pattern analysis covers repeat, oscillation, stuck cases
    - History window prevents stale pattern detection
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl05_validate_test_suite.puml ---

@startuml sq_evl05_validate_test_suite
' ============================================================
' Title:     EVL-05 — VALIDATE Test Suite
' Boundary:  nasim code agent
' Purpose:   Run test suite and collect pass/fail/skip results
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EVL-05 VALIDATE Test Suite

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #F9FBE7
  participant "EvaluationEngine" as engine
  participant "TestRunner" as runner
end box
box "Tool Layer" #F3E5F5
  participant "ShellRunner" as shell
end box

note over participants
  Scope:          Execute test suite and collect structured results
  Preconditions:  Test framework configured, test files present
  Excludes:       LLM-based review, quality signal recording
  Contexts:       EVL-01 EVALUATE Task delegates test validation here
  Rollback:       No state change — read-only execution
  Design:         TestRunner invokes configured test framework, parses output into structured results
  Classification: Process Decomposition
end note

== EVL-05 VALIDATE Test Suite ==

agent -> engine : VALIDATE_TEST_SUITE(test_command, project_path)
activate engine

engine -> runner : run_test_suite(test_command, project_path)
activate runner

runner -> shell : execute(test_command, timeout=120s, cwd=project_path)
activate shell
shell --> runner : TestOutput(exit_code, stdout, stderr)
deactivate shell

runner -> runner : parse_test_results(stdout)

runner -> runner : classify_results(parsed_output)

runner --> engine : TestSuiteResult(total, passed, failed, skipped, errors[])
deactivate runner

engine --> agent : TestSuiteResult
deactivate engine

note over participants
  Flow:    EvaluationEngine -> TestRunner -> run test suite -> collect results -> return
  State:   <back:#ECEFF1>IDLE</back> → RUNNING → PARSING → DONE
  Failure: Test framework error → TestSuiteResult with error details
  Success: TestSuiteResult with counts and failure details
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl02_check_task_completion.puml ---

@startuml sq_evl02_check_task_completion
' ============================================================
' Title:     EVL-02 — CHECK Task Completion
' Boundary:  nasim code agent
' Purpose:   Evaluate task completion against defined criteria
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EVL-02 CHECK Task Completion

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #F9FBE7
  participant "EvaluationEngine" as engine
  participant "TaskEvaluator" as evaluator
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as tool
end box

note over participants
  Scope:          Check whether a task meets its completion criteria
  Preconditions:  Task defined with acceptance criteria, tool results available
  Excludes:       Success check execution (EVL-03), retry coordination (EVL-04)
  Contexts:       EVL-01 EVALUATE Task delegates completion check here
  Rollback:       No state change — read-only evaluation
  Design:         TaskEvaluator compares tool outputs against criteria predicates
  Classification: Process Decomposition
end note

== EVL-02 CHECK Task Completion ==

agent -> engine : CHECK_TASK_COMPLETION(task_id, criteria[])
activate engine

engine -> evaluator : evaluate_completion(task_id, criteria)
activate evaluator

loop for each criterion
    evaluator -> evaluator : extract_criterion_result(criterion)
    evaluator -> tool : query_task_state(task_id, criterion.target)
    activate tool
    tool --> evaluator : criterion_state
    deactivate tool

    evaluator -> evaluator : evaluate_predicate(criterion, criterion_state)
end

evaluator -> evaluator : aggregate_completion(criteria_results[])

evaluator --> engine : CompletionStatus(completed, details[])
deactivate evaluator

engine --> agent : CompletionStatus
deactivate engine

note over participants
  Flow:    EvaluationEngine -> TaskEvaluator -> evaluate against criteria -> return completion status
  State:   <back:#ECEFF1>IDLE</back> → <back:#F9FBE7>EVALUATING</back> → AGGREGATING → DONE
  Failure: No state change on evaluation failure — returns partial status
  Success: CompletionStatus with per-criterion pass/fail
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl01_evaluate_task.puml ---

@startuml sq_evl01_evaluate_task
' ============================================================
' Title:     EVL-01 — EVALUATE Task
' Boundary:  nasim code agent
' Purpose:   Evaluate task completion via success checks and quality signals
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Layer" #FFF3E0
  participant "SuccessChecker" as checker
  participant "ShellRunner" as shell
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as tool
end box

note over user, tool
  Scope:          Evaluate task completion via success checks and quality signals
  Preconditions:  EDT-05 completed (edit applied and user-approved), shell environment available
  Excludes:       LLM-based review (EVL-04), repetition detection (EVL-08)
  Contexts:       Called after edit application to verify correctness; feeds into EVL-06 (COORDINATE Retry) on failure
  Rollback:       Check failure -> report to EVL-06 for retry coordination
  Design:         SuccessChecker runs configured check commands with timeout; aggregate pass/fail across all checks
  Classification: Primary Orchestrator
end note

== EVL-01 EVALUATE Task ==

agent -> checker : RUN_CHECKS(file_path, check_commands[])
activate checker

loop for each check_command
    checker -> shell : execute(check_command, timeout=30s)
    activate shell
    alt exit_code == 0
        shell --> checker : CheckOutput(exit_code=0, stdout, stderr="")
    else exit_code != 0
        shell --> checker : CheckOutput(exit_code, stdout, stderr)
    end
    deactivate shell

    checker -> checker : record_result(check_command, output)
end

checker -> checker : aggregate_results()

checker --> agent : CheckResult(passed, results[])
deactivate checker

note over user, tool
  Flow:    AgentOrchestrator -> SuccessChecker -> [ShellRunner]* -> CheckResult
  State:   <back:#ECEFF1>IDLE</back> -> <back:#F9FBE7>EVALUATING</back> -> <back:#ECEFF1>IDLE</back>
  Failure: Any check fails -> CheckResult(passed=false)
  Success: All checks pass -> CheckResult(passed=true)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl19_persist_memory.puml ---

@startuml sq_tl19_persist_memory
' ============================================================
' Title:     TL-19 — Persist Memory
' Boundary:  nasim code agent
' Purpose:   Persist knowledge to memory via MemoryTool
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-19 Persist Memory

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "MemoryTool" as tool
end box
participant "MemoryStore" as mem

note over participants
  Scope:          Persist a knowledge item to the memory store
  Preconditions:  MemoryTool initialized
  Excludes:       Memory recall, search, scoping
  Contexts:       Called by AGT-02; delegates to MEM-01
  Rollback:       Error string returned to LLM
  Design:         Delegates to MEM-01 PERSIST Knowledge
  Classification: Process Decomposition
end note

== TL-19 Persist Memory ==

agent -> registry : execute("persist_memory", {key, value, scope})
registry -> tool : execute(key, value, scope)
tool -> mem : MEM-01 persist(key, value, scope)

break Storage failure
    mem --> tool : StorageError
    tool --> registry : ToolResult(success=False, error="persist failed")
    registry --> agent : ToolResult
end

mem --> tool : persisted
tool --> registry : ToolResult(success=True)
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> MemoryTool -> MEM-01 PERSIST Knowledge -> ToolResult
  State:   Knowledge item stored
  Failure: Storage failure -> ToolResult(success=False)
  Success: Knowledge persisted
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl03_edit_file.puml ---

@startuml sq_tl03_edit_file
' ============================================================
' Title:     TL-03 — Edit File
' Boundary:  nasim code agent CLI
' Purpose:   Replace an exact string in a file
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "EditFileTool" as ft
end box
participant "Host Filesystem" as fs

note over user, fs
  Scope:          Find-and-replace in a file
  Preconditions:  Path, old_string, new_string provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       Read, write
  Rollback:       Error if old_string not found or ambiguous
  Design:         Fails if old_string appears 0 or >1 times
  Classification: Primary Orchestrator
  Safety:         Requires permission check (SAF-01)
end note

== TL-03 EDIT File ==

user -> repl : (entry via AGT-01)
repl -> agent : (entry via AGT-01)
agent -> registry : execute("edit_file", {path, old_string, new_string})
registry -> ft : execute(path, old_string, new_string)
ft -> fs : Path(path).read_text()

break File not found
    fs --> ft : FileNotFoundError
    ft --> registry : ToolResult(success=False, error="Error: file not found")
    registry --> agent : ToolResult
end

ft -> ft : content.count(old_string)

alt count == 0
    ft --> registry : ToolResult(success=False, error="old_string not found")
    registry --> agent : ToolResult
else count > 1
    ft --> registry : ToolResult(success=False, error="old_string found N times (ambiguous)")
    registry --> agent : ToolResult
else count == 1
    ft -> ft : content.replace(old_string, new_string, 1)
    ft -> fs : Path(path).write_text(new_content)
    ft --> registry : ToolResult(success=True, content="Edited: replaced 1 occurrence")
    registry --> agent : ToolResult
end

note over user, fs
  Flow:    read -> count -> replace -> write -> ToolResult
  State:   No state change
  Failure: Not found or ambiguous -> ToolResult(success=False)
  Success: Single replacement written
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl12_dispatch_mcp_extension.puml ---

@startuml sq_tl12_dispatch_mcp_extension
' ============================================================
' Title:     TL-12 — Dispatch MCP Extension
' Boundary:  nasim code agent CLI
' Purpose:   Invoke tools from MCP server extensions
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

participant "ToolRegistry" as registry
participant "MCPToolAdapter" as mcp
participant "MCP Server" as server

box "Tool Layer" #F3E5F5
end box
box "External" #FFEBEE
end box

note over mcp
  Scope:          Invoke MCP server extension tools
  Preconditions:  MCP server configured and running
  Excludes:       MCP server startup, tool discovery
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       MCP error returned as error string
  Design:         Wraps MCP tools as nasim Tool instances
  Classification: Process Decomposition
end note

registry -> mcp : execute(tool_name, args)
mcp -> server : MCP call(tool_name, args) via stdio/SSE

break MCP server not running
    server --> mcp : ConnectionRefused
    mcp --> registry : "Error: MCP server not reachable"
end

break Tool not found on server
    server --> mcp : UnknownTool error
    mcp --> registry : "Error: tool not found on MCP server"
end

server --> mcp : result
mcp -> mcp : wrap in ToolResult(success=True, content=result)
mcp --> registry : ToolResult

note over mcp
  Flow:    tool_name -> MCP server call -> result -> ToolResult
  State:   No state change
  Failure: Server down, tool not found -> error string
  Success: MCP tool result wrapped in ToolResult
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl10_search_web.puml ---

@startuml sq_tl10_search_web
' ============================================================
' Title:     TL-10 — SEARCH Web
' Boundary:  nasim code agent CLI
' Purpose:   Search the web for information
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

participant "ToolRegistry" as registry
participant "WebSearchTool" as search
participant "Search Backend" as backend

box "Tool Layer" #F3E5F5
end box

note over search
  Scope:          Web search with ranked results
  Preconditions:  Query provided by LLM
  Excludes:       URL fetching (TL-09)
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Backend error returned as error string
  Design:         Configurable backend: DuckDuckGo, Brave, SerpAPI
  Classification: Process Decomposition
end note

registry -> search : execute(query, num_results)
search -> backend : search(query, num_results)

break Backend unavailable
    backend --> search : ConnectionError
    search --> registry : "Error: search backend unavailable"
end

backend --> search : results [{title, url, snippet}, ...]
search -> search : format results
search --> registry : formatted results string

note over search
  Flow:    query -> backend -> results -> formatted string
  State:   No state change
  Failure: Backend unavailable -> error string
  Success: Ranked search results with titles, URLs, snippets
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl21_insert_plan.puml ---

@startuml sq_tl21_insert_plan
' ============================================================
' Title:     TL-21 — Insert Plan
' Boundary:  nasim code agent
' Purpose:   Add a new plan step via PlanTool
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-21 Insert Plan

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "PlanTool" as tool
end box

note over participants
  Scope:          Add a new step to the execution plan
  Preconditions:  PlanTool initialized
  Excludes:       Plan update, deletion, listing
  Contexts:       Called by AGT-02
  Rollback:       Error string returned to LLM
  Design:         Auto-generates step ID; initial status PENDING
  Classification: Process Decomposition
end note

== TL-21 Insert Plan ==

agent -> registry : execute("insert_plan", {description, dependencies?})
registry -> tool : execute(description, dependencies)
tool -> tool : generate step ID, set status PENDING
tool --> registry : ToolResult(success=True, step_id)
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> PlanTool -> add plan step -> ToolResult
  State:   New plan step created (PENDING)
  Failure: Invalid input -> ToolResult(success=False)
  Success: Plan step ID returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl22_update_plan.puml ---

@startuml sq_tl22_update_plan
' ============================================================
' Title:     TL-22 — Update Plan
' Boundary:  nasim code agent
' Purpose:   Update status or content of an existing plan step
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-22 Update Plan

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "PlanTool" as tool
end box

note over participants
  Scope:          Update status or content of a plan step by ID
  Preconditions:  Plan step exists with given ID
  Excludes:       Plan step creation, deletion, listing
  Contexts:       Called by AGT-02
  Rollback:       Error string returned to LLM
  Design:         Validates status transitions
  Classification: Process Decomposition
end note

== TL-22 Update Plan ==

agent -> registry : execute("update_plan", {step_id, status, description})
registry -> tool : execute(step_id, status, description)

break Step not found
    tool --> registry : ToolResult(success=False, error="step not found")
    registry --> agent : ToolResult
end

break Invalid status transition
    tool --> registry : ToolResult(success=False, error="invalid transition")
    registry --> agent : ToolResult
end

tool -> tool : update fields
tool --> registry : ToolResult(success=True, step)
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> PlanTool -> update plan step -> ToolResult
  State:   Plan step status/content updated
  Failure: Step not found or invalid transition -> ToolResult(success=False)
  Success: Updated plan step returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl05_dispatch_shell_command.puml ---

@startuml sq_tl05_dispatch_shell_command
' ============================================================
' Title:     TL-05 — Dispatch Shell Command
' Boundary:  nasim code agent CLI
' Purpose:   Shell command execution with timeout
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "ShellTool" as st
end box
participant "Host Shell" as shell

note over user, shell
  Scope:          Execute shell command with timeout
  Preconditions:  Command string provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       File operations
  Rollback:       Error string returned to LLM
  Design:         subprocess.run with shell=True, configurable timeout
  Classification: Primary Orchestrator
  Safety:         Unsafe tool — requires permission check (SAF-01)
end note

== TL-05 EXECUTE Shell Command ==

user -> repl : (entry via AGT-01)
repl -> agent : (entry via AGT-01)
agent -> registry : execute("shell_exec", {command, timeout})
registry -> st : execute(command, timeout)
st -> shell : subprocess.run(command, shell=True, timeout=timeout)

break Timeout
    shell --> st : TimeoutExpired
    st --> registry : ToolResult(success=False, error="command timed out after Ns")
    registry --> agent : ToolResult
end

break Execution error
    shell --> st : Exception
    st --> registry : ToolResult(success=False, error="Error executing command")
    registry --> agent : ToolResult
end

shell --> st : CompletedProcess(stdout, stderr, returncode)
st -> st : format output (stdout + stderr + exit code)
st --> registry : ToolResult(success=True, content=command_output)
registry --> agent : ToolResult

note over user, shell
  Flow:    command -> subprocess.run -> format output -> ToolResult
  State:   No state change
  Failure: Timeout, execution error -> ToolResult(success=False)
  Success: Command output (stdout + stderr)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl08_find_files.puml ---

@startuml sq_tl08_find_files
' ============================================================
' Title:     TL-08 — Find Files
' Boundary:  nasim code agent CLI
' Purpose:   Find files by name pattern with depth limit
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

participant "ToolRegistry" as registry
participant "FindFileTool" as find

box "Tool Layer" #F3E5F5
end box

note over find
  Scope:          Find files by name pattern with max depth
  Preconditions:  Name pattern and path provided by LLM
  Excludes:       Content search, glob patterns
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Uses os.walk with depth limit
  Classification: Process Decomposition
end note

registry -> find : execute(name_pattern, path, max_depth)
find -> find : os.walk(path) with depth tracking
find -> find : fnmatch.fnmatch(filename, pattern)

break Path not found
    find --> registry : "Error: path not found: path"
end

find --> registry : matching file paths

note over find
  Flow:    pattern -> os.walk(depth-limited) -> fnmatch -> paths
  State:   No state change
  Failure: Path not found -> error string
  Success: List of matching file paths
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl17_update_todo.puml ---

@startuml sq_tl17_update_todo
' ============================================================
' Title:     TL-17 — Update Todo
' Boundary:  nasim code agent
' Purpose:   Update status or content of an existing todo item
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-17 Update Todo

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "TodoTool" as tool
end box

note over participants
  Scope:          Update status or content of a todo item by ID
  Preconditions:  Todo exists with given ID
  Excludes:       Todo creation, deletion, listing
  Contexts:       Called by AGT-02
  Rollback:       Error string returned to LLM
  Design:         Validates status transitions
  Classification: Process Decomposition
end note

== TL-17 Update Todo ==

agent -> registry : execute("update_todo", {todo_id, status, description})
registry -> tool : execute(todo_id, status, description)

break Todo not found
    tool --> registry : ToolResult(success=False, error="todo not found")
    registry --> agent : ToolResult
end

break Invalid status transition
    tool --> registry : ToolResult(success=False, error="invalid transition")
    registry --> agent : ToolResult
end

tool -> tool : update fields
tool --> registry : ToolResult(success=True, todo)
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> TodoTool -> update status -> ToolResult
  State:   Todo status/content updated
  Failure: Todo not found or invalid transition -> ToolResult(success=False)
  Success: Updated todo returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl16_insert_todo.puml ---

@startuml sq_tl16_insert_todo
' ============================================================
' Title:     TL-16 — Insert Todo
' Boundary:  nasim code agent
' Purpose:   Add a new todo item via TodoTool
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-16 Insert Todo

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "TodoTool" as tool
end box

note over participants
  Scope:          Add a new todo item with title and optional description
  Preconditions:  TodoTool initialized
  Excludes:       Todo update, delete, list
  Contexts:       Called by AGT-02
  Rollback:       Error string returned to LLM
  Design:         Auto-generates ID; initial status OPEN
  Classification: Process Decomposition
end note

== TL-16 Insert Todo ==

agent -> registry : execute("insert_todo", {title, description})
registry -> tool : execute(title, description)
tool -> tool : generate ID, set status OPEN
tool --> registry : ToolResult(success=True, todo_id)
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> TodoTool -> add todo item -> ToolResult
  State:   New todo item created (OPEN)
  Failure: Invalid input -> ToolResult(success=False)
  Success: Todo ID returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl07_glob_files.puml ---

@startuml sq_tl07_glob_files
' ============================================================
' Title:     TL-07 — Glob Files
' Boundary:  nasim code agent CLI
' Purpose:   Find files by glob pattern
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "GlobTool" as glob
end box

note over registry, glob
  Scope:          Find files matching glob pattern
  Preconditions:  Glob pattern provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       Content search, file reading
  Rollback:       Error string returned to LLM
  Design:         Uses pathlib.Path.glob()
  Classification: Process Decomposition
end note

== TL-07 GLOB Files ==

registry -> glob : execute(pattern, base_path)
glob -> glob : Path(base_path).glob(pattern)
glob -> glob : collect and sort matching paths

break Permission denied
    glob --> registry : "Error: permission denied: path"
end

glob --> registry : sorted list of matching file paths

note over registry, glob
  Flow:    pattern -> pathlib.glob -> sorted paths
  State:   No state change
  Failure: Permission denied -> error string
  Success: Sorted list of matching file paths
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl15_spawn_subagent.puml ---

@startuml sq_tl15_spawn_subagent
' ============================================================
' Title:     TL-15 — Spawn Subagent
' Boundary:  nasim code agent
' Purpose:   Create a child subagent via SubagentTool
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-15 Spawn Subagent

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "SubagentTool" as tool
end box
participant "SubagentCoordinator" as coord

note over participants
  Scope:          Spawn a child subagent with a task prompt
  Preconditions:  SubagentCoordinator initialized
  Excludes:       Subagent result collection, cancellation
  Contexts:       Called by AGT-02
  Rollback:       Error string returned to LLM
  Design:         Fire-and-forget spawn; child runs independently
  Classification: Process Decomposition
end note

== TL-15 Spawn Subagent ==

agent -> registry : execute("spawn_subagent", {prompt, subagent_type})
registry -> tool : execute(prompt, subagent_type)
tool -> coord : create_child(prompt, subagent_type)

break Coordinator unavailable or limit reached
    coord --> tool : CapacityError
    tool --> registry : ToolResult(success=False, error="spawn limit reached")
    registry --> agent : ToolResult
end

coord --> tool : child_id
tool --> registry : ToolResult(success=True, child_id=child_id)
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> SubagentTool -> SubagentCoordinator -> create child -> ToolResult(child_id)
  State:   New child subagent spawned
  Failure: Coordinator unavailable or spawn limit -> ToolResult(success=False)
  Success: Child subagent ID returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl13_read_lsp.puml ---

@startuml sq_tl13_read_lsp
' ============================================================
' Title:     TL-13 — Read LSP
' Boundary:  nasim code agent
' Purpose:   Query LSP server for hover, definition, or references
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-13 Read LSP

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "LspTool" as tool
end box
participant "LSP Server" as lsp

note over participants
  Scope:          Query LSP server for hover, definition, or references
  Preconditions:  LSP server running for target language
  Excludes:       LSP initialization, diagnostics, code actions
  Contexts:       Called by AGT-02
  Rollback:       Error string returned to LLM
  Design:         Stateless query; no session-side cache
  Classification: Process Decomposition
end note

== TL-13 Read LSP ==

agent -> registry : execute("lsp", {query, params})
registry -> tool : execute(query, params)
tool -> lsp : send request(query, params)

break LSP server unreachable or times out
    lsp --> tool : ConnectionError / TimeoutError
    tool --> registry : ToolResult(success=False, error="LSP unavailable")
    registry --> agent : ToolResult
end

break Query returns no results
    lsp --> tool : empty result
    tool --> registry : ToolResult(success=False, error="no results")
    registry --> agent : ToolResult
end

lsp --> tool : hover/definition/references result
tool --> registry : ToolResult(success=True, result)
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> LspTool -> LSP server -> hover/definition/references -> ToolResult
  State:   No state change
  Failure: LSP unavailable or no results -> ToolResult(success=False)
  Success: LSP query result returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl04_list_directory.puml ---

@startuml sq_tl04_list_directory
' ============================================================
' Title:     TL-04 — List Directory
' Boundary:  nasim code agent CLI
' Purpose:   List files and directories at a path
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "DirTool" as dt
end box
participant "Host Filesystem" as fs

note over user, fs
  Scope:          List directory entries sorted by type then name
  Preconditions:  Path provided (default: current directory)
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       File read/write
  Rollback:       Error string returned to LLM
  Design:         Directories first, then files, alphabetical
  Classification: Primary Orchestrator
end note

== TL-04 LIST Directory ==

user -> repl : (entry via AGT-01)
repl -> agent : (entry via AGT-01)
agent -> registry : execute("list_dir", {path})
registry -> dt : execute(path)
dt -> fs : Path(path).resolve()

break Path not found
    fs --> dt : FileNotFoundError
    dt --> registry : ToolResult(success=False, error="path not found")
    registry --> agent : ToolResult
end

break Not a directory
    dt --> registry : ToolResult(success=False, error="not a directory")
    registry --> agent : ToolResult
end

dt -> fs : sorted(p.iterdir())
fs --> dt : entries
dt -> dt : format with d/ prefix for dirs
dt --> registry : ToolResult(success=True, content=formatted_listing)
registry --> agent : ToolResult

note over user, fs
  Flow:    resolve -> iterdir -> sort -> format -> ToolResult
  State:   No state change
  Failure: Not found or not directory -> ToolResult(success=False)
  Success: Directory listing with type prefixes
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl06_grep_search.puml ---

@startuml sq_tl06_grep_search
' ============================================================
' Title:     TL-06 — Grep Search
' Boundary:  nasim code agent CLI
' Purpose:   Search file contents by regex pattern
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "GrepTool" as grep
  participant "ShellTool" as shell
end box

note over registry, shell
  Scope:          Search file contents by regex pattern
  Preconditions:  Pattern and path provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       File globbing, file reading
  Rollback:       Error string returned to LLM
  Design:         Prefers ripgrep; falls back to Python re
  Classification: Process Decomposition
end note

== TL-06 GREP Search ==

registry -> grep : execute(pattern, path, case_sensitive, include_glob)

alt ripgrep available
    grep -> shell : subprocess: rg --json pattern path
    shell --> grep : JSON output
    grep -> grep : parse matches -> file:line:content format
else ripgrep not found
    grep -> grep : Python os.walk + re.search fallback
end

break No matches found
    grep --> registry : "No matches found for pattern"
end

break Permission denied / path error
    grep --> registry : "Error: permission denied / path not found"
end

grep --> registry : formatted matches string

note over registry, shell
  Flow:    pattern -> ripgrep/Python -> matches -> formatted string
  State:   No state change
  Failure: No matches, permission error -> error string
  Success: List of matching file:line:content
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl14_list_registered_tools.puml ---

@startuml sq_tl14_list_registered_tools
' ============================================================
' Title:     TL-14 — List Registered Tools
' Boundary:  nasim code agent
' Purpose:   Return list of all tools registered in the ToolRegistry
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-14 List Registered Tools

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over participants
  Scope:          List all registered tools with names and descriptions
  Preconditions:  ToolRegistry initialized
  Excludes:       Tool execution, tool registration
  Contexts:       Called by AGT-02
  Rollback:       Error string returned to LLM
  Design:         Read-only; no mutation
  Classification: Process Decomposition
end note

== TL-14 List Registered Tools ==

agent -> registry : execute("list_tools", {})
registry -> registry : enumerate registered tools
registry --> agent : ToolResult(success=True, tools=[...])

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> list all registered tools -> ToolResult
  State:   No state change
  Failure: N/A (read-only query)
  Success: List of tool names and descriptions
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl02_write_file.puml ---

@startuml sq_tl02_write_file
' ============================================================
' Title:     TL-02 — Write File
' Boundary:  nasim code agent CLI
' Purpose:   Create or overwrite a file
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "WriteFileTool" as ft
end box
participant "Host Filesystem" as fs

note over user, fs
  Scope:          Write content to a file
  Preconditions:  Path and content provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       Read, edit
  Rollback:       Error string returned to LLM
  Design:         Creates parent directories automatically
  Classification: Primary Orchestrator
  Safety:         Requires permission check (SAF-01)
end note

== TL-02 WRITE File ==

user -> repl : (entry via AGT-01)
repl -> agent : (entry via AGT-01)
agent -> registry : execute("write_file", {path, content})
registry -> ft : execute(path, content)
ft -> fs : Path(path).mkdir(parents=True)
ft -> fs : Path(path).write_text(content)

break Write error (permissions, disk full)
    fs --> ft : PermissionError / OSError
    ft --> registry : ToolResult(success=False, error="Error writing path: exception")
    registry --> agent : ToolResult
end

fs --> ft : OK
ft --> registry : ToolResult(success=True, content="Wrote N bytes to path")
registry --> agent : ToolResult

note over user, fs
  Flow:    mkdir -> write_text -> ToolResult
  State:   No state change
  Failure: Permissions, disk space -> ToolResult(success=False)
  Success: ToolResult(success=True, "Wrote N bytes")
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl09_fetch_web_content.puml ---

@startuml sq_tl09_fetch_web_content
' ============================================================
' Title:     TL-09 — FETCH Web Content
' Boundary:  nasim code agent CLI
' Purpose:   Fetch URL content and convert to markdown
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

participant "ToolRegistry" as registry
participant "WebFetchTool" as fetch
participant "Web" as web

box "Tool Layer" #F3E5F5
end box

note over fetch
  Scope:          Fetch URL content as markdown text
  Preconditions:  URL provided by LLM
  Excludes:       Web search (TL-10)
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       HTTP error returned as error string
  Design:         Uses httpx + html2text for conversion
  Classification: Process Decomposition
end note

registry -> fetch : execute(url, timeout)
fetch -> web : httpx GET url (timeout=timeout)

break HTTP error (4xx, 5xx)
    web --> fetch : HTTPError
    fetch --> registry : "Error: HTTP {status_code} for {url}"
end

break Timeout
    web --> fetch : TimeoutException
    fetch --> registry : "Error: timeout fetching {url}"
end

web --> fetch : HTML content
fetch -> fetch : html2text.convert(html) -> markdown
fetch --> registry : markdown text

note over fetch
  Flow:    URL -> HTTP GET -> html2text -> markdown
  State:   No state change
  Failure: HTTP error, timeout -> error string
  Success: Page content as markdown text
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl20_recall_memory.puml ---

@startuml sq_tl20_recall_memory
' ============================================================
' Title:     TL-20 — Recall Memory
' Boundary:  nasim code agent
' Purpose:   Recall knowledge from memory via MemoryTool
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-20 Recall Memory

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "MemoryTool" as tool
end box
participant "MemoryStore" as mem

note over participants
  Scope:          Recall knowledge from the memory store by query
  Preconditions:  MemoryTool initialized, memory not empty
  Excludes:       Memory persist, search, scoping
  Contexts:       Called by AGT-02; delegates to MEM-02
  Rollback:       Error string returned to LLM
  Design:         Delegates to MEM-02 RECALL Knowledge
  Classification: Process Decomposition
end note

== TL-20 Recall Memory ==

agent -> registry : execute("recall_memory", {query, scope?})
registry -> tool : execute(query, scope)
tool -> mem : MEM-02 recall(query, scope)

break No matching knowledge
    mem --> tool : empty result
    tool --> registry : ToolResult(success=False, error="no match")
    registry --> agent : ToolResult
end

mem --> tool : matching knowledge
tool --> registry : ToolResult(success=True, knowledge)
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> MemoryTool -> MEM-02 RECALL Knowledge -> ToolResult
  State:   No state change
  Failure: No matching knowledge -> ToolResult(success=False)
  Success: Recalled knowledge returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl11_read_git_status.puml ---

@startuml sq_tl11_read_git_status
' ============================================================
' Title:     TL-11 — Read Git Status
' Boundary:  nasim code agent CLI
' Purpose:   Git operations: status, diff, commit
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

participant "ToolRegistry" as registry
participant "GitTool" as git
participant "Host Shell" as shell

box "Tool Layer" #F3E5F5
end box

note over git
  Scope:          Git status, diff, and commit operations
  Preconditions:  Git repo in working directory
  Excludes:       Branch operations, merge, push
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Git error returned as error string
  Design:         Delegates to git CLI via subprocess
  Classification: Process Decomposition
end note

registry -> git : execute(action, args)

alt action = "status"
    git -> shell : subprocess: git status --porcelain
    shell --> git : status output
    git --> registry : formatted status
else action = "diff"
    git -> shell : subprocess: git diff [args]
    shell --> git : diff output
    git --> registry : diff text
else action = "commit"
    git -> shell : subprocess: git add -A && git commit -m msg
    shell --> git : commit output
    git --> registry : commit confirmation
end

break Not a git repo
    shell --> git : fatal: not a git repository
    git --> registry : "Error: not a git repository"
end

break Nothing to commit
    shell --> git : nothing to commit
    git --> registry : "Nothing to commit"
end

note over git
  Flow:    action -> git CLI -> output -> formatted string
  State:   No state change
  Failure: Not a repo, nothing to commit -> error string
  Success: Git operation output
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl18_read_todos.puml ---

@startuml sq_tl18_read_todos
' ============================================================
' Title:     TL-18 — Read Todos
' Boundary:  nasim code agent
' Purpose:   List all todo items or filter by status
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-18 Read Todos

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "TodoTool" as tool
end box

note over participants
  Scope:          List todo items, optionally filtered by status
  Preconditions:  TodoTool initialized
  Excludes:       Todo creation, update, deletion
  Contexts:       Called by AGT-02
  Rollback:       Error string returned to LLM
  Design:         Read-only; supports status filter
  Classification: Process Decomposition
end note

== TL-18 Read Todos ==

agent -> registry : execute("read_todos", {status_filter?})
registry -> tool : execute(status_filter)
tool -> tool : query todos, apply filter
tool --> registry : ToolResult(success=True, todos=[...])
registry --> agent : ToolResult

note over participants
  Flow:    AgentOrchestrator -> ToolRegistry -> TodoTool -> list todos -> ToolResult
  State:   No state change
  Failure: N/A (read-only query)
  Success: List of todo items
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl01_read_file.puml ---

@startuml sq_tl01_read_file
' ============================================================
' Title:     TL-01 — Read File
' Boundary:  nasim code agent CLI
' Purpose:   File read tool execution
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "ReadFileTool" as ft
end box
participant "Host Filesystem" as fs

note over agent, fs
  Scope:          Read file contents with line numbers
  Preconditions:  File path provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       Write, edit, directory listing
  Rollback:       Error string returned to LLM
  Design:         Supports offset/limit for large files
  Classification: Process Decomposition (called by AGT-02, no actor)
end note

== TL-01 READ File ==

agent -> registry : execute("read_file", {path, offset, limit})
registry -> ft : execute(path, offset, limit)
ft -> fs : Path(path).read_text()

break File not found or not a file
    fs --> ft : FileNotFoundError / IsADirectoryError
    ft --> registry : ToolResult(success=False, error="file not found")
    registry --> agent : ToolResult
end

break Read error (encoding, permissions)
    fs --> ft : PermissionError / UnicodeDecodeError
    ft --> registry : ToolResult(success=False, error="Error reading path")
    registry --> agent : ToolResult
end

fs --> ft : file content
ft -> ft : add line numbers, apply offset/limit
ft --> registry : ToolResult(success=True, content=numbered_content)
registry --> agent : ToolResult

note over agent, fs
  Flow:    AgentOrchestrator -> ToolRegistry -> ReadFileTool -> Host Filesystem -> ToolResult
  State:   No state change
  Failure: File not found, permissions, encoding -> ToolResult(success=False)
  Success: File content with line numbers
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt02_dispatch_tool_call.puml ---

@startuml sq_agt02_dispatch_tool_call
' ============================================================
' Title:     AGT-02 — DISPATCH Tool Call
' Boundary:  nasim code agent
' Purpose:   Tool dispatch with Safety Pipeline (no God Object)
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Meta-Software Designer audit 2026-06-21
' Pattern:   Service (AgentOrchestrator) -> Safety (SafetyCoordinator) -> Repository (ToolRegistry)
' ============================================================

title nasim — AGT-02 DISPATCH Tool Call

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "SafetyCoordinator" as safety
  participant "ErrorBoundary" as eb
end box
box "Safety Layer" #FFF9C4
  participant "PermissionGate" as gate
  participant "InjectionScanner" as inj
  participant "EgressInspector" as egr
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
  participant "Tool" as tool
end box
box "Observability Layer" #E0F2F1
  participant "StructuredLogger" as logger
end box

note over agent, logger
  Scope:          Dispatch a single tool call with full safety pipeline
  Preconditions:  Tool call from LLM, ToolRegistry populated, SafetyCoordinator initialized
  Excludes:       LLM call logic (PRV-02), Permission prompt rendering (CLI-06), Tool result display (CLI-03)
  Contexts:       Called by AGT-01 (PROCESS User Task) for each tool_call in the inner loop
  Rollback:       Safety violation -> ToolResult(success=false); Tool error -> ErrorBoundary -> ToolResult(error)
  Design:         NO GOD OBJECT: AgentOrchestrator delegates safety to SafetyCoordinator (AGT-15).
                  SafetyCoordinator composes PermissionGate, InjectionScanner, EgressInspector.
                  ToolResult is always structured (success, content, error)
  Classification: UC-level Sub-flow
end note

== AGT-02 DISPATCH Tool Call ==

agent -> agent : receive tool_call from LLM response

hnote over agent #FFF9C4 : **State: AWAITING_APPROVAL** (if unsafe)

' --- NO GOD OBJECT: Delegate to SafetyCoordinator (AGT-15) ---
agent -> safety : RUN_SAFETY_PIPELINE(tool_call)
activate safety
ref over safety
  AGT-15: DISPATCH Safety Pipeline (injection, egress, permission)
end ref
safety --> agent : SafetyResult(approved/denied)
deactivate safety

alt safety denied
    agent -> agent : ToolResult(success=false, error="safety violation")
    ref over agent, logger
      OBS-01: STREAM Structured Log (tool blocked by safety)
    end ref
else safety approved
    hnote over agent #F3E5F5 : **State: TOOL_EXEC**

    agent -> registry : find(tool_call.name)
    activate registry
    alt tool not found
        registry --> agent : null
        agent -> eb : handle(UnknownTool)
        activate eb
        eb --> agent : RecoveryAction(abort)
        deactivate eb
        agent -> agent : ToolResult(success=false, error="unknown tool")
    else tool found
        registry --> tool : tool
        deactivate registry
        activate tool
        agent -> tool : execute(tool_call.arguments)
        tool --> agent : ToolResult
        deactivate tool
        ref over agent, logger
          OBS-01: STREAM Structured Log (tool execution result)
        end ref
    end
end

agent -> agent : append ToolResult to messages

hnote over agent #FFF3E0 : **State: THINKING**

note over agent, logger
  Flow:    AgentOrchestrator -> SafetyCoordinator (AGT-15) -> ToolRegistry -> Tool.execute()
  State:   <back:#FFF3E0>THINKING</back> -> <back:#FFF9C4>AWAITING_APPROVAL</back> (if unsafe) -> <back:#F3E5F5>TOOL_EXEC</back> -> <back:#FFF3E0>THINKING</back>
  Failure: Safety violation -> ToolResult(error); Unknown tool -> ErrorBoundary -> ToolResult(error)
  Success: ToolResult appended to ConversationHistory
  Key invariants: Every tool goes through SafetyCoordinator. No direct PermissionGate call from AgentOrchestrator
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt09_spawn_subagent.puml ---

@startuml sq_agt09_spawn_subagent
' ============================================================
' Title:     AGT-09 — Spawn Subagent
' Boundary:  nasim code agent
' Purpose:   Delegate work to a child agent process
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-09 Spawn Subagent

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "SubagentCoordinator" as coord
end box
box "Session Layer" #F1F8E9
  participant "SessionStore" as store
end box

note over agent, store
  Scope:          Spawn a child agent for parallel or isolated work
  Preconditions:  AgentOrchestrator initialized, parent session active
  Excludes:       Result collection (AGT-10), persona delegation (AGT-11)
  Contexts:       Called via ref from AGT-02 (DISPATCH Tool Call)
  Rollback:       Spawn failure → report error to parent, no child created
  Design:         SubagentCoordinator manages child lifecycle; each child gets its own session
  Classification: Process Decomposition
end note

== AGT-09 Spawn Subagent ==

agent -> coord : spawn(task_prompt, parent_id)
activate coord

coord -> coord : validate parent session exists
coord -> store : create child session
activate store
store --> coord : child_session_id
deactivate store

coord -> coord : initialize child AgentOrchestrator
coord -> coord : assign isolated ConversationHistory
coord --> agent : child_id
deactivate coord

break Spawn failure
    coord --> agent : SpawnError
    agent -> agent : log error, report to parent
end

note over agent, store
  Flow:    AgentOrchestrator → SubagentCoordinator → create child session → return child_id
  State:   <back:#ECEFF1>IDLE</back> → SPAWNING → READY
  Failure: Spawn error → report to parent, no child
  Success: child_id returned for later collection (AGT-10)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt01_process_user_task.puml ---

@startuml sq_agt01_process_user_task
' ============================================================
' Title:     AGT-01 — PROCESS User Task
' Boundary:  nasim code agent
' Purpose:   Core agentic loop: LLM call -> tool dispatch -> repeat
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-01 PROCESS User Task

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
  participant "SafetyCoordinator" as safety
end box
box "Provider Layer" #FFF3E0
  participant "LiteLLMProxy" as provider
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as tool
end box
box "Observability Layer" #E0F2F1
  participant "TraceCorrelator" as trace
end box

note over user, trace
  Scope:          Core agentic loop — single complete task execution cycle
  Preconditions:  Agent initialized with Provider, ToolRegistry, ConversationHistory
  Excludes:       Slash command handling (CLI-02), streaming display (CLI-03), session save/load (SSN-01/02)
  Contexts:       Called by CLI-01 (PROCESS User Input) after REPL input parsed; entry point for entire agentic loop
  Rollback:       LLM call failure -> append error message -> ERROR state -> IDLE; Tool execution failure -> append error message -> ERROR state -> IDLE; Max iterations exceeded -> force Done event
  Design:         AgentOrchestrator yields AgentEvent objects (no print()); Max iterations configurable; PermissionGate consulted before every tool execution; Recursive: after tool dispatch, re-calls Provider for next response
  Classification: Primary Orchestrator
end note

== AGT-01 PROCESS User Task ==

user -> repl : types input
repl -> agent : PROCESS(user_input)
activate agent

ref over agent, trace
  OBS-03: CORRELATE Trace
end ref

ref over agent, history
  AGT-03: UPDATE Conversation (append user message)
end ref

ref over agent, provider
  HK-04: DISPATCH Pre-LLM Hook
end ref

ref over agent, provider
  PRV-02: REQUEST Chat (or PRV-03: STREAM)
end ref

ref over agent, provider
  HK-05: DISPATCH Post-LLM Hook
end ref

alt LLM returns text only
    ref over agent, history
      AGT-03: UPDATE Conversation (append assistant message)
    end ref
    agent --> repl : AgentEvent(Done)
else LLM returns tool calls
    ref over agent, history
      AGT-03: UPDATE Conversation (append assistant message with tool_calls)
    end ref
    loop for each tool_call
        ref over agent, tool
          AGT-02: DISPATCH Tool Call
        end ref
    end
    ref over agent, provider
      PRV-02: Call Provider Chat [recurse — agt01 loops]
    end ref
    ref over agent, history
      AGT-03: UPDATE Conversation (append assistant message)
    end ref
    agent --> repl : AgentEvent(Done)
end

break LLM call fails or tool execution errors
    ref over agent, history
      AGT-03: UPDATE Conversation (append error message)
    end ref
    agent --> repl : AgentEvent(Error)
end

deactivate agent

note over user, trace
  Flow:    User -> REPLSession -> AgentOrchestrator -> [OBS-03] -> [AGT-03] -> [HK-04] -> Provider -> [HK-05] -> [AGT-03] -> (tool loop via AGT-02) -> Done
  State:   <back:#ECEFF1>IDLE</back> -> <back:#E8EAF6>LISTENING</back> -> <back:#FFF3E0>THINKING</back> -> [<back:#F3E5F5>TOOL_EXEC</back>]* -> <back:#E8F5E9>RESPONDING</back> -> <back:#ECEFF1>IDLE</back>
  Failure: LLM error or tool error -> ERROR -> IDLE
  Success: Done event with final text response
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt08_approve_plan.puml ---

@startuml sq_agt08_approve_plan
' ============================================================
' Title:     AGT-08 — APPROVE Plan
' Boundary:  nasim code agent CLI
' Purpose:   Execute queued tool calls from plan mode
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PlanSession" as plan
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over agent, registry
  Scope:          Execute queued tool calls after plan approval
  Preconditions:  Plan mode active with queued calls
  Contexts:       Called by CLI-02 (/approve command)
  Excludes:       Plan queuing (AGT-07)
  Rollback:       Partial execution on failure
  Design:         Drains pending_calls queue sequentially
  Classification: Process Decomposition
end note

== AGT-08 APPROVE Plan ==

agent -> plan : approve_plan()
plan -> plan : get pending_calls
plan -> plan : clear pending_calls

loop for each queued call
    plan -> registry : execute(tool_name, args)
    registry --> plan : ToolResult
    plan -> plan : collect results
end

plan --> agent : all results

note over agent, registry
  Flow:    approve -> drain queue -> execute sequentially -> results
  State:   <back:#F1F8E9>PLANNING</back> -> <back:#F3E5F5>TOOL_EXEC</back> -> <back:#FFF3E0>THINKING</back>
  Failure: Partial execution on tool failure
  Success: All queued calls executed
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt10_collect_subagent_result.puml ---

@startuml sq_agt10_collect_subagent_result
' ============================================================
' Title:     AGT-10 — Collect Subagent Result
' Boundary:  nasim code agent
' Purpose:   Wait for child agent completion and aggregate result
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-10 Collect Subagent Result

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "SubagentCoordinator" as coord
end box
box "Session Layer" #F1F8E9
  participant "SessionStore" as store
end box

note over agent, store
  Scope:          Collect and aggregate result from a completed child agent
  Preconditions:  Child agent spawned via AGT-09, child_id valid
  Excludes:       Spawn logic (AGT-09), persona delegation (AGT-11)
  Contexts:       Called after AGT-09 when parent needs child result
  Rollback:       Timeout → cancel child, return partial result
  Design:         Blocking wait with configurable timeout; result aggregated into parent context
  Classification: Process Decomposition
end note

== AGT-10 Collect Subagent Result ==

agent -> coord : collect(child_id, timeout)
activate coord

coord -> store : get child session status
activate store
store --> coord : child_status (running | completed | failed)
deactivate store

alt child completed
    coord -> store : get child result
    activate store
    store --> coord : child_result
    deactivate store
    coord -> coord : aggregate result into parent context
    coord --> agent : result
else child still running
    coord -> coord : wait with timeout
    alt timeout exceeded
        coord -> coord : cancel child execution
        coord --> agent : PartialResult(timeout)
    else child completes in time
        coord -> store : get child result
        activate store
        store --> coord : child_result
        deactivate store
        coord --> agent : result
    end
else child failed
    coord -> coord : collect error details
    coord --> agent : ChildError
end

deactivate coord

note over agent, store
  Flow:    AgentOrchestrator → SubagentCoordinator → wait → collect → aggregate
  State:   WAITING → COLLECTING → DONE
  Failure: Timeout → cancel child → partial result; child error → propagate
  Success: Aggregated result returned to parent
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt12_load_persona.puml ---

@startuml sq_agt12_load_persona
' ============================================================
' Title:     AGT-12 — Load Persona
' Boundary:  nasim code agent
' Purpose:   Load persona configuration and apply system prompt
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-12 Load Persona

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PersonaManager" as pm
end box
box "Config Layer" #FCE4EC
  participant "PersonaRegistry" as reg
end box

note over agent, reg
  Scope:          Load a persona configuration and apply its system prompt
  Preconditions:  PersonaManager initialized, persona name provided
  Excludes:       Persona switch (AGT-13), delegation (AGT-11)
  Contexts:       Called by AGT-11 or directly by AgentOrchestrator
  Rollback:       Config parse error → log error, retain current persona
  Design:         Persona config includes system prompt, allowed tools, model override
  Classification: Process Decomposition
end note

== AGT-12 Load Persona ==

agent -> pm : load(persona_name)
activate pm

pm -> reg : get_persona_config(persona_name)
activate reg
reg --> pm : config
deactivate reg

alt config valid
    pm -> pm : parse system prompt
    pm -> pm : extract tool allowlist
    pm -> pm : extract model override (if set)
    pm -> agent : PersonaLoaded(config)
else config invalid
    pm -> agent : PersonaLoadError
end

deactivate pm

note over agent, reg
  Flow:    AgentOrchestrator → PersonaManager → load persona config → apply system prompt
  State:   <back:#ECEFF1>IDLE</back> → LOADING → <back:#2E7D32>ACTIVE</back>
  Failure: Config error → log, retain current persona
  Success: Persona config loaded and applied
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt11_delegate_to_persona.puml ---

@startuml sq_agt11_delegate_to_persona
' ============================================================
' Title:     AGT-11 — Delegate to Persona
' Boundary:  nasim code agent
' Purpose:   Select and delegate task execution to a persona
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-11 Delegate to Persona

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PersonaManager" as pm
end box
box "Config Layer" #FCE4EC
  participant "PersonaRegistry" as reg
end box

note over agent, reg
  Scope:          Select a persona and delegate task execution
  Preconditions:  PersonaManager initialized, at least one persona registered
  Excludes:       Persona load/switch (AGT-12/13), subagent spawn (AGT-09)
  Contexts:       Called by AgentOrchestrator when task requires specialized behavior
  Rollback:       Persona not found → fallback to default persona
  Design:         Persona selection based on task tags or explicit request
  Classification: Process Decomposition
end note

== AGT-11 Delegate to Persona ==

agent -> pm : delegate(task, persona_hint)
activate pm

pm -> reg : lookup persona(hint)
activate reg
reg --> pm : persona_config
deactivate reg

alt persona found
    pm -> pm : load persona system prompt
    pm -> pm : apply persona to agent context
    pm --> agent : PersonaDelegated
else persona not found
    pm -> pm : fallback to default persona
    pm --> agent : PersonaDelegated(default)
end

deactivate pm

note over agent, reg
  Flow:    AgentOrchestrator → PersonaManager → select persona → delegate task
  State:   <back:#ECEFF1>IDLE</back> → DELEGATING → <back:#2E7D32>ACTIVE</back>
  Failure: Persona not found → fallback to default
  Success: Task delegated with persona context applied
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt06_compact_context.puml ---

@startuml sq_agt06_compact_context
' ============================================================
' Title:     AGT-06 — COMPACT Context
' Boundary:  nasim code agent CLI
' Purpose:   Context compaction when token budget exceeded
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
  participant "ContextCompactor" as compactor
end box

note over agent, compactor
  Scope:          Context compaction when token budget exceeded
  Preconditions:  token_count > context_budget
  Contexts:       Called by AGT-03 (Manage Conversation)
  Excludes:       Token tracking (CTX-01)
  Rollback:       Truncate oldest messages as fallback
  Design:         Secondary LLM call to summarize old exchanges
  Classification: Process Decomposition
end note

== AGT-06 COMPACT Context ==

agent -> history : check token_count > budget
history --> agent : COMPACT_NEEDED
agent -> compactor : compact(messages, budget)
ref over compactor
  CTX-02: COMPACT Context
end ref
compactor --> agent : shortened messages
agent -> history : replace messages with shortened list

note over agent, compactor
  Flow:    budget check -> select old -> summarize -> replace
  State:   <back:#FFF3E0>THINKING</back> -> <back:#E0F2F1>COMPACTING</back> -> <back:#FFF3E0>THINKING</back>
  Failure: LLM fails -> truncate fallback
  Success: Messages shortened, token count reduced
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt05_check_permission.puml ---

@startuml sq_agt05_check_permission
' ============================================================
' Title:     AGT-05 — CHECK Tool Permission
' Boundary:  nasim code agent
' Purpose:   Per-tool safety gate before execution (internal step of AGT-02)
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    Meta-Software Designer audit 2026-06-21
' Note:      Process decomposition — internal step of AGT-02 (DISPATCH Tool Call).
'            Not a standalone UC. Actor forbidden per sq.md classification rules.
' ============================================================

title nasim — AGT-05 CHECK Tool Permission

box "Agent Layer" #E3F2FD
  participant "SafetyCoordinator" as safety
  participant "PermissionGate" as gate
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over safety, registry
  Scope:          Per-tool safety gate — checks tool.safe flag against safety_mode
  Preconditions:  Tool call received, SafetyCoordinator initialized
  Excludes:       Tool execution, user approval prompt (CLI-06), injection/egress checks
  Contexts:       Internal step of AGT-15 (DISPATCH Safety Pipeline), called by AGT-02
  Rollback:       Rejected -> SafetyViolation returned to caller
  Design:         First stage of safety pipeline. Checks tool.safe flag + safety_mode config
  Classification: Process Decomposition (no actor — parent is AGT-02/AGT-15)
end note

== AGT-05 CHECK Tool Permission ==

safety -> gate : check_permission(tool_name, args)
activate gate

gate -> registry : get_tool(tool_name)
activate registry
registry --> gate : Tool(safe=True/False)
deactivate registry

gate -> gate : check tool.safe against safety_mode

alt safety_mode = ask AND tool.unsafe
    gate --> safety : SafetyViolation(permission_denied)
else safety_mode = off AND tool.unsafe
    gate --> safety : SafetyViolation(permission_denied)
else safe tool or auto mode
    gate --> safety : SafetyPassed
end

deactivate gate

note over safety, registry
  Flow:    SafetyCoordinator -> PermissionGate -> ToolRegistry.get_tool() -> check safe flag -> return
  State:   No state change (delegated by AGT-15)
  Failure: Unsafe tool in ask/off mode -> SafetyViolation
  Success: SafetyPassed -> proceed to next pipeline stage (injection, egress)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt07_queue_plan.puml ---

@startuml sq_agt07_queue_plan
' ============================================================
' Title:     AGT-07 — Queue Plan
' Boundary:  nasim code agent CLI
' Purpose:   Queue tool calls in plan mode without executing
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PlanSession" as plan
end box

note over agent, plan
  Scope:          Queue tool calls in plan mode
  Preconditions:  Plan mode active (/plan toggled)
  Contexts:       Called by AGT-01 (PROCESS User Task) in plan mode
  Excludes:       Tool execution, permission checks
  Rollback:       N/A — queued calls are never executed until approved
  Design:         Tool calls displayed as plan, not executed
  Classification: Process Decomposition
end note

== AGT-07 Queue Plan ==

agent -> plan : queue_tool_call(tool_name, args)
plan -> plan : append to pending_calls list
plan --> agent : queued

agent -> plan : display_plan()
plan --> agent : formatted plan text

note over agent, plan
  Flow:    tool call -> queue -> display as plan
  State:   <back:#FFF3E0>THINKING</back> -> <back:#F1F8E9>PLANNING</back>
  Failure: N/A
  Success: Tool calls queued and displayed as plan
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt13_switch_persona.puml ---

@startuml sq_agt13_switch_persona
' ============================================================
' Title:     AGT-13 — Switch Persona
' Boundary:  nasim code agent
' Purpose:   Unload current persona and load a new one
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-13 Switch Persona

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PersonaManager" as pm
end box
box "Config Layer" #FCE4EC
  participant "PersonaRegistry" as reg
end box

note over agent, reg
  Scope:          Unload current persona and load a new one in one operation
  Preconditions:  PersonaManager active with current persona loaded
  Excludes:       Load only (AGT-12), delegation (AGT-11)
  Contexts:       Called when user or task requests persona change mid-session
  Rollback:       New persona load fails → retain previous persona
  Design:         Atomic switch: unload current → load new; partial failure retains old
  Classification: Process Decomposition
end note

== AGT-13 Switch Persona ==

agent -> pm : switch(new_persona_name)
activate pm

pm -> pm : unload current persona
pm -> pm : clear system prompt
pm -> pm : clear tool allowlist

pm -> reg : get_persona_config(new_persona_name)
activate reg
reg --> pm : new_config
deactivate reg

alt new config valid
    pm -> pm : parse new system prompt
    pm -> pm : apply new config
    pm -> agent : PersonaSwitched(new_persona)
else new config invalid
    pm -> pm : reload previous persona config
    pm -> agent : PersonaSwitchFailed(retained previous)
end

deactivate pm

note over agent, reg
  Flow:    AgentOrchestrator → PersonaManager → unload current → load new → apply
  State:   <back:#2E7D32>ACTIVE</back> → SWITCHING → <back:#2E7D32>ACTIVE</back>
  Failure: New config invalid → retain previous persona
  Success: Persona switched, new system prompt active
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt14_handle_error.puml ---

@startuml sq_agt14_handle_error
' ============================================================
' Title:     AGT-14 — Handle Error
' Boundary:  nasim code agent
' Purpose:   Classify errors and determine recovery action
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-14 Handle Error

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ErrorBoundary" as eb
end box
box "Safety Layer" #FFF9C4
  participant "SafetyCoordinator" as safety
end box

note over agent, safety
  Scope:          Classify errors and determine recovery strategy
  Preconditions:  Error occurred in agent loop (LLM, tool, or session)
  Excludes:       Error display (CLI-03), error logging (OBS-01)
  Contexts:       Called by AGT-01 when LLM or tool call fails
  Rollback:       Unrecoverable error → terminate task with error event
  Design:         Error classification drives retry, fallback, or abort decisions
  Classification: Process Decomposition
end note

== AGT-14 Handle Error ==

agent -> eb : handle(error)
activate eb

eb -> eb : classify error type
eb -> eb : determine severity

alt retryable error (transient)
    eb -> eb : set retry policy (backoff + max retries)
    eb --> agent : RecoveryAction(retry)
else recoverable error (config)
    eb -> safety : check safety constraints
    activate safety
    safety --> eb : safety_status
    deactivate safety
    eb -> eb : determine fallback strategy
    eb --> agent : RecoveryAction(fallback)
else unrecoverable error
    eb -> eb : log error details
    eb --> agent : RecoveryAction(abort)
end

deactivate eb

note over agent, safety
  Flow:    AgentOrchestrator → ErrorBoundary → classify → determine recovery → return action
  State:   <back:#FFEBEE>ERROR</back> → CLASSIFYING → <back:#FBE9E7>RETRY</back> | FALLBACK | ABORT
  Failure: Unrecoverable → abort with error event
  Success: Recovery action returned for agent to execute
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt15_dispatch_safety_pipeline.puml ---

@startuml sq_agt15_dispatch_safety_pipeline
' ============================================================
' Title:     AGT-15 — Dispatch Safety Pipeline
' Boundary:  nasim code agent
' Purpose:   Run injection scan, egress inspect, and permission check
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-15 Dispatch Safety Pipeline

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "SafetyCoordinator" as safety
end box
box "Safety Layer" #FFF9C4
  participant "InjectionScanner" as inj
  participant "EgressInspector" as egr
  participant "PermissionGate" as perm
end box

note over agent, perm
  Scope:          Run full safety pipeline before tool execution
  Preconditions:  Tool call queued, SafetyCoordinator initialized
  Excludes:       Individual safety checks (SAF-01/02/03)
  Contexts:       Called by AGT-02 before every tool dispatch
  Rollback:       Any stage fails → block tool execution, report violation
  Design:         Pipeline stages run sequentially; first failure short-circuits
  Classification: Process Decomposition
end note

== AGT-15 Dispatch Safety Pipeline ==

agent -> safety : dispatch_safety_check(tool_call)
activate safety

safety -> inj : scan_prompt(injected_content)
activate inj
inj --> safety : scan_result (pass | block)
deactivate inj

alt injection detected
    safety --> agent : SafetyViolation(injection)
end

safety -> egr : inspect_output(tool_output)
activate egr
egr --> safety : inspect_result (pass | flag)
deactivate egr

alt egress violation
    safety --> agent : SafetyViolation(egress)
end

safety -> perm : check_permission(tool_name, args)
activate perm
perm --> safety : perm_result (allow | deny)
deactivate perm

alt permission denied
    safety --> agent : SafetyViolation(permission)
end

safety --> agent : SafetyPassed
deactivate safety

note over agent, perm
  Flow:    AgentOrchestrator → SafetyCoordinator → injection scan → egress inspect → permission check → return
  State:   CHECKING → INJECTION → EGRESS → PERMISSION → PASSED | BLOCKED
  Failure: Any stage fails → block, report violation
  Success: SafetyPassed, tool execution allowed
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt03_update_conversation.puml ---

@startuml sq_agt03_update_conversation
' ============================================================
' Title:     AGT-03 — Update Conversation
' Boundary:  nasim code agent CLI
' Purpose:   Message list management and token tracking
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
end box

note over agent, history
  Scope:          Message list management and token tracking
  Preconditions:  ConversationHistory initialized
  Contexts:       Called by AGT-01 (PROCESS User Task)
  Excludes:       Context compaction (CTX-02)
  Rollback:       N/A
  Design:         Owns messages + token_count; triggers compaction
  Classification: Process Decomposition
end note

== AGT-03 Manage Conversation ==

agent -> history : add_message(msg)
history -> history : self.messages.append(msg)
history -> history : self.token_count += estimate_tokens(msg)

alt token_count > context_budget
    history --> agent : COMPACT_NEEDED
    ref over history, agent
      CTX-02: COMPACT Context
    end ref
else within budget
    history --> agent : ok
end

agent -> history : get_messages()
history --> agent : messages list

note over agent, history
  Flow:    add message -> track tokens -> check budget -> compact if needed
  State:   No state change (or COMPACTING if budget exceeded)
  Failure: N/A
  Success: Messages managed, token count tracked
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt04_delete_history.puml ---

@startuml sq_agt04_delete_history
' ============================================================
' Title:     AGT-04 — Delete History
' Boundary:  nasim code agent CLI
' Purpose:   Clear conversation history
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
end box

note over agent, history
  Scope:          Clear conversation history keeping system prompt
  Preconditions:  Agent initialized with system prompt
  Contexts:       Called by CLI-02 (/reset slash command)
  Excludes:       Session persistence
  Rollback:       N/A
  Design:         Keeps system prompt, clears all other messages
  Classification: Process Decomposition
end note

== AGT-04 Reset History ==

agent -> history : reset()
history -> history : self.messages = [system_prompt]
history -> history : self.token_count = estimate_tokens(system_prompt)

history --> agent : history cleared

note over agent, history
  Flow:    reset -> keep system prompt -> clear rest
  State:   No state change
  Failure: N/A
  Success: Conversation reset to initial state
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt03_apply_whole_file.puml ---

@startuml sq_edt03_apply_whole_file
' ============================================================
' Title:     EDT-03 — Apply Whole File
' Boundary:  nasim code agent CLI
' Purpose:   Verify edit applied correctly
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Layer" #FFF3E0
  participant "EditValidator" as validator
  participant "FileSystem" as fs
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as tool
end box

note over user, tool
  Scope:
    - edt03 VALIDATE Edit — verify edit applied correctly

  Preconditions:
    - EDT-02 completed (EditResult available)
    - File exists at target path

  Contexts:
    - Called after EDT-02 (Apply Edit)
    - Feeds into EDT-04 (Stage Edit) on success

  Excludes:
    - Edit execution (handled by EDT-02)
    - Diff staging (handled by EDT-04)
    - Semantic correctness (handled by EVL-01/02)

  Rollback:
    - Validation failure → trigger revert via backup_path

  Design:
  Classification: Primary Orchestrator
    - EditValidator reads edited file and compares with expected
    - Syntax check via language-specific linter (if available)
    - Diff verification ensures intended changes applied
    - Returns structured validation result

  Returns:
    - Success: ValidationResult with pass/fail details
    - Failure: ValidationResult with failure reasons
end note

== edt03 VALIDATE Edit ==

agent -> validator : VALIDATE_EDIT(edit_result)
activate validator

validator -> fs : read_file(edit_result.file_path)
activate fs
fs --> validator : actual_content
deactivate fs

validator -> validator : verify_diff_applies(edit_result.diff, actual_content)

validator -> tool : run_linter(file_path)
activate tool
tool --> validator : lint_result
deactivate tool

validator -> validator : check_syntax(lint_result)

validator -> validator : verify_no_unintended_changes(actual_content, edit_result)

validator --> agent : ValidationResult(passed, reasons[])
deactivate validator

note over user, tool
  Flow:
    - AgentOrchestrator → EditValidator → FileSystem + ToolRegistry → ValidationResult

  State:
    - <back:#ECEFF1>IDLE</back> → READING → CHECKING → LINTING → DONE

  Failure:
    - Diff mismatch → validation fails
    - Syntax error → validation fails

  Success:
    - ValidationResult with pass=true

  Key invariants:
    - Edited file always read fresh for validation
    - Linter run only if language supported
    - Validation is deterministic for same input
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt01_select_strategy.puml ---

@startuml sq_edt01_select_strategy
' ============================================================
' Title:     EDT-01 — SELECT Strategy
' Boundary:  nasim code agent
' Purpose:   Choose optimal edit format for the target model
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-01 SELECT Strategy

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Layer" #FFF3E0
  participant "StrategySelector" as selector
  participant "EditStrategy" as strategy
end box
box "Config Layer" #FCE4EC
  participant "ConfigLoader" as config
end box

note over agent, config
  Scope:          Choose optimal edit format for the target model
  Preconditions:  Agent has identified a file to edit, Config loaded
  Excludes:       Edit execution (EDT-02..09), diff staging (EDT-10)
  Contexts:       Called before EDT-02 (APPLY Search-Replace); entry point for edit subsystem
  Rollback:       No valid strategy -> return error, suggest manual edit
  Design:         StrategySelector evaluates model capabilities vs edit requirements; format selected by diff size and model support
  Classification: Primary Orchestrator
end note

== EDT-01 SELECT Strategy ==

agent -> selector : SELECT_STRATEGY(file_path, edit_description, model_id)
activate selector

selector -> config : get_supported_formats(model_id)
activate config
config --> selector : supported_formats[]
deactivate config

selector -> selector : estimate_diff_size(edit_description)

alt diff_size <= 5 lines
    selector -> strategy : CREATE_SEARCH_REPLACE(file_path, edit_description)
    activate strategy
    strategy --> selector : SearchReplaceEdit
    deactivate strategy
else diff_size <= 50 lines
    selector -> strategy : CREATE_UNIFIED_DIFF(file_path, edit_description)
    activate strategy
    strategy --> selector : UnifiedDiffEdit
    deactivate strategy
else diff_size > 50 lines
    selector -> strategy : CREATE_FULL_REWRITE(file_path, edit_description)
    activate strategy
    strategy --> selector : FullRewriteEdit
    deactivate strategy
end

selector -> selector : validate_format_compatibility(strategy, model_id)

selector --> agent : EditStrategy(format, parameters, confidence)
deactivate selector

note over agent, config
  Flow:    AgentOrchestrator -> StrategySelector -> Config + EditStrategy -> EditStrategy
  State:   <back:#ECEFF1>IDLE</back> -> <back:#FFF3E0>THINKING</back> -> <back:#ECEFF1>IDLE</back>
  Failure: No compatible format -> error + manual suggestion
  Success: EditStrategy with chosen format and parameters
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt09_apply_inline_patch.puml ---

@startuml sq_edt09_apply_inline_patch
' ============================================================
' Title:     EDT-09 — APPLY Inline Patch
' Boundary:  nasim code agent
' Purpose:   Apply inline patch with line-level precision
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-09 APPLY Inline Patch

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Layer" #FFF3E0
  participant "EditStrategyManager" as esm
  participant "InlinePatchCoder" as ipc
end box
box "FileSystem Layer" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Inline patch application with line-level precision
  Preconditions:  Patch generated with line offsets, target file readable
  Excludes:       Whole-file rewrites, sandbox isolation, AST manipulation
  Contexts:       EDT-01 SELECT Strategy selects this for precise line-targeted edits
  Rollback:       Patch context mismatch → reject patch, report conflict
  Design:         InlinePatchCoder parses patch format, validates context lines, applies at offset
  Classification: Process Decomposition
end note

== EDT-09 APPLY Inline Patch ==

agent -> esm : APPLY_INLINE_PATCH(file_path, patch)
activate esm

esm -> ipc : code_inline_patch(file_path, patch)
activate ipc

ipc -> ipc : parse_patch(patch)

ipc -> fs : read_file(file_path)
activate fs
fs --> ipc : source_lines
deactivate fs

ipc -> ipc : validate_context_lines(source_lines, patch.context_lines)

alt context validation passes
    ipc -> ipc : apply_hunks(source_lines, patch.hunks)

    ipc -> fs : write_file(file_path, patched_source)
    activate fs
    fs --> ipc : write_result
    deactivate fs

    ipc -> ipc : validate_no_conflicts(patched_source)
else context mismatch
    ipc -> ipc : reject_patch(reason="context mismatch")
end

ipc --> esm : EditResult(success, file_path, lines_changed)
deactivate ipc

esm --> agent : EditResult
deactivate esm

note over participants
  Flow:    AgentOrchestrator → EditStrategyManager → InlinePatchCoder → parse patch → apply → validate
  State:   <back:#ECEFF1>IDLE</back> → PARSING → VALIDATING → APPLYING → DONE
  Failure: Context mismatch → patch rejected, conflict reported
  Success: EditResult with patched file and line change count
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt10_stage_diff.puml ---

@startuml sq_edt10_stage_diff
' ============================================================
' Title:     EDT-10 — STAGE Diff
' Boundary:  nasim code agent
' Purpose:   Stage edit in DiffSandboxManager for review before sandbox-validated apply
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Meta-Software Designer audit 2026-06-21
' Note:      Process decomposition — internal step of edit flow. No actor per sq.md rules.
' ============================================================

title nasim — EDT-10 STAGE Diff

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Sandbox Layer" #F1F8E9
  participant "DiffSandboxManager" as diff_mgr
  participant "EditStagingArea" as staging
  participant "DiffComputer" as diff_comp
end box

note over agent, diff_comp
  Scope:          Stage edit in DiffSandboxManager for review
  Preconditions:  Edit strategy applied, DiffSandboxManager initialized
  Excludes:       Edit execution (EDT-02..09), user review (SAF-02), file system writes
  Contexts:       Called by EDT-01 (SELECT Strategy) when diff_sandbox mode selected
  Rollback:       Staging failure → discard from sandbox
  Design:         DiffSandboxManager holds pending edits in isolated staging area via EditStagingArea. DiffComputer computes diffs for review.
  Classification: Process Decomposition
end note

== EDT-10 STAGE Diff ==

agent -> diff_mgr : STAGE_DIFF(edit_result)
activate diff_mgr

diff_mgr -> staging : allocate_edit_slot()
activate staging

staging -> staging : store_edit(edit_result)

staging -> diff_comp : compute_staged_diff(original, staged)
activate diff_comp
diff_comp --> staging : diff_summary
deactivate diff_comp

staging --> diff_mgr : StagedEdit(edit_id, diff_summary, timestamp)
deactivate staging

diff_mgr --> agent : StagedEdit(edit_id, diff_summary)
deactivate diff_mgr

note over agent, diff_comp
  Flow:    AgentOrchestrator → DiffSandboxManager → EditStagingArea → DiffComputer → return
  State:   <back:#F1F8E9>STAGING</back>
  Failure: Staging failure → discard edit
  Success: StagedEdit with edit_id and diff summary for review
  Key invariants:
    - Each staged edit has unique ID
    - Sandbox is in-memory (no file system side effects)
    - Edits can be applied atomically or discarded
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt07_apply_diff_sandbox.puml ---

@startuml sq_edt07_apply_diff_sandbox
' ============================================================
' Title:     EDT-07 — APPLY Diff Sandbox
' Boundary:  nasim code agent
' Purpose:   Apply diff in isolated sandbox before committing to real file
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-07 APPLY Diff Sandbox

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Layer" #FFF3E0
  participant "EditStrategyManager" as esm
  participant "DiffSandboxCoder" as dsc
end box
box "Sandbox Layer" #B3E5FC
  participant "DiffSandboxManager" as dsm
end box
box "FileSystem Layer" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Apply diff in sandbox, validate, then commit to real file
  Preconditions:  Diff generated, sandbox environment available
  Excludes:       Direct file edits, AST-level manipulation
  Contexts:       EDT-01 SELECT Strategy chooses this for risky or large diffs
  Rollback:       Sandbox validation fails → discard sandbox, report error
  Design:         DiffSandboxCoder delegates to DiffSandboxManager for isolation
  Classification: Process Decomposition
end note

== EDT-07 APPLY Diff Sandbox ==

agent -> esm : APPLY_DIFF_SANDBOX(file_path, diff_patch)
activate esm

esm -> dsc : code_sandboxed_diff(file_path, diff_patch)
activate dsc

dsc -> dsm : create_sandbox(file_path)
activate dsm
dsm -> fs : copy_to_sandbox(file_path)
activate fs
fs --> dsm : sandbox_path
deactivate fs
dsm --> dsc : SandboxHandle(sandbox_path)
deactivate dsm

dsc -> dsm : apply_diff(sandbox_path, diff_patch)
activate dsm
dsm -> fs : apply_patch(sandbox_path, diff_patch)
activate fs
fs --> dsm : patch_result
deactivate fs
dsm --> dsc : DiffApplyResult
deactivate dsm

dsc -> dsm : validate_sandbox(sandbox_path)
activate dsm
dsm -> dsm : run_syntax_check(sandbox_path)
dsm -> dsm : run_basic_validation(sandbox_path)
dsm --> dsc : ValidationResult
deactivate dsm

alt validation passes
    dsc -> dsm : commit_sandbox(sandbox_path, file_path)
    activate dsm
    dsm -> fs : move_sandbox_to_target(sandbox_path, file_path)
    activate fs
    fs --> dsm : write_result
    deactivate fs
    dsm --> dsc : CommitResult
    deactivate dsm
else validation fails
    dsc -> dsm : discard_sandbox(sandbox_path)
    activate dsm
    dsm --> dsc : DiscardResult
    deactivate dsm
end

dsc --> esm : EditResult(success, file_path)
deactivate dsc

esm --> agent : EditResult
deactivate esm

note over participants
  Flow:    AgentOrchestrator → EditStrategyManager → DiffSandboxCoder → DiffSandboxManager → sandbox validate → apply
  State:   <back:#ECEFF1>IDLE</back> → SANDBOXING → APPLYING → VALIDATING → COMMITTING → DONE
  Failure: Validation fails → sandbox discarded, error reported
  Success: EditResult with sandbox-validated file applied
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt02_apply_search_replace.puml ---

@startuml sq_edt02_apply_search_replace
' ============================================================
' Title:     EDT-02 — APPLY Search-Replace
' Boundary:  nasim code agent
' Purpose:   Execute edit via search-replace strategy
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Prompt audit 2026-06-21 (cop.md: PermissionGate removed, safety at AGT-15 level)
' ============================================================

title nasim — EDT-02 APPLY Search-Replace

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Layer" #FFF3E0
  participant "EditApplier" as applier
  participant "SearchReplaceCoder" as strategy
end box
box "Sandbox Layer" #F1F8E9
  participant "FileSystem" as fs
end box

note over agent, fs
  Scope:          Execute edit via search-replace strategy
  Preconditions:  EDT-01 completed (EditStrategy selected), target file exists and is writable
  Contexts:       Called by AgentOrchestrator after EDT-01
  Excludes:       Strategy selection (EDT-01), post-edit validation (EDT-03), diff staging (EDT-10)
  Rollback:       Write failure -> restore original file from backup
  Design:         EditApplier reads original, applies SearchReplaceCoder strategy, writes result. Backup created before modification.
  Classification: Process Decomposition
end note

== EDT-02 APPLY Search-Replace ==

agent -> applier : APPLY_EDIT(strategy, file_path)
activate applier

applier -> fs : read_file(file_path)
activate fs
fs --> applier : original_content
deactivate fs

applier -> fs : create_backup(file_path)
activate fs
fs --> applier : backup_path
deactivate fs

applier -> strategy : apply(original_content)
activate strategy
strategy --> applier : modified_content
deactivate strategy

applier -> fs : write_file(file_path, modified_content)
activate fs
fs --> applier : write_success
deactivate fs

applier -> applier : compute_diff(original_content, modified_content)

applier --> agent : EditResult(diff, file_path, backup_path)
deactivate applier

note over agent, fs
  Flow:    AgentOrchestrator -> EditApplier -> SearchReplaceCoder + FileSystem -> EditResult
  State:   <back:#ECEFF1>IDLE</back> -> READING -> BACKING_UP -> WRITING -> DIFFING -> DONE
  Failure: Write failure -> restore from backup
  Success: EditResult with diff and backup path
  Key invariants:
    - Backup always created before modification
    - Original file restored on any failure
    - Safety checked at AGT-15 level before tool dispatch
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt04_apply_unified_diff.puml ---

@startuml sq_edt04_apply_unified_diff
' ============================================================
' Title:     EDT-04 — APPLY Unified Diff
' Boundary:  nasim code agent
' Purpose:   Apply unified diff format edit to file
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-04 APPLY Unified Diff

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Layer" #FFF3E0
  participant "EditStrategyManager" as mgr
  participant "UnifiedDiffCoder" as coder
end box

note over agent, coder
  Scope:          Apply unified diff format edit to file
  Preconditions:  EditStrategyManager initialized, file exists
  Excludes:       Strategy selection (EDT-01), validation (EDT-03)
  Contexts:       Called by AGT-02 DISPATCH Tool Call
  Rollback:       Diff application failure returns error
  Design:         Parses unified diff, applies hunks sequentially
  Classification: Process Decomposition
end note

== EDT-04 APPLY Unified Diff ==

agent -> mgr : APPLY_UNIFIED_DIFF(file, diff)
activate mgr

mgr -> coder : apply(diff, file_content)
activate coder

coder -> coder : parse diff hunks
coder -> coder : apply each hunk

break Hunk application fails
  coder --> mgr : DiffError(hunk_mismatch)
end

coder --> mgr : ModifiedContent
deactivate coder

mgr --> agent : ToolResult(success=True)
deactivate mgr

note over agent, coder
  Flow:    Agent -> EditStrategyManager -> UnifiedDiffCoder -> parse hunks -> apply -> result
  State:   No state change
  Failure: Hunk mismatch, file not found -> ToolResult(success=False)
  Success: File modified with unified diff
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt05_apply_fenced_block.puml ---

@startuml sq_edt05_apply_fenced_block
' ============================================================
' Title:     EDT-05 — APPLY Fenced Block
' Boundary:  nasim code agent
' Purpose:   Apply fenced code block format edit
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-05 APPLY Fenced Block

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Layer" #FFF3E0
  participant "EditStrategyManager" as mgr
  participant "FencedBlockCoder" as coder
end box

note over agent, coder
  Scope:          Apply fenced code block format edit
  Preconditions:  EditStrategyManager initialized, file exists
  Excludes:       Strategy selection (EDT-01), validation (EDT-03)
  Contexts:       Called by AGT-02 DISPATCH Tool Call
  Rollback:       Block extraction failure returns error
  Design:         Extracts fenced code block, replaces matching section
  Classification: Process Decomposition
end note

== EDT-05 APPLY Fenced Block ==

agent -> mgr : APPLY_FENCED_BLOCK(file, block)
activate mgr

mgr -> coder : apply(block, file_content)
activate coder

coder -> coder : extract fenced block content
coder -> coder : locate matching section in file
coder -> coder : replace section

break Section not found
  coder --> mgr : BlockError(section_not_found)
end

coder --> mgr : ModifiedContent
deactivate coder

mgr --> agent : ToolResult(success=True)
deactivate mgr

note over agent, coder
  Flow:    Agent -> EditStrategyManager -> FencedBlockCoder -> extract -> locate -> replace
  State:   No state change
  Failure: Section not found, ambiguous match -> ToolResult(success=False)
  Success: File modified with fenced block replacement
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt06_apply_function_level.puml ---

@startuml sq_edt06_apply_function_level
' ============================================================
' Title:     EDT-06 — APPLY Function-Level
' Boundary:  nasim code agent
' Purpose:   Edit a single function via AST-aware replace
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-06 APPLY Function-Level

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Layer" #FFF3E0
  participant "EditStrategyManager" as esm
  participant "FunctionLevelCoder" as flc
end box
box "Tool Layer" #F3E5F5
  participant "ASTParser" as ast
end box
box "FileSystem Layer" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Function-level edit via AST parse and targeted replace
  Preconditions:  File identified, function boundary determinable
  Excludes:       Multi-file edits, whole-file rewrites
  Contexts:       EDT-01 SELECT Strategy selects this for function-scoped diffs
  Rollback:       AST parse failure → fallback to EDT-02 or EDT-03
  Design:         FunctionLevelCoder locates function node, replaces body, validates AST integrity
  Classification: Process Decomposition
end note

== EDT-06 APPLY Function-Level ==

agent -> esm : APPLY_FUNCTION_LEVEL(file_path, function_name, new_body)
activate esm

esm -> flc : code_function_edit(file_path, function_name, new_body)
activate flc

flc -> fs : read_file(file_path)
activate fs
fs --> flc : source_content
deactivate fs

flc -> ast : parse(source_content)
activate ast
ast --> flc : ast_root
deactivate ast

flc -> flc : locate_function_node(ast_root, function_name)

flc -> flc : replace_function_body(node, new_body)

flc -> flc : validate_ast_integrity(ast_root)

flc -> fs : write_file(file_path, modified_source)
activate fs
fs --> flc : write_result
deactivate fs

flc --> esm : EditResult(success, file_path, function_name)
deactivate flc

esm --> agent : EditResult
deactivate esm

note over participants
  Flow:    AgentOrchestrator → EditStrategyManager → FunctionLevelCoder → AST parse → replace function → validate
  State:   <back:#ECEFF1>IDLE</back> → PARSING → REPLACING → VALIDATING → DONE
  Failure: AST parse error → fallback to EDT-02/EDT-03; function not found → error
  Success: EditResult with modified file and function scope
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt08_apply_architect.puml ---

@startuml sq_edt08_apply_architect
' ============================================================
' Title:     EDT-08 — APPLY Architect
' Boundary:  nasim code agent
' Purpose:   Plan and apply multi-file edits via architectural decomposition
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-08 APPLY Architect

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Layer" #FFF3E0
  participant "EditStrategyManager" as esm
  participant "ArchitectCoder" as arch
end box
box "Tool Layer" #F3E5F5
  participant "ASTParser" as ast
end box
box "FileSystem Layer" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Multi-file edit planning and coordinated application
  Preconditions:  Edit intent spans multiple files, dependency graph derivable
  Excludes:       Single-file edits, sandbox isolation
  Contexts:       EDT-01 SELECT Strategy selects this for cross-file refactors
  Rollback:       Partial application detected → revert all changed files
  Design:         ArchitectCoder plans edit order, applies sequentially, validates each step
  Classification: Process Decomposition
end note

== EDT-08 APPLY Architect ==

agent -> esm : APPLY_ARCHITECT(edit_plan[])
activate esm

esm -> arch : code_architectural_edit(edit_plan)
activate arch

arch -> arch : analyze_dependencies(edit_plan)

arch -> arch : sort_edit_order(dependency_graph)

loop for each file_edit in ordered_edits
    arch -> fs : read_file(file_edit.file_path)
    activate fs
    fs --> arch : source_content
    deactivate fs

    arch -> ast : parse(source_content)
    activate ast
    ast --> arch : ast_root
    deactivate ast

    arch -> arch : apply_file_edit(ast_root, file_edit)

    arch -> fs : write_file(file_edit.file_path, modified_source)
    activate fs
    fs --> arch : write_result
    deactivate fs

    arch -> arch : validate_step(file_edit.file_path)
end

arch -> arch : validate_cross_file_integrity()

arch --> esm : EditResult(success, files_modified[])
deactivate arch

esm --> agent : EditResult
deactivate esm

note over participants
  Flow:    AgentOrchestrator → EditStrategyManager → ArchitectCoder → plan multi-file edit → apply across files
  State:   <back:#ECEFF1>IDLE</back> → <back:#F1F8E9>PLANNING</back> → EDITING → VALIDATING → DONE
  Failure: Cross-file validation fails → revert all changed files
  Success: EditResult with list of modified files and integrity confirmation
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim05_embed_code.puml ---

@startuml sq_rim05_embed_code
' ============================================================
' Title:     RIM-05 — EMBED Code
' Boundary:  nasim code agent
' Purpose:   Generate vector embeddings for code fragments
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-05 EMBED Code

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Intelligence Layer" #F9FBE7
  participant "RepoIntelligenceManager" as rim
  participant "EmbeddingAdapter" as embed
end box
box "External Layer" #F5F5F5
  participant "EmbeddingProvider" as provider
end box
box "Storage Layer" #F3E5F5
  participant "VectorStore" as vstore
end box

note over participants
  Scope:          Generate vector embeddings for code fragments and store them
  Preconditions:  Embedding provider configured, code fragments identified
  Excludes:       Semantic search (handled by RIM-06), AST indexing
  Contexts:       RIM-01 INDEX Codebase identifies fragments; RIM-06 SEARCH Semantic consumes embeddings
  Rollback:       Provider failure → partial embeddings retained, error reported
  Design:         EmbeddingAdapter batches fragments, calls provider, stores vectors
  Classification: Process Decomposition
end note

== RIM-05 EMBED Code ==

agent -> rim : EMBED_CODE(code_fragments[])
activate rim

rim -> embed : generate_embeddings(code_fragments)
activate embed

loop for each batch of fragments
    embed -> provider : embed(batch)
    activate provider
    provider --> embed : vectors[]
    deactivate provider

    embed -> embed : validate_dimensions(vectors)
end

embed -> vstore : store_vectors(code_fragments, vectors)
activate vstore
vstore --> embed : store_result
deactivate vstore

embed --> rim : EmbeddingResult(count, dimensions)
deactivate embed

rim --> agent : EmbeddingResult
deactivate rim

note over participants
  Flow:    RepoIntelligenceManager -> EmbeddingAdapter -> generate embeddings -> return vectors
  State:   <back:#ECEFF1>IDLE</back> → BATCHING → EMBEDDING → STORING → DONE
  Failure: Provider failure → partial embeddings retained
  Success: EmbeddingResult with fragment count and vector dimensions
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim02_build_symbol_graph.puml ---

@startuml sq_rim02_build_symbol_graph
' ============================================================
' Title:     RIM-02 — BUILD Symbol Graph
' Boundary:  nasim code agent
' Purpose:   Build cross-file symbol reference graph
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-02 BUILD Symbol Graph

box "Repo Intelligence Layer" #E0F2F1
  participant "RepoIntelligenceManager" as rim
  participant "SymbolGraph" as graph
end box

note over rim, graph
  Scope:          Build cross-file symbol reference graph
  Preconditions:  AST index available from RIM-01
  Excludes:       AST parsing (RIM-01), search (RIM-06)
  Contexts:       Called after RIM-01 INDEX Codebase
  Rollback:       Partial graph on parse errors
  Design:         Builds directed graph of symbols and their references
  Classification: Process Decomposition
end note

== RIM-02 BUILD Symbol Graph ==

rim -> graph : BUILD from AST index
activate graph

graph -> graph : extract symbols per file
graph -> graph : resolve cross-file references
graph -> graph : build edges (defines, references, imports)

break Reference resolution fails
  graph --> rim : partial graph with unresolved refs
end

graph --> rim : SymbolGraph(symbols, edges)
deactivate graph

note over rim, graph
  Flow:    RepoIntelligenceManager -> SymbolGraph -> extract symbols -> resolve refs -> build graph
  State:   No state change
  Failure: Partial graph on unresolved references
  Success: Complete symbol reference graph
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim06_search_semantic.puml ---

@startuml sq_rim06_search_semantic
' ============================================================
' Title:     RIM-06 — Search Semantic
' Boundary:  nasim code agent CLI
' Purpose:   Embedding-based code similarity search across repository
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Index Layer" #FFF3E0
  participant "RepoIndexer" as indexer
  participant "SemanticSearch" as search
  participant "EmbeddingStore" as embeddings
end box
box "Provider Layer" #E3F2FD
  participant "Provider" as provider
end box

note over user, provider
  Scope:
    - rim03 SEARCH Semantic — embedding-based code similarity search

  Preconditions:
    - RIM-01 completed (AST index available)
    - EmbeddingStore populated with code embeddings
    - Provider available for embedding generation

  Contexts:
    - Called by AgentOrchestrator when user query requires semantic understanding
    - Complementary to RIM-02 (structural ranking)

  Excludes:
    - Structural/graph-based search (handled by RIM-02)
    - Full-text grep search (handled by TL-02)

  Rollback:
    - Embedding generation failure → return empty results
    - Store unavailable → fall back to keyword search

  Design:
  Classification: Primary Orchestrator
    - SemanticSearch embeds query via Provider
    - Cosine similarity against EmbeddingStore
    - Top-K results returned with similarity scores
    - Results filtered by minimum similarity threshold (default 0.3)

  Returns:
    - Success: SearchResultList with snippets and scores
    - Failure: Empty results with fallback flag
end note

== rim03 SEARCH Semantic ==

agent -> search : SEARCH(query, top_k=10)
activate search

search -> provider : embed(query_text)
activate provider
provider --> search : query_embedding
deactivate provider

search -> embeddings : cosine_search(query_embedding, top_k=10)
activate embeddings
embeddings --> search : raw_results[]
deactivate embeddings

search -> search : filter_by_threshold(results, min_sim=0.3)

search -> search : format_snippets(filtered_results)

search --> agent : SearchResultList(results, scores, snippets)
deactivate search

note over user, provider
  Flow:
    - AgentOrchestrator → SemanticSearch → Provider(embed) → EmbeddingStore → SearchResultList

  State:
    - <back:#ECEFF1>IDLE</back> → EMBEDDING → SEARCHING → FILTERING → DONE

  Failure:
    - Embedding failure → empty results + fallback flag
    - Store unavailable → keyword fallback

  Success:
    - SearchResultList with similarity-scored snippets

  Key invariants:
    - Query embedding generated fresh each search
    - Similarity threshold prevents low-quality matches
    - Top-K bounded to prevent excessive results
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim03_rank_results.puml ---

@startuml sq_rim03_rank_results
' ============================================================
' Title:     RIM-03 — Rank Results
' Boundary:  nasim code agent CLI
' Purpose:   PageRank ranking with chat-personalization for symbol importance
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Index Layer" #FFF3E0
  participant "RepoIndexer" as indexer
  participant "SymbolRanker" as ranker
  participant "SymbolGraph" as graph
end box
box "Chat Layer" #E8F5E9
  participant "ConversationHistory" as history
end box

note over user, history
  Scope:
    - rim02 RANK Symbols — PageRank ranking with chat-personalization

  Preconditions:
    - RIM-01 completed successfully (SymbolGraph populated)
    - ConversationHistory has chat context for personalization

  Contexts:
    - Called after RIM-01 or when user context shifts
    - Output feeds into RIM-04 (Inject RepoMap)

  Excludes:
    - Embedding-based ranking (handled by RIM-03)
    - File system traversal (handled by RIM-01)

  Rollback:
    - PageRank convergence failure → fall back to degree-centrality ranking
    - Empty graph → return empty ranking

  Design:
  Classification: Primary Orchestrator
    - SymbolRanker runs iterative PageRank on SymbolGraph
    - Chat personalization boosts symbols mentioned in recent conversation
    - Personalization weight is configurable (default 0.3)
    - Ranking is re-computed when chat context changes significantly

  Returns:
    - Success: RankedSymbolList with scores
    - Failure: Empty list with fallback flag
end note

== rim02 RANK Symbols ==

agent -> ranker : RANK_SYMBOLS(graph, chat_context)
activate ranker

ranker -> graph : get_adjacency()
activate graph
graph --> ranker : adjacency_map
deactivate graph

ranker -> history : get_recent_tokens(last_n=50)
activate history
history --> ranker : recent_tokens
deactivate history

ranker -> ranker : extract_mentioned_symbols(recent_tokens)

ranker -> ranker : initialize_pagerank_scores(nodes, damping=0.85)

loop until convergence or max_iterations=50
    ranker -> ranker : iterate_pagerank_step()
end

ranker -> ranker : apply_chat_boost(scores, mentioned_symbols, weight=0.3)

ranker -> ranker : sort_by_score_desc()

ranker --> agent : RankedSymbolList(symbols, scores)
deactivate ranker

note over user, history
  Flow:
    - AgentOrchestrator → SymbolRanker → SymbolGraph + ConversationHistory → RankedSymbolList

  State:
    - <back:#ECEFF1>IDLE</back> → COMPUTING → CONVERGING → BOOSTING → SORTED

  Failure:
    - Convergence failure → fallback to degree centrality
    - Empty graph → empty ranking

  Success:
    - RankedSymbolList sorted by importance score

  Key invariants:
    - PageRank always converges for connected graphs
    - Chat boost never exceeds max_score of base ranking
    - Ranking is deterministic for same input
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim01_index_codebase.puml ---

@startuml sq_rim01_index_codebase
' ============================================================
' Title:     RIM-01 — INDEX Codebase
' Boundary:  nasim code agent
' Purpose:   Build AST index and symbol graph from project source
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-01 INDEX Codebase

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Intelligence Layer" #EDE7F6
  participant "RepoIntelligenceManager" as rim
  participant "ASTIndexAdapter" as ast
  participant "SymbolGraph" as graph
end box
box "External" #F5F5F5
  participant "Host Filesystem" as fs
end box

note over agent, fs
  Scope:          Build AST index and symbol graph from project source
  Preconditions:  Project root accessible, supported source files present
  Excludes:       Embedding generation (RIM-05), semantic search (RIM-06)
  Contexts:       Called at session start or on-demand; prerequisite for RIM-02/03
  Rollback:       Parse error -> skip file, log warning; complete failure -> empty index
  Design:         RepoIntelligenceManager orchestrates pipeline; ASTParser extracts definitions; SymbolGraph builds relationships
  Classification: Primary Orchestrator
end note

== RIM-01 INDEX Codebase ==

agent -> rim : INDEX(project_root)
activate rim

rim -> fs : list_source_files(project_root)
activate fs
fs --> rim : source_files[]
deactivate fs

loop for each source_file
    rim -> ast : parse(source_file)
    activate ast

    break Parse error
        ast --> rim : ParseError(file, reason)
    end

    ast --> rim : ASTNode[]
    deactivate ast

    rim -> graph : extract_symbols(ast_nodes)
    activate graph
    graph --> rim : symbols[]
    deactivate graph

    rim -> graph : link_relationships(symbols)
    activate graph
    graph --> rim : edges[]
    deactivate graph
end

rim -> graph : build_adjacency_index()
activate graph
graph --> rim : adjacency_map
deactivate graph

rim --> agent : IndexStats(files, symbols, edges)
deactivate rim

note over agent, fs
  Flow:    AgentOrchestrator -> RepoIntelligenceManager -> [FileSystem -> ASTIndexAdapter -> SymbolGraph]* -> IndexStats
  State:   No state change
  Failure: Parse error -> skip file; complete failure -> empty index + error
  Success: IndexStats with file count, symbol count, edge count
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim04_inject_repomap.puml ---

@startuml sq_rim04_inject_repomap
' ============================================================
' Title:     RIM-04 — INJECT RepoMap (Token-budgeted Context Injection)
' Boundary:  nasim code agent CLI
' Purpose:   Token-budgeted repo-map injection into LLM context
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Index Layer" #FFF3E0
  participant "RepoIndexer" as indexer
  participant "SymbolRanker" as ranker
  participant "RepoMapInjector" as injector
end box
box "Context Layer" #E8F5E9
  participant "TokenBudget" as budget
  participant "ConversationHistory" as history
end box

note over user, history
  Scope:
    - rim04 INJECT RepoMap — token-budgeted repo-map injection into context

  Preconditions:
    - RIM-01 completed (AST index available)
    - RIM-02 completed (symbols ranked)
    - TokenBudget initialized with model limits

  Contexts:
    - Called before each LLM call to provide repository context
    - Output is prepended to conversation messages

  Excludes:
    - Full file content injection (handled by AGT-02)
    - Embedding search results (handled by RIM-03)

  Rollback:
    - Budget exceeded → truncate to fit budget
    - Empty index → inject empty map with warning

  Design:
  Classification: Primary Orchestrator
    - RepoMapInjector selects top-ranked symbols within token budget
    - Budget split: 60% structure overview, 25% relevant snippets, 15% reserves
    - Output formatted as structured text for LLM consumption
    - Injection point: system message or first user message

  Returns:
    - Success: RepoMapContext with formatted text and token count
    - Failure: Empty context with warning
end note

== rim04 INJECT RepoMap ==

agent -> injector : INJECT_REPOMAP(budget_tokens, ranked_symbols)
activate injector

injector -> budget : get_available_budget()
activate budget
budget --> injector : available_tokens
deactivate budget

injector -> injector : split_budget(available_tokens, ratios=[0.6, 0.25, 0.15])

injector -> ranker : get_top_symbols(structure_budget)
activate ranker
ranker --> injector : structure_symbols[]
deactivate ranker

injector -> ranker : get_relevant_snippets(snippet_budget)
activate ranker
ranker --> injector : snippet_symbols[]
deactivate ranker

injector -> injector : format_repo_map(structure_symbols, snippet_symbols)

injector -> injector : truncate_to_budget(formatted_map, max_tokens)

injector -> history : prepend_context(repo_map_text)
activate history
history --> injector : context_injected
deactivate history

injector --> agent : RepoMapContext(text, token_count)
deactivate injector

note over user, history
  Flow:
    - AgentOrchestrator → RepoMapInjector → TokenBudget + SymbolRanker + ConversationHistory → RepoMapContext

  State:
    - <back:#ECEFF1>IDLE</back> → BUDGETING → SELECTING → FORMATTING → TRUNCATING → INJECTED

  Failure:
    - Budget exceeded → truncate to fit
    - Empty index → empty map + warning

  Success:
    - RepoMapContext with formatted text within token budget

  Key invariants:
    - Total injected tokens never exceed budget
    - Budget ratios ensure balanced coverage
    - Injection is idempotent (replaces previous injection)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RTG/sq_rtg03_classify_task.puml ---

@startuml sq_rtg03_classify_task
' ============================================================
' Title:     RTG-03 — Classify Task
' Boundary:  nasim code agent
' Purpose:   Classify task type and select optimal model
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RTG-03 Classify Task

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Router Layer" #EDE7F6
  participant "ModelRouter" as router
end box

note over participants
  Scope:          Classify incoming task and select optimal model
  Preconditions:  ModelRouter initialized with model catalog
  Excludes:       Model switching, fallback application
  Contexts:       Called by AGT-01 or RTG-01
  Rollback:       Default model used on classification failure
  Design:         Heuristic or LLM-based classification
  Classification: Process Decomposition
end note

== RTG-03 Classify Task ==

agent -> router : classify(task_description, context)

break Classification fails
    router --> agent : default_model
end

router -> router : analyze task type (code, research, refactor, etc.)
router -> router : select model by capability match
router --> agent : selected_model

note over participants
  Flow:    AgentOrchestrator -> ModelRouter -> classify task type -> select optimal model
  State:   No state change
  Failure: Classification failure -> default model returned
  Success: Optimal model selected for task type
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RTG/sq_rtg01_select_model.puml ---

@startuml sq_rtg01_select_model
' ============================================================
' Title:     RTG-01 — SELECT Model
' Boundary:  nasim code agent
' Purpose:   Model selection and fallback routing
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RTG-01 SELECT Model

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Router Layer" #EDE7F6
  participant "ModelRouter" as router
  participant "FallbackChain" as fallback
  participant "ProviderCapabilities" as caps
end box
box "Config Layer" #FCE4EC
  participant "ConfigLoader" as cfg
end box
box "Provider Layer" #FFF3E0
  participant "LiteLLMProxy" as provider
end box

note over agent, provider
  Scope:          Model selection and fallback routing
  Preconditions:  ModelRouter initialized, Config loaded
  Excludes:       Model switching (RTG-04), task classification (RTG-03)
  Contexts:       Called by AGT-01 before PRV-02 REQUEST Chat
  Rollback:       Fallback to default model on selection failure
  Design:         Composite strategy: classify task -> select model -> fallback chain
  Classification: Process Decomposition
end note

== RTG-01 SELECT Model ==

agent -> router : select_model(task_type)
activate router

router -> cfg : get_model_config()
activate cfg
cfg --> router : Config(model, fallback_chain)
deactivate cfg

router -> router : classify_task(input)

router -> caps : check_capabilities(model)
activate caps
caps --> router : supported_models
deactivate caps

break No supported model found
    router -> fallback : get_default_model()
    activate fallback
    fallback --> router : default_model
    deactivate fallback
end

router -> fallback : resolve(primary_model, fallback_chain)
activate fallback
fallback --> router : selected_model
deactivate fallback

router --> agent : selected_model
deactivate router

note over agent, provider
  Flow:    AgentOrchestrator -> ModelRouter -> classify -> check caps -> fallback chain -> return model
  State:   <back:#EDE7F6>ROUTING</back>
  Failure: No supported model -> fallback to default
  Success: Selected model returned to agent
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RTG/sq_rtg02_apply_fallback.puml ---

@startuml sq_rtg02_apply_fallback
' ============================================================
' Title:     RTG-02 — APPLY Fallback
' Boundary:  nasim code agent
' Purpose:   Apply fallback chain when primary model fails
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RTG-02 APPLY Fallback

box "Router Layer" #EDE7F6
  participant "ModelRouter" as router
  participant "FallbackChain" as fallback
end box
box "Provider Layer" #FFF3E0
  participant "LiteLLMProxy" as provider
end box

note over router, provider
  Scope:          Apply fallback chain when primary model fails
  Preconditions:  FallbackChain initialized with model list
  Excludes:       Model selection (RTG-01), task classification (RTG-03)
  Contexts:       Called by RTG-01 when primary model unavailable
  Rollback:       Return error if all models in chain fail
  Design:         Circuit breaker pattern with exponential backoff
  Classification: Process Decomposition
end note

== RTG-02 APPLY Fallback ==

router -> fallback : apply(primary_model, chain)
activate fallback

loop for each model in fallback_chain
    fallback -> provider : check_availability(model)
    activate provider

    alt provider available
        provider --> fallback : available
        deactivate provider
        fallback --> router : selected_model(model)
        deactivate fallback
    else provider unavailable
        provider --> fallback : unavailable
        deactivate provider
    end
end

break All models unavailable
    fallback --> router : FallbackError("all models unavailable")
end

note over router, provider
  Flow:    ModelRouter -> FallbackChain -> check each model -> return first available
  State:   No state change
  Failure: All models unavailable -> FallbackError
  Success: First available model returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RTG/sq_rtg04_switch_model.puml ---

@startuml sq_rtg04_switch_model
' ============================================================
' Title:     RTG-04 — Switch Model
' Boundary:  nasim code agent
' Purpose:   Change the active model at runtime
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RTG-04 Switch Model

box "CLI Layer" #E8F5E9
  participant "Developer" as dev
end box
box "Router Layer" #EDE7F6
  participant "ModelRouter" as router
end box

note over participants
  Scope:          Change active model via CLI or agent request
  Preconditions:  Target model available in catalog
  Excludes:       Model classification, fallback
  Contexts:       Called by CLI-07 SWITCH Model or AGT-01
  Rollback:       Previous model restored on switch failure
  Design:         Atomic config update; validates model availability
  Classification: Process Decomposition
end note

== RTG-04 Switch Model ==

dev -> router : switch_model(target_model)

break Model not in catalog
    router --> dev : Error("model not available")
end

router -> router : validate model availability
router -> router : update active_model config
router --> dev : switched to target_model

note over participants
  Flow:    Developer/Agent -> ModelRouter -> change active model -> update config
  State:   Active model updated
  Failure: Model not available -> error returned
  Success: Active model switched
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx06_track_token_budget.puml ---

@startuml sq_ctx06_track_token_budget
' ============================================================
' Title:     CTX-06 — Track Token Budget
' Boundary:  nasim code agent CLI
' Purpose:   Track token count as messages are added
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
end box

note over agent, history
  Scope:          Track token count as messages accumulate
  Preconditions:  ConversationHistory initialized
  Contexts:       Called by AGT-01 after each message append
  Excludes:       Context compaction (CTX-02)
  Rollback:       N/A — tracking is passive
  Design:         Heuristic: len(str) / 4 for estimation
  Classification: Process Decomposition
end note

== CTX-01 Track Token Count ==

agent -> history : add_message(msg)
history -> history : self.messages.append(msg)
history -> history : self.token_count += estimate_tokens(msg)

alt token_count > context_budget
    history --> agent : COMPACT_NEEDED
    agent -> agent : trigger CTX-02 (COMPACT Context)
else within budget
    history --> agent : ok
end

note over agent, history
  Flow:    message -> append -> estimate tokens -> check budget
  State:   No state change (or triggers COMPACTING)
  Failure: N/A
  Success: Message added, token count updated
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx01_process_context.puml ---

@startuml sq_ctx01_process_context
' ============================================================
' Title:     CTX-01 — PROCESS Context
' Boundary:  nasim code agent
' Purpose:   Orchestrate context processing pipeline stages
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CTX-01 PROCESS Context

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PipelineOrchestrator" as pipeline
end box
box "Context Graph Group" #E0F2F1
  participant "ContextGraph" as graph
  participant "TokenBudgetTracker" as tracker
end box

note over agent, tracker
  Scope:          Orchestrate context processing pipeline stages in order
  Preconditions:  ContextGraph initialized, budget set
  Excludes:       Individual processor logic (CTX-02..05)
  Contexts:       Called by AGT-01 when context needs processing
  Rollback:       Pipeline failure returns partial context
  Design:         Pipeline stages: truncation -> distillation -> injection -> compaction
  Classification: Process Decomposition
end note

== CTX-01 PROCESS Context ==

agent -> pipeline : PROCESS(graph, budget)
activate pipeline

pipeline -> tracker : CHECK budget
activate tracker
tracker --> pipeline : remaining_budget
deactivate tracker

ref over pipeline, graph
  CTX-05: COMPACT Nodes
end ref

ref over pipeline, graph
  CTX-02: TRUNCATE Nodes
end ref

ref over pipeline, graph
  CTX-03: DISTILL Nodes
end ref

ref over pipeline, graph
  CTX-04: INJECT Context
end ref

pipeline --> agent : ProcessedContext
deactivate pipeline

note over agent, tracker
  Flow:    Agent -> PipelineOrchestrator -> truncation -> distillation -> injection -> compaction
  State:   No state change
  Failure: Processor failure returns partial context
  Success: Optimized context graph within budget
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx03_distill_nodes.puml ---

@startuml sq_ctx03_distill_nodes
' ============================================================
' Title:     CTX-03 — Distill Nodes
' Boundary:  nasim code agent CLI
' Purpose:   Summarize old message exchanges into compact form
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "ContextCompactor" as compactor
end box
box "Provider Layer" #FFF3E0
  participant "Provider" as provider
end box

note over compactor, provider
  Scope:          Summarize selected old exchanges
  Preconditions:  ContextCompactor has selected messages to summarize
  Contexts:       Called by CTX-02 (COMPACT Context)
  Excludes:       Budget tracking, message selection
  Rollback:       Empty summary -> use truncated raw content
  Design:         Uses same provider as main agent for consistency
  Classification: Process Decomposition
end note

== CTX-03 Summarize Old Exchanges ==

compactor -> compactor : extract_oldest(messages, count)
compactor -> compactor : build prompt: "Summarize these exchanges concisely"
compactor -> provider : chat([summary_prompt + old_messages])

break Summary is empty or provider fails
    provider --> compactor : empty/error
    compactor -> compactor : use truncated raw content as summary
end

provider --> compactor : summary text
compactor -> compactor : create summary message {role: "system", content: summary}
compactor --> compactor : return summary message

note over compactor, provider
  Flow:    select old -> build prompt -> LLM summarize -> summary message
  State:   <back:#E0F2F1>COMPACTING</back>
  Failure: Empty summary -> truncated raw fallback
  Success: Summary message ready to replace old exchanges
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx05_compact_nodes.puml ---

@startuml sq_ctx05_compact_nodes
' ============================================================
' Title:     CTX-05 — Compact Nodes
' Boundary:  nasim code agent CLI
' Purpose:   Merge overlapping context nodes to reduce token usage
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CTX-05 Compact Nodes

box "Context Layer" #E8EAF6
  participant "PipelineOrchestrator" as pipe
  participant "CompactionProcessor" as comp
end box
box "Provider Layer" #FFF3E0
  participant "Provider" as provider
end box

note over pipe, provider
  Scope:          Merge overlapping context nodes to reduce token usage
  Preconditions:  Context graph has overlapping or redundant nodes
  Excludes:       Context injection (CTX-04), token tracking (CTX-06)
  Contexts:       Called when token budget is tight and nodes overlap
  Rollback:       Merge failure → retain original nodes
  Design:         Identifies overlapping nodes and merges via secondary LLM or heuristics
  Classification: Process Decomposition
end note

== CTX-05 Compact Nodes ==

pipe -> comp : compact(graph, budget)
activate comp

comp -> comp : identify overlapping nodes
comp -> comp : calculate merge candidates

alt merge candidates found
    comp -> provider : merge_nodes(candidates)
    activate provider
    provider --> comp : merged_nodes
    deactivate provider

    comp -> comp : replace original nodes with merged
    comp -> comp : recalculate token count
else no overlap
    comp -> comp : skip merge
end

comp --> pipe : CompactionResult(nodes_removed, tokens_saved)
deactivate comp

break Secondary LLM merge fails
    provider --> comp : ProviderError
    comp -> comp : fallback: drop lowest-ranked nodes
    comp --> pipe : CompactionResult(nodes_dropped, tokens_saved)
end

note over pipe, provider
  Flow:    PipelineOrchestrator → CompactionProcessor → find overlapping nodes → merge → return
  State:   <back:#E0F2F1>COMPACTING</back> → READY
  Failure: LLM merge fails → drop lowest-ranked nodes
  Success: Nodes compacted, token count reduced
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx04_inject_context.puml ---

@startuml sq_ctx04_inject_context
' ============================================================
' Title:     CTX-04 — Inject Context
' Boundary:  nasim code agent CLI
' Purpose:   Retrieve and inject context into the reasoning graph
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CTX-04 Inject Context

box "Context Layer" #E8EAF6
  participant "PipelineOrchestrator" as pipe
  participant "InjectionProcessor" as inj
end box
box "RIM Layer" #F3E5F5
  participant "RepoIndex" as rim
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box

note over pipe, agent
  Scope:          Retrieve relevant context and inject into reasoning graph
  Preconditions:  PipelineOrchestrator active, RepoIndex available
  Excludes:       Context compaction (CTX-02/05), token tracking (CTX-06)
  Contexts:       Called before LLM call to enrich prompt context
  Rollback:       Injection failure → proceed with existing context
  Design:         InjectionProcessor queries RepoIndex for relevant code/docs
  Classification: Process Decomposition
end note

== CTX-04 Inject Context ==

pipe -> inj : inject(task_description, graph)
activate inj

inj -> rim : query_relevant(task_description)
activate rim
rim --> inj : relevant_nodes [file_refs, snippets]
deactivate rim

inj -> inj : filter by relevance score
inj -> inj : format context blocks

inj -> inj : inject into reasoning graph
inj --> pipe : InjectionResult(nodes_added, tokens_used)
deactivate inj

break RepoIndex unavailable
    rim --> inj : IndexError
    inj -> inj : skip injection
    inj --> pipe : InjectionResult(0, 0)
end

note over pipe, agent
  Flow:    PipelineOrchestrator → InjectionProcessor → retrieve context → inject into graph
  State:   INJECTING → READY
  Failure: Index unavailable → skip, proceed with existing context
  Success: Context nodes injected, token count updated
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx02_compact_context.puml ---

@startuml sq_ctx02_compact_context
' ============================================================
' Title:     CTX-02 — COMPACT Context
' Boundary:  nasim code agent CLI
' Purpose:   Compact context when token budget exceeded
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Agent Layer" #E3F2FD
  participant "ConversationHistory" as history
  participant "ContextCompactor" as compactor
end box
box "Provider Layer" #FFF3E0
  participant "Provider" as provider
end box

note over history, provider
  Scope:          Compact context when token budget exceeded
  Preconditions:  token_count > context_budget
  Contexts:       Called by CTX-01 when budget exceeded
  Excludes:       Token tracking (CTX-01)
  Rollback:       Secondary LLM fails -> truncate oldest messages
  Design:         Summarize oldest N exchanges via secondary LLM call
  Classification: Process Decomposition
end note

== CTX-02 COMPACT Context ==

history -> compactor : compact(messages, budget)
compactor -> compactor : select oldest exchanges (keep system prompt + recent)
compactor -> compactor : build summarization prompt

compactor -> provider : chat([summary_prompt + selected_messages])

break Secondary LLM call fails
    provider --> compactor : ProviderError
    compactor -> compactor : fallback: truncate oldest messages
    compactor --> history : shortened messages (truncated)
end

provider --> compactor : summary text
compactor -> compactor : create summary message
compactor -> compactor : replace selected messages with summary
compactor --> history : shortened messages (summarized)

note over history, provider
  Flow:    budget exceeded -> select old -> summarize -> replace
  State:   <back:#E0F2F1>COMPACTING</back> -> <back:#FFF3E0>THINKING</back>
  Failure: LLM fails -> truncate fallback
  Success: Messages shortened, token count reduced
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli07_switch_model.puml ---

@startuml sq_cli07_switch_model
' ============================================================
' Title:     CLI-07 — Switch Model
' Boundary:  nasim code agent CLI
' Purpose:   Switch active model via slash command
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CLI-07 Switch Model

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
  participant "SlashCommandHandler" as cmd
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Routing Layer" #E8EAF6
  participant "RTGModelRouter" as rtg
end box

note over user, rtg
  Scope:          Switch active model via /model slash command
  Preconditions:  REPLSession active, model registry available
  Excludes:       Provider registration (PRV-01), fallback logic (RTG-02)
  Contexts:       Invoked by Developer via /model command
  Rollback:       Model not found → display error, retain current model
  Design:         Delegates to RTG-04 SWITCH Model for actual provider switch
  Classification: Primary Orchestrator
end note

== CLI-07 Switch Model ==

user -> repl : "/model {model_name}"
repl -> cmd : dispatch("/model {model_name}")
activate cmd

cmd -> cmd : parse model name
cmd -> rtg : switch_model(model_name)
activate rtg

rtg -> rtg : validate model availability
rtg -> rtg : update active model pointer

rtg --> cmd : ModelSwitched(new_model)
deactivate rtg

cmd --> repl : CommandResult("Switched to {model_name}")
deactivate cmd

repl --> user : "Active model: {model_name}"

break Model not found
    rtg --> cmd : ModelNotFoundError
    cmd --> repl : CommandError
    repl --> user : "Model '{model_name}' not available"
end

note over user, rtg
  Flow:    Developer → REPLSession → SlashCommandHandler → RTG-04 SWITCH Model → confirm
  State:   <back:#ECEFF1>IDLE</back> → SWITCHING → <back:#ECEFF1>IDLE</back>
  Failure: Model not found → display error, retain current
  Success: Model switched, confirmation shown
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli03_stream_output.puml ---

@startuml sq_cli03_stream_output
' ============================================================
' Title:     CLI-03 — Stream Output
' Boundary:  nasim code agent CLI
' Purpose:   Streaming token-by-token output with rich formatting
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
  participant "Renderer" as renderer
end box

note over user, renderer
  Scope:          Rendering AgentEvents to terminal
  Preconditions:  Agent event stream active
  Contexts:       Called by CLI-01 (PROCESS User Input)
  Excludes:       Agent loop logic, tool execution
  Rollback:       N/A — renderer is passive consumer
  Design:         Uses Rich library for colors, diffs, formatting
  Classification: Primary Orchestrator
end note

== CLI-03 STREAM Output ==

repl -> renderer : subscribe to AgentEvent stream

loop for each event
    alt TextChunk event
        repl -> renderer : TextChunk(text)
        renderer -> renderer : colored output (green for nasim>)
        renderer --> user : streamed token
    else ToolStart event
        repl -> renderer : ToolStart(name, args)
        renderer -> renderer : dimmed box with tool name + args
        renderer --> user : tool call display
    else ToolResult event
        repl -> renderer : ToolResult(name, result, truncated)
        renderer -> renderer : truncated result (max 200 chars)
        renderer --> user : tool result preview
    else Error event
        repl -> renderer : Error(message)
        renderer -> renderer : red highlight
        renderer --> user : error display
    else Done event
        repl -> renderer : Done()
        renderer -> renderer : newline + reset
    end
end

note over user, renderer
  Flow:    Event stream -> Renderer -> formatted terminal output
  State:   No state change
  Failure: N/A — renderer is passive
  Success: All events rendered with appropriate formatting
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli01_process_user_input.puml ---

@startuml sq_cli01_process_user_input
' ============================================================
' Title:     CLI-01 — PROCESS User Input
' Boundary:  nasim code agent CLI
' Purpose:   REPL input loop delegates to agent and renders output
' Milestone: v1.0
' Version:   3.0.0
' Source:    docs/UC/README.md
' Review:    Meta-Software Designer audit 2026-06-21
' ============================================================

title nasim — CLI-01 PROCESS User Input

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
  participant "Renderer" as renderer
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ErrorBoundary" as eb
end box
box "Observability Layer" #E0F2F1
  participant "StructuredLogger" as logger
end box

note over user, logger
  Scope:          Single user input processing cycle
  Preconditions:  REPL initialized, AgentOrchestrator ready
  Excludes:       Slash commands (CLI-02), session persistence (SSN-01/02)
  Contexts:       Called by main REPL loop
  Rollback:       Error -> display error via Renderer -> return to IDLE
  Design:         Events emitted by agent, rendered by Renderer. ErrorBoundary handles all agent failures
  Classification: Primary Orchestrator
end note

== CLI-01 PROCESS User Input ==

user -> repl : types input

ref over repl, logger
  OBS-01: STREAM Structured Log (user input received)
end ref

repl -> repl : check for slash command

alt is slash command
    ref over repl
      CLI-02: DISPATCH Slash Command
    end ref
else normal input
    repl -> agent : PROCESS(user_input)
    activate agent

    hnote over agent #FFF3E0 : **State: THINKING**

    ref over agent
      AGT-01: PROCESS User Task
    end ref

    agent --> repl : AgentEvent stream

    hnote over repl #E8F5E9 : **State: RESPONDING**

    loop for each AgentEvent
        alt TextChunk event
            repl -> renderer : render TextChunk
            renderer --> user : streamed token
        else ToolStart event
            repl -> renderer : render ToolStart
            renderer --> user : tool call display
        else ToolResult event
            repl -> renderer : render ToolResult
            renderer --> user : tool result preview
        else Done event
            repl -> renderer : render Done
            renderer --> user : formatted output
        end
    end

    deactivate agent
end

break Agent throws exception
    repl -> eb : handle(Exception)
    activate eb
    eb --> repl : ErrorEvent
    deactivate eb
    ref over repl, logger
      OBS-01: STREAM Structured Log (error)
    end ref
    repl -> renderer : render Error event
    renderer --> user : red error display
end

hnote over repl #ECEFF1 : **State: IDLE**

note over user, logger
  Flow:    User -> REPLSession -> AgentOrchestrator -> [AGT-01] -> events -> Renderer -> User
  State:   <back:#ECEFF1>IDLE</back> -> <back:#E8EAF6>LISTENING</back> -> <back:#FFF3E0>THINKING</back> -> [<back:#F3E5F5>TOOL_EXEC</back>]* -> <back:#E8F5E9>RESPONDING</back> -> <back:#ECEFF1>IDLE</back>
  Failure: Exception -> ErrorBoundary -> Error event -> IDLE
  Success: Final text rendered to user
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli05_enable_plan_mode.puml ---

@startuml sq_cli05_enable_plan_mode
' ============================================================
' Title:     CLI-05 — Enable Plan Mode
' Boundary:  nasim code agent CLI
' Purpose:   Toggle plan mode via slash command
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CLI-05 Enable Plan Mode

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
  participant "SlashCommandHandler" as cmd
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box

note over user, agent
  Scope:          Toggle plan mode on/off via slash command
  Preconditions:  REPLSession active, SlashCommandHandler registered
  Excludes:       Plan execution (AGT-07/08), model switching (CLI-07)
  Contexts:       Invoked by Developer via /plan-mode command
  Rollback:       Toggle failure → display error, retain current state
  Design:         Plan mode flag stored in session state; affects AGT-01 loop behavior
  Classification: Primary Orchestrator
end note

== CLI-05 Enable Plan Mode ==

user -> repl : "/plan-mode"
repl -> cmd : dispatch("/plan-mode")
activate cmd

cmd -> cmd : parse command arguments
cmd -> cmd : toggle plan_mode flag

cmd -> agent : set_plan_mode(enabled/disabled)
activate agent
agent --> cmd : plan_mode_updated
deactivate agent

cmd --> repl : CommandResult(confirmation)
deactivate cmd

repl --> user : "Plan mode: ON/OFF"

break Toggle error
    cmd --> repl : CommandError
    repl --> user : "Failed to toggle plan mode"
end

note over user, agent
  Flow:    Developer → REPLSession → SlashCommandHandler → toggle → confirm
  State:   <back:#ECEFF1>IDLE</back> → TOGGLING → <back:#ECEFF1>IDLE</back>
  Failure: Toggle error → display error, retain state
  Success: Plan mode toggled, confirmation shown
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli08_list_sessions.puml ---

@startuml sq_cli08_list_sessions
' ============================================================
' Title:     CLI-08 — List Sessions
' Boundary:  nasim code agent CLI
' Purpose:   List sessions via slash command
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CLI-08 List Sessions

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
  participant "SlashCommandHandler" as cmd
end box
box "Session Layer" #F1F8E9
  participant "SessionStore" as ssn
end box

note over user, ssn
  Scope:          List available sessions via /sessions slash command
  Preconditions:  REPLSession active, SessionStore initialized
  Excludes:       Session read (SSN-02), session persist (SSN-01)
  Contexts:       Invoked by Developer via /sessions command
  Rollback:       Read error → display error message
  Design:         Delegates to SSN-03 LIST Sessions for actual retrieval
  Classification: Primary Orchestrator
end note

== CLI-08 List Sessions ==

user -> repl : "/sessions"
repl -> cmd : dispatch("/sessions")
activate cmd

cmd -> ssn : list_sessions()
activate ssn

ssn -> ssn : scan session directory
ssn --> cmd : session_list [id, created_at, summary]
deactivate ssn

cmd -> cmd : format session table

cmd --> repl : CommandResult(formatted_table)
deactivate cmd

repl --> user : displayed session list

break Session directory unreadable
    ssn --> cmd : IOError
    cmd --> repl : CommandError
    repl --> user : "Failed to list sessions"
end

note over user, ssn
  Flow:    Developer → REPLSession → SlashCommandHandler → SSN-03 LIST Sessions → display
  State:   <back:#ECEFF1>IDLE</back> → LISTING → <back:#ECEFF1>IDLE</back>
  Failure: Directory error → display error
  Success: Session list formatted and displayed
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli02_dispatch_slash_command.puml ---

@startuml sq_cli02_dispatch_slash_command
' ============================================================
' Title:     CLI-02 — Dispatch Slash Command
' Boundary:  nasim code agent CLI
' Purpose:   Slash command routing and execution
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
  participant "SlashCommandHandler" as cmd
  participant "Renderer" as renderer
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box

note over user, agent
  Scope:          Slash command parsing and dispatch
  Preconditions:  REPL running, input starts with /
  Contexts:       Called by CLI-01 (PROCESS User Input)
  Excludes:       Normal user input (CLI-01)
  Rollback:       Unknown command -> error message
  Design:         Commands: /help, /reset, /model, /quit, /plan, /sessions
  Classification: Primary Orchestrator
end note

== CLI-02 Execute Slash Command ==

user -> repl : /command
repl -> cmd : dispatch("/command")
cmd -> cmd : parse command name and args

alt /help
    cmd -> renderer : display help text
    renderer --> user : help menu
else /reset
    cmd -> agent : reset()
    agent -> agent : clear conversation history
    cmd -> renderer : "History cleared."
    renderer --> user : confirmation
else /model
    cmd -> renderer : display current model name
    renderer --> user : model info
else /plan
    cmd -> agent : toggle_plan_mode()
    agent -> agent : toggle PLANNING state
    cmd -> renderer : "Plan mode: ON/OFF"
    renderer --> user : confirmation
else /sessions
    cmd -> renderer : list available sessions
    renderer --> user : session list
else /quit or /exit
    cmd -> repl : signal exit
    repl --> user : "Bye."
else unknown command
    cmd -> renderer : "Unknown command: /cmd"
    renderer --> user : error display
end

note over user, agent
  Flow:    /cmd -> SlashCommandHandler -> action -> Renderer -> User
  State:   No state change (except /plan toggles PLANNING, /reset clears history)
  Failure: Unknown command -> error message
  Success: Command action completed
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli04_read_cli_arguments.puml ---

@startuml sq_cli04_read_cli_arguments
' ============================================================
' Title:     CLI-04 — Read CLI Arguments
' Boundary:  nasim code agent CLI
' Purpose:   Startup argument parsing and config initialization
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "ArgParser" as parser
end box
box "Config Layer" #E0F7FA
  participant "ConfigLoader" as cfg
end box

note over user, cfg
  Scope:          CLI argument parsing and config initialization
  Preconditions:  Developer invokes nasim command
  Contexts:       Entry point for all CLI invocations
  Excludes:       Runtime input processing (CLI-01)
  Rollback:       Invalid args -> print usage -> exit(1)
  Design:         Args override config; layered resolution
  Classification: Primary Orchestrator
end note

== CLI-04 Parse CLI Arguments ==

user -> parser : nasim [args]
parser -> parser : argparse.ArgumentParser.parse_args()
parser -> cfg : load(cli_args=argv)
cfg -> cfg : read ~/.nasim/config.yaml
cfg -> cfg : read .nasim/config.yaml
cfg -> cfg : read NASIM_* env vars
cfg -> cfg : merge: CLI > env > project > global
cfg -> cfg : validate Config fields
cfg --> parser : Config object

break Invalid arguments
    parser -> parser : print usage
    parser --> user : exit(1)
end

break Invalid config
    cfg -> cfg : raise ConfigError
    cfg --> parser : ConfigError
    parser --> user : "Config error: details"
end

parser --> user : Config ready, start REPL or single-shot

note over user, cfg
  Flow:    argv -> ArgParser -> ConfigLoader -> layered merge -> Config
  State:   No state change
  Failure: Invalid args or config -> error + exit
  Success: Config object ready for component initialization
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli06_request_approval.puml ---

@startuml sq_cli06_request_approval
' ============================================================
' Title:     CLI-06 — Request Approval
' Boundary:  nasim code agent CLI
' Purpose:   Display approval prompt and collect developer decision
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CLI-06 Request Approval

actor "Developer" as user

box "CLI Layer" #E8F5E9
  participant "Renderer" as renderer
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Safety Layer" #FFF9C4
  participant "SafetyCoordinator" as safety
end box

note over user, safety
  Scope:          Display approval prompt for dangerous operations and collect decision
  Preconditions:  SafetyCoordinator flagged operation requiring approval
  Excludes:       Permission checks (SAF-01), auto-approve scenarios
  Contexts:       Called by AGT-02 when tool requires user confirmation
  Rollback:       Timeout → default deny
  Design:         Renderer displays prompt; blocks until user responds or timeout
  Classification: Primary Orchestrator
end note

== CLI-06 Request Approval ==

agent -> safety : requires_approval(tool_call)
activate safety
safety --> agent : true
deactivate safety

agent -> renderer : request_approval(tool_description, args)
activate renderer

renderer --> user : "Allow {tool}({args})? [y/N]"
user --> renderer : decision (y/n/timeout)

alt approved
    renderer --> agent : Approved
else denied
    renderer --> agent : Denied
else timeout
    renderer --> agent : Denied(timeout)
end

deactivate renderer

note over user, safety
  Flow:    AgentOrchestrator → Renderer → display prompt → Developer → decision
  State:   PENDING → APPROVED | DENIED
  Failure: Timeout → default deny
  Success: Developer decision returned to agent
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk06_validate_hook_result.puml ---

@startuml sq_hk06_validate_hook_result
' ============================================================
' Title:     HK-06 — VALIDATE Hook Result
' Boundary:  nasim code agent
' Purpose:   Validate a HookResult for correctness and safety
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-06 VALIDATE Hook Result

box "Hooks Layer" #FFFDE7
  participant "HookManager" as hooks
end box

note over hooks
  Scope:          Validate a HookResult for allow/deny/modify correctness
  Preconditions:  HookResult produced by a hook
  Excludes:       Hook execution, hook registration
  Contexts:       Called internally by HookManager after each hook execution
  Rollback:       Invalid result treated as DENY
  Design:         Ensures result schema compliance
  Classification: Process Decomposition
end note

== HK-06 VALIDATE Hook Result ==

hooks -> hooks : validate(hook_result)

break Result schema invalid
    hooks --> hooks : treat as DENY
end

break action not in [ALLOW, DENY, MODIFY]
    hooks --> hooks : treat as DENY
end

hooks --> hooks : validated result

note over hooks
  Flow:    HookManager -> validate HookResult -> allow/deny/modify -> return validated result
  State:   No state change
  Failure: Invalid schema or unknown action -> treated as DENY
  Success: Validated HookResult returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk03_dispatch_post_tool_hook.puml ---

@startuml sq_hk03_dispatch_post_tool_hook
' ============================================================
' Title:     HK-03 — DISPATCH Post-Tool Hook
' Boundary:  nasim code agent
' Purpose:   Execute hooks after tool execution
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-03 DISPATCH Post-Tool Hook

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as tools
end box
box "Hooks Layer" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box

note over agent, hook
  Scope:          Execute hooks after tool execution
  Preconditions:  Tool execution completed, hooks registered for PostToolCall event
  Excludes:       Pre-tool hooks (HK-02), LLM hooks (HK-04/05)
  Contexts:       Called by AGT-02 (DISPATCH Tool Call) after tool execution
  Rollback:       Hook failure logged; pipeline continues
  Design:         Priority-ordered execution; short-circuit on deny
  Classification: Process Decomposition
end note

== HK-03 DISPATCH Post-Tool Hook ==

agent -> tools : execute(tool_name, args)
activate tools
tools --> agent : ToolResult
deactivate tools

agent -> hooks : dispatch(PostToolCall, tool_name, result)
activate hooks
hooks -> hooks : find hooks for PostToolCall

loop for each hook in priority order
    hooks -> hook : execute(tool_name, result)
    activate hook
    hook --> hooks : HookResult(action, data?)
    deactivate hook

    break action == DENY
        hooks --> agent : HookResult(action=DENY, reason)
    end
end

hooks --> agent : HookResult(action=ALLOW, modified_result?)
deactivate hooks

note over agent, hook
  Flow:    Tool execution -> AgentOrchestrator -> HookManager -> find hooks -> execute in priority order -> return HookResult
  State:   <back:#FFFDE7>HOOK_RUNNING</back>
  Failure: Hook failure logged; remaining hooks still execute
  Success: HookResult returned to agent
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk05_dispatch_post_llm_hook.puml ---

@startuml sq_hk05_dispatch_post_llm_hook
' ============================================================
' Title:     HK-05 — DISPATCH Post-LLM Hook
' Boundary:  nasim code agent
' Purpose:   Execute hooks after LLM call completes
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-05 DISPATCH Post-LLM Hook

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Hooks Layer" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box

note over agent, hook
  Scope:          Execute hooks after LLM call completes
  Preconditions:  LLM call completed, hooks registered for PostLLMCall event
  Excludes:       Pre-LLM hooks (HK-04), tool hooks (HK-02/03)
  Contexts:       Called by AGT-01 (PROCESS User Task) after PRV-02
  Rollback:       Hook failure logged; pipeline continues
  Design:         Priority-ordered execution; short-circuit on deny
  Classification: Process Decomposition
end note

== HK-05 DISPATCH Post-LLM Hook ==

agent -> hooks : dispatch(PostLLMCall, llm_result)
activate hooks
hooks -> hooks : find hooks for PostLLMCall

loop for each hook in priority order
    hooks -> hook : execute(llm_result)
    activate hook
    hook --> hooks : HookResult(action, data?)
    deactivate hook

    break action == DENY
        hooks --> agent : HookResult(action=DENY, reason)
    end
end

hooks --> agent : HookResult(action=ALLOW, modified_data?)
deactivate hooks

note over agent, hook
  Flow:    AgentOrchestrator -> HookManager -> find hooks -> execute in priority order -> return HookResult
  State:   <back:#FFFDE7>HOOK_RUNNING</back>
  Failure: Hook failure logged; remaining hooks still execute
  Success: HookResult returned to agent
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk02_dispatch_pre_tool_hook.puml ---

@startuml sq_hk02_dispatch_pre_tool_hook
' ============================================================
' Title:     HK-02 — DISPATCH Pre-Tool Hook
' Boundary:  nasim code agent
' Purpose:   Execute hooks before tool execution
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-02 DISPATCH Pre-Tool Hook

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Hooks Layer" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box
box "Tool Layer" #F3E5F5
  participant "ToolRegistry" as tools
end box

note over agent, tools
  Scope:          Execute hooks before tool execution
  Preconditions:  Hooks registered for PreToolCall event
  Excludes:       Post-tool hooks (HK-03), LLM hooks (HK-04/05)
  Contexts:       Called by AGT-02 (DISPATCH Tool Call) before tool execution
  Rollback:       Hook deny blocks tool execution
  Design:         Priority-ordered execution; short-circuit on deny
  Classification: Process Decomposition
end note

== HK-02 DISPATCH Pre-Tool Hook ==

agent -> hooks : dispatch(PreToolCall, tool_name, args)
activate hooks
hooks -> hooks : find hooks for PreToolCall

loop for each hook in priority order
    hooks -> hook : execute(tool_name, args)
    activate hook
    hook --> hooks : HookResult(action, data?)
    deactivate hook

    break action == DENY
        hooks --> agent : HookResult(action=DENY, reason)
    end
end

hooks --> agent : HookResult(action=ALLOW, modified_args?)
deactivate hooks

note over agent, tools
  Flow:    AgentOrchestrator -> HookManager -> find hooks -> execute in priority order -> return HookResult
  State:   <back:#FFFDE7>HOOK_RUNNING</back>
  Failure: Hook deny blocks tool execution, returns DENY
  Success: HookResult(action=ALLOW) returned to agent
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk01_register_hook.puml ---

@startuml sq_hk01_register_hook
' ============================================================
' Title:     HK-01 — REGISTER Hook
' Boundary:  nasim code agent
' Purpose:   Register a hook in the HookManager
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-01 REGISTER Hook

box "Plugins Layer" #EDE7F6
  participant "PluginLoader" as loader
end box
box "Hooks Layer" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box

note over loader, hook
  Scope:          Register a hook in the HookManager
  Preconditions:  HookManager initialized, PluginLoader active
  Excludes:       Hook execution (HK-02..05), hook validation (HK-06)
  Contexts:       Called by PLG-04 (REGISTER Plugin Hooks)
  Rollback:       Registration failure logged, hook not added
  Design:         PluginLoader registers plugin-provided hooks at load time
  Classification: Process Decomposition
end note

== HK-01 REGISTER Hook ==

loader -> hooks : register(event, handler, priority)
activate hooks
hooks -> hook : Hook(name, event, handler, priority)
activate hook
hook --> hooks : hook instance
deactivate hook
hooks --> hooks : hooks[event].append(hook)
hooks --> loader : registered
deactivate hooks

note over loader, hook
  Flow:    PluginLoader -> HookManager -> Hook creation -> append to registry
  State:   No state change
  Failure: Duplicate hook name -> log warning, skip
  Success: Hook registered for event
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk04_pre_llm_hook.puml ---

@startuml sq_hk04_pre_llm_hook
' ============================================================
' Title:     HK-04 — DISPATCH Pre-LLM Hook
' Boundary:  nasim code agent
' Purpose:   Execute hooks before LLM call
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-04 DISPATCH Pre-LLM Hook

box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Hooks Layer" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box
box "Provider Layer" #FFF3E0
  participant "LiteLLMProxy" as provider
end box

note over agent, provider
  Scope:          Execute hooks before LLM call
  Preconditions:  Hooks registered for PreLLMCall event
  Excludes:       Post-LLM hooks (HK-05), tool hooks (HK-02/03)
  Contexts:       Called by AGT-01 (PROCESS User Task) before PRV-02
  Rollback:       Hook deny blocks LLM call
  Design:         Priority-ordered execution; short-circuit on deny
  Classification: Process Decomposition
end note

== HK-04 DISPATCH Pre-LLM Hook ==

agent -> hooks : dispatch(PreLLMCall, messages)
activate hooks
hooks -> hooks : find hooks for PreLLMCall

loop for each hook in priority order
    hooks -> hook : execute(messages)
    activate hook
    hook --> hooks : HookResult(action, data?)
    deactivate hook

    break action == DENY
        hooks --> agent : HookResult(action=DENY, reason)
    end
end

hooks --> agent : HookResult(action=ALLOW, modified_messages?)
deactivate hooks

note over agent, provider
  Flow:    AgentOrchestrator -> HookManager -> find hooks -> execute in priority order -> return HookResult
  State:   <back:#FFFDE7>HOOK_RUNNING</back>
  Failure: Hook deny blocks LLM call, returns DENY
  Success: HookResult(action=ALLOW) returned to agent
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CFG/sq_cfg03_apply_layered_config.puml ---

@startuml sq_cfg03_apply_layered_config
' ============================================================
' Title:     CFG-03 — Apply Layered Config
' Boundary:  nasim code agent CLI
' Purpose:   Config layer merge with precedence
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Config Layer" #E0F7FA
  participant "ConfigLoader" as cfg
end box

note over cfg
  Scope:          Merge 4 config layers with precedence
  Preconditions:  All sources loaded
  Contexts:       Called by CFG-01 (Load Config)
  Excludes:       Validation (CFG-02)
  Rollback:       N/A — merge always produces a result
  Design:         Precedence: CLI > env > project > global
  Classification: Process Decomposition
end note

== CFG-03 Merge Layered Config ==

cfg -> cfg : start with global_defaults
cfg -> cfg : overlay project_overrides (skip None values)
cfg -> cfg : overlay env_overrides (skip None values)
cfg -> cfg : overlay cli_args (skip None values)
cfg -> cfg : return merged Config

note over cfg
  Flow:    global -> project -> env -> CLI -> merged Config
  State:   No state change
  Failure: N/A — merge is always defined
  Success: Merged Config with correct precedence
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CFG/sq_cfg02_validate_config.puml ---

@startuml sq_cfg02_validate_config
' ============================================================
' Title:     CFG-02 — Validate Config
' Boundary:  nasim code agent CLI
' Purpose:   Config field validation
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "Config Layer" #E0F7FA
  participant "ConfigLoader" as cfg
end box

note over cfg
  Scope:          Validate Config fields against schema
  Preconditions:  Config loaded from sources
  Contexts:       Called by CFG-01 (Load Config) after merge
  Excludes:       Config loading (CFG-01)
  Rollback:       Validation error -> ConfigError with details
  Design:         Typed dataclass with __post_init__ validation
  Classification: Process Decomposition
end note

== CFG-02 Validate Config ==

cfg -> cfg : Config.__post_init__()
cfg -> cfg : check provider in ["ollama", "openai", "anthropic"]
cfg -> cfg : check safety_mode in ["ask", "auto", "off"]
cfg -> cfg : check context_budget > 0
cfg -> cfg : check timeout > 0

break Validation fails
    cfg -> cfg : raise ConfigError("field: message")
end

cfg --> cfg : Config valid

note over cfg
  Flow:    Config dataclass -> field checks -> valid or ConfigError
  State:   No state change
  Failure: Invalid field value -> ConfigError
  Success: Config validated
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CFG/sq_cfg01_load_config.puml ---

@startuml sq_cfg01_load_config
' ============================================================
' Title:     CFG-01 — Load Config
' Boundary:  nasim code agent CLI
' Purpose:   Layered config loading from all sources
' Milestone: v1.0
' Version:   2.0.0
' Source:    docs/UC/README.md
' Review:    —
' ============================================================

box "CLI Layer" #E8F5E9
  participant "ArgParser" as parser
end box
box "Config Layer" #E0F7FA
  participant "ConfigLoader" as cfg
end box
database "Global YAML" as global_yaml
database "Project YAML" as project_yaml
database "Env Vars" as env_vars

note over parser, cfg
  Scope:          Load config from all sources and merge
  Preconditions:  CLI invoked
  Contexts:       Called by CLI-04 (Parse CLI Arguments)
  Excludes:       Runtime config changes
  Rollback:       Invalid YAML -> ConfigError
  Design:         4-layer merge: global < project < env < CLI
  Classification: Process Decomposition
end note

== CFG-01 Load Config ==

parser -> cfg : load(cli_args=argv)
cfg -> global_yaml : read ~/.nasim/config.yaml
global_yaml --> cfg : global_defaults
cfg -> project_yaml : read .nasim/config.yaml
project_yaml --> cfg : project_overrides
cfg -> env_vars : read NASIM_* vars
env_vars --> cfg : env_overrides
cfg -> cfg : merge(global_defaults, project_overrides, env_overrides, cli_args)
cfg -> cfg : validate Config fields

break Invalid YAML or missing required fields
    cfg -> cfg : raise ConfigError("details")
    cfg --> parser : ConfigError
end

cfg --> parser : Config object

note over parser, cfg
  Flow:    4 sources -> merge -> validate -> Config
  State:   No state change
  Failure: Invalid YAML or validation error -> ConfigError
  Success: Typed Config dataclass ready
end note

@enduml




--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/README.md ---

# nasim — SQ Inventory (API-First)

Sequence diagrams organised by UC group. 148 diagrams across 21 groups.
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## API-First Convention

All SQ diagrams follow the API-First delegation chain:

```
User → [Interface Container] → API (ServerRouter) → AgentOrchestrator → Repository
```

- **Single Actor:** `User` (replaces Developer + HTTP Client)
- **Entry Gate:** All interface containers route through `ServerRouter` (API Group)
- **No Bypass:** No interface may call `AgentOrchestrator`, `SessionStore`, or any core service directly
- **CSR Pattern:** Controller (ServerRouter) → Service (AgentOrchestrator) → Repository (ToolRegistry, SessionStore, MemoryStore)
- **ROD AIP-193:** All failure paths use `{error: {code, message, status}}` format

## Groups

| Group | Boundary | Diagrams | Subdirectory |
| ----- | -------- | :------: | ------------ |
| AGT | Agent Core — orchestrator, history, permissions, plans, subagents | 14 | `AGT/` |
| CLI | CLI Interface Container — REPL, parsing, rendering (routes through API) | 8 | `CLI/` |
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
| SRV | API Group (Entry Gate) — REST API, SSE streaming | 11 | `SRV/` |
| SSN | Session — persistence and resumption | 9 | `SSN/` |
| TL | Tool Layer — all tool implementations | 22 | `TL/` |
| VCS | Version Control — Git status, diff, commit | 4 | `VCS/` |
| WRL | Wire Log — append-only event store, fork, checkpoint | 5 | `WRL/` |

**Total: 148 SQ diagrams across 21 groups**

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version (7.0.0), source, review status
2. **Lifelines** — Single `User` actor, participants grouped by layer (colored boxes)
3. **Intro Note** — Scope, Preconditions, Contexts, Excludes, Rollback, Classification, Design, Returns
4. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks
5. **Summary Note** — Flow summary, state transitions, success/failure paths, key invariants

## API-First Transformation (2026-06-23)

CAR refinement loop transforming nasim to API-First architecture.

### Changes Applied

| Layer | Change | Impact |
|-------|--------|--------|
| C4 Context | Single `User` actor replaces `Developer` + `HTTP Client` | All diagrams |
| C4 Container | 4 interface containers (CLI, WebApp, DesktopApp, MobileApp) → API → Backend | Architecture |
| C4 Component | Server Group renamed to API Group (Entry Gate) | Component diagrams |
| UC | CLI group reduced to 3 interface-only UCs; SRV renamed to API Group with 11 ROD UCs | UC diagrams |
| SM | All entry/exit transitions use `API-06` as sole entry gate | SM diagrams |
| SQ | All 148 diagrams: `Developer` → `User`, `HTTPClient` → `User`, version → 7.0.0 | SQ diagrams |

### Invariants Enforced

- **No Bypass:** No interface container may call core services directly
- **Single Entry:** `ServerRouter` is the sole entry gate for all business operations
- **CSR Chain:** Controller (ServerRouter) → Service (AgentOrchestrator) → Repository (ToolRegistry, SessionStore)
- **ROD Compliance:** All API interactions use standard methods or custom methods (AIP-136) with AIP-193 errors

### Cross-Layer Sync Results

- **C4 ↔ SQ:** All lifelines in SQ diagrams exist as C4 components ✓
- **UC ↔ SQ:** 148 UCs → 148 SQs — 1:1 mapping ✓
- **SM ↔ SQ:** All state transitions in SQs match valid SM transitions ✓
- **Method Consistency:** API-06, AGT-01, PRV-02 identical across layers ✓
- **API-First:** All entry chains go through ServerRouter ✓

### Design Chain Consistency: 100%



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MCP/sq_mcp02_discover_mcp_tools.puml ---

@startuml sq_mcp02_discover_mcp_tools
' ============================================================
' Title:     MCP-02 — DISCOVER MCP Tools
' Boundary:  nasim code agent
' Purpose:   Discover and register tools from connected MCP server
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    CAR audit 2026-06-26 (refactored to API-First entry chain)
' ============================================================

title nasim — MCP-02 DISCOVER McpTools

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "MCP Group" #EDE7F6
  participant "MCPClientRuntime" as mcp
  participant "MCPDiscovery" as discovery
  participant "MCPToolAdapter" as adapter
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
end box
box "External" #F5F5F5
  participant "MCP Server" as server
end box

note over user, server
  Scope:          MCP-02 DISCOVER McpTools — tool discovery from connected MCP server
  Preconditions:  MCP server connected (MCP-01 complete)
  Contexts:       Agent initialization, server reconnection
  Excludes:       Connection management (MCP-01), tool adaptation (MCP-03)
  Rollback:       Clear partially discovered tools on failure
  Design:         Lazy discovery with caching
  Classification: Process Decomposition
  Returns:
    - Success: DiscoveryComplete(count, tools[])
    - Failure: 503 UNAVAILABLE — server disconnected during discovery
end note

== MCP-02 DISCOVER McpTools ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> mcp : MCP-02 DISCOVER McpTools(connection)
activate mcp

mcp -> discovery : MCP-02 DISCOVER McpTools(connection)
activate discovery

discovery -> server : MCP-02 LIST McpTools(connection)
activate server
server --> discovery : ToolList(tools[name, description, schema])
deactivate server

loop for each tool in tool_list
    discovery -> adapter : MCP-03 ADAPT McpTool(tool_definition)
    activate adapter
    adapter --> discovery : WrappedTool(name, schema)
    deactivate adapter

    discovery -> registry : MCP-02 REGISTER Tool(wrapped_tool)
    activate registry
    registry --> discovery : RegistrationConfirmed(name)
    deactivate registry
end

discovery --> mcp : DiscoveryComplete(count, tools[])
deactivate discovery

mcp --> agent : ToolResult(success=true, content="DiscoveryComplete")
deactivate mcp

agent --> router : AgentEvent(Done)

note over user, server
  Flow:    User → ServerRouter → AgentOrchestrator → MCPClientRuntime → MCPDiscovery → list tools → wrap each → register → DiscoveryComplete
  State:   No state change
  Success: all tools available in ToolRegistry
  Failure: 503 UNAVAILABLE — partial discovery, register available tools
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MCP/sq_mcp01_connect_mcp_server.puml ---

@startuml sq_mcp01_connect_mcp_server
' ============================================================
' Title:     MCP-01 — CONNECT MCP Server
' Boundary:  nasim code agent
' Purpose:   Connect to external MCP server via stdio/SSE
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    CAR audit 2026-06-26 (refactored to API-First entry chain)
' ============================================================

title nasim — MCP-01 CONNECT McpServer

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "MCP Group" #EDE7F6
  participant "MCPClientRuntime" as mcp
end box
box "External" #F5F5F5
  participant "MCP Server" as server
end box

note over user, server
  Scope:          MCP-01 CONNECT McpServer — connection establishment to external MCP server
  Preconditions:  MCP server endpoint configured in config
  Contexts:       Called by TL-12 (DISPATCH MCP Extension) or agent initialization
  Excludes:       Tool discovery (MCP-02), tool adaptation (MCP-03)
  Rollback:       Close socket on failure, map to AIP-193 error
  Design:         Connection pooling and heartbeat monitoring
  Classification: Process Decomposition
  Returns:
    - Success: ConnectionActive(handle, capabilities)
    - Failure: 503 UNAVAILABLE — MCP Server unreachable
    - Failure: 504 TIMEOUT — handshake timeout
end note

== MCP-01 CONNECT McpServer ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> mcp : MCP-01 CONNECT McpServer(endpoint, transport)
activate mcp

mcp -> server : MCP-01 CONNECT McpServer(endpoint, transport)
activate server

break Connection refused / timeout
    server --> mcp : ConnectionError
    mcp --> agent : ToolResult(success=false, error="MCP Server unreachable")
    agent --> router : AgentEvent(Error)
end

server --> mcp : connection established
deactivate server

mcp -> server : MCP-01 INITIALIZE Handshake(capabilities)
activate server
server --> mcp : HandshakeResponse(server_capabilities)
deactivate server

mcp -> mcp : store connection state

mcp --> agent : ToolResult(success=true, content="ConnectionActive")
deactivate mcp

agent --> router : AgentEvent(Done)

note over user, server
  Flow:    User → ServerRouter → AgentOrchestrator → MCPClientRuntime → MCP Server → handshake → store state
  State:   No state change
  Success: ConnectionActive with server capabilities
  Failure: 503 UNAVAILABLE — MCP Server unreachable
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MCP/sq_mcp04_expose_nasim_tools.puml ---

@startuml sq_mcp04_expose_nasim_tools
' ============================================================
' Title:     MCP-04 — EXPOSE Nasim Tools
' Boundary:  nasim code agent
' Purpose:   Expose nasim tools to external MCP clients
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    CAR audit 2026-06-26 (refactored to API-First entry chain)
' ============================================================

title nasim — MCP-04 EXPOSE NasimTools

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "MCP Group" #EDE7F6
  participant "MCPServerRuntime" as server
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
end box
box "External" #F5F5F5
  participant "MCP Client" as client
end box

note over user, client
  Scope:          MCP-04 EXPOSE NasimTools — serving nasim tools via MCP server interface
  Preconditions:  MCPServerRuntime initialized, tools registered
  Contexts:       External MCP client connection lifecycle
  Excludes:       Tool discovery (MCP-02), tool adaptation (MCP-03)
  Rollback:       Disconnect client on tool execution failure
  Design:         Request validation and rate limiting
  Classification: Process Decomposition
  Returns:
    - Success: ToolDefinitions(tools[])
    - Success: ToolResult(result)
    - Failure: 404 NOT_FOUND — tool not found
    - Failure: 500 INTERNAL — execution failed
end note

== MCP-04 EXPOSE NasimTools ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> server : MCP-04 EXPOSE NasimTools()
activate server

server -> registry : MCP-04 READ ToolRegistry()
activate registry
registry --> server : ToolDefinitions(tools[])
deactivate registry

server --> client : 200 OK — ToolDefinitions(tools[])
deactivate server

client -> server : MCP-04 EXECUTE NasimTool(name, args)
activate server

break Tool not found
    server --> client : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "tool not found"}}
    server --> agent : ToolResult(success=false, error="tool not found")
    agent --> router : AgentEvent(Error)
end

server -> registry : MCP-04 EXECUTE Tool(name, args)
activate registry
registry --> server : ToolResult(result)
deactivate registry

break Execution failure
    server --> client : 500 INTERNAL {error: {code: "INTERNAL", message: "execution failed"}}
    server --> agent : ToolResult(success=false, error="execution failed")
    agent --> router : AgentEvent(Error)
end

server --> client : 200 OK — ToolResult(result)
deactivate server

server --> agent : ToolResult(success=true, content="ToolResult")
agent --> router : AgentEvent(Done)

note over user, client
  Flow:    User → ServerRouter → AgentOrchestrator → MCPServerRuntime → ToolRegistry → MCP Client
  State:   No state change
  Success: ToolResult with execution result
  Failure: 404 NOT_FOUND — tool not found; 500 INTERNAL — execution failed
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MCP/sq_mcp03_adapt_mcp_tool.puml ---

@startuml sq_mcp03_adapt_mcp_tool
' ============================================================
' Title:     MCP-03 — ADAPT MCP Tool
' Boundary:  nasim code agent
' Purpose:   Wrap MCP server tool into nasim Tool format
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    CAR audit 2026-06-26 (refactored to API-First entry chain)
' ============================================================

title nasim — MCP-03 ADAPT McpTool

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "MCP Group" #EDE7F6
  participant "MCPClientRuntime" as mcp
  participant "MCPToolAdapter" as adapter
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over user, registry
  Scope:          MCP-03 ADAPT McpTool — tool format adaptation from MCP to nasim
  Preconditions:  Tool discovered from MCP server (MCP-02)
  Contexts:       Called by MCPDiscovery during tool registration
  Excludes:       Discovery logic (MCP-02), registration logic
  Rollback:       Reject incompatible tool schemas
  Design:         Schema mapping with type coercion
  Classification: Process Decomposition
  Returns:
    - Success: ToolRegistered(name, version)
    - Failure: SchemaIncompatible — skip tool, log warning
end note

== MCP-03 ADAPT McpTool ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> mcp : MCP-03 ADAPT McpTool(tool_definition)
activate mcp

mcp -> adapter : MCP-03 ADAPT McpTool(tool_definition)
activate adapter

adapter -> adapter : parse MCP tool schema

break Incompatible schema
    adapter --> mcp : SchemaIncompatible(tool_name, reason)
    mcp --> agent : ToolResult(success=false, error="Schema incompatible")
    agent --> router : AgentEvent(Error)
end

adapter -> adapter : map types to nasim Tool format
adapter -> adapter : create execution wrapper

adapter -> registry : MCP-03 REGISTER Tool(adapted_tool)
activate registry
registry --> adapter : ToolRegistered(name, version)
deactivate registry

adapter --> mcp : ToolRegistered(name, version)
deactivate adapter

mcp --> agent : ToolResult(success=true, content="ToolRegistered")
deactivate mcp

agent --> router : AgentEvent(Done)

note over user, registry
  Flow:    User → ServerRouter → AgentOrchestrator → MCPClientRuntime → MCPToolAdapter → parse → map → register → ToolRegistered
  State:   No state change
  Success: ToolRegistered — tool available in nasim ToolRegistry with MCP backend
  Failure: SchemaIncompatible — skip tool, log warning
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SBX/sq_sbx01_isolate_command.puml ---

@startuml sq_sbx01_isolate_command
' ============================================================
' Title:     SBX-01 — ISOLATE Command
' Boundary:  nasim code agent
' Purpose:   Execute command in OS-level sandbox
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SBX-01 INSERT Command

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Sandbox Group" #F1F8E9
  participant "SandboxExecutor" as executor
  participant "SandboxPolicy" as policy
end box
box "External" #F5F5F5
  participant "Sandbox Runtime" as runtime
end box

note over user, runtime
  Scope:          SBX-01 ISOLATE Command — sandboxed command execution
  Preconditions:  SandboxExecutor initialized, policy loaded
  Contexts:       Called by TL-05 (DISPATCH Shell Command)
  Excludes:       Policy management (SBX-02), monitoring (SBX-03)
  Rollback:       Kill sandbox process on timeout or violation
  Design:         Process isolation with namespace and cgroup
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={output, exit_code})
    - Failure: Result(success=false, error="timeout")
    - Failure: Result(success=false, error="policy_violation")
end note

== SBX-01 ISOLATE Command ==

user -> router : types input
router -> agent : SBX-01 PROCESS(user_input)

agent -> executor : SBX-01 ISOLATE Command(command, policy)
activate executor

executor -> policy : SBX-01 APPLY Rules(policy)
activate policy
policy --> executor : rules_applied
deactivate policy

executor -> executor : SBX-01 CREATE Sandbox(namespace, cgroup)
executor -> runtime : SBX-01 SPAWN Process(command)
activate runtime

break Timeout or resource violation
    runtime --> executor : timeout/violation error
    executor --> agent : Result(success=false, error="timeout")
    agent --> router : AgentEvent(Error)
end

runtime --> executor : execution_result(output, exit_code)
deactivate runtime

executor --> agent : Result(success=true, data={output, exit_code})
deactivate executor

agent --> router : AgentEvent(Done)

note over user, runtime
  Flow:    SBX-01 -> User -> ServerRouter -> AgentOrchestrator -> SandboxExecutor -> apply policy -> create sandbox -> execute -> return
  State:   <back:#F1F8E9>STAGING</back>
  Success: Result(success=true, data={output, exit_code})
  Failure: Result(success=false, error="timeout") — kill sandbox, return violation error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SBX/sq_sbx02_apply_sandbox_policy.puml ---

@startuml sq_sbx02_apply_sandbox_policy
' ============================================================
' Title:     SBX-02 — APPLY Sandbox Policy
' Boundary:  nasim code agent
' Purpose:   Load and apply sandbox security policy
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SBX-02 UPDATE Sandbox Policy

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Sandbox Group" #F1F8E9
  participant "SandboxExecutor" as executor
  participant "SandboxPolicy" as policy
end box

note over user, policy
  Scope:          SBX-02 APPLY SandboxPolicy — sandbox policy loading and application
  Preconditions:  Policy file exists, SandboxPolicy initialized
  Contexts:       Called by SBX-01 before command execution
  Excludes:       Command execution (SBX-01), monitoring (SBX-03)
  Rollback:       Revert to default policy on validation failure
  Design:         Declarative policy with rule inheritance
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={rules_count})
    - Failure: Result(success=false, error="policy_invalid") — reverted to defaults
end note

== SBX-02 APPLY Sandbox Policy ==

user -> router : types input
router -> agent : SBX-02 PROCESS(user_input)

agent -> executor : SBX-02 APPLY SandboxPolicy(policy_path)
activate executor

executor -> policy : SBX-02 LOAD Policy(policy_path)
activate policy

policy -> policy : SBX-02 READ PolicyFile(policy_path)

break Policy file not found
    policy --> executor : default policy applied
    executor --> agent : Result(success=true, data={rules_count, fallback=true})
    agent --> router : AgentEvent(Done)
end

policy -> policy : SBX-02 VALIDATE Rules(rules)

break Invalid policy rules
    policy --> executor : revert to defaults, log error
    executor --> agent : Result(success=false, error="policy_invalid")
    agent --> router : AgentEvent(Error)
end

policy -> policy : SBX-02 APPLY ToSandbox(instance)

policy --> executor : Result(success=true, data={rules_count})
deactivate policy

executor --> agent : Result(success=true, data={rules_count})
deactivate executor

agent --> router : AgentEvent(Done)

note over user, policy
  Flow:    SBX-02 -> User -> ServerRouter -> AgentOrchestrator -> SandboxExecutor -> SandboxPolicy -> read policy -> validate -> apply -> confirm
  State:   No state change
  Success: Result(success=true, data={rules_count})
  Failure: Result(success=false, error="policy_invalid") — revert to defaults, log error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SBX/sq_sbx04_limit_resources.puml ---

@startuml sq_sbx04_limit_resources
' ============================================================
' Title:     SBX-04 — LIMIT Resources
' Boundary:  nasim code agent
' Purpose:   Enforce CPU, memory, and disk quotas per sandbox instance
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SBX-04 UPDATE Resources

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Sandbox Group" #F1F8E9
  participant "SandboxExecutor" as executor
  participant "ResourceLimiter" as limiter
end box

note over user, limiter
  Scope:          SBX-04 LIMIT Resources — resource quota enforcement via cgroups
  Preconditions:  Sandbox instance created, limits defined
  Contexts:       Called by SandboxExecutor during sandbox creation
  Excludes:       Process monitoring (SBX-03)
  Rollback:       Remove cgroup on setup failure
  Design:         Linux cgroup v2 with CPU, memory, disk I/O limits
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={cgroup_id})
    - Failure: Result(success=false, error="cgroup_setup_failed")
end note

== SBX-04 LIMIT Resources ==

user -> router : types input
router -> agent : SBX-04 PROCESS(user_input)

agent -> executor : SBX-04 LIMIT Resources(cgroup_id, quotas)
activate executor

executor -> limiter : SBX-04 SET Limits(cgroup_id, quotas)
activate limiter

limiter -> limiter : SBX-04 CREATE CgroupHierarchy()

break Cgroup setup fails
    limiter --> executor : CgroupError("setup failed")
    executor --> agent : Result(success=false, error="cgroup_setup_failed")
    agent --> router : AgentEvent(Error)
end

limiter -> limiter : SBX-04 SET CpuMax(CPU quota)
limiter -> limiter : SBX-04 SET MemoryMax(memory limit)
limiter -> limiter : SBX-04 SET IoMax(disk I/O limit)

limiter --> executor : Result(success=true, data={cgroup_id})
deactivate limiter

executor --> agent : Result(success=true, data={cgroup_id})
deactivate executor

agent --> router : AgentEvent(Done)

note over user, limiter
  Flow:    SBX-04 -> User -> ServerRouter -> AgentOrchestrator -> SandboxExecutor -> ResourceLimiter -> create cgroup -> set CPU -> set memory -> set I/O -> confirm
  State:   No state change
  Success: Result(success=true, data={cgroup_id})
  Failure: Result(success=false, error="cgroup_setup_failed") — remove partial cgroup, return error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SBX/sq_sbx03_monitor_process.puml ---

@startuml sq_sbx03_monitor_process
' ============================================================
' Title:     SBX-03 — MONITOR Process
' Boundary:  nasim code agent
' Purpose:   Monitor sandboxed process for timeout and resource usage
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SBX-03 READ Process

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Sandbox Group" #F1F8E9
  participant "SandboxExecutor" as executor
  participant "SandboxMonitor" as monitor
end box

note over user, monitor
  Scope:          SBX-03 MONITOR Process — process monitoring within sandbox
  Preconditions:  Sandbox process running (SBX-01)
  Contexts:       Long-running commands, background processes
  Excludes:       Resource limiting (SBX-04)
  Rollback:       Kill process on timeout, enforce resource limits
  Design:         Watchdog thread with configurable intervals
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={stats})
    - Failure: Result(success=false, error="timeout_exceeded")
    - Failure: Result(success=false, error="resource_limit_exceeded")
end note

== SBX-03 MONITOR Process ==

user -> router : types input
router -> agent : SBX-03 PROCESS(user_input)

agent -> executor : SBX-03 MONITOR Process(process_id, limits)
activate executor

executor -> monitor : SBX-03 START Watch(process_id, limits)
activate monitor

loop while process running
    monitor -> monitor : SBX-03 POLL ProcessStatus()
    monitor -> monitor : SBX-03 CHECK TimeoutElapsed()
    monitor -> monitor : SBX-03 CHECK ResourceUsage(CPU, memory)
end

alt timeout exceeded
    monitor -> executor : SBX-03 KILL Process(SIGKILL)
    executor --> monitor : process_killed
    monitor --> executor : watch_complete(stats)
    executor --> agent : Result(success=false, error="timeout_exceeded")
    agent --> router : AgentEvent(Error)
else resource limit exceeded
    monitor -> executor : SBX-03 ENFORCE Limit(violation)
    executor --> monitor : limit_enforced
    monitor --> executor : watch_complete(stats)
    executor --> agent : Result(success=false, error="resource_limit_exceeded")
    agent --> router : AgentEvent(Error)
else normal completion
    monitor -> monitor : SBX-03 RECORD FinalStats()
    monitor --> executor : watch_complete(stats)
    executor --> agent : Result(success=true, data={stats})
    agent --> router : AgentEvent(Done)
end

deactivate monitor
deactivate executor

note over user, monitor
  Flow:    SBX-03 -> User -> ServerRouter -> AgentOrchestrator -> SandboxExecutor -> SandboxMonitor -> poll -> enforce limits -> complete
  State:   No state change
  Success: Result(success=true, data={stats})
  Failure: Result(success=false, error="timeout_exceeded") or Result(success=false, error="resource_limit_exceeded") — kill/enforce
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs05_expose_metrics.puml ---

@startuml sq_obs05_expose_metrics
' ============================================================
' Title:     OBS-05 — EXPOSE Metrics
' Boundary:  nasim code agent
' Purpose:   Serve /metrics endpoint for Prometheus pull scrape
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — OBS-05 EXPOSE Metrics

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerApp" as server
end box
box "Service Group" #F3E5F5
  participant "MetricsCollector" as metrics
end box
box "Repository Group" #E8F5E9
  participant "ObservabilityRepository" as obs_repo
end box

note over user, metrics
  Scope:          OBS-05 EXPOSE Metrics — serve metrics for pull scrape
  Preconditions:  MetricsCollector configured (metrics_enabled), ServerApp running (HTTP mode)
  Contexts:       HTTP mode: /metrics served by ServerApp. Prometheus pull-scrapes periodically
  Excludes:       Metrics recording (OBS-02), structured logging (OBS-01), OTel export (OBS-06)
  Rollback:       Metrics disabled -> 503 response
  Design:         MetricsCollector exposes prometheus-client generate_latest(). ServerApp adds /metrics route (GET only). No authentication required
  Returns:
    - Success: 200 OK — metrics text (Prometheus format)
    - Failure: 503 SERVICE_UNAVAILABLE — metrics disabled
end note

== OBS-05 EXPOSE Metrics (HTTP mode) ==

user -> server : GET /metrics
activate server

server -> metrics : OBS-05 EXPOSE Metrics()
activate metrics
metrics -> metrics : collect all metric families
metrics --> server : MetricsText(format=prometheus)
deactivate metrics

server --> user : 200 OK — Content-Type: text/plain; version=0.0.4
deactivate server

note over user, metrics
  Flow:    OBS-05 → ServerApp → MetricsCollector → metrics text
  State:   No state change
  Success: 200 OK — Prometheus-compatible metrics text
  Failure: 503 SERVICE_UNAVAILABLE — metrics disabled
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs04_redact_sensitive.puml ---

@startuml sq_obs04_redact_sensitive
' ============================================================
' Title:     OBS-04 — REDACT Sensitive Data
' Boundary:  nasim code agent
' Purpose:   Strip secrets before emission to structured logs or wire
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — OBS-04 REDACT SensitiveData

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Observability Group" #E0F2F1
  participant "StructuredLogger" as logger
  participant "WireAppender" as wire
  participant "LogRedactor" as redactor
end box
box "Config Group" #E0F7FA
  participant "Config" as config
end box
box "Repository Group" #E8F5E9
  participant "ObservabilityRepository" as obs_repo
end box

note over user, config
  Scope:          OBS-04 REDACT SensitiveData — strip secrets before any emission
  Preconditions:  LogRedactor initialized with redaction rules, Config loaded
  Contexts:       Called before every emission to structured logs (OBS-01) and wire events (WRL-01)
  Excludes:       Log emission (OBS-01), wire append (WRL-01)
  Rollback:       Rule load failure -> use default rules only
  Design:         LogRedactor applies regex patterns to record fields. Always on — cannot be disabled
  Returns:
    - Success: SanitizedRecord(redacted=true)
    - Success: SanitizedPayload(redacted=true)
    - Failure: Rule load failure -> default rules only
end note

== OBS-04 REDACT SensitiveData (structured log) ==

user -> router : OBS-04 REDACT SensitiveData(record)
activate router
router -> agent : OBS-04 REDACT SensitiveData(record)
activate agent

agent -> logger : OBS-04 REDACT SensitiveData(record)
activate logger

logger -> redactor : OBS-04 REDACT SensitiveData(record)
activate redactor

redactor -> config : config.load_redaction_rules()
activate config
config --> redactor : rules[]
deactivate config

loop for each rule in rules
    redactor -> redactor : apply_pattern(record, rule.pattern, rule.replacement)
end

redactor -> redactor : set_redacted_flag(record)

redactor --> logger : SanitizedRecord(redacted=true)
deactivate redactor

logger --> agent : SanitizedRecord
deactivate logger

== OBS-04 REDACT SensitiveData (wire event) ==

wire -> redactor : OBS-04 REDACT SensitiveData(payload)
activate redactor

redactor -> config : config.load_redaction_rules()
activate config
config --> redactor : rules[]
deactivate config

loop for each rule in rules
    redactor -> redactor : apply_pattern(payload, rule.pattern, rule.replacement)
end

redactor --> wire : SanitizedPayload(redacted=true)
deactivate redactor

agent --> router : None
deactivate agent
deactivate router

note over user, config
  Flow:    OBS-04 → User → ServerRouter → AgentOrchestrator → StructuredLogger/WireAppender → LogRedactor → Config (rules) → sanitized record/payload
  State:   No state change
  Success: SanitizedRecord with redacted=true flag
  Failure: Rule load failure -> default rules only
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs02_record_metrics.puml ---

@startuml sq_obs02_record_metrics
' ============================================================
' Title:     OBS-02 — RECORD Metrics
' Boundary:  nasim code agent
' Purpose:   Record metric points for token usage, latency, tool calls
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — OBS-02 RECORD Metrics

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Provider Group" #FFF3E0
  participant "Provider" as provider
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as tools
end box
box "Observability Group" #E0F2F1
  participant "MetricsCollector" as metrics
  participant "TraceCorrelator" as trace
end box
box "Repository Group" #E8F5E9
  participant "ObservabilityRepository" as obs_repo
end box

note over user, trace
  Scope:          OBS-02 RECORD Metrics — increment counters, observe histograms
  Preconditions:  MetricsCollector configured (enabled)
  Contexts:       Called on every LLM request, tool call, error, session event
  Excludes:       Structured logging (OBS-01), trace correlation (OBS-03), OTel export (OBS-06)
  Rollback:       Record failure -> silently ignored (never blocks agent)
  Design:         MetricsCollector provides counter/gauge/histogram handles. Labels are low-cardinality. Pull-based only — never pushes to Prometheus
  Returns:
    - Success: None (fire-and-forget)
    - Failure: Record failure -> silently ignored
end note

== OBS-02 RECORD Metrics (LLM Request) ==

user -> router : OBS-02 RECORD Metrics(llm_request)
activate router
router -> agent : OBS-02 RECORD Metrics(llm_request)
activate agent

agent -> metrics : OBS-02 RECORD Metrics(llm_request, model, provider, latency_ms, tokens)
activate metrics

metrics -> metrics : llm_latency_ms.labels(model, provider).observe(latency_ms)
metrics -> metrics : llm_tokens_total.labels(model, provider).inc(tokens)
metrics -> metrics : llm_requests_total.labels(model, provider).inc()

metrics --> agent : None
deactivate metrics

== OBS-02 RECORD Metrics (Tool Call) ==

tools -> metrics : OBS-02 RECORD Metrics(tool_call, tool, success, duration_ms)
activate metrics

metrics -> metrics : tool_duration_ms.labels(tool).observe(duration_ms)
metrics -> metrics : tool_calls_total.labels(tool, success).inc()

metrics --> tools : None
deactivate metrics

== OBS-02 RECORD Metrics (Error) ==

agent -> metrics : OBS-02 RECORD Metrics(error, error_type)
activate metrics

metrics -> metrics : errors_total.labels(type=error_type).inc()

metrics --> agent : None
deactivate metrics

agent --> router : None
deactivate agent
deactivate router

note over user, trace
  Flow:    OBS-02 → User → ServerRouter → AgentOrchestrator/ToolRegistry → MetricsCollector → in-memory metrics
  State:   No state change
  Success: Metric point recorded in memory
  Failure: Record failure -> silently ignored (never blocks agent)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs06_export_otlp.puml ---

@startuml sq_obs06_export_otlp
' ============================================================
' Title:     OBS-06 — EXPORT OTLP
' Boundary:  nasim code agent
' Purpose:   Export traces and metrics to OTel-compatible backend
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — OBS-06 EXPORT Otlp

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Observability Group" #E0F2F1
  participant "OTelExporter" as otel
  participant "TraceCorrelator" as trace
  participant "MetricsCollector" as metrics
end box
box "External" #F5F5F5
  participant "OTel Backend" as backend
end box
box "Repository Group" #E8F5E9
  participant "ObservabilityRepository" as obs_repo
end box

note over user, backend
  Scope:          OBS-06 EXPORT Otlp — export traces and metrics to OTel-compatible backend
  Preconditions:  OTel feature flag enabled, backend reachable
  Contexts:       Called periodically or on shutdown
  Excludes:       Local log emission (OBS-01), redaction (OBS-04)
  Rollback:       Export failure logged, data buffered for retry
  Design:         Behind otel feature flag. Bridges spans + metrics to OTel SDK
  Returns:
    - Success: 200 OK — OtlpExportResult(traces, metrics)
    - Failure: Export failed -> buffer for retry
end note

== OBS-06 EXPORT Otlp ==

user -> router : OBS-06 EXPORT Otlp()
activate router
router -> agent : OBS-06 EXPORT Otlp()
activate agent

agent -> otel : OBS-06 EXPORT Otlp()
activate otel

otel -> trace : trace.export_spans()
activate trace
trace --> otel : SpanBatch(spans[])
deactivate trace

otel -> metrics : metrics.export_metrics()
activate metrics
metrics --> otel : MetricBatch(metrics[])
deactivate metrics

otel -> backend : OBS-06 POST /v1/traces + /v1/metrics
activate backend

break Backend unreachable
  backend --> otel : ConnectionError
  otel -> otel : buffer for retry
end

backend --> otel : 200 OK
deactivate backend

otel --> agent : OtlpExportResult(traces, metrics)
deactivate otel

agent --> router : None
deactivate agent
deactivate router

note over user, backend
  Flow:    OBS-06 → User → ServerRouter → AgentOrchestrator → OTelExporter → TraceCorrelator + MetricsCollector → POST to backend
  State:   No state change
  Success: 200 OK — traces and metrics exported to OTel backend
  Failure: Backend unreachable -> buffer and retry
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs03_correlate_trace.puml ---

@startuml sq_obs03_correlate_trace
' ============================================================
' Title:     OBS-03 — CORRELATE Trace
' Boundary:  nasim code agent
' Purpose:   Generate and propagate trace context across nasim surfaces
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — OBS-03 CORRELATE Trace

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Observability Group" #E0F2F1
  participant "TraceCorrelator" as trace
  participant "ContextPropagator" as propagator
end box
box "Provider Group" #FFF3E0
  participant "Provider" as provider
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as tools
end box
box "Repository Group" #E8F5E9
  participant "ObservabilityRepository" as obs_repo
end box

note over user, tools
  Scope:          OBS-03 CORRELATE Trace — generate and propagate trace context
  Preconditions:  TraceCorrelator initialized (contextvars available)
  Contexts:       Called at entrypoint: CLI turn start or HTTP request
  Excludes:       Structured logging (OBS-01), metrics recording (OBS-02), wire log (WRL)
  Rollback:       Trace generation failure -> fallback to random ids
  Design:         TraceCorrelator generates root trace/span per entrypoint. ContextPropagator ensures trace flows across boundaries
  Returns:
    - Success: TraceContext(trace_id, span_id)
    - Failure: Fallback to random ids on generation failure
end note

== OBS-03 CORRELATE Trace (CLI turn) ==

user -> router : OBS-03 CORRELATE Trace(cli_turn)
activate router
router -> agent : OBS-03 CORRELATE Trace(cli_turn)
activate agent

agent -> trace : OBS-03 NEW Trace(cli_turn)
activate trace
trace -> trace : generate trace_id (uuid4)
trace -> trace : generate span_id (uuid4hex)
trace -> trace : bind to contextvars
trace --> agent : TraceContext(trace_id, span_id)
deactivate trace

agent -> propagator : propagator.propagate()
activate propagator
propagator --> agent : TraceContext(trace_id, span_id, parent_span_id)
deactivate propagator

agent -> provider : PRV-03 STREAM ProviderChat(messages, trace_ctx)
activate provider
provider -> provider : create child_span("llm.chat")
provider --> agent : Stream(TextChunk)
deactivate provider

agent -> tools : TL-02 DISPATCH ToolCall(tool_call, trace_ctx)
activate tools
tools -> tools : create child_span("tool.exec")
tools --> agent : ToolResult(result)
deactivate tools

agent --> router : AgentEvent stream
deactivate agent
deactivate router

note over user, tools
  Flow:    OBS-03 → User → ServerRouter → AgentOrchestrator → TraceCorrelator → ContextPropagator → Provider + ToolRegistry
  State:   No state change
  Success: End-to-end correlation across all surfaces
  Failure: Trace generation failure -> fallback to random ids
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/OBS/sq_obs01_stream_log.puml ---

@startuml sq_obs01_stream_log
' ============================================================
' Title:     OBS-01 — STREAM Structured Log
' Boundary:  nasim code agent
' Purpose:   Emit structured JSON log record to stdout
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — OBS-01 STREAM StructuredLog

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Observability Group" #E0F2F1
  participant "StructuredLogger" as logger
  participant "LogRedactor" as redactor
  participant "TraceCorrelator" as trace
  participant "DualOutputAdapter" as adapter
end box
box "External" #F5F5F5
  participant "Stdout" as stdout
end box

note over user, stdout
  Scope:          OBS-01 STREAM StructuredLog — emit structured JSON log record to stdout
  Preconditions:  StructuredLogger configured, LogRedactor available
  Contexts:       Called on every significant agent event (turn, LLM call, tool exec, error)
  Excludes:       Wire log append (WRL-01), metrics recording (OBS-02)
  Rollback:       Write failure -> stderr warning, never raises to caller
  Design:         StructuredLogger constructs LogRecord with trace context; LogRedactor strips secrets; DualOutputAdapter writes JSON to stdout
  Returns:
    - Success: None (fire-and-forget)
    - Failure: Write failure -> stderr warning, never raises
end note

== OBS-01 STREAM StructuredLog ==

user -> router : OBS-01 STREAM StructuredLog(msg, level, extra)
activate router
router -> agent : OBS-01 STREAM StructuredLog(msg, level, extra)
activate agent

agent -> logger : OBS-01 STREAM StructuredLog(msg, level, extra)
activate logger

logger -> trace : trace.current_span()
activate trace
trace --> logger : TraceContext(trace_id, span_id, parent_span_id)
deactivate trace

logger -> logger : build_record(msg, level, trace_ctx, extra)

logger -> redactor : OBS-04 REDACT SensitiveData(record)
activate redactor
redactor --> logger : SanitizedRecord
deactivate redactor

logger -> adapter : OBS-01 EMIT LogRecord(sanitized_record)
activate adapter

adapter -> adapter : serialize_json(record)
adapter -> stdout : write_json(record)

adapter --> logger : None
deactivate adapter

deactivate logger

agent --> router : None
deactivate agent
deactivate router

note over user, stdout
  Flow:    OBS-01 → User → ServerRouter → AgentOrchestrator → StructuredLogger → TraceCorrelator + LogRedactor → DualOutputAdapter → Stdout
  State:   No state change
  Success: JSON line written to stdout
  Failure: Write failure -> stderr warning, never raises
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv06_dispatch_message.puml ---

@startuml sq_srv06_dispatch_message
' ============================================================
' Title:     SRV-06 — SEND Message
' Boundary:  nasim code agent HTTP API
' Purpose:   Dispatch a user message through the agent and stream SSE response
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    Meta-Software Designer audit 2026-06-21
' Pattern:   Controller (ServerRouter) -> Service (AgentOrchestrator) -> Repository (SessionStore)
' ============================================================

title nasim — SRV-06 SEND Message

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ErrorBoundary" as eb
end box
box "Repository Group" #E8F5E9
  participant "SessionStore" as store
end box
box "Observability Group" #E0F2F1
  participant "SSEHandler" as sse
  participant "TraceCorrelator" as trace
end box

note over user, trace
  Scope:          Dispatch a user message through the agent and stream SSE response
  Preconditions:  Session exists, ServerRouter initialized
  Contexts:       Called by HTTPClient via POST /v1/sessions/{id}:dispatch
  Excludes:       Session CRUD (SRV-01..05), Tool listing (SRV-08..09)
  Rollback:       404 if session not found, 400 if invalid body, 502 if agent fails
  Design:         CSR: Controller(ServerRouter) -> Service(AgentOrchestrator) -> Repository(SessionStore). ROD: custom method :dispatch (AIP-136)
  Classification: Primary Orchestrator
  Returns:        200 OK with SSE event stream, or 400/404/502 error
end note

== SRV-06 SEND Message ==

ref over agent, trace
  OBS-03: CORRELATE Trace
end ref

user -> router : POST /v1/sessions/{id}:dispatch
activate router

router -> router : Phase 1: validate request body
alt Structural validation failed [400]
  router --> user : 400 INVALID_ARGUMENT {error: {code: "INVALID_ARGUMENT", message: "Invalid request", status: "INVALID_ARGUMENT"}}
end

router -> agent : SRV-06 SEND Message(sessionId, message)
activate agent

agent -> store : readSessionExists(sessionId)
activate store
store --> agent : SessionEntity
deactivate store

break Session not found [404]
  agent --> router : 404 NOT_FOUND
  router --> user : 404 NOT_FOUND
end

hnote over agent #FFF3E0 : **State: THINKING**

ref over agent
  AGT-01: PROCESS User Task
end ref

break Agent error [502]
  agent -> eb : handle(AgentError)
  activate eb
  eb --> agent : RecoveryAction(retry/abort)
  deactivate eb
  agent --> router : 502 UNAVAILABLE
  router --> user : 502 UNAVAILABLE {error: {code: "UNAVAILABLE", message: "Agent error", status: "UNAVAILABLE"}}
end

agent --> router : AgentEventStream
deactivate agent

hnote over sse #E8F5E9 : **State: RESPONDING**

router -> sse : stream(events)
activate sse
sse --> user : Content-Type: text/event-stream
sse --> user : SSE: TextChunk, ToolStart, ToolResult, Done
deactivate sse

router --> user : 200 OK (stream complete)
deactivate router

note over user, trace
  Flow:    SRV-06 → validate → dispatch → agent loop → SSE stream
  State:   IDLE → SERVING → THINKING → RESPONDING → IDLE
  Success: 200 OK with SSE event stream
  Failure: 404 NOT_FOUND, 400 INVALID_ARGUMENT, 502 UNAVAILABLE
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv11_update_config.puml ---

@startuml sq_srv11_update_config
' ============================================================
' Title:     SRV-11 — UPDATE Config
' Boundary:  nasim code agent HTTP API
' Purpose:   Update agent configuration at runtime
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-11 UPDATE Config

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #FCE4EC
  participant "ConfigService" as svc
end box
box "Repository Group" #E8F5E9
  participant "ConfigLoader" as config
end box

note over user, config
  Scope:          Update agent configuration at runtime
  Preconditions:  ConfigLoader initialized
  Contexts:       Called by HTTPClient via PATCH /v1/config
  Excludes:       Config read, config validation
  Rollback:       400 if invalid config values
  Design:         CSR: Controller(ServerRouter) -> Service(ConfigService) -> Repository(ConfigLoader). ROD: standard update (AIP-134). Partial config patch. Triggers CFG-03 APPLY.
  Classification: Primary Orchestrator
  Returns:        200 OK with updated config, or 400 INVALID_ARGUMENT error
end note

== SRV-11 UPDATE Config ==

user -> router : PATCH /v1/config
activate router

router -> router : Phase 1: validate patch body
alt Structural validation failed [400]
  router --> user : 400 INVALID_ARGUMENT
end

router -> svc : SRV-11 UPDATE Config(patchData)
activate svc

svc -> svc : Phase 2: validate business rules
svc -> config : updateConfig(patch)
activate config

break Invalid config [400]
  config --> svc : ConfigError(invalid_value)
  deactivate config
  svc --> router : 400 INVALID_ARGUMENT
  router --> user : 400 INVALID_ARGUMENT {error: {code: "INVALID_ARGUMENT", message: "Invalid config", status: "INVALID_ARGUMENT"}}
end

config --> svc : applied
deactivate config

svc --> router : ConfigResponseDTO
deactivate svc
router --> user : 200 OK {config: {updated_fields: [...]}}
deactivate router

note over user, config
  Flow:    SRV-11 → validate → updateConfig → respond
  State:   No state change
  Success: 200 OK with updated config
  Failure: 400 invalid config values
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv01_list_sessions.puml ---

@startuml sq_srv01_list_sessions
' ============================================================
' Title:     SRV-01 — LIST Sessions
' Boundary:  nasim code agent HTTP API
' Purpose:   List all sessions with pagination
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    Prompt audit 2026-06-21 (cop.md: AIP-193 error path added)
' ============================================================

title nasim — SRV-01 LIST Sessions

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
end box
box "Repository Group" #E8F5E9
  participant "SessionStore" as store
end box

note over user, store
  Scope:          List all sessions with pagination
  Preconditions:  ServerRouter initialized, SessionService available
  Contexts:       Called by HTTPClient via GET /v1/sessions
  Excludes:       Session CRUD (SRV-02..05), Message operations (SRV-06..07)
  Rollback:       None (read-only operation)
  Design:         CSR: Controller(ServerRouter) -> Service(SessionService) -> Repository(SessionStore). ROD: standard list (AIP-132)
  Classification: Primary Orchestrator
  Returns:        200 OK with session list and pagination token, or 500 INTERNAL error
end note

== SRV-01 LIST Sessions ==

user -> router : GET /v1/sessions?page_size=10&page_token=abc
activate router

router -> svc : SRV-01 LIST Sessions(pageSize=10, pageToken="abc")
activate svc

svc -> store : listSessions(limit=10, cursor="abc")
activate store

break Store read failure [500]
    store --> svc : InternalError
    deactivate store
    svc --> router : 500 INTERNAL
    router --> user : 500 INTERNAL {error: {code: "INTERNAL", message: "Failed to list sessions", status: "INTERNAL"}}
end

alt Sessions exist
    store --> svc : sessions, next_page_token
    deactivate store
    svc --> router : ListSessionsResponse {sessions, nextPageToken}
    router --> user : 200 OK {sessions: [...], next_page_token: "def"}
else No sessions
    store --> svc : empty list, no token
    deactivate store
    svc --> router : ListSessionsResponse {sessions: [], nextPageToken: ""}
    router --> user : 200 OK {sessions: [], next_page_token: null}
end

deactivate svc
deactivate router

note over user, store
  Flow:    SRV-01 → validate → listSessions → respond
  State:   No state change
  Success: 200 OK with session list and pagination token
  Failure: 500 INTERNAL on store read failure
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv03_read_session.puml ---

@startuml sq_srv03_read_session
' ============================================================
' Title:     SRV-03 — READ Session
' Boundary:  nasim code agent HTTP API
' Purpose:   Read a session's current state and messages
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-03 READ Session

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
end box
box "Repository Group" #E8F5E9
  participant "SessionStore" as store
end box

note over user, store
  Scope:          Read a session's current state and messages
  Preconditions:  Session exists on disk
  Contexts:       Called by HTTPClient via GET /v1/sessions/{id}
  Excludes:       Session creation (SRV-02), message dispatch (SRV-06)
  Rollback:       404 if session not found
  Design:         CSR: Controller(ServerRouter) -> Service(SessionService) -> Repository(SessionStore). ROD: standard get (AIP-131)
  Classification: Primary Orchestrator
  Returns:        200 OK with session data, or 404 NOT_FOUND error
end note

== SRV-03 READ Session ==

user -> router : GET /v1/sessions/{id}
activate router

router -> svc : SRV-03 READ Session(sessionId)
activate svc

svc -> store : readSession(sessionId)
activate store

break Session not found [404]
  store --> svc : NotFound
  deactivate store
  svc --> router : 404 NOT_FOUND
  router --> user : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

store --> svc : SessionEntity
deactivate store

svc --> router : SessionResponseDTO
deactivate svc
router --> user : 200 OK {session: {id, messages, created_at, updated_at}}
deactivate router

note over user, store
  Flow:    SRV-03 → readSession → respond
  State:   No state change
  Success: 200 OK with session data
  Failure: 404 session not found
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv02_insert_session.puml ---

@startuml sq_srv02_insert_session
' ============================================================
' Title:     SRV-02 — INSERT Session
' Boundary:  nasim code agent HTTP API
' Purpose:   Create and persist a new agent session
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

title nasim — SRV-02 INSERT Session

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
end box
box "Repository Group" #E8F5E9
  participant "SessionStore" as store
end box

note over user, store
  Scope:          Create and persist a new agent session
  Preconditions:  ServerRouter initialized, SessionService available
  Contexts:       Called by HTTPClient via POST /v1/sessions
  Excludes:       Session dispatch (SRV-06), Session deletion (API-05)
  Rollback:       500 if SessionStore write fails
  Design:         CSR: Controller(ServerRouter) -> Service(SessionService) -> Repository(SessionStore). ROD: standard create (AIP-133)
  Classification: Primary Orchestrator
  Returns:        201 Created with session metadata, or 400/500 error
end note

== SRV-02 INSERT Session ==

user -> router : POST /v1/sessions
activate router

router -> router : Phase 1: validate request body
alt Structural validation failed [400]
  router --> user : 400 INVALID_ARGUMENT {error: {code: "INVALID_ARGUMENT", message: "Invalid request", status: "INVALID_ARGUMENT"}}
end

router -> svc : SRV-02 INSERT Session(sessionData)
activate svc

svc -> svc : Phase 2: validate business rules
svc -> svc : generateResourceId()
svc -> store : save(SessionEntity)
activate store
store --> svc : SessionEntity
deactivate store

break Store write fails [500]
  svc --> router : 500 INTERNAL
  router --> user : 500 INTERNAL {error: {code: "INTERNAL", message: "Failed to create session", status: "INTERNAL"}}
end

svc --> router : SessionResponseDTO
deactivate svc
router --> user : 201 Created {id, created_at, model, state}
deactivate router

note over user, store
  Flow:    SRV-02 → validate → createSession → persist → respond
  State:   No state change
  Success: 201 Created with session metadata
  Failure: 400 invalid body, 500 store write failure
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv09_read_tool.puml ---

@startuml sq_srv09_read_tool
' ============================================================
' Title:     SRV-09 — READ Tool
' Boundary:  nasim code agent HTTP API
' Purpose:   Read details of a specific registered tool
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-09 READ Tool

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
  participant "ToolService" as svc
end box
box "Repository Group" #E8F5E9
  participant "ToolRegistry" as registry
end box

note over user, registry
  Scope:          Read details of a specific registered tool
  Preconditions:  ToolRegistry initialized
  Contexts:       Called by HTTPClient via GET /v1/tools/{name}
  Excludes:       Tool execution, tool listing
  Rollback:       404 if tool not found
  Design:         CSR: Controller(ServerRouter) -> Service(ToolService) -> Repository(ToolRegistry). ROD: standard get (AIP-131)
  Classification: Primary Orchestrator
  Returns:        200 OK with tool metadata, or 404 NOT_FOUND error
end note

== SRV-09 READ Tool ==

user -> router : GET /v1/tools/{name}
activate router

router -> svc : SRV-09 READ Tool(name)
activate svc

svc -> registry : readTool(name)
activate registry

break Tool not found [404]
  registry --> svc : NotFound
  deactivate registry
  svc --> router : 404 NOT_FOUND
  router --> user : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Tool not found", status: "NOT_FOUND"}}
end

registry --> svc : ToolMetadata
deactivate registry

svc --> router : ToolResponseDTO
deactivate svc
router --> user : 200 OK {tool: {name, description, safe, parameters}}
deactivate router

note over user, registry
  Flow:    SRV-09 → readTool → respond
  State:   No state change
  Success: 200 OK with tool metadata
  Failure: 404 tool not found
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv08_list_tools.puml ---

@startuml sq_srv08_list_tools
' ============================================================
' Title:     SRV-08 — LIST Tools
' Boundary:  nasim code agent HTTP API
' Purpose:   List all registered tools available to the agent
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    Prompt audit 2026-06-21 (cop.md: AIP-193 error path added)
' ============================================================

title nasim — SRV-08 LIST Tools

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
  participant "ToolService" as svc
end box
box "Repository Group" #E8F5E9
  participant "ToolRegistry" as registry
end box

note over user, registry
  Scope:          List all registered tools available to the agent
  Preconditions:  ToolRegistry initialized
  Contexts:       Called by HTTPClient via GET /v1/tools
  Excludes:       Tool execution, tool registration
  Rollback:       500 if registry read fails
  Design:         CSR: Controller(ServerRouter) -> Service(ToolService) -> Repository(ToolRegistry). ROD: standard list (AIP-132)
  Classification: Primary Orchestrator
  Returns:        200 OK with tool list, or 500 INTERNAL error
end note

== SRV-08 LIST Tools ==

user -> router : GET /v1/tools
activate router

router -> svc : SRV-08 LIST Tools()
activate svc

svc -> registry : listTools()
activate registry

break Registry read failure [500]
    registry --> svc : InternalError
    deactivate registry
    svc --> router : 500 INTERNAL
    router --> user : 500 INTERNAL {error: {code: "INTERNAL", message: "Failed to list tools", status: "INTERNAL"}}
end

registry --> svc : ToolList
deactivate registry

svc --> router : ListToolsResponse {tools: [...]}
deactivate svc
router --> user : 200 OK {tools: [...]}
deactivate router

note over user, registry
  Flow:    SRV-08 → listTools → respond
  State:   No state change
  Success: 200 OK with tool list
  Failure: 500 INTERNAL on registry read failure
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv04_update_session.puml ---

@startuml sq_srv04_update_session
' ============================================================
' Title:     SRV-04 — UPDATE Session
' Boundary:  nasim code agent HTTP API
' Purpose:   Update session metadata or settings
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SRV-04 UPDATE Session

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
end box
box "Repository Group" #E8F5E9
  participant "SessionStore" as store
end box

note over user, store
  Scope:          Update session metadata or settings
  Preconditions:  Session exists on disk
  Contexts:       Called by HTTPClient via PATCH /v1/sessions/{id}
  Excludes:       Message dispatch (SRV-06), session deletion
  Rollback:       404 if not found, 400 if invalid body
  Design:         CSR: Controller(ServerRouter) -> Service(SessionService) -> Repository(SessionStore). ROD: standard update (AIP-134)
  Classification: Primary Orchestrator
  Returns:        200 OK with updated session metadata, or 400/404 error
end note

== SRV-04 UPDATE Session ==

user -> router : PATCH /v1/sessions/{id}
activate router

router -> router : Phase 1: validate patch body
alt Structural validation failed [400]
  router --> user : 400 INVALID_ARGUMENT
end

router -> svc : SRV-04 UPDATE Session(sessionId, patchData)
activate svc

svc -> store : readSessionExists(sessionId)
activate store

break Session not found [404]
  store --> svc : NotFound
  deactivate store
  svc --> router : 404 NOT_FOUND
  router --> user : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

store --> svc : SessionEntity
deactivate store

svc -> svc : Phase 2: validate business rules
svc -> svc : applyUpdateMask(existing, patchData)
svc -> store : save(updatedSession)
activate store
store --> svc : updated
deactivate store

svc --> router : SessionResponseDTO
deactivate svc
router --> user : 200 OK {session: {id, updated_at}}
deactivate router

note over user, store
  Flow:    SRV-04 → validate → read → applyMask → save → respond
  State:   No state change
  Success: 200 OK with updated session metadata
  Failure: 404 not found, 400 invalid body
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv07_list_messages.puml ---

@startuml sq_srv07_list_messages
' ============================================================
' Title:     SRV-07 — LIST Messages
' Boundary:  nasim code agent HTTP API
' Purpose:   Retrieve message history for a session
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

title nasim — SRV-07 LIST Messages

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
end box
box "Repository Group" #E8F5E9
  participant "SessionStore" as store
end box

note over user, store
  Scope:          Retrieve message history for a session
  Preconditions:  Session exists, ServerRouter initialized
  Contexts:       Called by HTTPClient via GET /v1/sessions/{id}/messages
  Excludes:       Session CRUD (SRV-01..05), Message dispatch (SRV-06)
  Rollback:       404 if session not found
  Design:         CSR: Controller(ServerRouter) -> Service(SessionService) -> Repository(SessionStore). ROD: standard list (AIP-132)
  Classification: Primary Orchestrator
  Returns:        200 OK with message list, or 404 NOT_FOUND error
end note

== SRV-07 LIST Messages ==

user -> router : GET /v1/sessions/{id}/messages
activate router

router -> svc : SRV-07 LIST Messages(sessionId)
activate svc

svc -> store : readSessionMessages(sessionId)
activate store

alt Session exists
    store --> svc : SessionEntity(messages=[...])
    deactivate store
    svc --> router : ListMessagesResponse {messages: [...]}
    router --> user : 200 OK {messages: [...]}
else Session not found [404]
    store --> svc : null
    deactivate store
    svc --> router : 404 NOT_FOUND
    router --> user : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

deactivate svc
deactivate router

note over user, store
  Flow:    SRV-07 → readMessages → respond
  State:   No state change
  Success: 200 OK with message list
  Failure: 404 session not found
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_srv10_read_config.puml ---

@startuml sq_srv10_read_config
' ============================================================
' Title:     SRV-10 — READ Config
' Boundary:  nasim code agent HTTP API
' Purpose:   Read current agent configuration
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    Prompt audit 2026-06-21 (cop.md: AIP-193 error path added)
' ============================================================

title nasim — SRV-10 READ Config

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #FCE4EC
  participant "ConfigService" as svc
end box
box "Repository Group" #E8F5E9
  participant "ConfigLoader" as config
end box

note over user, config
  Scope:          Read current agent configuration
  Preconditions:  ConfigLoader initialized
  Contexts:       Called by HTTPClient via GET /v1/config
  Excludes:       Config update, config validation
  Rollback:       500 if config read fails
  Design:         CSR: Controller(ServerRouter) -> Service(ConfigService) -> Repository(ConfigLoader). ROD: standard get (AIP-131). Returns sanitized config (no secrets).
  Classification: Primary Orchestrator
  Returns:        200 OK with sanitized config, or 500 INTERNAL error
end note

== SRV-10 READ Config ==

user -> router : GET /v1/config
activate router

router -> svc : SRV-10 READ Config()
activate svc

svc -> config : readConfig()
activate config

break Config read failure [500]
    config --> svc : InternalError
    deactivate config
    svc --> router : 500 INTERNAL
    router --> user : 500 INTERNAL {error: {code: "INTERNAL", message: "Failed to read config", status: "INTERNAL"}}
end

config --> svc : ConfigEntity
deactivate config

svc --> router : ConfigResponseDTO
deactivate svc
router --> user : 200 OK {config: {provider: "...", model: "...", safety_mode: "..."}}
deactivate router

note over user, config
  Flow:    SRV-10 → readConfig → respond
  State:   No state change
  Success: 200 OK with sanitized config
  Failure: 500 INTERNAL on config read failure
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SRV/sq_api05_delete_session.puml ---

@startuml sq_api05_delete_session
' ============================================================
' Title:     API-05 — DELETE Session
' Boundary:  nasim code agent HTTP API
' Purpose:   Delete a session (hard delete)
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — API-05 DELETE Session

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
end box
box "Repository Group" #E8F5E9
  participant "SessionStore" as store
end box

note over user, store
  Scope:          Delete a session (hard delete)
  Preconditions:  Session exists on disk
  Contexts:       Called by HTTPClient via DELETE /v1/sessions/{id}
  Excludes:       Hard delete, message operations
  Rollback:       404 if session not found
  Design:         CSR: Controller(ServerRouter) -> Service(SessionService) -> Repository(SessionStore). ROD: standard delete (AIP-135)
  Classification: Primary Orchestrator
  Returns:        200 OK with retired status, or 404 NOT_FOUND error
end note

== API-05 DELETE Session ==

user -> router : DELETE /v1/sessions/{id}
activate router

router -> svc : API-05 DELETE Session(sessionId)
activate svc

svc -> store : readSessionExists(sessionId)
activate store

break Session not found [404]
  store --> svc : NotFound
  deactivate store
  svc --> router : 404 NOT_FOUND
  router --> user : 404 NOT_FOUND {error: {code: "NOT_FOUND", message: "Session not found", status: "NOT_FOUND"}}
end

store --> svc : SessionEntity
deactivate store

svc -> svc : validateStateTransition(ACTIVE → CLOSED)
svc -> store : retireSession(sessionId)
activate store
store --> svc : retired
deactivate store

svc --> router : 200 OK
deactivate svc
router --> user : 200 OK {retired: true}
deactivate router

note over user, store
  Flow:    API-05 → read → validate state → retire → respond
  State:   ACTIVE → CLOSED
  Success: 200 OK with retired status
  Failure: 404 not found
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PRV/sq_prv03_stream_provider_chat.puml ---

@startuml sq_prv03_stream_provider_chat
' ============================================================
' Title:     PRV-03 — STREAM Provider Chat
' Boundary:  nasim code agent CLI
' Purpose:   Streaming LLM chat completion via provider abstraction
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PRV-03 STREAM ProviderChat

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Provider Group" #FFF3E0
  participant "Provider" as provider
end box
box "External" #F5F5F5
  participant "LLM Provider API" as api
end box

note over user, api
  Scope:          PRV-03 STREAM ProviderChat — streaming chat completion yielding chunks
  Preconditions:  Provider initialized and reachable
  Contexts:       Called by AGT-01 (Process User Task)
  Excludes:       Sync chat (PRV-02), tool execution
  Rollback:       Connection drop -> ProviderError
  Design:         Yields str | ToolCall chunks from HTTP stream
  Returns:
    - Success: Stream of TextChunk and ToolCall objects
    - Failure: ProviderError — stream interrupted
end note

== PRV-03 STREAM ProviderChat ==

user -> router : PRV-03 STREAM ProviderChat(messages, tools)
activate router
router -> agent : PRV-03 STREAM ProviderChat(messages, tools)
activate agent

agent -> provider : PRV-03 STREAM ProviderChat(messages, tools)
activate provider

provider -> api : HTTP POST /api/chat {model, messages, tools, stream:true}
activate api

break Connection drops mid-stream
    api --> provider : broken pipe / timeout
    provider --> agent : ProviderError("Stream interrupted")
    agent -> agent : handle error -> ERROR state
end

loop for each chunk
    api --> provider : JSON chunk
    provider -> provider : parse chunk
    alt text content chunk
        provider --> agent : yield TextChunk(token)
    else tool_call chunk
        provider -> provider : accumulate ToolCall by index
    end
end

provider -> provider : yield accumulated ToolCalls
provider --> agent : StreamComplete
deactivate provider

agent --> router : StreamComplete
deactivate agent
deactivate router

note over user, api
  Flow:    PRV-03 → User → ServerRouter → AgentOrchestrator → Provider → HTTP stream → parse chunks → yield str | ToolCall
  State:   <back:#FFF3E0>THINKING</back> → <back:#FFF3E0>THINKING</back> (no state change)
  Success: Stream of text tokens and ToolCall objects
  Failure: Connection drop -> ProviderError
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PRV/sq_prv04_select_provider_backend.puml ---

@startuml sq_prv04_select_provider_backend
' ============================================================
' Title:     PRV-04 — SELECT Provider Backend
' Boundary:  nasim code agent CLI
' Purpose:   Map config.provider string to provider class
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PRV-04 SELECT ProviderBackend

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Config Group" #E0F7FA
  participant "ConfigLoader" as cfg
end box
box "Provider Group" #FFF3E0
  participant "ProviderFactory" as factory
end box

note over user, factory
  Scope:          PRV-04 SELECT ProviderBackend — provider backend selection from config
  Preconditions:  Config loaded with provider field
  Contexts:       Called by PRV-01 (REGISTER Provider)
  Excludes:       Provider instantiation (PRV-01)
  Rollback:       Unknown provider -> ConfigError
  Design:         Registry mapping: str -> class
  Returns:
    - Success: provider_class reference for instantiation
    - Failure: ConfigError — unknown provider name
end note

== PRV-04 SELECT ProviderBackend ==

user -> router : PRV-04 SELECT ProviderBackend(provider_name)
activate router
router -> agent : PRV-04 SELECT ProviderBackend(provider_name)
activate agent

agent -> cfg : PRV-04 READ Config(provider_field)
activate cfg
cfg --> agent : provider_string
deactivate cfg

agent -> factory : PRV-04 SELECT ProviderBackend(provider_string)
activate factory
factory -> factory : PROV_REGISTRY lookup

break Provider not in registry
    factory -> factory : raise ConfigError("Unknown provider: X")
    factory --> agent : ConfigError
    agent --> router : ConfigError
end

factory --> agent : provider_class
deactivate factory

agent --> router : provider_class
deactivate agent
deactivate router

note over user, factory
  Flow:    PRV-04 → User → ServerRouter → AgentOrchestrator → ConfigLoader → ProviderFactory → registry lookup → class
  State:   No state change
  Success: Provider class reference for instantiation
  Failure: Unknown provider name -> ConfigError
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PRV/sq_prv02_request_chat.puml ---

@startuml sq_prv02_request_chat
' ============================================================
' Title:     PRV-02 — REQUEST Chat
' Boundary:  nasim code agent CLI
' Purpose:   Synchronous LLM chat completion via provider abstraction
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PRV-02 REQUEST Chat

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Provider Group" #FFF3E0
  participant "Provider" as provider
end box
box "External" #F5F5F5
  participant "LLM Provider API" as api
end box

note over user, api
  Scope:          PRV-02 REQUEST Chat — single synchronous chat completion
  Preconditions:  Provider initialized and reachable
  Contexts:       Called by AGT-01 (Process User Task)
  Excludes:       Streaming (PRV-03), tool parsing
  Rollback:       HTTP error raised as ProviderError
  Design:         Uses httpx.AsyncClient with timeout
  Returns:
    - Success: LLMResponse(content, tool_calls)
    - Failure: ProviderError — connection failed
    - Failure: ProviderError — timeout
end note

== PRV-02 REQUEST Chat ==

user -> router : PRV-02 REQUEST Chat(messages, tools)
activate router
router -> agent : PRV-02 REQUEST Chat(messages, tools)
activate agent

hnote over provider #FFF3E0 : **State: THINKING**

agent -> provider : PRV-02 REQUEST Chat(messages, tools)
activate provider

provider -> api : HTTP POST /api/chat {model, messages, tools, stream:false}
activate api

break HTTP error or timeout
    api --> provider : connection error / timeout
    provider --> agent : ProviderError("Connection failed")
    agent -> agent : handle error -> ERROR state
end

api --> provider : JSON response
deactivate api

provider -> provider : parse response -> LLMResponse

provider --> agent : LLMResponse(content, tool_calls)
deactivate provider

agent --> router : LLMResponse(content, tool_calls)
deactivate agent
deactivate router

note over user, api
  Flow:    PRV-02 → User → ServerRouter → AgentOrchestrator → Provider → HTTP POST → JSON parse → LLMResponse
  State:   <back:#FFF3E0>THINKING</back> → <back:#FFF3E0>THINKING</back> (no state change)
  Success: LLMResponse with content and/or tool_calls
  Failure: HTTP error or timeout -> ProviderError
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PRV/sq_prv01_register_provider.puml ---

@startuml sq_prv01_register_provider
' ============================================================
' Title:     PRV-01 — REGISTER Provider
' Boundary:  nasim code agent CLI
' Purpose:   Provider instantiation from config
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — PRV-01 REGISTER Provider

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Provider Group" #FFF3E0
  participant "ProviderFactory" as factory
  participant "Provider" as proto
end box

note over user, proto
  Scope:          PRV-01 REGISTER Provider — provider instantiation from configuration
  Preconditions:  Config loaded with valid provider name
  Contexts:       Called by main() during startup
  Excludes:       Provider chat/stream (PRV-02, PRV-03)
  Rollback:       Unknown provider -> ConfigError
  Design:         Factory pattern; one class per backend
  Returns:
    - Success: Provider instance ready for chat/stream
    - Failure: ConfigError — unknown provider type
end note

== PRV-01 REGISTER Provider ==

user -> router : PRV-01 REGISTER Provider(ollama)
activate router
router -> agent : PRV-01 REGISTER Provider(config)
activate agent

agent -> factory : PRV-01 REGISTER Provider(config)
activate factory
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
    factory --> agent : ConfigError
    agent --> router : ConfigError
end

factory --> agent : Provider instance
deactivate factory

agent --> router : Provider ready
deactivate agent
deactivate router

note over user, proto
  Flow:    PRV-01 → User → ServerRouter → AgentOrchestrator → ProviderFactory → provider class lookup → instance
  State:   No state change
  Success: Provider instance ready for chat/stream
  Failure: Unknown provider type -> ConfigError
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/WRL/sq_wrl01_append_event.puml ---

@startuml sq_wrl01_append_event
' ============================================================
' Title:     WRL-01 — APPEND Event
' Boundary:  nasim code agent
' Purpose:   Append event to wire log
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — WRL-01 INSERT Event

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Group" #E0F2F1
  participant "WireLog" as wirelog
  participant "WireAppender" as appender
end box
box "External" #F5F5F5
  participant "Host Filesystem" as fs
end box

note over user, fs
  Scope:          Append event to wire log
  Preconditions:  Wire log file path configured, write access available
  Contexts:       Called on every significant agent event; prerequisite for WRL-02/03/04
  Excludes:       Log reading (WRL-02), session forking (WRL-04)
  Rollback:       Write failure -> event lost, log warning
  Design:         WireAppender appends serialized events; append-only log; buffered writes with flush on session end
  Classification: Process Decomposition
  Returns:        Success: AppendResult(event_id, offset); Failure: AppendError("write failed")
end note

== WRL-01 APPEND Event ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> wirelog : wrl01 APPEND Event(event)
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
    wirelog --> agent : 500 INTERNAL — AppendError("write failed")
    agent --> router : AgentEvent(Error)
end

fs --> wirelog : 200 OK — write_result
deactivate fs

wirelog --> agent : 200 OK — AppendResult(event_id, offset)
deactivate wirelog

agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    WRL-01 → serialize → add metadata → append to file
  State:   No state change
  Success: 200 OK — AppendResult with event_id and offset
  Failure: 500 INTERNAL — write failure, event lost, warning logged
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/WRL/sq_wrl04_fork_session.puml ---

@startuml sq_wrl04_fork_session
' ============================================================
' Title:     WRL-04 — Fork Session
' Boundary:  nasim code agent CLI
' Purpose:   Fork session at any turn
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Group" #FFF3E0
  participant "WireLogger" as logger
  participant "SessionForker" as forker
end box
box "Session Group" #E8F5E9
  participant "SessionManager" as session
end box

note over user, session
  Scope:
    - WRL-04 FORK Session — low-level storage-layer fork of wire log

  Preconditions:
    - Wire log has events for source session
    - SessionManager available for new session creation

  Contexts:
    - Called by SSN-08 (BRANCH Session) only — the domain-level fork operation
    - Uses WRL-02 (Read Log) to get events up to fork point

  Excludes:
    - Log reading (handled by WRL-02)
    - Session replay (handled by WRL-04)
    - Event writing (handled by WRL-01)
    - Session-level semantics (parent-child link, branch metadata) — handled by SSN-08

  Rollback:
    - Fork failure → no new session created

  Design:
    - Storage-layer operation only: reads events up to fork_point, writes new JSONL file
    - SessionForker reads events up to fork_point from wire log
    - Creates new session with copied event history
    - New session gets unique session_id
    - Fork point marked in wire log for traceability
    - Does NOT create parent-child link or branch metadata — SSN-08 owns that

  Classification: Primary Orchestrator

  Returns:
    - Success: ForkResult with new_session_id and fork_point
    - Failure: ForkError with details
end note

== wrl03 FORK Session ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> forker : wrl04 FORK Session(source_session_id, fork_turn)
activate forker

forker -> logger : wrl02 READ Log(source_session_id, up_to_turn=fork_turn)
activate logger
logger --> forker : 200 OK — events[]
deactivate logger

forker -> session : wrl04 CREATE Session(forked_from=source_session_id)
activate session
session --> forker : 200 OK — new_session_id
deactivate session

forker -> forker : copy_events_to_session(events, new_session_id)

forker -> logger : wrl01 APPEND Event(ForkEvent(source, fork_point, new_session_id))
activate logger
logger --> forker : 200 OK — append_success
deactivate logger

forker --> agent : 200 OK — ForkResult(new_session_id, fork_turn, event_count)
deactivate forker

agent --> router : AgentEvent(Done)

note over user, session
  Flow:
    - WRL-04 → read events → create session → copy events → append fork event

  State:
    - <back:#ECEFF1>IDLE</back> → READING → CREATING → COPYING → DONE

  Success:
    - 200 OK — ForkResult with new session ID

  Failure:
    - 500 INTERNAL — Fork failure → no session created

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
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Group" #FFF3E0
  participant "WireLogger" as logger
  participant "EventDeserializer" as deserializer
end box
box "FileSystem Group" #F3E5F5
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
    - WireLogger reads log file sequentially
    - EventDeserializer parses each line into Event objects
    - Supports filtering by session_id and event type
    - Streaming read for memory efficiency

  Classification: Primary Orchestrator

  Returns:
    - Success: EventStream with deserialized events
    - Failure: EventStream with partial results and error
end note

== wrl02 READ Log ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> logger : wrl02 READ Log(session_id, filter)
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

logger --> agent : 200 OK — EventStream(events[], count, truncated)
deactivate logger

agent --> router : AgentEvent(Done)

note over user, fs
  Flow:
    - WRL-02 → WireLogger → FileSystem + EventDeserializer → EventStream

  State:
    - <back:#ECEFF1>IDLE</back> → READING → DESERIALIZING → FILTERING → DONE

  Success:
    - 200 OK — EventStream with matching events

  Failure:
    - 500 INTERNAL — Read failure → partial events + error

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
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — WRL-03 READ Turn

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Group" #FFFDE7
  participant "TurnIndex" as idx
  participant "WireReader" as reader
end box

note over user, reader
  Scope:          Seek to a specific turn in the wire log
  Preconditions:  Wire log exists, TurnIndex built
  Contexts:       Called by WRL-04 FORK Session or replay flows
  Excludes:       Log append (WRL-01), session fork (WRL-04)
  Rollback:       N/A (read-only)
  Design:         Uses TurnIndex for O(1) random access by turn number
  Classification: Process Decomposition
  Returns:        Success: WireEvents[turn]; Failure: NotFound — turn not in index
end note

== WRL-03 SEEK Turn ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> idx : wrl03 SEEK Turn(turn_number)

idx -> idx : LOOKUP turn_number
idx -> reader : wrl03 READ Wire Events(offset)
activate reader

break Turn not found
  reader --> idx : 404 NOT_FOUND
  idx --> agent : 404 NOT_FOUND — turn not in index
  agent --> router : AgentEvent(Error)
end

reader --> idx : 200 OK — WireEvents[turn]
deactivate reader

idx --> agent : 200 OK — WireEvents[turn]

agent --> router : AgentEvent(Done)

note over user, reader
  Flow:    WRL-03 → lookup offset → read events for turn
  State:   No state change
  Success: 200 OK — wire events for the requested turn
  Failure: 404 NOT_FOUND — turn not found in index
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/WRL/sq_wrl05_checkpoint_turn.puml ---

@startuml sq_wrl05_checkpoint_turn
' ============================================================
' Title:     WRL-05 — CHECKPOINT Turn
' Boundary:  nasim code agent
' Purpose:   Index current turn and persist checkpoint for resumption
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — WRL-05 INSERT Turn

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Wire Log Group" #FFFDE7
  participant "WireLog" as wl
  participant "TurnIndex" as ti
end box
box "FileSystem Group" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Index current conversation turn and persist checkpoint for session resumption
  Preconditions:  Turn data available, wire log initialized
  Contexts:       Called at turn boundaries or on-demand for persistence
  Excludes:       Event appending (WRL-01), log reading (WRL-02), session forking (WRL-04)
  Rollback:       Write failure → checkpoint not persisted, warning logged
  Design:         TurnIndex extracts turn metadata, builds checkpoint, persists to filesystem
  Classification: Process Decomposition
  Returns:        Success: CheckpointResult(turn_id, offset); Failure: checkpoint not persisted
end note

== WRL-05 CHECKPOINT Turn ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> wl : wrl05 CHECKPOINT Turn(turn_data)
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

wl --> agent : 200 OK — CheckpointResult
deactivate wl

agent --> router : AgentEvent(Done)

note over participants
  Flow:    WRL-05 → index turn → persist checkpoint
  State:   <back:#ECEFF1>IDLE</back> → INDEXING → PERSISTING → DONE
  Success: 200 OK — CheckpointResult with turn_id and file offset
  Failure: 500 INTERNAL — write failure, checkpoint not persisted, warning logged
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn02_read_session.puml ---

@startuml sq_ssn02_read_session
' ============================================================
' Title:     SSN-02 — Read Session
' Boundary:  nasim code agent CLI
' Purpose:   Load conversation history from disk
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F1F8E9
  participant "SessionStore" as store
end box
database "Session Directory" as dir

note over user, dir
  Scope:          Load session messages from JSON Lines file
  Preconditions:  Session ID provided (--continue or --session)
  Contexts:       Called by CLI-04 or SSN-04 (Resume Session)
  Excludes:       Session saving (SSN-01)
  Rollback:       Not found -> start fresh session
  Design:         Deserialize JSON Lines back to message list
  Classification: Process Decomposition
  Returns:        Success: Session(id, created_at, messages); Failure: FileNotFoundError -> start fresh
end note

== SSN-02 Load Session ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> store : ssn02 READ Session(session_id)
store -> dir : read session.jsonl

break Session file not found
    dir --> store : FileNotFoundError
    store --> agent : 404 NOT_FOUND
    agent -> agent : start fresh session
    agent --> router : AgentEvent(Done)
end

store -> store : deserialize JSON Lines -> messages
store --> agent : 200 OK — Session(id, created_at, messages)
agent --> router : AgentEvent(Done)

note over user, dir
  Flow:    SSN-02 → read file → deserialize → Session
  State:   No state change
  Success: 200 OK — session with restored messages
  Failure: 404 NOT_FOUND — file not found, start fresh
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn07_search_sessions.puml ---

@startuml sq_ssn07_search_sessions
' ============================================================
' Title:     SSN-07 — Search Sessions
' Boundary:  nasim code agent CLI
' Purpose:   Full-text search across session history
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-07 LIST Sessions

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F1F8E9
  participant "SessionSearch" as search
end box
database "FTS5 Index" as fts

note over user, fts
  Scope:          Full-text search across all session history
  Preconditions:  FTS5 index built on session messages
  Contexts:       Called when user searches past conversations
  Excludes:       Session read (SSN-02), session persist (SSN-01)
  Rollback:       Index missing → fallback to linear scan
  Design:         FTS5 for fast search; results ranked by relevance
  Classification: Process Decomposition
  Returns:        Success: SearchResult[session_id, turn_id, snippet, score]; Failure: IndexError → linear scan
end note

== SSN-07 Search Sessions ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> search : ssn07 SEARCH Session History(query, limit)
activate search

search -> fts : FTS5 query(query)
activate fts
fts --> search : raw_results [session_id, turn_id, snippet, rank]
deactivate fts

search -> search : rank results by relevance
search -> search : format snippets

search --> agent : 200 OK — SearchResult[session_id, turn_id, snippet, score]
deactivate search

agent --> router : AgentEvent(Done)

break Index not available
    fts --> search : IndexError
    search -> search : fallback: linear scan
    search --> agent : 200 OK — SearchResult[linear_scan_results]
    agent --> router : AgentEvent(Done)
end

note over user, fts
  Flow:    SSN-07 → FTS5 query → rank → return
  State:   No state change (read-only query)
  Success: 200 OK — ranked search results returned
  Failure: 500 INTERNAL — index missing, linear scan fallback
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn03_list_sessions.puml ---

@startuml sq_ssn03_list_sessions
' ============================================================
' Title:     SSN-03 — List Sessions
' Boundary:  nasim code agent CLI
' Purpose:   List available saved sessions
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F1F8E9
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
  Returns:        Success: [(id, created_at, message_count), ...]; Failure: [] (empty list)
end note

== SSN-03 List Sessions ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> store : ssn03 LIST Sessions()
store -> dir : scan ~/.nasim/sessions/

break No sessions directory
    dir --> store : FileNotFoundError
    store --> agent : 404 NOT_FOUND — [] (empty list)
    agent --> router : AgentEvent(Done)
end

store -> store : read metadata from each session
store --> agent : 200 OK — [(id, created_at, message_count), ...]
agent --> router : AgentEvent(Done)

note over user, dir
  Flow:    SSN-03 → scan directory → read metadata → list
  State:   No state change
  Success: 200 OK — formatted list of sessions
  Failure: 404 NOT_FOUND — no directory, empty list
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn06_revert_turn.puml ---

@startuml sq_ssn06_revert_turn
' ============================================================
' Title:     SSN-06 — Revert Turn
' Boundary:  nasim code agent CLI
' Purpose:   Restore session to a previous snapshot or turn
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-06 UPDATE Turn

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F1F8E9
  participant "SessionVersioning" as ver
end box
database "Snapshot Store" as snap

note over user, snap
  Scope:          Restore session to a previous snapshot or specific turn
  Preconditions:  Snapshot exists (created via SSN-05)
  Contexts:       Called when user requests undo or revert
  Excludes:       Snapshot creation (SSN-05), session persistence (SSN-01)
  Rollback:       Snapshot not found → display error, retain current state
  Design:         Revert replaces current messages with snapshot copy
  Classification: Process Decomposition
  Returns:        Success: Reverted(snapshot_id, turn_count); Failure: RevertError → retain current
end note

== SSN-06 Revert Turn ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> ver : ssn06 REVERT Session(session_id, snapshot_id)
activate ver

ver -> snap : ssn06 READ Snapshot(snapshot_id)
activate snap
alt snapshot found
    snap --> ver : 200 OK — snapshot_messages
    deactivate snap
else snapshot not found
    snap --> ver : 404 NOT_FOUND
    deactivate snap
    ver --> agent : 404 NOT_FOUND — RevertError("snapshot not found")
    agent --> router : AgentEvent(Error)
end

ver -> ver : replace current messages with snapshot
ver -> ver : truncate messages after snapshot point

ver --> agent : 200 OK — Reverted(snapshot_id, turn_count)
deactivate ver

agent --> router : AgentEvent(Done)

break Snapshot load error
    snap --> ver : IOError
    ver --> agent : 500 INTERNAL — RevertError("snapshot unreadable")
    agent --> router : AgentEvent(Error)
end

note over user, snap
  Flow:    SSN-06 → find snapshot → restore to turn
  State:   <back:#2E7D32>ACTIVE</back> → REVERTING → <back:#2E7D32>ACTIVE</back>
  Success: 200 OK — session restored to snapshot point
  Failure: 404 NOT_FOUND — snapshot not found, retain current
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn01_persist_session.puml ---

@startuml sq_ssn01_persist_session
' ============================================================
' Title:     SSN-01 — Persist Session
' Boundary:  nasim code agent CLI
' Purpose:   Persist conversation history to disk
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F1F8E9
  participant "SessionStore" as store
end box
database "Session Directory" as dir

note over user, dir
  Scope:          Save session messages to JSON Lines file
  Preconditions:  AgentOrchestrator has messages to save
  Contexts:       Called by AGT-01 after each task turn
  Excludes:       Session loading (SSN-02)
  Rollback:       Write error -> log warning, session lost
  Design:         One file per session: ~/.nasim/sessions/<id>/session.jsonl
  Classification: Process Decomposition
  Returns:        Success: Result(success=true, data={session_id}); Failure: Result(success=false, error="write_failed")
end note

== SSN-01 Save Session ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> store : ssn01 PERSIST Session(session_id, messages)
store -> store : serialize messages to JSON Lines
store -> dir : write session.jsonl

break Disk write error
    dir --> store : IOError
    store --> agent : 500 INTERNAL — log warning("Session save failed")
    agent --> router : AgentEvent(Error)
end

store --> agent : 200 OK — save complete
agent --> router : AgentEvent(Done)

note over user, dir
  Flow:    SSN-01 → serialize → write JSON Lines
  State:   No state change
  Success: 200 OK — session persisted to disk
  Failure: 500 INTERNAL — disk error, log warning, continue
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn08_branch_session.puml ---

@startuml sq_ssn08_branch_session
' ============================================================
' Title:     SSN-08 — Branch Session
' Boundary:  nasim code agent CLI
' Purpose:   Fork session into a new branch for parallel exploration
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-08 INSERT Session

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F1F8E9
  participant "SessionFork" as fork
end box
database "Session Store" as store

note over user, store
  Scope:          Fork current session into a new branch
  Preconditions:  Active session with message history
  Contexts:       Called when user requests to explore alternative path
  Excludes:       Session revert (SSN-06), session search (SSN-07)
  Rollback:       Fork failure → display error, retain current session
  Design:         High-level domain operation. Calls WRL-04 (FORK Session) for
                  the low-level storage-layer fork (wire log slice + new file).
                  This UC owns session-level semantics (parent-child link,
                  branch metadata); WRL-04 owns event-log-level semantics.
  Classification: Process Decomposition
  Returns:        Success: BranchCreated(branch_session_id, parent_id); Failure: BranchError → retain current
end note

== SSN-08 Branch Session ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> fork : ssn08 BRANCH Session(session_id, from_turn)
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
fork -> fork : call WRL-04 (FORK Session) for wire log fork

fork --> agent : 200 OK — BranchCreated(branch_session_id, parent_id)
deactivate fork

agent --> router : AgentEvent(Done)

break Copy failure
    store --> fork : IOError
    fork --> agent : 500 INTERNAL — BranchError
    agent --> router : AgentEvent(Error)
end

note over user, store
  Flow:    SSN-08 → copy session → create branch
  State:   <back:#2E7D32>ACTIVE</back> → BRANCHING → <back:#2E7D32>ACTIVE</back> (parent + child)
  Success: 200 OK — branch session created, new session_id returned
  Failure: 500 INTERNAL — copy error, display error, retain current
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn09_delete_session.puml ---

@startuml sq_ssn09_delete_session
' ============================================================
' Title:     SSN-09 — DELETE Session
' Boundary:  nasim code agent
' Purpose:   Permanently delete a session and its associated data
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-09 DELETE Session

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F3E5F5
  participant "SessionStore" as store
end box
box "External" #F5F5F5
  participant "Host Filesystem" as fs
end box

note over user, fs
  Scope:          Permanently delete a session and its associated data
  Preconditions:  Session exists on disk
  Contexts:       Called by API-05 (DELETE Session) for hard delete
  Excludes:       Hard delete (API-05), session read (SSN-02)
  Rollback:       Deletion is irreversible; backup recommended
  Design:         Removes session directory and all associated files
  Classification: Process Decomposition
  Returns:        Success: delete_confirmed(session_id); Failure: DeleteError(session not found | permission denied)
end note

== SSN-09 DELETE Session ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> store : ssn09 DELETE Session(session_id)
activate store

store -> store : validate_session_exists(session_id)

break Session not found
    store --> agent : 404 NOT_FOUND — DeleteError("session not found")
    agent --> router : AgentEvent(Error)
end

store -> fs : ssn09 REMOVE Directory(session_path)
activate fs

break Permission denied
    fs --> store : PermissionError
    store --> agent : 403 FORBIDDEN — DeleteError("permission denied")
    agent --> router : AgentEvent(Error)
end

fs --> store : 200 OK — removed
deactivate fs

store -> store : clear_session_index(session_id)

store --> agent : 200 OK — delete_confirmed(session_id)
deactivate store

agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    SSN-09 → validate → remove directory → clear index → confirm
  State:   <back:#757575>CLOSED</back>
  Success: 200 OK — session permanently deleted
  Failure: 404 NOT_FOUND — session not found; 403 FORBIDDEN — permission denied
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn05_snapshot_session.puml ---

@startuml sq_ssn05_snapshot_session
' ============================================================
' Title:     SSN-05 — Snapshot Session
' Boundary:  nasim code agent CLI
' Purpose:   Create a point-in-time snapshot of session state
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — SSN-05 INSERT Session

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F1F8E9
  participant "SessionVersioning" as ver
end box
database "Snapshot Store" as snap

note over user, snap
  Scope:          Create a point-in-time snapshot of session messages
  Preconditions:  Active session with messages
  Contexts:       Called before risky operations or on explicit request
  Excludes:       Session read (SSN-02), revert (SSN-06)
  Rollback:       Snapshot failure → log warning, continue without snapshot
  Design:         Snapshot stored as immutable copy; supports revert via SSN-06
  Classification: Process Decomposition
  Returns:        Success: SnapshotCreated(snapshot_id); Failure: SnapshotError → log warning
end note

== SSN-05 Snapshot Session ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> ver : ssn05 SNAPSHOT Session(session_id)
activate ver

ver -> ver : serialize current messages
ver -> snap : write snapshot (immutable copy)
activate snap
snap --> ver : snapshot_id
deactivate snap

ver --> agent : 200 OK — SnapshotCreated(snapshot_id)
deactivate ver

agent --> router : AgentEvent(Done)

break Disk write error
    snap --> ver : IOError
    ver --> agent : 500 INTERNAL — SnapshotError
    agent --> router : AgentEvent(Error)
end

note over user, snap
  Flow:    SSN-05 → serialize → create snapshot → store
  State:   No state change (snapshot is side-effect)
  Success: 200 OK — snapshot ID returned for future revert (SSN-06)
  Failure: 500 INTERNAL — disk error, log warning, continue
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SSN/sq_ssn04_restore_session.puml ---

@startuml sq_ssn04_restore_session
' ============================================================
' Title:     SSN-04 — Restore Session
' Boundary:  nasim code agent CLI
' Purpose:   Resume a previous session by loading its history
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Session Group" #F1F8E9
  participant "SessionStore" as store
end box

note over user, agent
  Scope:          Resume session from --continue or --session flag
  Preconditions:  CLI invoked with --continue or --session <id>
  Contexts:       Called by CLI-04 (Parse CLI Arguments)
  Excludes:       New session creation
  Rollback:       No session found -> start fresh
  Design:         --continue loads latest; --session loads by ID
  Classification: Primary Orchestrator
  Returns:        Success: Session(id, messages); Failure: FileNotFoundError -> start fresh
end note

== SSN-04 Resume Session ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> store : ssn04 READ Session(session_id)
ref over store
  SSN-02: Load Session
end ref

alt Session found
    store --> agent : 200 OK — Session(id, messages)
    agent -> agent : ssn01 PERSIST Session(session_id, messages)
    agent --> router : AgentEvent(Done)
else Session not found
    store --> agent : 404 NOT_FOUND
    agent -> agent : start fresh
    agent --> router : AgentEvent(Done)
end

note over user, agent
  Flow:    SSN-04 → load session → restore messages → continue
  State:   No state change
  Success: 200 OK — conversation restored, ready for input
  Failure: 404 NOT_FOUND — no session, start fresh
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg04_register_plugin_hooks.puml ---

@startuml sq_plg04_register_plugin_hooks
' ============================================================
' Title:     PLG-04 — Register Plugin Hooks
' Boundary:  nasim code agent
' Purpose:   Register all hooks declared in a plugin manifest
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "PluginLoader" as loader
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hm
end box

note over user, hm
  Scope:          Register plugin-declared hooks into HookManager
  Preconditions:  Valid PluginManifest loaded (PLG-02)
  Contexts:       Called during plugin enable (PLG-05)
  Excludes:       Tool registration, plugin activation
  Rollback:       Registration failure logged; other hooks still registered
  Design:         Plugin hooks prefixed with plugin name
  Classification: Process Decomposition
  Returns:        all hooks registered or RegistrationError with hook skipped
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== PLG-04 Register Plugin Hooks ==

agent -> loader : PLG-04 REGISTER_PLUGIN_HOOKS(manifest)
activate loader

loader -> loader : enumerate hooks from PluginManifest

loop for each hook in manifest
    loader -> hm : register(event, handler, priority)

    break Registration failure
        hm --> loader : RegistrationError
        loader --> loader : log warning, skip hook
    end

    hm --> loader : registered
end

loader --> agent : all hooks registered
deactivate loader

agent --> router : AgentEvent(Done)

note over user, hm
  Flow:    PLG-04 AgentOrchestrator -> PluginLoader -> enumerate plugin hooks -> register in HookManager
  State:   Hooks added to HookManager
  Success: All plugin hooks registered
  Failure: Registration failure -> hook skipped with warning
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg06_disable_plugin.puml ---

@startuml sq_plg06_disable_plugin
' ============================================================
' Title:     PLG-06 — Disable Plugin
' Boundary:  nasim code agent
' Purpose:   Deactivate plugin tools and hooks, set state DISABLED
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "PluginLoader" as loader
  participant "ToolRegistry" as registry
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hm
end box

note over user, hm
  Scope:          Deactivate plugin tools and hooks, set state DISABLED
  Preconditions:  Plugin is currently ENABLED
  Contexts:       Called by CLI or PluginLoader
  Excludes:       Plugin enable, discovery, removal
  Rollback:       Partial disable logged; state set to ERROR
  Design:         Reverse of PLG-05; unregister tools then hooks
  Classification: Process Decomposition
  Returns:        plugin disabled or state ERROR with partial disable logged
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== PLG-06 Disable Plugin ==

agent -> loader : PLG-06 DISABLE_PLUGIN(plugin_id)
activate loader

loader -> registry : unregister plugin tools
loader -> hm : unregister plugin hooks
loader -> loader : set state DISABLED

break Unregister failure
    loader -> loader : set state ERROR, log failure
end

loader --> agent : plugin disabled
deactivate loader

agent --> router : AgentEvent(Done)

note over user, hm
  Flow:    PLG-06 AgentOrchestrator -> PluginLoader -> deactivate tools + hooks -> set state DISABLED
  State:   Plugin state: ENABLED -> DISABLED (or ERROR)
  Success: Plugin disabled with tools and hooks removed
  Failure: Unregister failure -> state ERROR, partial disable logged
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg02_load_manifest.puml ---

@startuml sq_plg02_load_manifest
' ============================================================
' Title:     PLG-02 — Load Manifest
' Boundary:  nasim code agent
' Purpose:   Read and parse a plugin's manifest.yaml file
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Plugins Group" #EDE7F6
  participant "PluginLoader" as loader
end box
participant "Host Filesystem" as fs

note over user, fs
  Scope:          Read manifest.yaml and parse plugin metadata
  Preconditions:  Plugin directory exists
  Contexts:       Called during plugin discovery (PLG-01)
  Excludes:       Tool/hook registration, plugin activation
  Rollback:       Plugin skipped with warning
  Design:         Strict schema validation; fail-fast on malformed YAML
  Classification: Process Decomposition
  Returns:        PluginManifest or plugin skipped with warning
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== PLG-02 Load Manifest ==

agent -> loader : PLG-02 LOAD_MANIFEST(manifest_path)
activate loader

loader -> fs : read(manifest.yaml)
activate fs

break File not found
    fs --> loader : FileNotFoundError
    loader --> agent : PluginSkipped(manifest_path, reason="not found")
    deactivate loader
    agent --> router : AgentEvent(Done)
    stop
end

break YAML parse error
    fs --> loader : valid YAML
    loader -> loader : validate schema
    loader --> agent : PluginSkipped(manifest_path, reason="invalid YAML")
    deactivate loader
    agent --> router : AgentEvent(Done)
    stop
end

fs --> loader : raw YAML content
deactivate fs

loader -> loader : parse metadata (name, version, tools, hooks)

loader --> agent : PluginManifest
deactivate loader

agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    PLG-02 AgentOrchestrator -> PluginLoader -> read manifest.yaml -> parse metadata -> return PluginManifest
  State:   No state change
  Success: Validated PluginManifest returned
  Failure: File not found or malformed YAML -> plugin skipped
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg03_register_plugin_tools.puml ---

@startuml sq_plg03_register_plugin_tools
' ============================================================
' Title:     PLG-03 — Register Plugin Tools
' Boundary:  nasim code agent
' Purpose:   Register all tools declared in a plugin manifest
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "PluginLoader" as loader
  participant "ToolRegistry" as registry
end box

note over user, registry
  Scope:          Register plugin-declared tools into ToolRegistry
  Preconditions:  Valid PluginManifest loaded (PLG-02)
  Contexts:       Called during plugin enable (PLG-05)
  Excludes:       Hook registration, plugin activation
  Rollback:       Registration failure logged; other tools still registered
  Design:         Namespaced tool names to avoid collisions
  Classification: Process Decomposition
  Returns:        all tools registered or CollisionError with tool skipped
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== PLG-03 Register Plugin Tools ==

agent -> loader : PLG-03 REGISTER_PLUGIN_TOOLS(manifest)
activate loader

loader -> loader : enumerate tools from PluginManifest

loop for each tool in manifest
    loader -> registry : register(plugin::tool_name, handler)

    break Name collision
        registry --> loader : CollisionError
        loader --> loader : log warning, skip tool
    end

    registry --> loader : registered
end

loader --> agent : all tools registered
deactivate loader

agent --> router : AgentEvent(Done)

note over user, registry
  Flow:    PLG-03 AgentOrchestrator -> PluginLoader -> enumerate plugin tools -> register in ToolRegistry
  State:   Tools added to registry
  Success: All plugin tools registered
  Failure: Name collision -> tool skipped with warning
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg05_enable_plugin.puml ---

@startuml sq_plg05_enable_plugin
' ============================================================
' Title:     PLG-05 — Enable Plugin
' Boundary:  nasim code agent
' Purpose:   Load plugin and activate its tools and hooks
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "PluginLoader" as loader
  participant "ToolRegistry" as registry
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hm
end box

note over user, hm
  Scope:          Load plugin, register tools and hooks, set state ENABLED
  Preconditions:  Valid PluginManifest loaded (PLG-02)
  Contexts:       Called by CLI or PluginLoader
  Excludes:       Plugin discovery, disable
  Rollback:       Partial enable logged; state set to ERROR
  Design:         Atomic enable: tools + hooks + state
  Classification: Process Decomposition
  Returns:        plugin enabled or state ERROR with partial enable logged
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== PLG-05 Enable Plugin ==

agent -> loader : PLG-05 ENABLE_PLUGIN(plugin_id)
activate loader

loader -> loader : PLG-03 register_plugin_tools()
loader -> loader : PLG-04 register_plugin_hooks()
loader -> loader : set state ENABLED

break Tool or hook registration fails
    loader -> loader : set state ERROR, log failure
end

loader --> agent : plugin enabled
deactivate loader

agent --> router : AgentEvent(Done)

note over user, hm
  Flow:    PLG-05 AgentOrchestrator -> PluginLoader -> load plugin -> activate tools + hooks -> set state ENABLED
  State:   Plugin state: DISABLED -> ENABLED (or ERROR)
  Success: Plugin enabled with tools and hooks active
  Failure: Registration failure -> state ERROR, partial enable logged
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/PLG/sq_plg01_discover_plugins.puml ---

@startuml sq_plg01_discover_plugins
' ============================================================
' Title:     PLG-01 — DISCOVER Plugins
' Boundary:  nasim code agent
' Purpose:   Discover plugins from plugin directory
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Plugins Group" #EDE7F6
  participant "PluginLoader" as loader
end box
participant "Host Filesystem" as fs

note over user, fs
  Scope:          Discover plugins from plugin directory
  Preconditions:  Plugin directory configured (~/.nasim/plugins/)
  Contexts:       Called during agent initialization
  Excludes:       Tool/hook registration (PLG-03/04), activation (PLG-05)
  Rollback:       Malformed plugins skipped with warning
  Design:         Scan plugin directory for manifest.yaml files
  Classification: Process Decomposition
  Returns:        list[PluginManifest] or empty list on failure
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== PLG-01 DISCOVER Plugins ==

agent -> loader : PLG-01 DISCOVER(plugin_dir)
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

agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    PLG-01 AgentOrchestrator -> PluginLoader -> scan directory -> load manifests -> return list
  State:   <back:#ECEFF1>DISCOVERED</back>
  Success: List of discovered PluginManifests returned
  Failure: Malformed plugin skipped with warning
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SAF/sq_saf01_check_permission.puml ---

@startuml sq_saf01_check_permission
' ============================================================
' Title:     SAF-01 — CHECK Permission
' Boundary:  nasim code agent
' Purpose:   Per-tool safety check before execution (internal step of AGT-15)
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    Prompt audit 2026-06-21 (gro.md: God Object residual fixed)
' Note:      Process decomposition — internal step of AGT-15
' ============================================================

title nasim — SAF-01 READ Permission

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Safety Group" #FFF9C4
  participant "PermissionGate" as gate
  participant "SafetyCoordinator" as safety
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
end box
box "Repository Group" #E8F5E9
  participant "PolicyRepository" as policy_repo
end box

note over user, registry
  Scope:          SAF-01 CHECK Permission — check tool permission before execution
  Preconditions:  Tool call received from LLM, SafetyCoordinator initialized
  Contexts:       Called by AGT-15 (DISPATCH Safety Pipeline)
  Excludes:       User approval prompt (SAF-02), injection/egress checks
  Rollback:       Rejected -> SafetyViolation returned to caller
  Design:         SafetyCoordinator delegates to PermissionGate for safe-flag check
  Classification: Process Decomposition
  Returns:
    - Success: SafetyPassed
    - Failure: SafetyViolation(permission_denied)
end note

== SAF-01 CHECK Permission ==

user -> router : types input
router -> agent : SAF-01 PROCESS(user_input)

agent -> safety : SAF-01 CHECK Permission(tool_name, safety_mode)
activate safety

safety -> gate : SAF-01 CHECK Permission(tool_name, safety_mode)
activate gate

gate -> registry : SAF-01 READ Tool(tool_name)
activate registry
registry --> gate : Tool(safe=True/False)
deactivate registry

gate -> gate : SAF-01 VALIDATE ToolSafety(tool.safe, safety_mode)

alt tool.safe = True
    gate --> safety : SafetyPassed
else tool.safe = False AND safety_mode = "auto"
    gate --> safety : SafetyPassed
else tool.safe = False AND safety_mode = "ask"
    gate --> safety : SafetyViolation(permission_denied)
    safety --> agent : SafetyViolation(permission_denied)
    agent --> router : AgentEvent(Error)
else safety_mode = "off"
    gate --> safety : SafetyPassed
end

deactivate gate

safety --> agent : SafetyPassed
deactivate safety

agent --> router : AgentEvent(Done)

note over user, registry
  Flow:    SAF-01 -> User -> ServerRouter -> AgentOrchestrator -> SafetyCoordinator -> PermissionGate -> ToolRegistry.READ -> check safe flag -> return
  State:   No state change (delegated by AGT-15)
  Success: SafetyPassed — proceed to next pipeline stage
  Failure: SafetyViolation(permission_denied) — propagate back through entry chain
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SAF/sq_saf03_apply_safety_mode.puml ---

@startuml sq_saf03_apply_safety_mode
' ============================================================
' Title:     SAF-03 — Apply Safety Mode
' Boundary:  nasim code agent CLI
' Purpose:   Configure safety mode from config
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

title nasim — SAF-03 UPDATE Safety Mode

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PermissionGate" as gate
end box
box "Config Group" #E0F7FA
  participant "ConfigLoader" as cfg
end box
box "Repository Group" #E8F5E9
  participant "PolicyRepository" as policy_repo
end box

note over user, cfg
  Scope:          SAF-03 APPLY SafetyMode — apply safety mode from config to PermissionGate
  Preconditions:  Config loaded with safety_mode field
  Contexts:       Called during AgentOrchestrator initialization
  Excludes:       Runtime permission checks (SAF-01)
  Rollback:       N/A — mode is always set
  Design:         ask | auto | off — set once at startup
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={safety_mode})
    - Failure: N/A
end note

== SAF-03 Apply Safety Mode ==

user -> router : types input
router -> agent : SAF-03 PROCESS(user_input)

agent -> cfg : SAF-03 READ SafetyModeConfig()
activate cfg
cfg --> agent : config.safety_mode
deactivate cfg

agent -> gate : SAF-03 APPLY SafetyMode(config.safety_mode)
gate -> gate : SAF-03 SET self.mode(config.safety_mode)

gate --> agent : Result(success=true, data={safety_mode})

agent --> router : AgentEvent(Done)

note over user, cfg
  Flow:    SAF-03 -> User -> ServerRouter -> AgentOrchestrator -> ConfigLoader -> PermissionGate -> set mode
  State:   No state change
  Success: Result(success=true, data={safety_mode})
  Failure: N/A
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/SAF/sq_saf02_prompt_user_approval.puml ---

@startuml sq_saf02_prompt_user_approval
' ============================================================
' Title:     SAF-02 — Prompt User Approval
' Boundary:  nasim code agent CLI
' Purpose:   Display approval prompt for unsafe tool execution
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

title nasim — SAF-02 PROMPT User Approval

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
  participant "Renderer" as renderer
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PermissionGate" as gate
end box
box "Repository Group" #E8F5E9
  participant "PolicyRepository" as policy_repo
end box

note over user, gate
  Scope:          SAF-02 PROMPT User Approval — prompt user for approval of unsafe tool
  Preconditions:  safety_mode=ask AND tool.safe=False
  Contexts:       Called by SAF-01 (CHECK Tool Permission)
  Excludes:       Permission check logic (SAF-01)
  Rollback:       User rejects -> tool skipped
  Design:         Shows tool name + args, prompts [y/N]
  Classification: Primary Orchestrator
  Returns:
    - Success: approved (bool)
    - Failure: rejected (bool)
end note

== SAF-02 Prompt User Approval ==

user -> router : types input
router -> agent : SAF-02 PROCESS(user_input)

agent -> gate : SAF-02 PROMPT UserApproval(tool_name, args)
activate gate

gate -> renderer : SAF-02 DISPLAY Approval(tool_name, args)
activate renderer
renderer --> user : "Allow <tool_name>(<args>)? [y/N]"

user -> renderer : y or N
renderer --> gate : choice (bool)

alt user = y
    renderer --> gate : approved
    gate --> agent : approved
    agent --> router : AgentEvent(Done)
else user = N
    renderer --> gate : rejected
    gate --> agent : rejected
    agent --> router : AgentEvent(Done)
end

deactivate gate
deactivate renderer

note over user, gate
  Flow:    SAF-02 -> User -> ServerRouter -> AgentOrchestrator -> PermissionGate -> Renderer -> user prompt -> choice -> gate
  State:   <back:#F3E5F5>TOOL_EXEC</back> -> <back:#FFF9C4>AWAITING_APPROVAL</back> -> <back:#F3E5F5>TOOL_EXEC</back> or <back:#ECEFF1>IDLE</back>
  Success: approved — tool executes
  Failure: rejected — tool skipped
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MEM/sq_mem03_search_knowledge.puml ---

@startuml sq_mem03_search_knowledge
' ============================================================
' Title:     MEM-03 — SEARCH Knowledge
' Boundary:  nasim code agent
' Purpose:   Full-text search across knowledge store
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Memory Group" #E0F2F1
  participant "MemoryIndex" as index
end box

note over user, index
  Scope:          Full-text search across all knowledge
  Preconditions:  MemoryIndex populated with entries
  Contexts:       Called by TL-20 (RECALL Memory), cross-project discovery
  Excludes:       Direct key recall (MEM-02)
  Rollback:       No rollback needed (read-only operation)
  Design:         BM25 ranking with relevance scoring
  Classification: Process Decomposition
  Returns:        ranked_results[] or empty list
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== MEM-03 SEARCH Knowledge ==

agent -> index : MEM-03 SEARCH(query, filters)
activate index

index -> index : tokenize query
index -> index : FTS5 virtual table query (memory_fts) with BM25 ranking
index -> index : rank results by relevance score
index -> index : apply scope filters (global/project/session)

break No results found
    index --> agent : empty list
end

index --> agent : ranked_results
deactivate index

agent --> router : AgentEvent(Done)

note over user, index
  Flow:    MEM-03 AgentOrchestrator -> MemoryIndex -> tokenize -> FTS5 query -> rank -> return
  State:   No state change
  Success: Agent receives ranked search results
  Failure: No results -> return empty list, log query
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MEM/sq_mem01_persist_knowledge.puml ---

@startuml sq_mem01_persist_knowledge
' ============================================================
' Title:     MEM-01 — PERSIST Knowledge
' Boundary:  nasim code agent
' Purpose:   Store cross-session knowledge entries
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Memory Group" #E0F2F1
  participant "MemoryStore" as store
  participant "MemoryScope" as scope
  participant "MemoryIndex" as index
end box

note over user, index
  Scope:          Store cross-session knowledge entries
  Preconditions:  MemoryStore initialized, scope valid
  Contexts:       Called by TL-19 (PERSIST Memory), session checkpoint
  Excludes:       Search and recall (MEM-02, MEM-03)
  Rollback:       Transactional write with rollback on index failure
  Design:         Append-only store with index synchronization
  Classification: Process Decomposition
  Returns:        persist_confirmed(key) or PersistError("write failed")
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== MEM-01 PERSIST Knowledge ==

agent -> store : MEM-01 PERSIST(key, value, scope)
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

agent --> router : AgentEvent(Done)

note over user, index
  Flow:    MEM-01 AgentOrchestrator -> MemoryStore -> validate scope -> write disk -> index -> confirm
  State:   No state change
  Success: Entry persisted and indexed for search
  Failure: Disk write fails -> rollback, no index update
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MEM/sq_mem04_scope_knowledge.puml ---

@startuml sq_mem04_scope_knowledge
' ============================================================
' Title:     MEM-04 — SCOPE Knowledge
' Boundary:  nasim code agent
' Purpose:   Filter knowledge by scope (global, project, session)
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Memory Group" #E0F2F1
  participant "MemoryScope" as scope
  participant "MemoryStore" as store
end box

note over user, store
  Scope:          Scope-based filtering of knowledge entries
  Preconditions:  MemoryStore with multi-scope entries
  Contexts:       Called by MEM-01 and MEM-02 for scope validation
  Excludes:       Search and recall (MEM-02, MEM-03)
  Rollback:       No rollback needed (read-only operation)
  Design:         Three-level scope hierarchy: global > project > session
  Classification: Process Decomposition
  Returns:        scoped_entries[] or global scope entries (fallback)
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== MEM-04 SCOPE Knowledge ==

agent -> scope : MEM-04 FILTER(query, scope)
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

agent --> router : AgentEvent(Done)

note over user, store
  Flow:    MEM-04 AgentOrchestrator -> MemoryScope -> resolve hierarchy -> fetch entries -> apply mask -> return
  State:   No state change
  Success: Agent receives scope-filtered entries
  Failure: Invalid scope -> return global scope entries
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/MEM/sq_mem02_recall_knowledge.puml ---

@startuml sq_mem02_recall_knowledge
' ============================================================
' Title:     MEM-02 — RECALL Knowledge
' Boundary:  nasim code agent
' Purpose:   Retrieve previously stored knowledge
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Memory Group" #E0F2F1
  participant "MemoryStore" as store
  participant "MemoryScope" as scope
  participant "MemoryIndex" as index
end box

note over user, index
  Scope:          Knowledge retrieval by key or pattern
  Preconditions:  Knowledge entries exist in store
  Contexts:       Called by TL-20 (RECALL Memory), session rebuild
  Excludes:       Full-text search (MEM-03), scope filtering (MEM-04)
  Rollback:       No rollback needed (read-only operation)
  Design:         Key-based lookup with scope filtering
  Classification: Process Decomposition
  Returns:        recalled_entry or null (key not found)
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== MEM-02 RECALL Knowledge ==

agent -> store : MEM-02 RECALL(key, scope)
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

agent --> router : AgentEvent(Done)

note over user, index
  Flow:    MEM-02 AgentOrchestrator -> MemoryStore -> filter by scope -> lookup key -> return entry
  State:   No state change
  Success: Agent receives knowledge entry
  Failure: Key not found -> return null, log miss
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/VCS/sq_vcs03_read_diff.puml ---

@startuml sq_vcs03_read_diff
' ============================================================
' Title:     VCS-03 — READ Diff
' Boundary:  nasim code agent
' Purpose:   Read diff of staged or unstaged changes
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — VCS-03 READ Diff

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Git Group" #E8EAF6
  participant "GitStatus" as status
end box
box "External" #F5F5F5
  participant "Git Repository" as git
end box

note over user, git
  Scope:          VCS-03 READ Diff — diff inspection for staged/unstaged changes
  Preconditions:  Git repository with changes
  Contexts:       Pre-commit review, change inspection
  Excludes:       Commit operations (VCS-02)
  Rollback:       No rollback needed (read-only operation)
  Design:         Unified diff format with context lines
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={files, hunks})
    - Failure: Result(success=false, error="no_changes")
end note

== VCS-03 READ Diff ==

user -> router : types input
router -> agent : VCS-03 PROCESS(user_input)

agent -> status : VCS-03 READ Diff(scope)
activate status

status -> git : VCS-03 EXECUTE git_diff(scope)
activate git
git --> status : raw_diff
deactivate git

status -> status : VCS-03 PARSE DiffOutput(raw_diff)

break No changes detected
    status --> agent : Result(success=true, data={empty_diff})
    agent --> router : AgentEvent(Done)
end

status --> agent : Result(success=true, data={files, hunks})
deactivate status

agent --> router : AgentEvent(Done)

note over user, git
  Flow:    VCS-03 -> User -> ServerRouter -> AgentOrchestrator -> GitStatus -> determine scope -> execute git diff -> parse -> return
  State:   No state change
  Success: Result(success=true, data={files, hunks})
  Failure: Result(success=false, error="no_changes") — return empty diff
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/VCS/sq_vcs02_insert_commit.puml ---

@startuml sq_vcs02_insert_commit
' ============================================================
' Title:     VCS-02 — INSERT Commit
' Boundary:  nasim code agent
' Purpose:   Create a commit with conventional message
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — VCS-02 INSERT Commit

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Git Group" #E8EAF6
  participant "GitCommit" as commit
  participant "GitStatus" as status
end box
box "External" #F5F5F5
  participant "Git Repository" as git
end box

note over user, git
  Scope:          VCS-02 INSERT Commit — git commit creation with conventional format
  Preconditions:  Files staged, commit message valid
  Contexts:       Called by VCS-04 (AUTO-COMMIT), manual commit requests
  Excludes:       Status checking (VCS-01), diff (VCS-03)
  Rollback:       Reset HEAD if commit fails mid-operation
  Design:         Atomic commit with pre-commit hook validation
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={hash, files})
    - Failure: Result(success=false, error="no_staged_files")
    - Failure: Result(success=false, error="invalid_commit_message")
end note

== VCS-02 INSERT Commit ==

user -> router : types input
router -> agent : VCS-02 PROCESS(user_input)

agent -> commit : VCS-02 INSERT Commit(message, files)
activate commit

commit -> status : VCS-02 READ StagedFiles()
activate status
status --> commit : staged_files
deactivate status

break No staged files
    commit --> agent : Result(success=false, error="no_staged_files")
    agent --> router : AgentEvent(Error)
end

commit -> commit : VCS-02 VALIDATE Message(message)

break Invalid message format
    commit --> agent : Result(success=false, error="invalid_commit_message")
    agent --> router : AgentEvent(Error)
end

commit -> git : VCS-02 EXECUTE git_commit(message)
activate git
git --> commit : commit_output
deactivate git

commit --> agent : Result(success=true, data={hash, files})
deactivate commit

agent --> router : AgentEvent(Done)

note over user, git
  Flow:    VCS-02 -> User -> ServerRouter -> AgentOrchestrator -> GitCommit -> check staged -> validate message -> commit -> return hash
  State:   No state change
  Success: Result(success=true, data={hash, files})
  Failure: Result(success=false, error="no_staged_files") or Result(success=false, error="invalid_commit_message") — abort, return error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/VCS/sq_vcs01_read_git_status.puml ---

@startuml sq_vcs01_read_git_status
' ============================================================
' Title:     VCS-01 — READ Git Status
' Boundary:  nasim code agent
' Purpose:   Read working tree status and staged changes
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — VCS-01 READ Git Status

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Git Group" #E8EAF6
  participant "GitStatus" as status
end box
box "External" #F5F5F5
  participant "Git Repository" as git
end box

note over user, git
  Scope:          VCS-01 READ GitStatus — git working tree status inspection
  Preconditions:  Git repository initialized
  Contexts:       Called by TL-11 (READ Git Status), pre-commit validation
  Excludes:       Commit operations (VCS-02), diff (VCS-03)
  Rollback:       No rollback needed (read-only operation)
  Design:         Cached status with file system watch invalidation
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={staged, modified, untracked})
    - Failure: Result(success=false, error="not_a_git_repository")
end note

== VCS-01 READ Git Status ==

user -> router : types input
router -> agent : VCS-01 PROCESS(user_input)

agent -> status : VCS-01 READ GitStatus()
activate status

status -> git : VCS-01 EXECUTE git_status_porouslain()
activate git
git --> status : raw_output
deactivate git

status -> status : VCS-01 PARSE StatusOutput(raw_output)

break Not a git repo
    status --> agent : Result(success=false, error="not_a_git_repository")
    agent --> router : AgentEvent(Error)
end

status --> agent : Result(success=true, data={staged, modified, untracked})
deactivate status

agent --> router : AgentEvent(Done)

note over user, git
  Flow:    VCS-01 -> User -> ServerRouter -> AgentOrchestrator -> GitStatus -> execute git status -> parse -> return summary
  State:   No state change
  Success: Result(success=true, data={staged, modified, untracked})
  Failure: Result(success=false, error="not_a_git_repository") — return error status
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/VCS/sq_vcs04_auto_commit.puml ---

@startuml sq_vcs04_auto_commit
' ============================================================
' Title:     VCS-04 — AUTO-COMMIT
' Boundary:  nasim code agent
' Purpose:   Automatically commit changes after edit operations
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — VCS-04 AUTO-COMMIT

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Git Group" #E8EAF6
  participant "GitIntegration" as integration
  participant "GitStatus" as status
  participant "GitCommit" as commit
end box
box "Repository Group" #E8F5E9
  participant "GitRepository" as git_repo
end box

note over user, commit
  Scope:          VCS-04 AUTO-COMMIT — automatic commit after file edits
  Preconditions:  File edits completed, working tree dirty
  Contexts:       Post-edit hook, batch operation cleanup
  Excludes:       Manual commit (VCS-02)
  Rollback:       Skip commit if no changes detected
  Design:         Debounced auto-commit with conventional message generation
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={hash})
    - Failure: Result(success=false, error="no_changes") — noop
end note

== VCS-04 AUTO-COMMIT ==

user -> router : types input
router -> agent : VCS-04 PROCESS(user_input)

agent -> integration : VCS-04 AUTO-COMMIT(edit_context)
activate integration

integration -> status : VCS-04 READ DirtyStatus()
activate status
status --> integration : is_dirty
deactivate status

break No changes detected
    integration --> agent : Result(success=false, error="no_changes")
    agent --> router : AgentEvent(Done)
end

integration -> commit : VCS-04 INSERT Commit(generated_message, files)
activate commit
commit --> integration : Result(success=true, data={hash})
deactivate commit

integration --> agent : Result(success=true, data={hash})
deactivate integration

agent --> router : AgentEvent(Done)

note over user, commit
  Flow:    VCS-04 -> User -> ServerRouter -> AgentOrchestrator -> GitIntegration -> check dirty -> generate message -> commit -> return
  State:   No state change
  Success: Result(success=true, data={hash})
  Failure: Result(success=false, error="no_changes") — skip commit, return noop
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl07_record_quality_signal.puml ---

@startuml sq_evl07_record_quality_signal
' ============================================================
' Title:     EVL-07 — RECORD Quality Signal
' Boundary:  nasim code agent
' Purpose:   Record accept/reject quality signal with feedback
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #F9FBE7
  participant "EvaluationEngine" as engine
  participant "QualitySignal" as signal
end box
box "Storage Group" #F3E5F5
  participant "SignalStore" as store
end box

note over user, store
  Scope:          Record accept/reject quality signal with feedback for future reference
  Preconditions:  Evaluation completed, decision made (accept or reject)
  Contexts:       Called after EVL-01..06 evaluation completes
  Excludes:       Evaluation logic, retry coordination
  Rollback:       Storage failure -> signal lost, warning logged
  Design:         QualitySignal persists accept/reject decision with contextual feedback
  Classification: Process Decomposition
  Returns:        SignalRecorded(signal_id)
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-07 RECORD Quality Signal ==

agent -> engine : EVL-07 RECORD_SIGNAL(task_id, decision, feedback?)
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

agent --> router : AgentEvent(Done)

note over user, store
  Flow:    EVL-07 AgentOrchestrator -> EvaluationEngine -> QualitySignal -> record accept/reject + feedback
  State:   <back:#ECEFF1>IDLE</back> → RECORDING → PERSISTED → DONE
  Success: SignalRecorded with signal_id for future reference
  Failure: Storage failure -> signal lost, warning logged
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl04_validate_with_llm.puml ---

@startuml sq_evl04_validate_with_llm
' ============================================================
' Title:     EVL-04 — Validate With LLM
' Boundary:  nasim code agent CLI
' Purpose:   LLM-as-judge scoring for edit quality
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #FFF3E0
  participant "LLMReviewer" as reviewer
end box
box "Provider Group" #E3F2FD
  participant "Provider" as provider
end box
box "Edit Group" #FFF3E0
  participant "FileSystem" as fs
end box

note over user, fs
  Scope:          LLM-as-judge scoring for edit quality
  Preconditions:  Edit applied to file system, Provider available, review prompt template configured
  Contexts:       Called after EVL-01 (Run Success Checks) as complementary evaluation; provides semantic quality assessment beyond exit codes
  Excludes:       Shell-based checks (handled by EVL-01), retry coordination (handled by EVL-06)
  Rollback:       LLM call failure -> skip review, proceed with exit code results only
  Design:         LLMReviewer sends original + edited file to Provider; prompt asks for quality score (1-10) and feedback; score below threshold triggers retry via EVL-06; review is non-blocking
  Classification: Primary Orchestrator
  Returns:        ReviewResult(score, feedback, passed) or ReviewResult(skip=true) on failure
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-04 Validate With LLM ==

agent -> reviewer : EVL-04 REVIEW_EDIT(original_file, edited_file)
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

agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    EVL-04 AgentOrchestrator -> LLMReviewer -> FileSystem + Provider -> ReviewResult
  State:   <back:#ECEFF1>IDLE</back> → READING → PROMPTING → SCORING → DONE
  Success: ReviewResult with score and feedback
  Failure: LLM call failure -> skip review; Parse failure -> skip review
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl03_check_success.puml ---

@startuml sq_evl03_check_success
' ============================================================
' Title:     EVL-03 — CHECK Success
' Boundary:  nasim code agent
' Purpose:   Run user-defined success checks and return pass/fail
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #F9FBE7
  participant "EvaluationEngine" as engine
  participant "SuccessCheckRunner" as runner
end box
box "Tool Group" #F3E5F5
  participant "ShellRunner" as shell
end box
box "Repository Group" #E8F5E9
  participant "EvaluationRepository" as eval_repo
end box

note over user, shell
  Scope:          Run user-defined success checks and aggregate pass/fail
  Preconditions:  Success check commands configured, shell environment available
  Contexts:       EVL-01 EVALUATE Task delegates success checks here
  Excludes:       Task completion evaluation (EVL-02), retry coordination (EVL-06)
  Rollback:       No state change — read-only execution
  Design:         SuccessCheckRunner executes each check, captures exit codes and output
  Classification: Process Decomposition
  Returns:        SuccessCheckResult(passed, results[])
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-03 CHECK Success ==

agent -> engine : EVL-03 CHECK_SUCCESS(check_commands[])
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

agent --> router : AgentEvent(Done)

note over user, shell
  Flow:    EVL-03 AgentOrchestrator -> EvaluationEngine -> SuccessCheckRunner -> run user-defined checks -> return pass/fail
  State:   <back:#ECEFF1>IDLE</back> → RUNNING → AGGREGATING → DONE
  Success: All checks pass → SuccessCheckResult(passed=true)
  Failure: Any check fails → SuccessCheckResult(passed=false)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl09_inject_turn_budget.puml ---

@startuml sq_evl09_inject_turn_budget
' ============================================================
' Title:     EVL-09 — Inject Turn Budget
' Boundary:  nasim code agent CLI
' Purpose:   Turn budget injection per-turn
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #FFF3E0
  participant "TurnBudgetInjector" as injector
  participant "TurnBudget" as budget
end box
box "Context Group" #E8F5E9
  participant "ConversationHistory" as history
end box
box "Repository Group" #E8F5E9
  participant "EvaluationRepository" as eval_repo
end box

note over user, history
  Scope:          Turn budget injection per-turn
  Preconditions:  TurnBudget initialized with max_turns, ConversationHistory tracks turn count
  Contexts:       Called at start of each agentic turn; injects budget status into context for LLM awareness
  Excludes:       Repetition detection (handled by EVL-08), edit evaluation (handled by EVL-01/02)
  Rollback:       Budget exceeded -> force task completion
  Design:         TurnBudgetInjector computes remaining budget; injects formatted status into system message; warns when budget drops below threshold (20%); forces completion at zero budget
  Classification: Primary Orchestrator
  Returns:        BudgetStatus(remaining, warning, continue=true) or BudgetExhausted(current_turn, max_turns)
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-09 INJECT Turn Budget ==

agent -> injector : EVL-09 INJECT_BUDGET(current_turn)
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

agent --> router : AgentEvent(Done)

note over user, history
  Flow:    EVL-09 AgentOrchestrator -> TurnBudgetInjector -> TurnBudget + ConversationHistory -> BudgetStatus
  State:   <back:#ECEFF1>IDLE</back> → COMPUTING → CHECKING → INJECTING → DONE
  Success: BudgetStatus with remaining turns
  Failure: Budget exhausted -> BudgetExhausted error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl06_coordinate_retry.puml ---

@startuml sq_evl06_coordinate_retry
' ============================================================
' Title:     EVL-06 — Coordinate Retry
' Boundary:  nasim code agent CLI
' Purpose:   Retry with feedback on failure
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #FFF3E0
  participant "RetryCoordinator" as retry
  participant "FeedbackInjector" as feedback
  participant "TurnBudgetInjector" as budget
end box
box "Sandbox Group" #F1F8E9
  participant "FileSystem" as fs
end box

note over user, fs
  Scope:          Retry with feedback on failure
  Preconditions:  EVL-01 or EVL-02 identified failure, backup file available for revert, turn budget not exhausted
  Contexts:       Called after evaluation failure (EVL-01 or EVL-02); triggers new EDT cycle with injected feedback
  Excludes:       Evaluation logic (handled by EVL-01/02), turn budget management (handled by EVL-09)
  Rollback:       Max retries exceeded -> abort, report to user; turn budget exhausted -> abort, report to user
  Design:         RetryCoordinator manages retry count and limits; FeedbackInjector formats failure details for next LLM call; backup restored before retry attempt; max 3 retries per edit before escalating
  Classification: Primary Orchestrator
  Returns:        RetryResult(retry_count, feedback_context, continue=true) or RetryExhausted(retry_count, final_error)
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-06 COORDINATE Retry ==

agent -> retry : EVL-06 COORDINATE_RETRY(edit_result, check_result, review_result)
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

agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    EVL-06 AgentOrchestrator -> RetryCoordinator -> FileSystem + FeedbackInjector -> RetryResult
  State:   <back:#ECEFF1>IDLE</back> → CHECKING_LIMIT → RESTORING → INJECTING → DONE
  Success: RetryResult with feedback for next attempt
  Failure: Max retries exceeded -> RetryExhausted error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl08_detect_repetition.puml ---

@startuml sq_evl08_detect_repetition
' ============================================================
' Title:     EVL-08 — DETECT Repetition
' Boundary:  nasim code agent
' Purpose:   Tool-call loop detection
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #FFF3E0
  participant "RepetitionDetector" as detector
  participant "ToolCallHistory" as history
end box
box "Repository Group" #E8F5E9
  participant "EvaluationRepository" as eval_repo
end box

note over user, history
  Scope:          Detect tool-call loops and repeated patterns
  Preconditions:  Tool call history available, RepetitionDetector initialized
  Contexts:       Called on each tool dispatch to detect loops
  Excludes:       Turn budget management (EVL-09), edit evaluation (EVL-01/02)
  Rollback:       Loop detected -> force abort, notify agent
  Design:         RepetitionDetector tracks tool call patterns; detects same tool+args repeated N times, oscillating patterns; configurable window and threshold
  Classification: Process Decomposition
  Returns:        LoopDetected(pattern, repeat_count) or RepetitionResult(detected=false, confidence)
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-08 DETECT Repetition ==

agent -> detector : EVL-08 CHECK_REPETITION(tool_call, call_history)
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

agent --> router : AgentEvent(Done)

note over user, history
  Flow:    EVL-08 AgentOrchestrator -> RepetitionDetector -> ToolCallHistory -> RepetitionResult
  State:   No state change
  Success: RepetitionResult with detected=false
  Failure: Loop detected -> LoopDetected error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl05_validate_test_suite.puml ---

@startuml sq_evl05_validate_test_suite
' ============================================================
' Title:     EVL-05 — VALIDATE Test Suite
' Boundary:  nasim code agent
' Purpose:   Run test suite and collect pass/fail/skip results
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #F9FBE7
  participant "EvaluationEngine" as engine
  participant "TestRunner" as runner
end box
box "Tool Group" #F3E5F5
  participant "ShellRunner" as shell
end box
box "Repository Group" #E8F5E9
  participant "EvaluationRepository" as eval_repo
end box

note over user, shell
  Scope:          Execute test suite and collect structured results
  Preconditions:  Test framework configured, test files present
  Contexts:       EVL-01 EVALUATE Task delegates test validation here
  Excludes:       LLM-based review, quality signal recording
  Rollback:       No state change — read-only execution
  Design:         TestRunner invokes configured test framework, parses output into structured results
  Classification: Process Decomposition
  Returns:        TestSuiteResult(total, passed, failed, skipped, errors[])
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-05 VALIDATE Test Suite ==

agent -> engine : EVL-05 VALIDATE_TEST_SUITE(test_command, project_path)
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

agent --> router : AgentEvent(Done)

note over user, shell
  Flow:    EVL-05 AgentOrchestrator -> EvaluationEngine -> TestRunner -> run test suite -> collect results -> return
  State:   <back:#ECEFF1>IDLE</back> → RUNNING → PARSING → DONE
  Success: TestSuiteResult with counts and failure details
  Failure: Test framework error -> TestSuiteResult with error details
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl02_check_task_completion.puml ---

@startuml sq_evl02_check_task_completion
' ============================================================
' Title:     EVL-02 — CHECK Task Completion
' Boundary:  nasim code agent
' Purpose:   Evaluate task completion against defined criteria
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #F9FBE7
  participant "EvaluationEngine" as engine
  participant "TaskEvaluator" as evaluator
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as tool
end box
box "Repository Group" #E8F5E9
  participant "EvaluationRepository" as eval_repo
end box

note over user, tool
  Scope:          Check whether a task meets its completion criteria
  Preconditions:  Task defined with acceptance criteria, tool results available
  Contexts:       EVL-01 EVALUATE Task delegates completion check here
  Excludes:       Success check execution (EVL-03), retry coordination (EVL-06)
  Rollback:       No state change — read-only evaluation
  Design:         TaskEvaluator compares tool outputs against criteria predicates
  Classification: Process Decomposition
  Returns:        CompletionStatus(completed, details[])
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-02 CHECK Task Completion ==

agent -> engine : EVL-02 CHECK_TASK_COMPLETION(task_id, criteria[])
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

agent --> router : AgentEvent(Done)

note over user, tool
  Flow:    EVL-02 AgentOrchestrator -> EvaluationEngine -> TaskEvaluator -> evaluate against criteria -> return completion status
  State:   <back:#ECEFF1>IDLE</back> → <back:#F9FBE7>EVALUATING</back> → AGGREGATING → DONE
  Success: CompletionStatus with per-criterion pass/fail
  Failure: No state change on evaluation failure — returns partial status
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EVL/sq_evl01_evaluate_task.puml ---

@startuml sq_evl01_evaluate_task
' ============================================================
' Title:     EVL-01 — EVALUATE Task
' Boundary:  nasim code agent
' Purpose:   Evaluate task completion via success checks and quality signals
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Evaluation Group" #FFF3E0
  participant "SuccessChecker" as checker
  participant "ShellRunner" as shell
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as tool
end box

note over user, tool
  Scope:          Evaluate task completion via success checks and quality signals
  Preconditions:  EDT-05 completed (edit applied and user-approved), shell environment available
  Contexts:       Called after edit application to verify correctness; feeds into EVL-06 (COORDINATE Retry) on failure
  Excludes:       LLM-based review (EVL-04), repetition detection (EVL-08)
  Rollback:       Check failure -> report to EVL-06 for retry coordination
  Design:         SuccessChecker runs configured check commands with timeout; aggregate pass/fail across all checks
  Classification: Primary Orchestrator
  Returns:        CheckResult(passed, results[])
end note

user -> router : types input
router -> agent : PROCESS(user_input)

== EVL-01 EVALUATE Task ==

agent -> checker : EVL-01 RUN_CHECKS(file_path, check_commands[])
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

agent --> router : AgentEvent(Done)

note over user, tool
  Flow:    EVL-01 AgentOrchestrator -> SuccessChecker -> [ShellRunner]* -> CheckResult
  State:   <back:#ECEFF1>IDLE</back> -> <back:#F9FBE7>EVALUATING</back> -> <back:#ECEFF1>IDLE</back>
  Success: All checks pass -> CheckResult(passed=true)
  Failure: Any check fails -> CheckResult(passed=false)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl19_persist_memory.puml ---

@startuml sq_tl19_persist_memory
' ============================================================
' Title:     TL-19 — Persist Memory
' Boundary:  nasim code agent
' Purpose:   Persist knowledge to memory via MemoryTool
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "MemoryTool" as tool
end box
participant "MemoryStore" as mem

note over user, mem
  Scope:          Persist a knowledge item to the memory store
  Preconditions:  MemoryTool initialized
  Excludes:       Memory recall, search, scoping
  Contexts:       Called by AGT-02 (DISPATCH Tool Call); delegates to MEM-01
  Rollback:       Error string returned to LLM
  Design:         Delegates to MEM-01 PERSIST Knowledge
  Classification: Process Decomposition
  Returns:        ToolResult(success=True) or ToolResult(success=False, error=str)
end note

== TL-19 Persist Memory ==

user -> router : types input
router -> agent : TL-19 PROCESS(user_input)
agent -> registry : TL-19 Persist Memory(key, value, scope)
registry -> tool : TL-19 Persist Memory(key, value, scope)
tool -> mem : MEM-01 persist(key, value, scope)

break Storage failure
    mem --> tool : StorageError
    tool --> registry : ToolResult(success=False, error="persist failed")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

mem --> tool : persisted
tool --> registry : ToolResult(success=True)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, mem
  Flow:    TL-19: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> MemoryTool -> MemoryStore -> ToolResult
  State:   Knowledge item stored
  Success: Knowledge persisted
  Failure: Storage failure -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl03_edit_file.puml ---

@startuml sq_tl03_edit_file
' ============================================================
' Title:     TL-03 — Edit File
' Boundary:  nasim code agent CLI
' Purpose:   Replace an exact string in a file
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
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
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content="Edited: replaced 1 occurrence") or ToolResult(success=False, error=str)
end note

== TL-03 EDIT File ==

user -> router : types input
router -> agent : TL-03 PROCESS(user_input)
agent -> registry : TL-03 EDIT File(path, old_string, new_string)
registry -> ft : TL-03 EDIT File(path, old_string, new_string)
ft -> fs : Path(path).read_text()

break File not found
    fs --> ft : FileNotFoundError
    ft --> registry : ToolResult(success=False, error="Error: file not found")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

ft -> ft : content.count(old_string)

alt count == 0
    ft --> registry : ToolResult(success=False, error="old_string not found")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
else count > 1
    ft --> registry : ToolResult(success=False, error="old_string found N times (ambiguous)")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
else count == 1
    ft -> ft : content.replace(old_string, new_string, 1)
    ft -> fs : Path(path).write_text(new_content)
    ft --> registry : ToolResult(success=True, content="Edited: replaced 1 occurrence")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Done)
end

note over user, fs
  Flow:    TL-03: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> EditFileTool -> Host Filesystem -> ToolResult
  State:   No state change
  Success: Single replacement written
  Failure: Not found or ambiguous -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl12_dispatch_mcp_extension.puml ---

@startuml sq_tl12_dispatch_mcp_extension
' ============================================================
' Title:     TL-12 — Dispatch MCP Extension
' Boundary:  nasim code agent CLI
' Purpose:   Invoke tools from MCP server extensions
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "MCPToolAdapter" as mcp
end box
participant "MCP Server" as server

note over user, server
  Scope:          Invoke MCP server extension tools
  Preconditions:  MCP server configured and running
  Excludes:       MCP server startup, tool discovery
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       MCP error returned as error string
  Design:         Wraps MCP tools as nasim Tool instances
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=result) or ToolResult(success=False, error=str)
end note

== TL-12 Dispatch MCP Extension ==

user -> router : types input
router -> agent : TL-12 PROCESS(user_input)
agent -> registry : TL-12 Dispatch MCP Extension(tool_name, args)
registry -> mcp : TL-12 Dispatch MCP Extension(tool_name, args)
mcp -> server : MCP call(tool_name, args) via stdio/SSE

break MCP server not running
    server --> mcp : ConnectionRefused
    mcp --> registry : ToolResult(success=False, error="Error: MCP server not reachable")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Tool not found on server
    server --> mcp : UnknownTool error
    mcp --> registry : ToolResult(success=False, error="Error: tool not found on MCP server")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

server --> mcp : result
mcp -> mcp : wrap in ToolResult(success=True, content=result)
mcp --> registry : ToolResult
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, server
  Flow:    TL-12: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> MCPToolAdapter -> MCP Server -> ToolResult
  State:   No state change
  Success: MCP tool result wrapped in ToolResult
  Failure: Server down, tool not found -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl10_search_web.puml ---

@startuml sq_tl10_search_web
' ============================================================
' Title:     TL-10 — SEARCH Web
' Boundary:  nasim code agent CLI
' Purpose:   Search the web for information
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "WebSearchTool" as search
end box
participant "Search Backend" as backend

note over user, backend
  Scope:          Web search with ranked results
  Preconditions:  Query provided by LLM
  Excludes:       URL fetching (TL-09)
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Backend error returned as error string
  Design:         Configurable backend: DuckDuckGo, Brave, SerpAPI
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=formatted_results) or ToolResult(success=False, error=str)
end note

== TL-10 SEARCH Web ==

user -> router : types input
router -> agent : TL-10 PROCESS(user_input)
agent -> registry : TL-10 SEARCH Web(query, num_results)
registry -> search : TL-10 SEARCH Web(query, num_results)
search -> backend : search(query, num_results)

break Backend unavailable
    backend --> search : ConnectionError
    search --> registry : ToolResult(success=False, error="Error: search backend unavailable")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

backend --> search : results [{title, url, snippet}, ...]
search -> search : format results
search --> registry : ToolResult(success=True, content=formatted_results)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, backend
  Flow:    TL-10: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> WebSearchTool -> Search Backend -> ToolResult
  State:   No state change
  Success: Ranked search results with titles, URLs, snippets
  Failure: Backend unavailable -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl21_insert_plan.puml ---

@startuml sq_tl21_insert_plan
' ============================================================
' Title:     TL-21 — Insert Plan
' Boundary:  nasim code agent
' Purpose:   Add a new plan step via PlanTool
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "PlanTool" as tool
end box

note over user, tool
  Scope:          Add a new step to the execution plan
  Preconditions:  PlanTool initialized
  Excludes:       Plan update, deletion, listing
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Auto-generates step ID; initial status PENDING
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, step_id=step_id) or ToolResult(success=False, error=str)
end note

== TL-21 Insert Plan ==

user -> router : types input
router -> agent : TL-21 PROCESS(user_input)
agent -> registry : TL-21 Insert Plan(description, dependencies?)
registry -> tool : TL-21 Insert Plan(description, dependencies)
tool -> tool : generate step ID, set status PENDING
tool --> registry : ToolResult(success=True, step_id)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, tool
  Flow:    TL-21: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> PlanTool -> ToolResult
  State:   New plan step created (PENDING)
  Success: Plan step ID returned
  Failure: Invalid input -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl22_update_plan.puml ---

@startuml sq_tl22_update_plan
' ============================================================
' Title:     TL-22 — Update Plan
' Boundary:  nasim code agent
' Purpose:   Update status or content of an existing plan step
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "PlanTool" as tool
end box

note over user, tool
  Scope:          Update status or content of a plan step by ID
  Preconditions:  Plan step exists with given ID
  Excludes:       Plan step creation, deletion, listing
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Validates status transitions
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, step=updated_step) or ToolResult(success=False, error=str)
end note

== TL-22 Update Plan ==

user -> router : types input
router -> agent : TL-22 PROCESS(user_input)
agent -> registry : TL-22 Update Plan(step_id, status, description)
registry -> tool : TL-22 Update Plan(step_id, status, description)

break Step not found
    tool --> registry : ToolResult(success=False, error="step not found")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Invalid status transition
    tool --> registry : ToolResult(success=False, error="invalid transition")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

tool -> tool : update fields
tool --> registry : ToolResult(success=True, step)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, tool
  Flow:    TL-22: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> PlanTool -> ToolResult
  State:   Plan step status/content updated
  Success: Updated plan step returned
  Failure: Step not found or invalid transition -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl05_dispatch_shell_command.puml ---

@startuml sq_tl05_dispatch_shell_command
' ============================================================
' Title:     TL-05 — Dispatch Shell Command
' Boundary:  nasim code agent CLI
' Purpose:   Shell command execution with timeout
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
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
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=command_output) or ToolResult(success=False, error=str)
end note

== TL-05 EXECUTE Shell Command ==

user -> router : types input
router -> agent : TL-05 PROCESS(user_input)
agent -> registry : TL-05 EXECUTE Shell Command(command, timeout)
registry -> st : TL-05 EXECUTE Shell Command(command, timeout)
st -> shell : subprocess.run(command, shell=True, timeout=timeout)

break Timeout
    shell --> st : TimeoutExpired
    st --> registry : ToolResult(success=False, error="command timed out after Ns")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Execution error
    shell --> st : Exception
    st --> registry : ToolResult(success=False, error="Error executing command")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

shell --> st : CompletedProcess(stdout, stderr, returncode)
st -> st : format output (stdout + stderr + exit code)
st --> registry : ToolResult(success=True, content=command_output)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, shell
  Flow:    TL-05: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> ShellTool -> Host Shell -> ToolResult
  State:   No state change
  Success: Command output (stdout + stderr)
  Failure: Timeout, execution error -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl08_find_files.puml ---

@startuml sq_tl08_find_files
' ============================================================
' Title:     TL-08 — Find Files
' Boundary:  nasim code agent CLI
' Purpose:   Find files by name pattern with depth limit
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "FindFileTool" as find
end box

note over user, find
  Scope:          Find files by name pattern with max depth
  Preconditions:  Name pattern and path provided by LLM
  Excludes:       Content search, glob patterns
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Uses os.walk with depth limit
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=matching_paths) or ToolResult(success=False, error=str)
end note

== TL-08 FIND Files ==

user -> router : types input
router -> agent : TL-08 PROCESS(user_input)
agent -> registry : TL-08 FIND Files(name_pattern, path, max_depth)
registry -> find : TL-08 FIND Files(name_pattern, path, max_depth)
find -> find : os.walk(path) with depth tracking
find -> find : fnmatch.fnmatch(filename, pattern)

break Path not found
    find --> registry : ToolResult(success=False, error="Error: path not found: path")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

find --> registry : ToolResult(success=True, content=matching_paths)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, find
  Flow:    TL-08: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> FindFileTool -> os.walk -> ToolResult
  State:   No state change
  Success: List of matching file paths
  Failure: Path not found -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl17_update_todo.puml ---

@startuml sq_tl17_update_todo
' ============================================================
' Title:     TL-17 — Update Todo
' Boundary:  nasim code agent
' Purpose:   Update status or content of an existing todo item
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "TodoTool" as tool
end box

note over user, tool
  Scope:          Update status or content of a todo item by ID
  Preconditions:  Todo exists with given ID
  Excludes:       Todo creation, deletion, listing
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Validates status transitions
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, todo=updated_todo) or ToolResult(success=False, error=str)
end note

== TL-17 Update Todo ==

user -> router : types input
router -> agent : TL-17 PROCESS(user_input)
agent -> registry : TL-17 Update Todo(todo_id, status, description)
registry -> tool : TL-17 Update Todo(todo_id, status, description)

break Todo not found
    tool --> registry : ToolResult(success=False, error="todo not found")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Invalid status transition
    tool --> registry : ToolResult(success=False, error="invalid transition")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

tool -> tool : update fields
tool --> registry : ToolResult(success=True, todo)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, tool
  Flow:    TL-17: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> TodoTool -> ToolResult
  State:   Todo status/content updated
  Success: Updated todo returned
  Failure: Todo not found or invalid transition -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl16_insert_todo.puml ---

@startuml sq_tl16_insert_todo
' ============================================================
' Title:     TL-16 — Insert Todo
' Boundary:  nasim code agent
' Purpose:   Add a new todo item via TodoTool
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "TodoTool" as tool
end box

note over user, tool
  Scope:          Add a new todo item with title and optional description
  Preconditions:  TodoTool initialized
  Excludes:       Todo update, delete, list
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Auto-generates ID; initial status OPEN
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, todo_id=todo_id) or ToolResult(success=False, error=str)
end note

== TL-16 Insert Todo ==

user -> router : types input
router -> agent : TL-16 PROCESS(user_input)
agent -> registry : TL-16 Insert Todo(title, description)
registry -> tool : TL-16 Insert Todo(title, description)
tool -> tool : generate ID, set status OPEN
tool --> registry : ToolResult(success=True, todo_id)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, tool
  Flow:    TL-16: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> TodoTool -> ToolResult
  State:   New todo item created (OPEN)
  Success: Todo ID returned
  Failure: Invalid input -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl07_glob_files.puml ---

@startuml sq_tl07_glob_files
' ============================================================
' Title:     TL-07 — Glob Files
' Boundary:  nasim code agent CLI
' Purpose:   Find files by glob pattern
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "GlobTool" as glob
end box

note over user, glob
  Scope:          Find files matching glob pattern
  Preconditions:  Glob pattern provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       Content search, file reading
  Rollback:       Error string returned to LLM
  Design:         Uses pathlib.Path.glob()
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=sorted_paths) or ToolResult(success=False, error=str)
end note

== TL-07 GLOB Files ==

user -> router : types input
router -> agent : TL-07 PROCESS(user_input)
agent -> registry : TL-07 GLOB Files(pattern, base_path)
registry -> glob : TL-07 GLOB Files(pattern, base_path)
glob -> glob : Path(base_path).glob(pattern)
glob -> glob : collect and sort matching paths

break Permission denied
    glob --> registry : ToolResult(success=False, error="Error: permission denied: path")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

glob --> registry : ToolResult(success=True, content=sorted_paths)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, glob
  Flow:    TL-07: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> GlobTool -> pathlib.glob -> ToolResult
  State:   No state change
  Success: Sorted list of matching file paths
  Failure: Permission denied -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl15_spawn_subagent.puml ---

@startuml sq_tl15_spawn_subagent
' ============================================================
' Title:     TL-15 — Spawn Subagent
' Boundary:  nasim code agent
' Purpose:   Create a child subagent via SubagentTool
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "SubagentTool" as tool
end box
participant "SubagentCoordinator" as coord

note over user, coord
  Scope:          Spawn a child subagent with a task prompt
  Preconditions:  SubagentCoordinator initialized
  Excludes:       Subagent result collection, cancellation
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Fire-and-forget spawn; child runs independently
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, child_id=child_id) or ToolResult(success=False, error=str)
end note

== TL-15 Spawn Subagent ==

user -> router : types input
router -> agent : TL-15 PROCESS(user_input)
agent -> registry : TL-15 Spawn Subagent(prompt, subagent_type)
registry -> tool : TL-15 Spawn Subagent(prompt, subagent_type)
tool -> coord : create_child(prompt, subagent_type)

break Coordinator unavailable or limit reached
    coord --> tool : CapacityError
    tool --> registry : ToolResult(success=False, error="spawn limit reached")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

coord --> tool : child_id
tool --> registry : ToolResult(success=True, child_id=child_id)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, coord
  Flow:    TL-15: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> SubagentTool -> SubagentCoordinator -> ToolResult
  State:   New child subagent spawned
  Success: Child subagent ID returned
  Failure: Coordinator unavailable or spawn limit -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl13_read_lsp.puml ---

@startuml sq_tl13_read_lsp
' ============================================================
' Title:     TL-13 — Read LSP
' Boundary:  nasim code agent
' Purpose:   Query LSP server for hover, definition, or references
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-13 READ LSP

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "LspTool" as tool
end box
participant "LSP Server" as lsp

note over user, lsp
  Scope:          Query LSP server for hover, definition, or references
  Preconditions:  LSP server running for target language
  Excludes:       LSP initialization, diagnostics, code actions
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Stateless query; no session-side cache
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=result) or ToolResult(success=False, error=str)
end note

== TL-13 Read LSP ==

user -> router : types input
router -> agent : TL-13 PROCESS(user_input)
agent -> registry : TL-13 Read LSP(query, params)
registry -> tool : TL-13 Read LSP(query, params)
tool -> lsp : send request(query, params)

break LSP server unreachable or times out
    lsp --> tool : ConnectionError / TimeoutError
    tool --> registry : ToolResult(success=False, error="LSP unavailable")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Query returns no results
    lsp --> tool : empty result
    tool --> registry : ToolResult(success=False, error="no results")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

lsp --> tool : hover/definition/references result
tool --> registry : ToolResult(success=True, result)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, lsp
  Flow:    TL-13: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> LspTool -> LSP Server -> ToolResult
  State:   No state change
  Success: LSP query result returned
  Failure: LSP unavailable or no results -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl04_list_directory.puml ---

@startuml sq_tl04_list_directory
' ============================================================
' Title:     TL-04 — List Directory
' Boundary:  nasim code agent CLI
' Purpose:   List files and directories at a path
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
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
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=formatted_listing) or ToolResult(success=False, error=str)
end note

== TL-04 LIST Directory ==

user -> router : types input
router -> agent : TL-04 PROCESS(user_input)
agent -> registry : TL-04 LIST Directory(path)
registry -> dt : TL-04 LIST Directory(path)
dt -> fs : Path(path).resolve()

break Path not found
    fs --> dt : FileNotFoundError
    dt --> registry : ToolResult(success=False, error="path not found")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Not a directory
    dt --> registry : ToolResult(success=False, error="not a directory")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

dt -> fs : sorted(p.iterdir())
fs --> dt : entries
dt -> dt : format with d/ prefix for dirs
dt --> registry : ToolResult(success=True, content=formatted_listing)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    TL-04: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> DirTool -> Host Filesystem -> ToolResult
  State:   No state change
  Success: Directory listing with type prefixes
  Failure: Not found or not directory -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl06_grep_search.puml ---

@startuml sq_tl06_grep_search
' ============================================================
' Title:     TL-06 — Grep Search
' Boundary:  nasim code agent CLI
' Purpose:   Search file contents by regex pattern
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "GrepTool" as grep
  participant "ShellTool" as shell
end box

note over user, shell
  Scope:          Search file contents by regex pattern
  Preconditions:  Pattern and path provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       File globbing, file reading
  Rollback:       Error string returned to LLM
  Design:         Prefers ripgrep; falls back to Python re
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=formatted_matches) or ToolResult(success=False, error=str)
end note

== TL-06 GREP Search ==

user -> router : types input
router -> agent : TL-06 PROCESS(user_input)
agent -> registry : TL-06 GREP Search(pattern, path, case_sensitive, include_glob)
registry -> grep : TL-06 GREP Search(pattern, path, case_sensitive, include_glob)

alt ripgrep available
    grep -> shell : subprocess: rg --json pattern path
    shell --> grep : JSON output
    grep -> grep : parse matches -> file:line:content format
else ripgrep not found
    grep -> grep : Python os.walk + re.search fallback
end

break No matches found
    grep --> registry : ToolResult(success=False, error="No matches found for pattern")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Permission denied / path error
    grep --> registry : ToolResult(success=False, error="Error: permission denied / path not found")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

grep --> registry : ToolResult(success=True, content=formatted_matches)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, shell
  Flow:    TL-06: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> GrepTool -> ripgrep/Python -> ToolResult
  State:   No state change
  Success: List of matching file:line:content
  Failure: No matches, permission error -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl14_list_registered_tools.puml ---

@startuml sq_tl14_list_registered_tools
' ============================================================
' Title:     TL-14 — List Registered Tools
' Boundary:  nasim code agent
' Purpose:   Return list of all tools registered in the ToolRegistry
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — TL-14 LIST Registered Tools

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
end box

note over user, registry
  Scope:          List all registered tools with names and descriptions
  Preconditions:  ToolRegistry initialized
  Excludes:       Tool execution, tool registration
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Read-only; no mutation
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, tools=[...])
end note

== TL-14 List Registered Tools ==

user -> router : types input
router -> agent : TL-14 PROCESS(user_input)
agent -> registry : TL-14 List Registered Tools({})
registry -> registry : enumerate registered tools
registry --> agent : ToolResult(success=True, tools=[...])
agent --> router : AgentEvent(Done)

note over user, registry
  Flow:    TL-14: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> list all registered tools -> ToolResult
  State:   No state change
  Success: List of tool names and descriptions
  Failure: N/A (read-only query)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl02_write_file.puml ---

@startuml sq_tl02_write_file
' ============================================================
' Title:     TL-02 — Write File
' Boundary:  nasim code agent CLI
' Purpose:   Create or overwrite a file
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
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
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content="Wrote N bytes") or ToolResult(success=False, error=str)
end note

== TL-02 WRITE File ==

user -> router : types input
router -> agent : TL-02 PROCESS(user_input)
agent -> registry : TL-02 WRITE File(path, content)
registry -> ft : TL-02 WRITE File(path, content)
ft -> fs : Path(path).mkdir(parents=True)
ft -> fs : Path(path).write_text(content)

break Write error (permissions, disk full)
    fs --> ft : PermissionError / OSError
    ft --> registry : ToolResult(success=False, error="Error writing path: exception")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

fs --> ft : OK
ft --> registry : ToolResult(success=True, content="Wrote N bytes to path")
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    TL-02: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> WriteFileTool -> Host Filesystem -> ToolResult
  State:   No state change
  Success: ToolResult(success=True, "Wrote N bytes")
  Failure: Permissions, disk space -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl09_fetch_web_content.puml ---

@startuml sq_tl09_fetch_web_content
' ============================================================
' Title:     TL-09 — FETCH Web Content
' Boundary:  nasim code agent CLI
' Purpose:   Fetch URL content and convert to markdown
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "WebFetchTool" as fetch
end box
participant "Web" as web

note over user, web
  Scope:          Fetch URL content as markdown text
  Preconditions:  URL provided by LLM
  Excludes:       Web search (TL-10)
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       HTTP error returned as error string
  Design:         Uses httpx + html2text for conversion
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=markdown) or ToolResult(success=False, error=str)
end note

== TL-09 FETCH Web Content ==

user -> router : types input
router -> agent : TL-09 PROCESS(user_input)
agent -> registry : TL-09 FETCH Web Content(url, timeout)
registry -> fetch : TL-09 FETCH Web Content(url, timeout)
fetch -> web : httpx GET url (timeout=timeout)

break HTTP error (4xx, 5xx)
    web --> fetch : HTTPError
    fetch --> registry : ToolResult(success=False, error="Error: HTTP {status_code} for {url}")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Timeout
    web --> fetch : TimeoutException
    fetch --> registry : ToolResult(success=False, error="Error: timeout fetching {url}")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

web --> fetch : HTML content
fetch -> fetch : html2text.convert(html) -> markdown
fetch --> registry : ToolResult(success=True, content=markdown)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, web
  Flow:    TL-09: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> WebFetchTool -> Web -> ToolResult
  State:   No state change
  Success: Page content as markdown text
  Failure: HTTP error, timeout -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl20_recall_memory.puml ---

@startuml sq_tl20_recall_memory
' ============================================================
' Title:     TL-20 — Recall Memory
' Boundary:  nasim code agent
' Purpose:   Recall knowledge from memory via MemoryTool
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "MemoryTool" as tool
end box
participant "MemoryStore" as mem

note over user, mem
  Scope:          Recall knowledge from the memory store by query
  Preconditions:  MemoryTool initialized, memory not empty
  Excludes:       Memory persist, search, scoping
  Contexts:       Called by AGT-02 (DISPATCH Tool Call); delegates to MEM-02
  Rollback:       Error string returned to LLM
  Design:         Delegates to MEM-02 RECALL Knowledge
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, knowledge=knowledge) or ToolResult(success=False, error=str)
end note

== TL-20 Recall Memory ==

user -> router : types input
router -> agent : TL-20 PROCESS(user_input)
agent -> registry : TL-20 Recall Memory(query, scope?)
registry -> tool : TL-20 Recall Memory(query, scope)
tool -> mem : MEM-02 recall(query, scope)

break No matching knowledge
    mem --> tool : empty result
    tool --> registry : ToolResult(success=False, error="no match")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

mem --> tool : matching knowledge
tool --> registry : ToolResult(success=True, knowledge)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, mem
  Flow:    TL-20: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> MemoryTool -> MemoryStore -> ToolResult
  State:   No state change
  Success: Recalled knowledge returned
  Failure: No matching knowledge -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl11_read_git_status.puml ---

@startuml sq_tl11_read_git_status
' ============================================================
' Title:     TL-11 — Read Git Status
' Boundary:  nasim code agent CLI
' Purpose:   Git operations: status, diff, commit
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "GitTool" as git
end box
participant "Host Shell" as shell

note over user, shell
  Scope:          Git status, diff, and commit operations
  Preconditions:  Git repo in working directory
  Excludes:       Branch operations, merge, push
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Git error returned as error string
  Design:         Delegates to git CLI via subprocess
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=git_output) or ToolResult(success=False, error=str)
end note

== TL-11 READ Git Status ==

user -> router : types input
router -> agent : TL-11 PROCESS(user_input)
agent -> registry : TL-11 READ Git Status(action, args)
registry -> git : TL-11 READ Git Status(action, args)

alt action = "status"
    git -> shell : subprocess: git status --porcelain
    shell --> git : status output
    git --> registry : ToolResult(success=True, content=formatted_status)
else action = "diff"
    git -> shell : subprocess: git diff [args]
    shell --> git : diff output
    git --> registry : ToolResult(success=True, content=diff_text)
else action = "commit"
    git -> shell : subprocess: git add -A && git commit -m msg
    shell --> git : commit output
    git --> registry : ToolResult(success=True, content=commit_confirmation)
end

break Not a git repo
    shell --> git : fatal: not a git repository
    git --> registry : ToolResult(success=False, error="Error: not a git repository")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Nothing to commit
    shell --> git : nothing to commit
    git --> registry : ToolResult(success=False, error="Nothing to commit")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, shell
  Flow:    TL-11: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> GitTool -> Host Shell -> ToolResult
  State:   No state change
  Success: Git operation output
  Failure: Not a repo, nothing to commit -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl18_read_todos.puml ---

@startuml sq_tl18_read_todos
' ============================================================
' Title:     TL-18 — Read Todos
' Boundary:  nasim code agent
' Purpose:   List all todo items or filter by status
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "TodoTool" as tool
end box

note over user, tool
  Scope:          List todo items, optionally filtered by status
  Preconditions:  TodoTool initialized
  Excludes:       Todo creation, update, deletion
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Rollback:       Error string returned to LLM
  Design:         Read-only; supports status filter
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, todos=[...])
end note

== TL-18 Read Todos ==

user -> router : types input
router -> agent : TL-18 PROCESS(user_input)
agent -> registry : TL-18 Read Todos(status_filter?)
registry -> tool : TL-18 Read Todos(status_filter)
tool -> tool : query todos, apply filter
tool --> registry : ToolResult(success=True, todos=[...])
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, tool
  Flow:    TL-18: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> TodoTool -> ToolResult
  State:   No state change
  Success: List of todo items
  Failure: N/A (read-only query)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/TL/sq_tl01_read_file.puml ---

@startuml sq_tl01_read_file
' ============================================================
' Title:     TL-01 — Read File
' Boundary:  nasim code agent CLI
' Purpose:   File read tool execution
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "ReadFileTool" as ft
end box
participant "Host Filesystem" as fs

note over user, fs
  Scope:          Read file contents with line numbers
  Preconditions:  File path provided by LLM
  Contexts:       Called by AGT-02 (DISPATCH Tool Call)
  Excludes:       Write, edit, directory listing
  Rollback:       Error string returned to LLM
  Design:         Supports offset/limit for large files
  Classification: Process Decomposition
  Returns:        ToolResult(success=True, content=numbered_content) or ToolResult(success=False, error=str)
end note

== TL-01 READ File ==

user -> router : types input
router -> agent : TL-01 PROCESS(user_input)
agent -> registry : TL-01 READ File(path, offset, limit)
registry -> ft : TL-01 READ File(path, offset, limit)
ft -> fs : Path(path).read_text()

break File not found or not a file
    fs --> ft : FileNotFoundError / IsADirectoryError
    ft --> registry : ToolResult(success=False, error="file not found")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

break Read error (encoding, permissions)
    fs --> ft : PermissionError / UnicodeDecodeError
    ft --> registry : ToolResult(success=False, error="Error reading path")
    registry --> agent : ToolResult
    agent --> router : AgentEvent(Error)
end

fs --> ft : file content
ft -> ft : add line numbers, apply offset/limit
ft --> registry : ToolResult(success=True, content=numbered_content)
registry --> agent : ToolResult
agent --> router : AgentEvent(Done)

note over user, fs
  Flow:    TL-01: User -> ServerRouter -> AgentOrchestrator -> ToolRegistry -> ReadFileTool -> Host Filesystem -> ToolResult
  State:   No state change
  Success: File content with line numbers
  Failure: File not found, permissions, encoding -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt02_dispatch_tool_call.puml ---

@startuml sq_agt02_dispatch_tool_call
' ============================================================
' Title:     AGT-02 — DISPATCH Tool Call
' Boundary:  nasim code agent
' Purpose:   Tool dispatch with Safety Pipeline (no God Object)
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    Meta-Software Designer audit 2026-06-21
' Pattern:   Service (AgentOrchestrator) -> Safety (SafetyCoordinator) -> Repository (ToolRegistry)
' ============================================================

title nasim — AGT-02 DISPATCH Tool Call

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ErrorBoundary" as eb
end box
box "Safety Group" #FFF9C4
  participant "SafetyCoordinator" as safety
  participant "PermissionGate" as gate
  participant "InjectionScanner" as inj
  participant "EgressInspector" as egr
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
  participant "Tool" as tool
end box
box "Observability Group" #E0F2F1
  participant "StructuredLogger" as logger
end box

note over user, logger
  Scope:          AGT-02 DISPATCH Tool Call
  Preconditions:  Tool call from LLM, ToolRegistry populated, SafetyCoordinator initialized
  Contexts:       Called by AGT-01 (PROCESS User Task) for each tool_call in the inner loop
  Excludes:       LLM call logic (PRV-02), Permission prompt rendering (CLI-06), Tool result display (CLI-03)
  Rollback:       Safety violation -> ToolResult(success=false); Tool error -> ErrorBoundary -> ToolResult(error)
  Design:         NO GOD OBJECT: AgentOrchestrator delegates safety to SafetyCoordinator (AGT-15).
                  SafetyCoordinator composes PermissionGate, InjectionScanner, EgressInspector.
                  ToolResult is always structured (success, content, error)
  Classification: UC-level Sub-flow
  Returns:        Success: ToolResult(success=true, content={result})
                  Failure: ToolResult(success=false, error="{error_type}") — safety violation, unknown tool, or execution error
end note

== AGT-02 DISPATCH Tool Call ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> agent : receive tool_call from LLM response

hnote over agent #FFF9C4 : **State: AWAITING_APPROVAL** (if unsafe)

' --- NO GOD OBJECT: Delegate to SafetyCoordinator (AGT-15) ---
agent -> safety : agt15 DISPATCH Safety Pipeline({tool_call})
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

agent --> router : AgentEvent(Done)
deactivate agent

note over user, logger
  Flow:    AGT-02 → [AGT-15: Safety Pipeline] → [ToolRegistry.find] → [Tool.execute] → ToolResult
  State:   <back:#FFF3E0>THINKING</back> -> <back:#FFF9C4>AWAITING_APPROVAL</back> (if unsafe) -> <back:#F3E5F5>TOOL_EXEC</back> -> <back:#FFF3E0>THINKING</back>
  Success: ToolResult(success=true, content={result}) appended to ConversationHistory
  Failure: ToolResult(success=false, error="{safety_violation|unknown_tool|execution_error}")
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt09_spawn_subagent.puml ---

@startuml sq_agt09_spawn_subagent
' ============================================================
' Title:     AGT-09 — SPAWN Subagent
' Boundary:  nasim code agent
' Purpose:   Delegate work to a child agent process
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-09 SPAWN Subagent

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "SubagentCoordinator" as coord
end box
box "Session Group" #F1F8E9
  participant "SessionStore" as store
end box

note over user, store
  Scope:          AGT-09 SPAWN Subagent
  Preconditions:  AgentOrchestrator initialized, parent session active
  Contexts:       Called via ref from AGT-02 (DISPATCH Tool Call)
  Excludes:       Result collection (AGT-10), persona delegation (AGT-11)
  Rollback:       Spawn failure → report error to parent, no child created
  Design:         SubagentCoordinator manages child lifecycle; each child gets its own session
  Classification: Process Decomposition
  Returns:        Success: child_id for later collection (AGT-10)
                  Failure: SpawnError — error reported to parent
end note

== AGT-09 SPAWN Subagent ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> coord : agt09 SPAWN Subagent({task_prompt}, {parent_id})
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
    agent --> router : AgentEvent(Error)
end

agent --> router : AgentEvent(SubagentSpawned)
deactivate agent

note over user, store
  Flow:    AGT-09 → validate parent → create child session → return child_id
  State:   <back:#ECEFF1>IDLE</back> -> SPAWNING -> READY
  Success: child_id returned for later collection (AGT-10)
  Failure: SpawnError — error reported to parent, no child
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt01_process_user_task.puml ---

@startuml sq_agt01_process_user_task
' ============================================================
' Title:     AGT-01 — PROCESS User Task (API-First)
' Boundary:  nasim code agent
' Purpose:   Core agentic loop: LLM call -> tool dispatch -> repeat
'            Entry via API (ServerRouter). No interface bypass.
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

title nasim — AGT-01 PROCESS User Task (API-First)

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
end box
box "Provider Group" #FFF3E0
  participant "LiteLLMProxy" as provider
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as tool
end box
box "Safety Group" #FFF9C4
  participant "SafetyCoordinator" as safety
end box
box "Observability Group" #E0F2F1
  participant "TraceCorrelator" as trace
end box

note over user, trace
  Scope:          AGT-01 PROCESS User Task (API-First)
  Preconditions:  Agent initialized with Provider, ToolRegistry, ConversationHistory
  Contexts:       Called by API-06 (DISPATCH Message) via ServerRouter
  Excludes:       Slash command handling (CLI-02), session CRUD (API-01..05)
  Rollback:       LLM call failure -> append error message -> ERROR state -> IDLE; Tool execution failure -> append error message -> ERROR state -> IDLE; Max iterations exceeded -> force Done event
  Design:         CSR: Controller(ServerRouter) → Service(AgentOrchestrator) → Repository(ToolRegistry, SessionStore).
                  AgentOrchestrator yields AgentEvent objects (no print()); Max iterations configurable;
                  SafetyCoordinator consulted before every tool execution; Recursive: after tool dispatch, re-calls Provider for next response
  Classification: Primary Orchestrator (via API Entry Gate)
  Returns:        Success: AgentEvent(Done) with final text response
                  Failure: AgentEvent(Error) — LLM error or tool execution failure
end note

== AGT-01 PROCESS User Task (API-First) ==

user -> router : API-06 DISPATCH Message(session_id, message)
activate router

router -> agent : dispatchMessage(session_id, message)
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
    agent --> router : AgentEvent(Done)
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
    agent --> router : AgentEvent(Done)
end

break LLM call fails or tool execution errors
    ref over agent, history
      AGT-03: UPDATE Conversation (append error message)
    end ref
    agent --> router : AgentEvent(Error)
end

deactivate agent

router --> user : SSE stream (AgentEvents)
deactivate router

note over user, trace
  Flow:    AGT-01 → User → API(ServerRouter) → AgentOrchestrator → [OBS-03] → [AGT-03] → [HK-04] → [PRV-02] → [HK-05] → [AGT-03] → (tool loop via AGT-02) → Done → SSE stream → User
  State:   <back:#ECEFF1>IDLE</back> -> <back:#E0F7FA>SERVING</back> -> <back:#FFF3E0>THINKING</back> -> [<back:#F3E5F5>TOOL_EXEC</back>]* -> <back:#E8F5E9>RESPONDING</back> -> <back:#ECEFF1>IDLE</back>
  Success: AgentEvent(Done) — final text response streamed to user via API SSE
  Failure: AgentEvent(Error) — LLM error or tool error; ERROR -> IDLE
  Invariant: AgentOrchestrator is NEVER called directly by any interface. ALL calls go through API (ServerRouter).
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt08_approve_plan.puml ---

@startuml sq_agt08_approve_plan
' ============================================================
' Title:     AGT-08 — APPROVE Plan
' Boundary:  nasim code agent
' Purpose:   Execute queued tool calls from plan mode
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-08 APPROVE Plan

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PlanSession" as plan
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as registry
end box
box "Repository Group" #E8F5E9
  participant "MemoryRepository" as memory
end box

note over user, registry
  Scope:          AGT-08 APPROVE Plan
  Preconditions:  Plan mode active with queued calls
  Contexts:       Called by CLI-02 (/approve command)
  Excludes:       Plan queuing (AGT-07)
  Rollback:       Partial execution on failure
  Design:         Drains pending_calls queue sequentially
  Classification: Process Decomposition
  Returns:        Success: all queued calls executed with results
                  Failure: partial execution on tool failure
end note

== AGT-08 APPROVE Plan ==

user -> router : /approve
router -> agent : APPROVE_Plan()
activate agent

agent -> plan : agt08 APPROVE Plan()
activate plan
plan -> plan : get pending_calls
plan -> plan : clear pending_calls

loop for each queued call
    plan -> registry : agt02 DISPATCH Tool Call({tool_name}, {args})
    activate registry
    registry --> plan : ToolResult
    deactivate registry
    plan -> plan : collect results
end

plan --> agent : all results
deactivate plan

agent --> router : AgentEvent(Done)
deactivate agent

note over user, registry
  Flow:    AGT-08 → approve → drain queue → execute sequentially → results
  State:   <back:#E3F2FD>PLANNING</back> -> <back:#F3E5F5>TOOL_EXEC</back> -> <back:#FFF3E0>THINKING</back>
  Success: all queued calls executed with results
  Failure: partial execution on tool failure
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt10_collect_subagent_result.puml ---

@startuml sq_agt10_collect_subagent_result
' ============================================================
' Title:     AGT-10 — COLLECT Subagent Result
' Boundary:  nasim code agent
' Purpose:   Wait for child agent completion and aggregate result
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-10 COLLECT Subagent Result

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "SubagentCoordinator" as coord
end box
box "Session Group" #F1F8E9
  participant "SessionStore" as store
end box

note over user, store
  Scope:          AGT-10 COLLECT Subagent Result
  Preconditions:  Child agent spawned via AGT-09, child_id valid
  Contexts:       Called after AGT-09 when parent needs child result
  Excludes:       Spawn logic (AGT-09), persona delegation (AGT-11)
  Rollback:       Timeout → cancel child, return partial result
  Design:         Blocking wait with configurable timeout; result aggregated into parent context
  Classification: Process Decomposition
  Returns:        Success: aggregated result from child agent
                  Failure: PartialResult(timeout) or ChildError
end note

== AGT-10 COLLECT Subagent Result ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> coord : agt10 COLLECT Subagent Result({child_id}, {timeout})
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

agent --> router : AgentEvent(Done)
deactivate agent

note over user, store
  Flow:    AGT-10 → wait → collect → aggregate
  State:   WAITING -> COLLECTING -> DONE
  Success: aggregated result returned to parent
  Failure: timeout -> cancel child -> partial result; child error -> propagate
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt12_load_persona.puml ---

@startuml sq_agt12_load_persona
' ============================================================
' Title:     AGT-12 — LOAD Persona
' Boundary:  nasim code agent
' Purpose:   Load persona configuration and apply system prompt
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-12 READ Persona

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PersonaManager" as pm
end box
box "Config Group" #FCE4EC
  participant "PersonaRegistry" as reg
end box
box "Repository Group" #E8F5E9
  participant "MemoryRepository" as memory
end box

note over user, reg
  Scope:          AGT-12 LOAD Persona
  Preconditions:  PersonaManager initialized, persona name provided
  Contexts:       Called by AGT-11 or directly by AgentOrchestrator
  Excludes:       Persona switch (AGT-13), delegation (AGT-11)
  Rollback:       Config parse error → log error, retain current persona
  Design:         Persona config includes system prompt, allowed tools, model override
  Classification: Process Decomposition
  Returns:        Success: PersonaLoaded(config)
                  Failure: PersonaLoadError — config parse error
end note

== AGT-12 LOAD Persona ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> pm : agt12 LOAD Persona({persona_name})
activate pm

pm -> reg : get_persona_config(persona_name)
activate reg
reg --> pm : config
deactivate reg

alt config valid
    pm -> pm : parse system prompt
    pm -> pm : extract tool allowlist
    pm -> pm : extract model override (if set)
    pm --> agent : PersonaLoaded(config)
else config invalid
    pm -> agent : PersonaLoadError
end

deactivate pm

agent --> router : AgentEvent(Done)
deactivate agent

note over user, reg
  Flow:    AGT-12 → load persona config → apply system prompt
  State:   <back:#ECEFF1>IDLE</back> -> LOADING -> <back:#2E7D32>ACTIVE</back>
  Success: persona config loaded and applied
  Failure: config error -> log, retain current persona
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt11_delegate_to_persona.puml ---

@startuml sq_agt11_delegate_to_persona
' ============================================================
' Title:     AGT-11 — DELEGATE to Persona
' Boundary:  nasim code agent
' Purpose:   Select and delegate task execution to a persona
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-11 DELEGATE to Persona

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PersonaManager" as pm
end box
box "Config Group" #FCE4EC
  participant "PersonaRegistry" as reg
end box
box "Repository Group" #E8F5E9
  participant "MemoryRepository" as memory
end box

note over user, reg
  Scope:          AGT-11 DELEGATE to Persona
  Preconditions:  PersonaManager initialized, at least one persona registered
  Contexts:       Called by AgentOrchestrator when task requires specialized behavior
  Excludes:       Persona load/switch (AGT-12/13), subagent spawn (AGT-09)
  Rollback:       Persona not found → fallback to default persona
  Design:         Persona selection based on task tags or explicit request
  Classification: Process Decomposition
  Returns:        Success: PersonaDelegated with persona context applied
                  Failure: PersonaDelegated(default) — fallback to default
end note

== AGT-11 DELEGATE to Persona ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> pm : agt11 DELEGATE to Persona({task}, {persona_hint})
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

agent --> router : AgentEvent(Done)
deactivate agent

note over user, reg
  Flow:    AGT-11 → select persona → delegate task
  State:   <back:#ECEFF1>IDLE</back> -> DELEGATING -> <back:#2E7D32>ACTIVE</back>
  Success: task delegated with persona context applied
  Failure: persona not found -> fallback to default
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt06_compact_context.puml ---

@startuml sq_agt06_compact_context
' ============================================================
' Title:     AGT-06 — COMPACT Context
' Boundary:  nasim code agent
' Purpose:   Context compaction when token budget exceeded
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-06 COMPACT Context

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
  participant "ContextCompactor" as compactor
end box
box "Repository Group" #E8F5E9
  participant "MemoryRepository" as memory
end box

note over user, compactor
  Scope:          AGT-06 COMPACT Context
  Preconditions:  token_count > context_budget
  Contexts:       Called by AGT-03 (UPDATE Conversation)
  Excludes:       Token tracking (CTX-01)
  Rollback:       Truncate oldest messages as fallback
  Design:         Secondary LLM call to summarize old exchanges
  Classification: Process Decomposition
  Returns:        Success: shortened messages list
                  Failure: truncated messages (fallback)
end note

== AGT-06 COMPACT Context ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> history : agt03 UPDATE Conversation({msg})
activate history
history -> history : check token_count > budget
history --> agent : COMPACT_NEEDED
deactivate history

agent -> compactor : agt06 COMPACT Context({messages}, {budget})
activate compactor
ref over compactor
  CTX-02: COMPACT Context
end ref
compactor --> agent : shortened messages
deactivate compactor

agent -> history : agt03 UPDATE Conversation({shortened_messages})
activate history
history -> history : replace messages with shortened list
history --> agent : ok
deactivate history

agent --> router : AgentEvent(Done)
deactivate agent

note over user, compactor
  Flow:    AGT-06 → budget check → select old → summarize → replace
  State:   <back:#FFF3E0>THINKING</back> -> <back:#E0F2F1>COMPACTING</back> -> <back:#FFF3E0>THINKING</back>
  Success: messages shortened, token count reduced
  Failure: LLM fails -> truncate fallback
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt07_queue_plan.puml ---

@startuml sq_agt07_queue_plan
' ============================================================
' Title:     AGT-07 — QUEUE Plan
' Boundary:  nasim code agent
' Purpose:   Queue tool calls in plan mode without executing
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-07 INSERT Plan

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PlanSession" as plan
end box
box "Repository Group" #E8F5E9
  participant "MemoryRepository" as memory
end box

note over user, plan
  Scope:          AGT-07 QUEUE Plan
  Preconditions:  Plan mode active (/plan toggled)
  Contexts:       Called by AGT-01 (PROCESS User Task) in plan mode
  Excludes:       Tool execution, permission checks
  Rollback:       N/A — queued calls are never executed until approved
  Design:         Tool calls displayed as plan, not executed
  Classification: Process Decomposition
  Returns:        Success: formatted plan text with queued calls
                  Failure: N/A (internal operation)
end note

== AGT-07 QUEUE Plan ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> plan : agt07 QUEUE Plan({tool_name}, {args})
activate plan
plan -> plan : append to pending_calls list
plan --> agent : queued
deactivate plan

agent -> plan : agt07 DISPLAY Plan()
activate plan
plan --> agent : formatted plan text
deactivate plan

agent --> router : AgentEvent(PlanDisplay)
deactivate agent

note over user, plan
  Flow:    AGT-07 → queue tool call → display as plan
  State:   <back:#FFF3E0>THINKING</back> -> <back:#E3F2FD>PLANNING</back>
  Success: tool calls queued and displayed as plan
  Failure: N/A (internal operation)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt13_switch_persona.puml ---

@startuml sq_agt13_switch_persona
' ============================================================
' Title:     AGT-13 — SWITCH Persona
' Boundary:  nasim code agent
' Purpose:   Unload current persona and load a new one
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-13 UPDATE Persona

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "PersonaManager" as pm
end box
box "Config Group" #FCE4EC
  participant "PersonaRegistry" as reg
end box
box "Repository Group" #E8F5E9
  participant "MemoryRepository" as memory
end box

note over user, reg
  Scope:          AGT-13 SWITCH Persona
  Preconditions:  PersonaManager active with current persona loaded
  Contexts:       Called when user or task requests persona change mid-session
  Excludes:       Load only (AGT-12), delegation (AGT-11)
  Rollback:       New persona load fails → retain previous persona
  Design:         Atomic switch: unload current → load new; partial failure retains old
  Classification: Process Decomposition
  Returns:        Success: PersonaSwitched(new_persona)
                  Failure: PersonaSwitchFailed(retained previous)
end note

== AGT-13 SWITCH Persona ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> pm : agt13 SWITCH Persona({new_persona_name})
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
    pm --> agent : PersonaSwitched(new_persona)
else new config invalid
    pm -> pm : reload previous persona config
    pm --> agent : PersonaSwitchFailed(retained previous)
end

deactivate pm

agent --> router : AgentEvent(Done)
deactivate agent

note over user, reg
  Flow:    AGT-13 → unload current → load new → apply
  State:   <back:#2E7D32>ACTIVE</back> -> SWITCHING -> <back:#2E7D32>ACTIVE</back>
  Success: persona switched, new system prompt active
  Failure: new config invalid -> retain previous persona
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt14_handle_error.puml ---

@startuml sq_agt14_handle_error
' ============================================================
' Title:     AGT-14 — HANDLE Error
' Boundary:  nasim code agent
' Purpose:   Classify errors and determine recovery action
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-14 HANDLE Error

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ErrorBoundary" as eb
end box
box "Safety Group" #FFF9C4
  participant "SafetyCoordinator" as safety
end box
box "Repository Group" #E8F5E9
  participant "MemoryRepository" as memory
end box

note over user, safety
  Scope:          AGT-14 HANDLE Error
  Preconditions:  Error occurred in agent loop (LLM, tool, or session)
  Contexts:       Called by AGT-01 when LLM or tool call fails
  Excludes:       Error display (CLI-03), error logging (OBS-01)
  Rollback:       Unrecoverable error → terminate task with error event
  Design:         Error classification drives retry, fallback, or abort decisions
  Classification: Process Decomposition
  Returns:        Success: RecoveryAction(retry | fallback | abort)
                  Failure: unrecoverable → abort with error event
end note

== AGT-14 HANDLE Error ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> eb : agt14 HANDLE Error({error})
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

agent --> router : AgentEvent(Error)
deactivate agent

note over user, safety
  Flow:    AGT-14 → classify → determine recovery → return action
  State:   <back:#FFEBEE>ERROR</back> -> CLASSIFYING -> <back:#FBE9E7>RETRY</back> | FALLBACK | ABORT
  Success: recovery action returned for agent to execute
  Failure: unrecoverable -> abort with error event
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt15_dispatch_safety_pipeline.puml ---

@startuml sq_agt15_dispatch_safety_pipeline
' ============================================================
' Title:     AGT-15 — DISPATCH Safety Pipeline
' Boundary:  nasim code agent
' Purpose:   Run injection scan, egress inspect, and permission check
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-15 DISPATCH Safety Pipeline

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Safety Group" #FFF9C4
  participant "SafetyCoordinator" as safety
  participant "InjectionScanner" as inj
  participant "EgressInspector" as egr
  participant "PermissionGate" as perm
end box

note over user, perm
  Scope:          AGT-15 DISPATCH Safety Pipeline
  Preconditions:  Tool call queued, SafetyCoordinator initialized
  Contexts:       Called by AGT-02 before every tool dispatch
  Excludes:       Individual safety checks (SAF-01/02/03)
  Rollback:       Any stage fails → block tool execution, report violation
  Design:         Pipeline stages run sequentially; first failure short-circuits
  Classification: Process Decomposition
  Returns:        Success: SafetyPassed — tool execution allowed
                  Failure: SafetyViolation(injection | egress | permission) — tool blocked
end note

== AGT-15 DISPATCH Safety Pipeline ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> safety : agt15 DISPATCH Safety Pipeline({tool_call})
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

agent --> router : AgentEvent(Done)
deactivate agent

note over user, perm
  Flow:    AGT-15 → injection scan → egress inspect → permission check → return
  State:   CHECKING -> INJECTION -> EGRESS -> PERMISSION -> PASSED | BLOCKED
  Success: SafetyPassed, tool execution allowed
  Failure: any stage fails -> block, report violation
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt03_update_conversation.puml ---

@startuml sq_agt03_update_conversation
' ============================================================
' Title:     AGT-03 — UPDATE Conversation
' Boundary:  nasim code agent
' Purpose:   Message list management and token tracking
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-03 UPDATE Conversation

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
end box
box "Repository Group" #E8F5E9
  participant "MemoryRepository" as memory
end box

note over user, history
  Scope:          AGT-03 UPDATE Conversation
  Preconditions:  ConversationHistory initialized
  Contexts:       Called by AGT-01 (PROCESS User Task)
  Excludes:       Context compaction (CTX-02)
  Rollback:       N/A
  Design:         Owns messages + token_count; triggers compaction
  Classification: Process Decomposition
  Returns:        Success: messages list
                  Failure: N/A (internal operation)
end note

== AGT-03 UPDATE Conversation ==

user -> router : types input
router -> agent : PROCESS(user_input)
activate agent

agent -> history : agt03 ADD Message({msg})
activate history
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

agent -> history : agt03 GET Messages()
history --> agent : messages list
deactivate history

agent --> router : AgentEvent(Done)
deactivate agent

note over user, history
  Flow:    AGT-03 → add message → track tokens → check budget → compact if needed
  State:   No state change (or COMPACTING if budget exceeded)
  Success: messages list returned
  Failure: N/A (internal operation)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/AGT/sq_agt04_delete_history.puml ---

@startuml sq_agt04_delete_history
' ============================================================
' Title:     AGT-04 — DELETE History
' Boundary:  nasim code agent
' Purpose:   Clear conversation history
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — AGT-04 DELETE History

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
end box

note over user, history
  Scope:          AGT-04 DELETE History
  Preconditions:  Agent initialized with system prompt
  Contexts:       Called by CLI-02 (/reset slash command)
  Excludes:       Session persistence
  Rollback:       N/A
  Design:         Keeps system prompt, clears all other messages
  Classification: Process Decomposition
  Returns:        Success: history cleared (system prompt retained)
                  Failure: N/A (internal operation)
end note

== AGT-04 DELETE History ==

user -> router : /reset
router -> agent : DELETE_History()
activate agent

agent -> history : agt04 DELETE History()
activate history
history -> history : self.messages = [system_prompt]
history -> history : self.token_count = estimate_tokens(system_prompt)
history --> agent : history cleared
deactivate history

agent --> router : AgentEvent(Done)
deactivate agent

note over user, history
  Flow:    AGT-04 → reset → keep system prompt → clear rest
  State:   No state change
  Success: history cleared, system prompt retained
  Failure: N/A (internal operation)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt03_apply_whole_file.puml ---

@startuml sq_edt03_apply_whole_file
' ============================================================
' Title:     EDT-03 — Apply Whole File
' Boundary:  nasim code agent CLI
' Purpose:   Verify edit applied correctly
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "EditValidator" as validator
  participant "FileSystem" as fs
end box
box "Tool Group" #F3E5F5
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
    - EditValidator reads edited file and compares with expected
    - Syntax check via language-specific linter (if available)
    - Diff verification ensures intended changes applied
    - Returns structured validation result

  Classification: Primary Orchestrator

  Returns:
    - Success: ValidationResult with pass/fail details
    - Failure: ValidationResult with failure reasons
end note

== edt03 VALIDATE Edit ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> validator : EDT-03 VALIDATE_EDIT(edit_result)
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

agent --> router : AgentEvent(Done)

note over user, tool
  Flow:
    - User → ServerRouter → AgentOrchestrator → EditValidator → FileSystem + ToolRegistry → ValidationResult

  State:
    - <back:#ECEFF1>IDLE</back> → READING → CHECKING → LINTING → DONE

  Success:
    - ValidationResult with pass=true

  Failure:
    - Diff mismatch → validation fails
    - Syntax error → validation fails

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
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-01 SELECT Strategy

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "StrategySelector" as selector
  participant "EditStrategy" as strategy
end box
box "Config Group" #FCE4EC
  participant "ConfigLoader" as config
end box

note over agent, config
  Scope:          Choose optimal edit format for the target model
  Preconditions:  Agent has identified a file to edit, Config loaded
  Contexts:       Called before EDT-02 (APPLY Search-Replace); entry point for edit subsystem
  Excludes:       Edit execution (EDT-02..09), diff staging (EDT-10)
  Rollback:       No valid strategy -> return error, suggest manual edit
  Design:         StrategySelector evaluates model capabilities vs edit requirements; format selected by diff size and model support
  Classification: Process Decomposition
  Returns:        EditStrategy(format, parameters, confidence) on success; error with manual suggestion on failure
end note

== EDT-01 SELECT Strategy ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> selector : EDT-01 SELECT_STRATEGY(file_path, edit_description, model_id)
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

agent --> router : AgentEvent(Done)

note over agent, config
  Flow:    User → ServerRouter → AgentOrchestrator → StrategySelector → Config + EditStrategy → EditStrategy
  State:   <back:#ECEFF1>IDLE</back> -> <back:#FFF3E0>THINKING</back> -> <back:#ECEFF1>IDLE</back>
  Success: EditStrategy with chosen format and parameters
  Failure: No compatible format -> error + manual suggestion
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt09_apply_inline_patch.puml ---

@startuml sq_edt09_apply_inline_patch
' ============================================================
' Title:     EDT-09 — APPLY Inline Patch
' Boundary:  nasim code agent
' Purpose:   Apply inline patch with line-level precision
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-09 UPDATE Inline Patch

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "EditStrategyManager" as esm
  participant "InlinePatchCoder" as ipc
end box
box "FileSystem Group" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Inline patch application with line-level precision
  Preconditions:  Patch generated with line offsets, target file readable
  Contexts:       EDT-01 SELECT Strategy selects this for precise line-targeted edits
  Excludes:       Whole-file rewrites, sandbox isolation, AST manipulation
  Rollback:       Patch context mismatch → reject patch, report conflict
  Design:         InlinePatchCoder parses patch format, validates context lines, applies at offset
  Classification: Process Decomposition
  Returns:        EditResult(success, file_path, lines_changed) on success; patch rejected on failure
end note

== EDT-09 APPLY Inline Patch ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> esm : EDT-09 APPLY_INLINE_PATCH(file_path, patch)
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

agent --> router : AgentEvent(Done)

note over participants
  Flow:    EDT-09 → parse patch → apply → validate
  State:   <back:#ECEFF1>IDLE</back> → PARSING → VALIDATING → APPLYING → DONE
  Success: EditResult(success=true, file_path, lines_changed) — patch applied
  Failure: EditResult(success=false, error) — context mismatch, patch rejected
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt10_stage_diff.puml ---

@startuml sq_edt10_stage_diff
' ============================================================
' Title:     EDT-10 — STAGE Diff
' Boundary:  nasim code agent
' Purpose:   Stage edit in DiffSandboxManager for review before sandbox-validated apply
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    Meta-Software Designer audit 2026-06-21
' Note:      Process decomposition — internal step of edit flow. Actor required per updated sq.md rules.
' ============================================================

title nasim — EDT-10 STAGE Diff

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Sandbox Group" #F1F8E9
  participant "DiffSandboxManager" as diff_mgr
  participant "EditStagingArea" as staging
  participant "DiffComputer" as diff_comp
end box

note over user, diff_comp
  Scope:          EDT-10 STAGE Diff
  Preconditions:  Edit strategy applied, DiffSandboxManager initialized
  Contexts:       Called by EDT-01 (SELECT Strategy) when diff_sandbox mode selected
  Excludes:       Edit execution (EDT-02..09), user review (SAF-02), file system writes
  Rollback:       Staging failure → discard from sandbox
  Design:         DiffSandboxManager holds pending edits in isolated staging area via EditStagingArea. DiffComputer computes diffs for review.
  Classification: Process Decomposition
  Returns:        Success: StagedDiff(diff_id, diff_text) — diff staged for review
                  Failure: StagingError — sandbox allocation or diff computation failed
end note

== EDT-10 STAGE Diff ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> diff_mgr : EDT-10 STAGE_DIFF(edit_result)
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

agent --> router : AgentEvent(Done)

note over user, diff_comp
  Flow:    User → ServerRouter → AgentOrchestrator → DiffSandboxManager → EditStagingArea → DiffComputer → return
  State:   <back:#F1F8E9>STAGING</back>
  Success: StagedDiff(diff_id, diff_text) — diff staged for review
  Failure: StagingError — sandbox allocation or diff computation failed
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
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-07 UPDATE Diff Sandbox

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "EditStrategyManager" as esm
  participant "DiffSandboxCoder" as dsc
end box
box "Sandbox Group" #B3E5FC
  participant "DiffSandboxManager" as dsm
end box
box "FileSystem Group" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Apply diff in sandbox, validate, then commit to real file
  Preconditions:  Diff generated, sandbox environment available
  Contexts:       EDT-01 SELECT Strategy chooses this for risky or large diffs
  Excludes:       Direct file edits, AST-level manipulation
  Rollback:       Sandbox validation fails → discard sandbox, report error
  Design:         DiffSandboxCoder delegates to DiffSandboxManager for isolation
  Classification: Process Decomposition
  Returns:        EditResult(success, file_path) on success; sandbox discarded on failure
end note

== EDT-07 APPLY Diff Sandbox ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> esm : EDT-07 APPLY_DIFF_SANDBOX(file_path, diff_patch)
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

agent --> router : AgentEvent(Done)

note over participants
  Flow:    EDT-07 → sandbox diff → validate → commit
  State:   <back:#ECEFF1>IDLE</back> → SANDBOXING → APPLYING → VALIDATING → COMMITTING → DONE
  Success: EditResult(success=true, file_path) — diff applied via sandbox
  Failure: EditResult(success=false, error) — sandbox validation failed
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt02_apply_search_replace.puml ---

@startuml sq_edt02_apply_search_replace
' ============================================================
' Title:     EDT-02 — APPLY Search-Replace
' Boundary:  nasim code agent
' Purpose:   Execute edit via search-replace strategy
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    CAR audit 2026-06-26 (removed EditApplier phantom, fixed box naming)
' ============================================================

title nasim — EDT-02 APPLY Search-Replace

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "SearchReplaceCoder" as strategy
end box
participant "Host Filesystem" as fs

note over agent, fs
  Scope:          Execute edit via search-replace strategy
  Preconditions:  EDT-01 completed (EditStrategy selected), target file exists and is writable
  Contexts:       Called by AgentOrchestrator after EDT-01
  Excludes:       Strategy selection (EDT-01), post-edit validation (EDT-03), diff staging (EDT-10)
  Rollback:       Write failure -> restore original file from backup
  Design:         AgentOrchestrator reads original, applies SearchReplaceCoder strategy, writes result. Backup created before modification.
  Classification: Process Decomposition
  Returns:        EditResult(diff, file_path, backup_path) on success; restored original on failure
end note

== EDT-02 APPLY Search-Replace ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> fs : read_file(file_path)
activate fs
fs --> agent : original_content
deactivate fs

agent -> fs : create_backup(file_path)
activate fs
fs --> agent : backup_path
deactivate fs

agent -> strategy : apply(original_content)
activate strategy
strategy --> agent : modified_content
deactivate strategy

agent -> fs : write_file(file_path, modified_content)
activate fs
fs --> agent : write_success
deactivate fs

agent -> agent : compute_diff(original_content, modified_content)

agent --> router : AgentEvent(Done)

note over agent, fs
  Flow:    User → ServerRouter → AgentOrchestrator → SearchReplaceCoder + Host Filesystem → EditResult
  State:   <back:#ECEFF1>IDLE</back> -> READING -> BACKING_UP -> WRITING -> DIFFING -> DONE
  Success: EditResult with diff and backup path
  Failure: Write failure -> restore from backup
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
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-04 UPDATE Unified Diff

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "EditStrategyManager" as mgr
  participant "UnifiedDiffCoder" as coder
end box

note over agent, coder
  Scope:          Apply unified diff format edit to file
  Preconditions:  EditStrategyManager initialized, file exists
  Contexts:       Called by AGT-02 DISPATCH Tool Call
  Excludes:       Strategy selection (EDT-01), validation (EDT-03)
  Rollback:       Diff application failure returns error
  Design:         Parses unified diff, applies hunks sequentially
  Classification: Process Decomposition
  Returns:        ToolResult(success=True) on success; ToolResult(success=False) on failure
end note

== EDT-04 APPLY Unified Diff ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> mgr : EDT-04 APPLY_UNIFIED_DIFF(file, diff)
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

agent --> router : AgentEvent(Done)

note over agent, coder
  Flow:    User → ServerRouter → AgentOrchestrator → EditStrategyManager → UnifiedDiffCoder → parse hunks → apply → result
  State:   No state change
  Success: File modified with unified diff
  Failure: Hunk mismatch, file not found -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt05_apply_fenced_block.puml ---

@startuml sq_edt05_apply_fenced_block
' ============================================================
' Title:     EDT-05 — APPLY Fenced Block
' Boundary:  nasim code agent
' Purpose:   Apply fenced code block format edit
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-05 UPDATE Fenced Block

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "EditStrategyManager" as mgr
  participant "FencedBlockCoder" as coder
end box

note over agent, coder
  Scope:          Apply fenced code block format edit
  Preconditions:  EditStrategyManager initialized, file exists
  Contexts:       Called by AGT-02 DISPATCH Tool Call
  Excludes:       Strategy selection (EDT-01), validation (EDT-03)
  Rollback:       Block extraction failure returns error
  Design:         Extracts fenced code block, replaces matching section
  Classification: Process Decomposition
  Returns:        ToolResult(success=True) on success; ToolResult(success=False) on failure
end note

== EDT-05 APPLY Fenced Block ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> mgr : EDT-05 APPLY_FENCED_BLOCK(file, block)
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

agent --> router : AgentEvent(Done)

note over agent, coder
  Flow:    User → ServerRouter → AgentOrchestrator → EditStrategyManager → FencedBlockCoder → extract → locate → replace
  State:   No state change
  Success: File modified with fenced block replacement
  Failure: Section not found, ambiguous match -> ToolResult(success=False)
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt06_apply_function_level.puml ---

@startuml sq_edt06_apply_function_level
' ============================================================
' Title:     EDT-06 — APPLY Function-Level
' Boundary:  nasim code agent
' Purpose:   Edit a single function via AST-aware replace
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-06 UPDATE Function-Level

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "EditStrategyManager" as esm
  participant "FunctionLevelCoder" as flc
end box
box "Tool Group" #F3E5F5
  participant "ASTParser" as ast
end box
box "FileSystem Group" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Function-level edit via AST parse and targeted replace
  Preconditions:  File identified, function boundary determinable
  Contexts:       EDT-01 SELECT Strategy selects this for function-scoped diffs
  Excludes:       Multi-file edits, whole-file rewrites
  Rollback:       AST parse failure → fallback to EDT-02 or EDT-03
  Design:         FunctionLevelCoder locates function node, replaces body, validates AST integrity
  Classification: Process Decomposition
  Returns:        EditResult(success, file_path, function_name) on success; fallback to EDT-02/EDT-03 on failure
end note

== EDT-06 APPLY Function-Level ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> esm : EDT-06 APPLY_FUNCTION_LEVEL(file_path, function_name, new_body)
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

agent --> router : AgentEvent(Done)

note over participants
  Flow:    User → ServerRouter → AgentOrchestrator → EditStrategyManager → FunctionLevelCoder → AST parse → replace function → validate
  State:   <back:#ECEFF1>IDLE</back> → PARSING → REPLACING → VALIDATING → DONE
  Success: EditResult with modified file and function scope
  Failure: AST parse error → fallback to EDT-02/EDT-03; function not found → error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/EDT/sq_edt08_apply_architect.puml ---

@startuml sq_edt08_apply_architect
' ============================================================
' Title:     EDT-08 — APPLY Architect
' Boundary:  nasim code agent
' Purpose:   Plan and apply multi-file edits via architectural decomposition
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — EDT-08 UPDATE Architect

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Edit Strategy Group" #FFF3E0
  participant "EditStrategyManager" as esm
  participant "ArchitectCoder" as arch
end box
box "Tool Group" #F3E5F5
  participant "ASTParser" as ast
end box
box "FileSystem Group" #F3E5F5
  participant "FileSystem" as fs
end box

note over participants
  Scope:          Multi-file edit planning and coordinated application
  Preconditions:  Edit intent spans multiple files, dependency graph derivable
  Contexts:       EDT-01 SELECT Strategy selects this for cross-file refactors
  Excludes:       Single-file edits, sandbox isolation
  Rollback:       Partial application detected → revert all changed files
  Design:         ArchitectCoder plans edit order, applies sequentially, validates each step
  Classification: Process Decomposition
  Returns:        EditResult(success, files_modified[]) on success; all files reverted on failure
end note

== EDT-08 APPLY Architect ==

user -> router : types input
router -> agent : PROCESS(user_input)

agent -> esm : EDT-08 APPLY_ARCHITECT(edit_plan[])
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

agent --> router : AgentEvent(Done)

note over participants
  Flow:    EDT-08 → plan multi-file edit → apply across files → validate
  State:   <back:#ECEFF1>IDLE</back> → <back:#E3F2FD>PLANNING</back> → EDITING → VALIDATING → DONE
  Success: EditResult(success=true, files_modified[]) — all files edited
  Failure: EditResult(success=false, error) — cross-file validation failed, all reverted
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim05_embed_code.puml ---

@startuml sq_rim05_embed_code
' ============================================================
' Title:     RIM-05 — EMBED Code
' Boundary:  nasim code agent
' Purpose:   Generate vector embeddings for code fragments
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-05 EMBED Code

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Intelligence Group" #EDE7F6
  participant "RepoIntelligenceManager" as rim
  participant "EmbeddingAdapter" as embed
end box
box "External" #F5F5F5
  participant "EmbeddingProvider" as provider
end box
box "Storage Group" #F3E5F5
  participant "VectorStore" as vstore
end box

note over user, vstore
  Scope:          RIM-05 EMBED Code — generate vector embeddings for code fragments
  Preconditions:  Embedding provider configured, code fragments identified
  Contexts:       RIM-01 INDEX Codebase identifies fragments; RIM-06 SEARCH Semantic consumes embeddings
  Excludes:       Semantic search (RIM-06), AST indexing (RIM-01)
  Rollback:       Provider failure -> partial embeddings retained, error reported
  Design:         EmbeddingAdapter batches fragments, calls provider, stores vectors
  Returns:
    - Success: EmbeddingResult(count, dimensions)
    - Failure: Partial embeddings retained on provider failure
end note

== RIM-05 EMBED Code ==

user -> router : RIM-05 EMBED Code(code_fragments)
activate router
router -> agent : RIM-05 EMBED Code(code_fragments)
activate agent

agent -> rim : RIM-05 EMBED Code(code_fragments)
activate rim

rim -> embed : RIM-05 EMBED Code(code_fragments)
activate embed

loop for each batch of fragments
    embed -> provider : provider.embed(batch)
    activate provider
    provider --> embed : vectors[]
    deactivate provider

    embed -> embed : validate_dimensions(vectors)
end

embed -> vstore : vstore.store_vectors(code_fragments, vectors)
activate vstore
vstore --> embed : store_result
deactivate vstore

embed --> rim : EmbeddingResult(count, dimensions)
deactivate embed

rim --> agent : EmbeddingResult(count, dimensions)
deactivate rim

agent --> router : EmbeddingResult(count, dimensions)
deactivate agent
deactivate router

note over user, vstore
  Flow:    RIM-05 → User → ServerRouter → AgentOrchestrator → RepoIntelligenceManager → EmbeddingAdapter → generate embeddings → return vectors
  State:   No state change
  Success: EmbeddingResult with fragment count and vector dimensions
  Failure: Provider failure -> partial embeddings retained
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim02_build_symbol_graph.puml ---

@startuml sq_rim02_build_symbol_graph
' ============================================================
' Title:     RIM-02 — BUILD Symbol Graph
' Boundary:  nasim code agent
' Purpose:   Build cross-file symbol reference graph
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-02 BUILD SymbolGraph

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Intelligence Group" #EDE7F6
  participant "RepoIntelligenceManager" as rim
  participant "SymbolGraph" as graph
end box

note over user, graph
  Scope:          RIM-02 BUILD SymbolGraph — build cross-file symbol reference graph
  Preconditions:  AST index available from RIM-01
  Contexts:       Called after RIM-01 INDEX Codebase
  Excludes:       AST parsing (RIM-01), search (RIM-06)
  Rollback:       Partial graph on parse errors
  Design:         Builds directed graph of symbols and their references
  Returns:
    - Success: SymbolGraph(symbols, edges)
    - Failure: Partial graph with unresolved refs
end note

== RIM-02 BUILD SymbolGraph ==

user -> router : RIM-02 BUILD SymbolGraph(ast_index)
activate router
router -> agent : RIM-02 BUILD SymbolGraph(ast_index)
activate agent

agent -> rim : RIM-02 BUILD SymbolGraph(ast_index)
activate rim

rim -> graph : RIM-02 BUILD SymbolGraph(ast_index)
activate graph

graph -> graph : extract symbols per file
graph -> graph : resolve cross-file references
graph -> graph : build edges (defines, references, imports)

break Reference resolution fails
  graph --> rim : PartialGraph(unresolved_refs)
end

graph --> rim : SymbolGraph(symbols, edges)
deactivate graph

rim --> agent : SymbolGraph(symbols, edges)
deactivate rim

agent --> router : SymbolGraph(symbols, edges)
deactivate agent
deactivate router

note over user, graph
  Flow:    RIM-02 → User → ServerRouter → AgentOrchestrator → RepoIntelligenceManager → SymbolGraph → extract symbols → resolve refs → build graph
  State:   No state change
  Success: Complete symbol reference graph
  Failure: Partial graph on unresolved references
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim06_search_semantic.puml ---

@startuml sq_rim06_search_semantic
' ============================================================
' Title:     RIM-06 — SEARCH Semantic
' Boundary:  nasim code agent CLI
' Purpose:   Embedding-based code similarity search across repository
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-06 LIST Semantic

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Intelligence Group" #EDE7F6
  participant "SemanticSearch" as search
end box
box "Provider Group" #FFF3E0
  participant "Provider" as provider
end box
box "Storage Group" #F3E5F5
  participant "EmbeddingStore" as embeddings
end box

note over user, embeddings
  Scope:          RIM-06 SEARCH Semantic — embedding-based code similarity search
  Preconditions:  RIM-01 completed (AST index available), EmbeddingStore populated, Provider available
  Contexts:       Called by AgentOrchestrator when user query requires semantic understanding. Complementary to RIM-02 (structural ranking)
  Excludes:       Structural/graph-based search (RIM-02), full-text grep search (TL-02)
  Rollback:       Embedding generation failure -> return empty results; store unavailable -> fall back to keyword search
  Design:         SemanticSearch embeds query via Provider. Cosine similarity against EmbeddingStore. Top-K results with minimum similarity threshold (0.3)
  Returns:
    - Success: SearchResultList(results, scores, snippets)
    - Failure: Empty results with fallback flag
end note

== RIM-06 SEARCH Semantic ==

user -> router : RIM-06 SEARCH Semantic(query, top_k)
activate router
router -> agent : RIM-06 SEARCH Semantic(query, top_k)
activate agent

agent -> search : RIM-06 SEARCH Semantic(query, top_k)
activate search

search -> provider : provider.embed(query_text)
activate provider
provider --> search : query_embedding
deactivate provider

search -> embeddings : embeddings.cosine_search(query_embedding, top_k)
activate embeddings
embeddings --> search : raw_results[]
deactivate embeddings

search -> search : filter_by_threshold(results, min_sim=0.3)

search -> search : format_snippets(filtered_results)

search --> agent : SearchResultList(results, scores, snippets)
deactivate search

agent --> router : SearchResultList(results, scores, snippets)
deactivate agent
deactivate router

note over user, embeddings
  Flow:    RIM-06 → User → ServerRouter → AgentOrchestrator → SemanticSearch → Provider(embed) → EmbeddingStore → SearchResultList
  State:   No state change
  Success: SearchResultList with similarity-scored snippets
  Failure: Embedding failure -> empty results + fallback flag; store unavailable -> keyword fallback
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim03_rank_results.puml ---

@startuml sq_rim03_rank_results
' ============================================================
' Title:     RIM-03 — RANK Results
' Boundary:  nasim code agent CLI
' Purpose:   PageRank ranking with chat-personalization for symbol importance
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-03 RANK Symbols

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Intelligence Group" #EDE7F6
  participant "SymbolRanker" as ranker
  participant "SymbolGraph" as graph
end box
box "Chat Group" #E8F5E9
  participant "ConversationHistory" as history
end box

note over user, history
  Scope:          RIM-03 RANK Symbols — PageRank ranking with chat-personalization
  Preconditions:  RIM-01 completed successfully (SymbolGraph populated), ConversationHistory has chat context
  Contexts:       Called after RIM-01 or when user context shifts. Output feeds into RIM-04
  Excludes:       Embedding-based ranking (RIM-06), file system traversal (RIM-01)
  Rollback:       PageRank convergence failure -> fall back to degree-centrality ranking; empty graph -> empty ranking
  Design:         SymbolRanker runs iterative PageRank on SymbolGraph. Chat personalization boosts symbols mentioned in recent conversation
  Returns:
    - Success: RankedSymbolList(symbols, scores)
    - Failure: Empty list with fallback flag
end note

== RIM-03 RANK Symbols ==

user -> router : RIM-03 RANK Symbols(graph, chat_context)
activate router
router -> agent : RIM-03 RANK Symbols(graph, chat_context)
activate agent

agent -> ranker : RIM-03 RANK Symbols(graph, chat_context)
activate ranker

ranker -> graph : graph.get_adjacency()
activate graph
graph --> ranker : adjacency_map
deactivate graph

ranker -> history : history.get_recent_tokens(last_n=50)
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

agent --> router : RankedSymbolList(symbols, scores)
deactivate agent
deactivate router

note over user, history
  Flow:    RIM-03 → User → ServerRouter → AgentOrchestrator → SymbolRanker → SymbolGraph + ConversationHistory → RankedSymbolList
  State:   No state change
  Success: RankedSymbolList sorted by importance score
  Failure: Convergence failure -> fallback to degree centrality; empty graph -> empty ranking
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim01_index_codebase.puml ---

@startuml sq_rim01_index_codebase
' ============================================================
' Title:     RIM-01 — INDEX Codebase
' Boundary:  nasim code agent
' Purpose:   Build AST index and symbol graph from project source
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-01 INDEX Codebase

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Intelligence Group" #EDE7F6
  participant "RepoIntelligenceManager" as rim
  participant "ASTIndexAdapter" as ast
  participant "SymbolGraph" as graph
end box
box "External" #F5F5F5
  participant "Host Filesystem" as fs
end box

note over user, fs
  Scope:          RIM-01 INDEX Codebase — build AST index and symbol graph from project source
  Preconditions:  Project root accessible, supported source files present
  Contexts:       Called at session start or on-demand; prerequisite for RIM-02/03
  Excludes:       Embedding generation (RIM-05), semantic search (RIM-06)
  Rollback:       Parse error -> skip file, log warning; complete failure -> empty index
  Design:         RepoIntelligenceManager orchestrates pipeline; ASTParser extracts definitions; SymbolGraph builds relationships
  Returns:
    - Success: IndexStats(files, symbols, edges)
    - Failure: Partial index with skipped files
    - Failure: Empty index on complete failure
end note

== RIM-01 INDEX Codebase ==

user -> router : RIM-01 INDEX Codebase(project_root)
activate router
router -> agent : RIM-01 INDEX Codebase(project_root)
activate agent

agent -> rim : RIM-01 INDEX Codebase(project_root)
activate rim

rim -> fs : rim.list_source_files(project_root)
activate fs
fs --> rim : source_files[]
deactivate fs

loop for each source_file
    rim -> ast : ast.parse(source_file)
    activate ast

    break Parse error
        ast --> rim : ParseError(file, reason)
    end

    ast --> rim : ASTNode[]
    deactivate ast

    rim -> graph : graph.extract_symbols(ast_nodes)
    activate graph
    graph --> rim : symbols[]
    deactivate graph

    rim -> graph : graph.link_relationships(symbols)
    activate graph
    graph --> rim : edges[]
    deactivate graph
end

rim -> graph : graph.build_adjacency_index()
activate graph
graph --> rim : adjacency_map
deactivate graph

rim --> agent : IndexStats(files, symbols, edges)
deactivate rim

agent --> router : IndexStats(files, symbols, edges)
deactivate agent
deactivate router

note over user, fs
  Flow:    RIM-01 → User → ServerRouter → AgentOrchestrator → RepoIntelligenceManager → [FileSystem → ASTIndexAdapter → SymbolGraph]* → IndexStats
  State:   No state change
  Success: IndexStats with file count, symbol count, edge count
  Failure: Parse error -> skip file; complete failure -> empty index
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RIM/sq_rim04_inject_repomap.puml ---

@startuml sq_rim04_inject_repomap
' ============================================================
' Title:     RIM-04 — INJECT RepoMap
' Boundary:  nasim code agent CLI
' Purpose:   Token-budgeted repo-map injection into LLM context
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RIM-04 INJECT RepoMap

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repo Intelligence Group" #EDE7F6
  participant "RepoMapInjector" as injector
  participant "SymbolRanker" as ranker
end box
box "Context Group" #E8F5E9
  participant "TokenBudget" as budget
  participant "ConversationHistory" as history
end box

note over user, history
  Scope:          RIM-04 INJECT RepoMap — token-budgeted repo-map injection into context
  Preconditions:  RIM-01 completed (AST index available), RIM-02 completed (symbols ranked), TokenBudget initialized
  Contexts:       Called before each LLM call to provide repository context
  Excludes:       Full file content injection (AGT-02), embedding search results (RIM-06)
  Rollback:       Budget exceeded -> truncate to fit budget; empty index -> inject empty map with warning
  Design:         RepoMapInjector selects top-ranked symbols within token budget. Budget split: 60% structure, 25% snippets, 15% reserves
  Returns:
    - Success: RepoMapContext(text, token_count)
    - Failure: Empty context with warning
end note

== RIM-04 INJECT RepoMap ==

user -> router : RIM-04 INJECT RepoMap(budget_tokens, ranked_symbols)
activate router
router -> agent : RIM-04 INJECT RepoMap(budget_tokens, ranked_symbols)
activate agent

agent -> injector : RIM-04 INJECT RepoMap(budget_tokens, ranked_symbols)
activate injector

injector -> budget : budget.get_available_budget()
activate budget
budget --> injector : available_tokens
deactivate budget

injector -> injector : split_budget(available_tokens, ratios=[0.6, 0.25, 0.15])

injector -> ranker : ranker.get_top_symbols(structure_budget)
activate ranker
ranker --> injector : structure_symbols[]
deactivate ranker

injector -> ranker : ranker.get_relevant_snippets(snippet_budget)
activate ranker
ranker --> injector : snippet_symbols[]
deactivate ranker

injector -> injector : format_repo_map(structure_symbols, snippet_symbols)

injector -> injector : truncate_to_budget(formatted_map, max_tokens)

injector -> history : history.prepend_context(repo_map_text)
activate history
history --> injector : context_injected
deactivate history

injector --> agent : RepoMapContext(text, token_count)
deactivate injector

agent --> router : RepoMapContext(text, token_count)
deactivate agent
deactivate router

note over user, history
  Flow:    RIM-04 → User → ServerRouter → AgentOrchestrator → RepoMapInjector → TokenBudget + SymbolRanker + ConversationHistory → RepoMapContext
  State:   No state change
  Success: RepoMapContext with formatted text within token budget
  Failure: Budget exceeded -> truncate to fit; empty index -> empty map + warning
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RTG/sq_rtg03_classify_task.puml ---

@startuml sq_rtg03_classify_task
' ============================================================
' Title:     RTG-03 — Classify Task
' Boundary:  nasim code agent
' Purpose:   Classify task type and select optimal model
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RTG-03 Classify Task

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Router Group" #EDE7F6
  participant "ModelRouter" as router
end box
box "Repository Group" #E8F5E9
  participant "ModelRepository" as model_repo
end box

note over user, router
  Scope:          RTG-03 CLASSIFY Task — classify task type and select optimal model
  Preconditions:  ModelRouter initialized with model catalog
  Contexts:       Called by AGT-01 or RTG-01
  Excludes:       Model switching, fallback application
  Rollback:       Default model used on classification failure
  Design:         Heuristic or LLM-based classification
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={selected_model, task_type})
    - Failure: Result(success=false, error="classification_failed")
end note

== RTG-03 Classify Task ==

user -> router : types input
router -> agent : RTG-03 PROCESS(user_input)

agent -> router : RTG-03 CLASSIFY Task(task_description, context)

break Classification fails (confidence < 0.6)
    router --> agent : default_model
    agent --> router : AgentEvent(Done)
end

router -> router : RTG-03 EXTRACT Signals(input_length, keywords, traceback, file_content)
router -> router : RTG-03 SCORE TaskType(keyword * 0.4 + context * 0.4 + length * 0.2)
router -> router : RTG-03 SELECT HighestScoring()

router -> router : RTG-03 MAP ModelTier(task_type, ModelCatalog)
router -> router : RTG-03 VERIFY ProviderCapabilities(selected_model)

break Model unavailable
    router -> router : RTG-03 RESOLVE NextModel(FallbackChain)
    router --> agent : Result(success=true, data={selected_model, task_type})
    agent --> router : AgentEvent(Done)
end

router --> agent : Result(success=true, data={selected_model, task_type})

agent --> router : AgentEvent(Done)

note over user, router
  Flow:    RTG-03 -> User -> ServerRouter -> AgentOrchestrator -> ModelRouter -> classify task type -> select optimal model
  State:   No state change
  Success: Result(success=true, data={selected_model, task_type})
  Failure: Result(success=false, error="classification_failed") — default model returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RTG/sq_rtg01_select_model.puml ---

@startuml sq_rtg01_select_model
' ============================================================
' Title:     RTG-01 — SELECT Model
' Boundary:  nasim code agent
' Purpose:   Model selection and fallback routing
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RTG-01 SELECT Model

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Router Group" #EDE7F6
  participant "ModelRouter" as router
  participant "FallbackChain" as fallback
  participant "ProviderCapabilities" as caps
end box
box "Config Group" #FCE4EC
  participant "ConfigLoader" as cfg
end box
box "Provider Group" #FFF3E0
  participant "LiteLLMProxy" as provider
end box
box "Repository Group" #E8F5E9
  participant "ModelRepository" as model_repo
end box

note over user, provider
  Scope:          RTG-01 SELECT Model — model selection and fallback routing
  Preconditions:  ModelRouter initialized, Config loaded
  Contexts:       Called by AGT-01 before PRV-02 REQUEST Chat
  Excludes:       Model switching (RTG-04), task classification (RTG-03)
  Rollback:       Fallback to default model on selection failure
  Design:         Composite strategy: classify task -> select model -> fallback chain
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data=selected_model)
    - Failure: Result(success=false, error="no_supported_model")
end note

== RTG-01 SELECT Model ==

user -> router : types input
router -> agent : RTG-01 PROCESS(user_input)

agent -> router : RTG-01 SELECT Model(task_type)
activate router

router -> cfg : RTG-01 READ ModelConfig()
activate cfg
cfg --> router : Config(model, fallback_chain)
deactivate cfg

router -> router : RTG-01 CLASSIFY Task(input)

router -> caps : RTG-01 READ Capabilities(model)
activate caps
caps --> router : supported_models
deactivate caps

break No supported model found
    router -> fallback : RTG-01 READ DefaultModel()
    activate fallback
    fallback --> router : default_model
    deactivate fallback
    router --> agent : Result(success=false, error="no_supported_model")
    agent --> router : AgentEvent(Error)
end

router -> fallback : RTG-01 RESOLVE Model(primary_model, fallback_chain)
activate fallback
fallback --> router : selected_model
deactivate fallback

router --> agent : Result(success=true, data=selected_model)
deactivate router

agent --> router : AgentEvent(Done)

note over user, provider
  Flow:    RTG-01 -> User -> ServerRouter -> AgentOrchestrator -> ModelRouter -> classify -> check caps -> fallback chain -> return model
  State:   <back:#EDE7F6>ROUTING</back>
  Success: Result(success=true, data=selected_model)
  Failure: Result(success=false, error="no_supported_model") — fallback to default
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RTG/sq_rtg02_apply_fallback.puml ---

@startuml sq_rtg02_apply_fallback
' ============================================================
' Title:     RTG-02 — APPLY Fallback
' Boundary:  nasim code agent
' Purpose:   Apply fallback chain when primary model fails
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RTG-02 UPDATE Fallback

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Router Group" #EDE7F6
  participant "ModelRouter" as router
  participant "FallbackChain" as fallback
end box
box "Provider Group" #FFF3E0
  participant "LiteLLMProxy" as provider
end box
box "Repository Group" #E8F5E9
  participant "ModelRepository" as model_repo
end box

note over user, provider
  Scope:          RTG-02 APPLY Fallback — apply fallback chain when primary model fails
  Preconditions:  FallbackChain initialized with model list
  Contexts:       Called by RTG-01 when primary model unavailable
  Excludes:       Model selection (RTG-01), task classification (RTG-03)
  Rollback:       Return error if all models in chain fail
  Design:         Circuit breaker pattern with exponential backoff
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data=selected_model)
    - Failure: Result(success=false, error="all_models_unavailable")
end note

== RTG-02 APPLY Fallback ==

user -> router : types input
router -> agent : RTG-02 PROCESS(user_input)

agent -> router : RTG-02 APPLY Fallback(primary_model, chain)
activate router

router -> fallback : RTG-02 APPLY Fallback(primary_model, chain)
activate fallback

loop for each model in fallback_chain
    fallback -> provider : RTG-02 CHECK Availability(model)
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
    router --> agent : Result(success=false, error="all_models_unavailable")
    agent --> router : AgentEvent(Error)
end

router --> agent : Result(success=true, data=selected_model)
deactivate router

agent --> router : AgentEvent(Done)

note over user, provider
  Flow:    RTG-02 -> User -> ServerRouter -> AgentOrchestrator -> ModelRouter -> FallbackChain -> check each model -> return first available
  State:   No state change
  Success: Result(success=true, data=selected_model)
  Failure: Result(success=false, error="all_models_unavailable") — all models unavailable
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/RTG/sq_rtg04_switch_model.puml ---

@startuml sq_rtg04_switch_model
' ============================================================
' Title:     RTG-04 — Switch Model
' Boundary:  nasim code agent
' Purpose:   Change the active model at runtime
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — RTG-04 UPDATE Model

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Router Group" #EDE7F6
  participant "ModelRouter" as router
end box

note over user, router
  Scope:          RTG-04 SWITCH Model — change active model via CLI or agent request
  Preconditions:  Target model available in catalog
  Contexts:       Called by CLI-07 SWITCH Model or AGT-01
  Excludes:       Model classification, fallback
  Rollback:       Previous model restored on switch failure
  Design:         Atomic config update; validates model availability
  Classification: Process Decomposition
  Returns:
    - Success: Result(success=true, data={previous_model, new_model})
    - Failure: Result(success=false, error="model_not_available")
end note

== RTG-04 Switch Model ==

user -> router : types input
router -> agent : RTG-04 PROCESS(user_input)

agent -> router : RTG-04 SWITCH Model(target_model)

break Model not in catalog
    router --> agent : Error("model not available")
    agent --> router : AgentEvent(Error)
end

router -> router : RTG-04 VALIDATE ModelAvailability(target_model)
router -> router : RTG-04 UPDATE ActiveModelConfig(target_model)

router --> agent : Result(success=true, data={previous_model, new_model})

agent --> router : AgentEvent(Done)

note over user, router
  Flow:    RTG-04 -> User -> ServerRouter -> AgentOrchestrator -> ModelRouter -> validate -> update config -> return
  State:   Active model updated
  Success: Result(success=true, data={previous_model, new_model})
  Failure: Result(success=false, error="model_not_available") — error returned
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx06_track_token_budget.puml ---

@startuml sq_ctx06_track_token_budget
' ============================================================
' Title:     CTX-06 — Track Token Budget
' Boundary:  nasim code agent CLI
' Purpose:   Track token count as messages are added
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
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
  Returns:        ok on success; COMPACT_NEEDED when budget exceeded
end note

== CTX-01 Track Token Count ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> history : CTX-06 ADD_MESSAGE(msg)
history -> history : self.messages.append(msg)
history -> history : self.token_count += estimate_tokens(msg)

alt token_count > context_budget
    history --> agent : COMPACT_NEEDED
    agent -> agent : trigger CTX-02 (COMPACT Context)
else within budget
    history --> agent : ok
end

agent --> router : AgentEvent(Done)

note over agent, history
  Flow:    User → ServerRouter → AgentOrchestrator → message → append → estimate tokens → check budget
  State:   No state change (or triggers COMPACTING)
  Success: Message added, token count updated
  Failure: N/A
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx01_process_context.puml ---

@startuml sq_ctx01_process_context
' ============================================================
' Title:     CTX-01 — PROCESS Context
' Boundary:  nasim code agent
' Purpose:   Orchestrate context processing pipeline stages
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    CAR audit 2026-06-26 (moved PipelineOrchestrator to Context Graph Group, removed TokenBudgetTracker phantom)
' ============================================================

title nasim — CTX-01 PROCESS Context

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Context Graph Group" #E0F2F1
  participant "PipelineOrchestrator" as pipeline
  participant "ContextGraph" as graph
  participant "ContextPrioritizer" as prioritizer
end box

note over agent, prioritizer
  Scope:          Orchestrate context processing pipeline stages in order
  Preconditions:  ContextGraph initialized, budget set
  Contexts:       Called by AGT-01 when context needs processing
  Excludes:       Individual processor logic (CTX-02..05)
  Rollback:       Pipeline failure returns partial context
  Design:         PipelineOrchestrator tracks token budget and drives stages: compact -> score -> truncate -> distill -> inject
  Classification: Process Decomposition
  Returns:        ProcessedContext on success; partial context on failure
end note

== CTX-01 PROCESS Context ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> pipeline : CTX-01 PROCESS(graph, budget)
activate pipeline

pipeline -> pipeline : check token budget, identify overage

ref over pipeline, graph
  CTX-05: COMPACT Nodes
end ref

pipeline -> pipeline : score node priorities

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

agent --> router : AgentEvent(Done)

note over agent, prioritizer
  Flow:    User → ServerRouter → AgentOrchestrator → PipelineOrchestrator → compact → score → truncate → distill → inject
  State:   No state change
  Success: Optimized context graph within budget
  Failure: Processor failure returns partial context
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx03_distill_nodes.puml ---

@startuml sq_ctx03_distill_nodes
' ============================================================
' Title:     CTX-03 — Distill Nodes
' Boundary:  nasim code agent CLI
' Purpose:   Summarize old message exchanges into compact form
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ContextCompactor" as compactor
end box
box "Provider Group" #FFF3E0
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
  Returns:        summary message on success; truncated raw content on failure
end note

== CTX-03 Summarize Old Exchanges ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> compactor : CTX-03 DISTILL(messages)
compactor -> compactor : build prompt: "Summarize these exchanges concisely"
compactor -> provider : chat([summary_prompt + old_messages])

break Summary is empty or provider fails
    provider --> compactor : empty/error
    compactor -> compactor : use truncated raw content as summary
end

provider --> compactor : summary text
compactor -> compactor : create summary message {role: "system", content: summary}
compactor --> compactor : return summary message

agent --> router : AgentEvent(Done)

note over compactor, provider
  Flow:    User → ServerRouter → AgentOrchestrator → select old → build prompt → LLM summarize → summary message
  State:   <back:#E0F2F1>COMPACTING</back>
  Success: Summary message ready to replace old exchanges
  Failure: Empty summary -> truncated raw fallback
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx05_compact_nodes.puml ---

@startuml sq_ctx05_compact_nodes
' ============================================================
' Title:     CTX-05 — Compact Nodes
' Boundary:  nasim code agent CLI
' Purpose:   Merge overlapping context nodes to reduce token usage
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CTX-05 COMPACT Nodes

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Context Group" #E8EAF6
  participant "PipelineOrchestrator" as pipe
  participant "CompactionProcessor" as comp
end box
box "Provider Group" #FFF3E0
  participant "Provider" as provider
end box

note over pipe, provider
  Scope:          Merge overlapping context nodes to reduce token usage
  Preconditions:  Context graph has overlapping or redundant nodes
  Contexts:       Called when token budget is tight and nodes overlap
  Excludes:       Context injection (CTX-04), token tracking (CTX-06)
  Rollback:       Merge failure → retain original nodes
  Design:         Identifies overlapping nodes and merges via secondary LLM or heuristics
  Classification: Process Decomposition
  Returns:        CompactionResult(nodes_removed, tokens_saved) on success; CompactionResult(nodes_dropped, tokens_saved) on failure
end note

== CTX-05 Compact Nodes ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> pipe : CTX-05 COMPACT(graph, budget)
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

agent --> router : AgentEvent(Done)

break Secondary LLM merge fails
    provider --> comp : ProviderError
    comp -> comp : fallback: drop lowest-ranked nodes
    comp --> pipe : CompactionResult(nodes_dropped, tokens_saved)
end

note over pipe, provider
  Flow:    User → ServerRouter → AgentOrchestrator → PipelineOrchestrator → CompactionProcessor → find overlapping nodes → merge → return
  State:   <back:#E0F2F1>COMPACTING</back> → READY
  Success: Nodes compacted, token count reduced
  Failure: LLM merge fails → drop lowest-ranked nodes
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx04_inject_context.puml ---

@startuml sq_ctx04_inject_context
' ============================================================
' Title:     CTX-04 — Inject Context
' Boundary:  nasim code agent CLI
' Purpose:   Retrieve and inject context into the reasoning graph
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CTX-04 INJECT Context

box "Context Group" #E8EAF6
  participant "PipelineOrchestrator" as pipe
  participant "InjectionProcessor" as inj
end box
box "RIM Group" #F3E5F5
  participant "RepoIndex" as rim
end box
actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box

note over pipe, agent
  Scope:          Retrieve relevant context and inject into reasoning graph
  Preconditions:  PipelineOrchestrator active, RepoIndex available
  Contexts:       Called before LLM call to enrich prompt context
  Excludes:       Context compaction (CTX-02/05), token tracking (CTX-06)
  Rollback:       Injection failure → proceed with existing context
  Design:         InjectionProcessor queries RepoIndex for relevant code/docs
  Classification: Process Decomposition
  Returns:        InjectionResult(nodes_added, tokens_used) on success; InjectionResult(0, 0) on failure
end note

== CTX-04 Inject Context ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> pipe : CTX-04 INJECT(task_description, graph)
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

agent --> router : AgentEvent(Done)

break RepoIndex unavailable
    rim --> inj : IndexError
    inj -> inj : skip injection
    inj --> pipe : InjectionResult(0, 0)
end

note over pipe, agent
  Flow:    User → ServerRouter → AgentOrchestrator → PipelineOrchestrator → InjectionProcessor → retrieve context → inject into graph
  State:   INJECTING → READY
  Success: Context nodes injected, token count updated
  Failure: Index unavailable → skip, proceed with existing context
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CTX/sq_ctx02_compact_context.puml ---

@startuml sq_ctx02_compact_context
' ============================================================
' Title:     CTX-02 — COMPACT Context
' Boundary:  nasim code agent
' Purpose:   Compact context when token budget exceeded
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ConversationHistory" as history
  participant "ContextCompactor" as compactor
end box
box "Provider Group" #FFF3E0
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
  Returns:        shortened messages on success; truncated messages on failure
end note

== CTX-02 COMPACT Context ==

user -> router : types input
router -> agent : PROCESS(user_input)
agent -> history : CTX-02 COMPACT(messages, budget)
compactor -> compactor : query ContextPrioritizer for node importance scores
compactor -> compactor : sort nodes by ascending importance (lowest first)
compactor -> compactor : protect system prompt nodes (never truncated)
compactor -> compactor : drop lowest-importance nodes until within budget
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

agent --> router : AgentEvent(Done)

note over history, provider
  Flow:    User → ServerRouter → AgentOrchestrator → budget exceeded → select old → summarize → replace
  State:   <back:#E0F2F1>COMPACTING</back> -> <back:#FFF3E0>THINKING</back>
  Success: Messages shortened, token count reduced
  Failure: LLM fails -> truncate fallback
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli07_switch_model.puml ---

@startuml sq_cli07_switch_model
' ============================================================
' Title:     CLI-07 — Switch Model
' Boundary:  nasim code agent CLI
' Purpose:   Switch active model via slash command
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CLI-07 UPDATE Model

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
  participant "SlashCommandHandler" as cmd
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Routing Group" #E8EAF6
  participant "RTGModelRouter" as rtg
end box
box "Repository Group" #E8F5E9
  participant "SessionRepository" as session_repo
end box

note over user, rtg
  Scope:          Switch active model via /model slash command
  Preconditions:  ServerRouter active, model registry available
  Contexts:       Invoked by Developer via /model command
  Excludes:       Provider registration (PRV-01), fallback logic (RTG-02)
  Rollback:       Model not found → display error, retain current model
  Design:         Delegates to RTG-04 SWITCH Model for actual provider switch
  Classification: Primary Orchestrator
  Returns:        Active model switched, confirmation shown
end note

== CLI-07 Switch Model ==

user -> repl : "/model {model_name}"
result -> cmd : dispatch("/model {model_name}")
activate cmd

cmd -> cmd : parse model name
cmd -> rtg : switchModel(model_name)
activate rtg

rtg -> rtg : validate model availability
rtg -> rtg : update active model pointer

rtg --> cmd : ModelSwitched(new_model)
deactivate rtg

cmd --> repl : CommandResult("Switched to {model_name}")
deactivate cmd


break Model not found
    rtg --> cmd : ModelNotFoundError
    cmd --> repl : CommandError
end

note over user, rtg
  Flow:    CLI-07 switchModel: User → ServerRouter → SlashCommandHandler → RTG-04 SWITCH Model → confirm
  State:   <back:#ECEFF1>IDLE</back> → SWITCHING → <back:#ECEFF1>IDLE</back>
  Success: Model switched, confirmation shown
  Failure: Model not found → display error, retain current
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli03_stream_output.puml ---

@startuml sq_cli03_stream_output
' ============================================================
' Title:     CLI-03 — Stream Output
' Boundary:  nasim code agent CLI
' Purpose:   Streaming token-by-token output with rich formatting
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
end box
box "Service Group" #F3E5F5
  participant "Renderer" as renderer
end box
box "Repository Group" #E8F5E9
  participant "SessionRepository" as session_repo
end box

note over user, renderer
  Scope:          Rendering AgentEvents to terminal
  Preconditions:  Agent event stream active
  Contexts:       Called by CLI-01 (PROCESS User Input)
  Excludes:       Agent loop logic, tool execution
  Rollback:       N/A — renderer is passive consumer
  Design:         Uses Rich library for colors, diffs, formatting
  Classification: Primary Orchestrator
  Returns:        Developer sees formatted terminal output
end note

== CLI-03 STREAM Output ==

result -> renderer : subscribe to AgentEvent stream

loop for each event
    alt TextChunk event
        result -> renderer : TextChunk(text)
        renderer -> renderer : colored output (green for nasim>)
        renderer --> user : streamed token
    else ToolStart event
        result -> renderer : ToolStart(name, args)
        renderer -> renderer : dimmed box with tool name + args
        renderer --> user : tool call display
    else ToolResult event
        result -> renderer : ToolResult(name, result, truncated)
        renderer -> renderer : truncated result (max 200 chars)
        renderer --> user : tool result preview
    else Error event
        result -> renderer : Error(message)
        renderer -> renderer : red highlight
        renderer --> user : error display
    else Done event
        result -> renderer : Done()
        renderer -> renderer : newline + reset
    end
end

note over user, renderer
  Flow:    CLI-03 streamOutput: Event stream -> Renderer -> formatted terminal output
  State:   No state change
  Success: All events rendered with appropriate formatting
  Failure: N/A — renderer is passive
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli01_process_user_input.puml ---

@startuml sq_cli01_process_user_input
' ============================================================
' Title:     CLI-01 — PROCESS User Input (API-First)
' Boundary:  nasim CLI Interface Container
' Purpose:   REPL input loop routes through API, renders SSE output
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

title nasim — CLI-01 PROCESS User Input (API-First)

actor "User" as user

box "CLI Interface Container" #E8F5E9
  participant "ServerRouter" as router
  participant "Renderer" as renderer
end box
box "API Group (Entry Gate)" #E8EAF6
  participant "ServerRouter" as router
  participant "APISchema" as schema
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
  participant "ErrorBoundary" as eb
end box
box "Observability Group" #E0F2F1
  participant "StructuredLogger" as logger
end box

note over user, logger
  Scope:          Single user input processing cycle (API-First)
  Preconditions:  REPL initialized, API (ServerRouter) available
  Contexts:       Called by main REPL loop
  Excludes:       Slash commands (CLI-02), session persistence (API-01..05)
  Rollback:       Error -> display error via Renderer -> return to IDLE
  Design:         CLI routes ALL requests through API (ServerRouter). No bypass to core.
                  ErrorBoundary handles all agent failures. AIP-193 error format.
  Classification: Interface Container → API Entry Gate → Core Service
  Returns:        User sees rendered output or error display
end note

== CLI-01 PROCESS User Input (API-First) ==

user -> repl : types input

ref over repl, logger
  OBS-01: STREAM Structured Log (user input received)
end ref

result -> result : check for slash command

alt is slash command
    ref over repl
      CLI-02: DISPATCH Slash Command (routes through API)
    end ref
else normal input
    result -> schema : validate(request_body)
    schema --> repl : ValidatedDispatchRequest

    repl -> router : API-06 DISPATCH Message(session_id, message)
    activate router

    hnote over router #E0F7FA : **State: SERVING**

    router -> agent : dispatchMessage(session_id, message)
    activate agent

    hnote over agent #FFF3E0 : **State: THINKING**

    ref over agent
      AGT-01: PROCESS User Task
    end ref

    agent --> router : AgentEventStream

    router --> repl : SSE stream (AgentEvents)

    hnote over repl #E8F5E9 : **State: RESPONDING**

    loop for each AgentEvent
        alt TextChunk event
            result -> renderer : render TextChunk
            renderer --> user : streamed token
        else ToolStart event
            result -> renderer : render ToolStart
            renderer --> user : tool call display
        else ToolResult event
            result -> renderer : render ToolResult
            renderer --> user : tool result preview
        else Done event
            result -> renderer : render Done
            renderer --> user : formatted output
        end
    end

    deactivate agent
    deactivate router
end

break Agent throws exception
    agent -> eb : handle(Exception)
    activate eb
    eb --> agent : RecoveryAction(retry/abort)
    deactivate eb
    agent --> router : AgentError
    router --> repl : 502 UNAVAILABLE {error: {code: "UNAVAILABLE", message: "Agent error"}}
    ref over repl, logger
      OBS-01: STREAM Structured Log (error)
    end ref
    result -> renderer : render Error event
    renderer --> user : red error display
end

hnote over repl #ECEFF1 : **State: IDLE**

note over user, logger
  Flow:    CLI-01 processUserInput: User -> ServerRouter -> API(ServerRouter) -> AgentOrchestrator -> [AGT-01] -> SSE stream -> Renderer -> User
  State:   <back:#ECEFF1>IDLE</back> -> <back:#E8EAF6>LISTENING</back> -> <back:#E0F7FA>SERVING</back> -> <back:#FFF3E0>THINKING</back> -> [<back:#F3E5F5>TOOL_EXEC</back>]* -> <back:#E8F5E9>RESPONDING</back> -> <back:#ECEFF1>IDLE</back>
  Success: SSE stream rendered to user via CLI Renderer
  Failure: Agent error -> ErrorBoundary -> 502 UNAVAILABLE -> IDLE
  Invariant: CLI NEVER calls AgentOrchestrator directly. ALL paths go through API (ServerRouter).
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli05_enable_plan_mode.puml ---

@startuml sq_cli05_enable_plan_mode
' ============================================================
' Title:     CLI-05 — Enable Plan Mode
' Boundary:  nasim code agent CLI
' Purpose:   Toggle plan mode via slash command
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CLI-05 ENABLE Plan Mode

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
  participant "SlashCommandHandler" as cmd
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box

note over user, agent
  Scope:          Toggle plan mode on/off via slash command
  Preconditions:  ServerRouter active, SlashCommandHandler registered
  Contexts:       Invoked by Developer via /plan-mode command
  Excludes:       Plan execution (AGT-07/08), model switching (CLI-07)
  Rollback:       Toggle failure → display error, retain current state
  Design:         Plan mode flag stored in session state; affects AGT-01 loop behavior
  Classification: Primary Orchestrator
  Returns:        Plan mode state toggled, confirmation shown
end note

== CLI-05 Enable Plan Mode ==

user -> repl : "/plan-mode"
result -> cmd : dispatch("/plan-mode")
activate cmd

cmd -> cmd : parse command arguments
cmd -> cmd : toggle plan_mode flag

cmd -> agent : setPlanMode(enabled/disabled)
activate agent
agent --> cmd : planModeUpdated
deactivate agent

cmd --> repl : CommandResult(confirmation)
deactivate cmd


break Toggle error
    cmd --> repl : CommandError
end

note over user, agent
  Flow:    CLI-05 enablePlanMode: User → ServerRouter → SlashCommandHandler → toggle → confirm
  State:   <back:#ECEFF1>IDLE</back> → TOGGLING → <back:#ECEFF1>IDLE</back>
  Success: Plan mode toggled, confirmation shown
  Failure: Toggle error → display error, retain state
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli08_list_sessions.puml ---

@startuml sq_cli08_list_sessions
' ============================================================
' Title:     CLI-08 — List Sessions
' Boundary:  nasim code agent CLI
' Purpose:   List sessions via slash command
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CLI-08 LIST Sessions

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ServerRouter" as router
  participant "SlashCommandHandler" as cmd
end box
box "Service Group" #F3E5F5
end box
box "Repository Group" #E8F5E9
  participant "SessionStore" as ssn
end box

note over user, ssn
  Scope:          List available sessions via /sessions slash command
  Preconditions:  ServerRouter active, SessionStore initialized
  Contexts:       Invoked by Developer via /sessions command
  Excludes:       Session read (SSN-02), session persist (SSN-01)
  Rollback:       Read error → display error message
  Design:         Delegates to SSN-03 LIST Sessions for actual retrieval
  Classification: Primary Orchestrator
  Returns:        Session list formatted and displayed
end note

== CLI-08 List Sessions ==

user -> router : "/sessions"
activate router
router -> cmd : dispatch("/sessions")
activate cmd

cmd -> ssn_svc : CLI-08 LIST Sessions()
activate ssn_svc

ssn_svc -> ssn : listSessions()
activate ssn

ssn -> ssn : scan session directory
ssn --> ssn_svc : sessionList [id, created_at, summary]
deactivate ssn

ssn_svc --> cmd : ListSessionsResponse {sessions: [...]}
deactivate ssn_svc

cmd -> cmd : format session table

cmd --> router : CommandResult(formatted_table)
deactivate cmd

router --> user : displayed session list
deactivate router

break Session directory unreadable [500]
    ssn --> ssn_svc : IOError
    ssn_svc --> cmd : 500 INTERNAL
    cmd --> router : CommandError
    router --> user : "Failed to list sessions"
end

note over user, ssn
  Flow:    CLI-08 listSessions: User → ServerRouter → SlashCommandHandler → SSN-03 LIST Sessions → display
  State:   <back:#ECEFF1>IDLE</back> → LISTING → <back:#ECEFF1>IDLE</back>
  Success: Session list formatted and displayed
  Failure: Directory error → display error
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli02_dispatch_slash_command.puml ---

@startuml sq_cli02_dispatch_slash_command
' ============================================================
' Title:     CLI-02 — Dispatch Slash Command
' Boundary:  nasim code agent CLI
' Purpose:   Slash command routing and execution
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
  participant "SlashCommandHandler" as cmd
  participant "Renderer" as renderer
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Repository Group" #E8F5E9
  participant "SessionRepository" as session_repo
end box

note over user, agent
  Scope:          Slash command parsing and dispatch
  Preconditions:  REPL running, input starts with /
  Contexts:       Called by CLI-01 (PROCESS User Input)
  Excludes:       Normal user input (CLI-01)
  Rollback:       Unknown command -> error message
  Design:         Commands: /help, /reset, /model, /quit, /plan, /sessions
  Classification: Primary Orchestrator
  Returns:        Developer sees command result or error message
end note

== CLI-02 Execute Slash Command ==

user -> repl : /command
result -> cmd : dispatch("/command")
cmd -> cmd : parse command name and args

alt /help
    cmd -> renderer : displayHelpText()
    renderer --> user : help menu
else /reset
    cmd -> agent : reset()
    agent -> agent : clear conversation history
    cmd -> renderer : displayConfirmation("History cleared.")
    renderer --> user : confirmation
else /model
    cmd -> renderer : displayModelInfo()
    renderer --> user : model info
else /plan
    cmd -> agent : togglePlanMode()
    agent -> agent : toggle PLANNING state
    cmd -> renderer : displayConfirmation("Plan mode: ON/OFF")
    renderer --> user : confirmation
else /sessions
    cmd -> renderer : displaySessionList()
    renderer --> user : session list
else /quit or /exit
    cmd -> repl : signal exit
else unknown command
    cmd -> renderer : displayError("Unknown command: /cmd")
    renderer --> user : error display
end

note over user, agent
  Flow:    CLI-02 dispatchSlashCommand: /cmd -> SlashCommandHandler -> action -> Renderer -> User
  State:   No state change (except /plan toggles PLANNING, /reset clears history)
  Success: Command action completed
  Failure: Unknown command -> error message
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli04_read_cli_arguments.puml ---

@startuml sq_cli04_read_cli_arguments
' ============================================================
' Title:     CLI-04 — Read CLI Arguments
' Boundary:  nasim code agent CLI
' Purpose:   Startup argument parsing and config initialization
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "Controller Group" #E3F2FD
  participant "ArgParser" as parser
end box
box "Service Group" #F3E5F5
  participant "ConfigLoader" as cfg
end box
box "Repository Group" #E8F5E9
  participant "SessionRepository" as session_repo
end box

note over user, cfg
  Scope:          CLI argument parsing and config initialization
  Preconditions:  Developer invokes nasim command
  Contexts:       Entry point for all CLI invocations
  Excludes:       Runtime input processing (CLI-01)
  Rollback:       Invalid args -> print usage -> exit(1)
  Design:         Args override config; layered resolution
  Classification: Primary Orchestrator
  Returns:        Config object ready for REPL or single-shot execution
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
  Flow:    CLI-04 readCliArguments: argv -> ArgParser -> ConfigLoader -> layered merge -> Config
  State:   No state change
  Success: Config object ready for component initialization
  Failure: Invalid args or config -> error + exit
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CLI/sq_cli06_request_approval.puml ---

@startuml sq_cli06_request_approval
' ============================================================
' Title:     CLI-06 — Request Approval
' Boundary:  nasim code agent CLI
' Purpose:   Display approval prompt and collect developer decision
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CLI-06 REQUEST Approval

actor "User" as user

box "Controller Group" #E3F2FD
  participant "Renderer" as renderer
end box
box "Service Group" #F3E5F5
  participant "AgentOrchestrator" as agent
end box
box "Safety Group" #FFF9C4
  participant "SafetyCoordinator" as safety
end box
box "Repository Group" #E8F5E9
  participant "SessionRepository" as session_repo
end box

note over user, safety
  Scope:          Display approval prompt for dangerous operations and collect decision
  Preconditions:  SafetyCoordinator flagged operation requiring approval
  Contexts:       Called by AGT-02 when tool requires user confirmation
  Excludes:       Permission checks (SAF-01), auto-approve scenarios
  Rollback:       Timeout → default deny
  Design:         Renderer displays prompt; blocks until user responds or timeout
  Classification: Primary Orchestrator
  Returns:        Approval decision (Approved/Denied) returned to AgentOrchestrator
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
  Flow:    CLI-06 requestApproval: AgentOrchestrator → Renderer → display prompt → User → decision
  State:   PENDING → APPROVED | DENIED
  Success: Developer decision returned to agent
  Failure: Timeout → default deny
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk06_validate_hook_result.puml ---

@startuml sq_hk06_validate_hook_result
' ============================================================
' Title:     HK-06 — VALIDATE Hook Result
' Boundary:  nasim code agent
' Purpose:   Validate a HookResult for correctness and safety
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-06 VALIDATE Hook Result

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hooks
end box
box "Repository Group" #E8F5E9
  participant "HookRepository" as hook_repo
end box

note over user, hooks
  Scope:          HK-06 VALIDATE Hook Result
  Preconditions:  HookResult produced by a hook
  Contexts:       Called internally by HookManager after each hook execution
  Excludes:       Hook execution, hook registration
  Rollback:       Invalid result treated as DENY
  Design:         Ensures result schema compliance
  Classification: Process Decomposition
  Returns:
    - Success: HookResult(validated) — action in [ALLOW, DENY, MODIFY]
    - Failure: HookResult(action=DENY) — invalid schema or unknown action
end note

== HK-06 VALIDATE Hook Result ==

user -> router : invoke agent
activate router
router -> agent : hk06 VALIDATE Hook Result(hook_result)
activate agent
agent -> hooks : hk06 VALIDATE Hook Result(hook_result)
activate hooks
hooks -> hooks : hk06 CHECK Schema(hook_result)

break Result schema invalid
    hooks --> agent : HookResult(action=DENY)
    agent --> router : HookResult(action=DENY)
end

break action not in [ALLOW, DENY, MODIFY]
    hooks --> agent : HookResult(action=DENY)
    agent --> router : HookResult(action=DENY)
end

hooks --> agent : validated result
deactivate hooks
agent --> router : validated result
deactivate agent
deactivate router

note over user, hooks
  Flow:    HK-06 → HookManager → validate HookResult → allow/deny/modify → return validated result
  State:   No state change
  Success: HookResult(validated) — action in [ALLOW, DENY, MODIFY]
  Failure: HookResult(action=DENY) — invalid schema or unknown action
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk03_dispatch_post_tool_hook.puml ---

@startuml sq_hk03_dispatch_post_tool_hook
' ============================================================
' Title:     HK-03 — DISPATCH Post-Tool Hook
' Boundary:  nasim code agent
' Purpose:   Execute hooks after tool execution
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-03 DISPATCH Post-Tool Hook

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as tools
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box
box "Repository Group" #E8F5E9
  participant "HookRepository" as hook_repo
end box

note over user, hook
  Scope:          HK-03 DISPATCH Post-Tool Hook
  Preconditions:  Tool execution completed, hooks registered for PostToolCall event
  Contexts:       Called by AGT-02 (DISPATCH Tool Call) after tool execution
  Excludes:       Pre-tool hooks (HK-02), LLM hooks (HK-04/05)
  Rollback:       Hook failure logged; pipeline continues
  Design:         Priority-ordered execution; short-circuit on deny
  Classification: Process Decomposition
  Returns:
    - Success: HookResult(action=ALLOW, modified_result?) — pipeline continues
    - Failure: HookResult(action=DENY, reason) — tool result blocked
end note

== HK-03 DISPATCH Post-Tool Hook ==

user -> router : invoke agent
activate router
router -> agent : hk03 DISPATCH Post-Tool Hook(tool_name, result)
activate agent
agent -> tools : agt02 EXECUTE Tool(tool_name, args)
activate tools
tools --> agent : ToolResult
deactivate tools

agent -> hooks : hk03 DISPATCH Post-Tool Hook(tool_name, result)
activate hooks
hooks -> hooks : hk03 FIND Hooks For Event(PostToolCall)

loop for each hook in priority order
    hooks -> hook : hk03 EXECUTE Hook(tool_name, result)
    activate hook
    hook --> hooks : HookResult(action, data?)
    deactivate hook

    break action == DENY
        hooks --> agent : HookResult(action=DENY, reason)
        agent --> router : HookResult(action=DENY)
    end
end

hooks --> agent : HookResult(action=ALLOW, modified_result?)
deactivate hooks
agent --> router : HookResult(action=ALLOW)
deactivate agent
deactivate router

note over user, hook
  Flow:    HK-03 → tool execution → HookManager → find hooks → execute in priority order → return HookResult
  State:   No state change
  Success: HookResult(action=ALLOW) — pipeline continues
  Failure: HookResult(action=DENY) — tool result blocked
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk05_dispatch_post_llm_hook.puml ---

@startuml sq_hk05_dispatch_post_llm_hook
' ============================================================
' Title:     HK-05 — DISPATCH Post-LLM Hook
' Boundary:  nasim code agent
' Purpose:   Execute hooks after LLM call completes
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-05 DISPATCH Post-LLM Hook

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box
box "Repository Group" #E8F5E9
  participant "HookRepository" as hook_repo
end box

note over user, hook
  Scope:          HK-05 DISPATCH Post-LLM Hook
  Preconditions:  LLM call completed, hooks registered for PostLLMCall event
  Contexts:       Called by AGT-01 (PROCESS User Task) after PRV-02
  Excludes:       Pre-LLM hooks (HK-04), tool hooks (HK-02/03)
  Rollback:       Hook failure logged; pipeline continues
  Design:         Priority-ordered execution; short-circuit on deny
  Classification: Process Decomposition
  Returns:
    - Success: HookResult(action=ALLOW, modified_data?) — pipeline continues
    - Failure: HookResult(action=DENY, reason) — LLM result blocked
end note

== HK-05 DISPATCH Post-LLM Hook ==

user -> router : invoke agent
activate router
router -> agent : hk05 DISPATCH Post-LLM Hook(llm_result)
activate agent
agent -> hooks : hk05 DISPATCH Post-LLM Hook(llm_result)
activate hooks
hooks -> hooks : hk05 FIND Hooks For Event(PostLLMCall)

loop for each hook in priority order
    hooks -> hook : hk05 EXECUTE Hook(llm_result)
    activate hook
    hook --> hooks : HookResult(action, data?)
    deactivate hook

    break action == DENY
        hooks --> agent : HookResult(action=DENY, reason)
        agent --> router : HookResult(action=DENY)
    end
end

hooks --> agent : HookResult(action=ALLOW, modified_data?)
deactivate hooks
agent --> router : HookResult(action=ALLOW)
deactivate agent
deactivate router

note over user, hook
  Flow:    HK-05 → HookManager → find hooks → execute in priority order → return HookResult
  State:   No state change
  Success: HookResult(action=ALLOW) — pipeline continues
  Failure: HookResult(action=DENY) — LLM result blocked
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk02_dispatch_pre_tool_hook.puml ---

@startuml sq_hk02_dispatch_pre_tool_hook
' ============================================================
' Title:     HK-02 — DISPATCH Pre-Tool Hook
' Boundary:  nasim code agent
' Purpose:   Execute hooks before tool execution
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-02 DISPATCH Pre-Tool Hook

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box
box "Tool Group" #F3E5F5
  participant "ToolRegistry" as tools
end box
box "Repository Group" #E8F5E9
  participant "HookRepository" as hook_repo
end box

note over user, tools
  Scope:          HK-02 DISPATCH Pre-Tool Hook
  Preconditions:  Hooks registered for PreToolCall event
  Contexts:       Called by AGT-02 (DISPATCH Tool Call) before tool execution
  Excludes:       Post-tool hooks (HK-03), LLM hooks (HK-04/05)
  Rollback:       Hook deny blocks tool execution
  Design:         Priority-ordered execution; short-circuit on deny
  Classification: Process Decomposition
  Returns:
    - Success: HookResult(action=ALLOW, modified_args?) — tool execution proceeds
    - Failure: HookResult(action=DENY, reason) — tool execution blocked
end note

== HK-02 DISPATCH Pre-Tool Hook ==

user -> router : invoke agent
activate router
router -> agent : hk02 DISPATCH Pre-Tool Hook(tool_name, args)
activate agent
agent -> hooks : hk02 DISPATCH Pre-Tool Hook(tool_name, args)
activate hooks
hooks -> hooks : hk02 FIND Hooks For Event(PreToolCall)

loop for each hook in priority order
    hooks -> hook : hk02 EXECUTE Hook(tool_name, args)
    activate hook
    hook --> hooks : HookResult(action, data?)
    deactivate hook

    break action == DENY
        hooks --> agent : HookResult(action=DENY, reason)
        agent --> router : HookResult(action=DENY)
    end
end

hooks --> agent : HookResult(action=ALLOW, modified_args?)
deactivate hooks
agent --> router : HookResult(action=ALLOW)
deactivate agent
deactivate router

note over user, tools
  Flow:    HK-02 → HookManager → find hooks → execute in priority order → return HookResult
  State:   No state change
  Success: HookResult(action=ALLOW) — tool execution proceeds
  Failure: HookResult(action=DENY) — tool execution blocked
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk01_register_hook.puml ---

@startuml sq_hk01_register_hook
' ============================================================
' Title:     HK-01 — REGISTER Hook
' Boundary:  nasim code agent
' Purpose:   Register a hook in the HookManager
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-01 REGISTER Hook

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Plugins Group" #EDE7F6
  participant "PluginLoader" as loader
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box
box "Repository Group" #E8F5E9
  participant "HookRepository" as hook_repo
end box

note over user, hook
  Scope:          HK-01 REGISTER Hook
  Preconditions:  HookManager initialized, PluginLoader active
  Contexts:       Called by PLG-04 (REGISTER Plugin Hooks)
  Excludes:       Hook execution (HK-02..05), hook validation (HK-06)
  Rollback:       Registration failure logged, hook not added
  Design:         PluginLoader registers plugin-provided hooks at load time
  Classification: Process Decomposition
  Returns:
    - Success: Hook(registered) — hook instance appended to registry
    - Failure: Warning logged — duplicate hook name skipped
end note

== HK-01 REGISTER Hook ==

user -> router : invoke agent
activate router
router -> agent : hk01 REGISTER Hook(hook_spec)
activate agent
agent -> loader : hk01 REGISTER Hook(hook_spec)
activate loader
loader -> hooks : hk01 REGISTER Hook(event, handler, priority)
activate hooks
hooks -> hook : hk01 CREATE Hook(name, event, handler, priority)
activate hook
hook --> hooks : hook instance
deactivate hook

alt Duplicate hook name
    hooks --> loader : warning logged, skip
    loader --> agent : warning logged
else New hook
    hooks --> hooks : hk01 APPEND To Registry(hook)
    hooks --> loader : registered
end
deactivate hooks

loader --> agent : registered
deactivate loader
agent --> router : hook registered
deactivate agent
deactivate router

note over user, hook
  Flow:    HK-01 → PluginLoader → HookManager → Hook creation → check duplicate → append to registry
  State:   No state change
  Success: Hook(registered) — hook instance appended to registry
  Failure: Warning logged — duplicate hook name skipped
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/HK/sq_hk04_pre_llm_hook.puml ---

@startuml sq_hk04_pre_llm_hook
' ============================================================
' Title:     HK-04 — DISPATCH Pre-LLM Hook
' Boundary:  nasim code agent
' Purpose:   Execute hooks before LLM call
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — HK-04 DISPATCH Pre-LLM Hook

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Hooks Group" #FFFDE7
  participant "HookManager" as hooks
  participant "Hook" as hook
end box
box "Provider Group" #FFF3E0
  participant "LiteLLMProxy" as provider
end box
box "Repository Group" #E8F5E9
  participant "HookRepository" as hook_repo
end box

note over user, provider
  Scope:          HK-04 DISPATCH Pre-LLM Hook
  Preconditions:  Hooks registered for PreLLMCall event
  Contexts:       Called by AGT-01 (PROCESS User Task) before PRV-02
  Excludes:       Post-LLM hooks (HK-05), tool hooks (HK-02/03)
  Rollback:       Hook deny blocks LLM call
  Design:         Priority-ordered execution; short-circuit on deny
  Classification: Process Decomposition
  Returns:
    - Success: HookResult(action=ALLOW, modified_messages?) — LLM call proceeds
    - Failure: HookResult(action=DENY, reason) — LLM call blocked
end note

== HK-04 DISPATCH Pre-LLM Hook ==

user -> router : invoke agent
activate router
router -> agent : hk04 DISPATCH Pre-LLM Hook(messages)
activate agent
agent -> hooks : hk04 DISPATCH Pre-LLM Hook(messages)
activate hooks
hooks -> hooks : hk04 FIND Hooks For Event(PreLLMCall)

loop for each hook in priority order
    hooks -> hook : hk04 EXECUTE Hook(messages)
    activate hook
    hook --> hooks : HookResult(action, data?)
    deactivate hook

    break action == DENY
        hooks --> agent : HookResult(action=DENY, reason)
        agent --> router : HookResult(action=DENY)
    end
end

hooks --> agent : HookResult(action=ALLOW, modified_messages?)
deactivate hooks
agent --> router : HookResult(action=ALLOW)
deactivate agent
deactivate router

note over user, provider
  Flow:    HK-04 → HookManager → find hooks → execute in priority order → return HookResult
  State:   No state change
  Success: HookResult(action=ALLOW) — LLM call proceeds
  Failure: HookResult(action=DENY) — LLM call blocked
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CFG/sq_cfg03_apply_layered_config.puml ---

@startuml sq_cfg03_apply_layered_config
' ============================================================
' Title:     CFG-03 — APPLY Layered Config
' Boundary:  nasim code agent CLI
' Purpose:   Config layer merge with precedence
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CFG-03 UPDATE Layered Config

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Config Group" #E0F7FA
  participant "ConfigLoader" as cfg
end box
box "Repository Group" #E8F5E9
  participant "ConfigRepository" as cfg_repo
end box

note over user, cfg
  Scope:          CFG-03 APPLY Layered Config
  Preconditions:  All sources loaded
  Contexts:       Called by CFG-01 (LOAD Config)
  Excludes:       Validation (CFG-02)
  Rollback:       N/A — merge always produces a result
  Design:         Precedence: CLI > env > project > global
  Classification: Process Decomposition
  Returns:
    - Success: Config(merged) — correct precedence applied
    - Failure: N/A — merge is always defined
end note

== CFG-03 APPLY Layered Config ==

user -> router : invoke agent
activate router
router -> agent : cfg03 APPLY Layered Config(sources)
activate agent
agent -> cfg : cfg03 APPLY Layered Config(sources)
activate cfg
cfg -> cfg : cfg03 MERGE Global Defaults(start)
cfg -> cfg : cfg03 MERGE Project Overrides(skip None)
cfg -> cfg : cfg03 MERGE Env Overrides(skip None)
cfg -> cfg : cfg03 MERGE CLI Args(skip None)
cfg -> cfg : cfg03 RETURN Merged Config

cfg --> agent : Config merged
agent --> router : Config merged
deactivate agent
deactivate router

note over user, cfg
  Flow:    CFG-03 → global → project → env → CLI → merged Config
  State:   No state change
  Success: Config(merged) — correct precedence applied
  Failure: N/A — merge is always defined
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CFG/sq_cfg02_validate_config.puml ---

@startuml sq_cfg02_validate_config
' ============================================================
' Title:     CFG-02 — VALIDATE Config
' Boundary:  nasim code agent CLI
' Purpose:   Config field validation
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    docs/SQ/README.md
' ============================================================

title nasim — CFG-02 VALIDATE Config

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Config Group" #E0F7FA
  participant "ConfigLoader" as cfg
end box
box "Repository Group" #E8F5E9
  participant "ConfigRepository" as cfg_repo
end box

note over user, cfg
  Scope:          CFG-02 VALIDATE Config
  Preconditions:  Config loaded from sources
  Contexts:       Called by CFG-01 (LOAD Config) after merge
  Excludes:       Config loading (CFG-01)
  Rollback:       Validation error -> ConfigError with details
  Design:         Typed dataclass with __post_init__ validation
  Classification: Process Decomposition
  Returns:
    - Success: Config(valid) — all fields pass schema checks
    - Failure: ConfigError — invalid field value with details
end note

== CFG-02 VALIDATE Config ==

user -> router : invoke agent
activate router
router -> agent : cfg02 VALIDATE Config(config)
activate agent
agent -> cfg : cfg02 VALIDATE Config(config)
activate cfg
cfg -> cfg : cfg02 CHECK Provider(provider in ["ollama", "openai", "anthropic"])
cfg -> cfg : cfg02 CHECK SafetyMode(safety_mode in ["ask", "auto", "off"])
cfg -> cfg : cfg02 CHECK ContextBudget(context_budget > 0)
cfg -> cfg : cfg02 CHECK Timeout(timeout > 0)

break Validation fails
    cfg --> agent : ConfigError("field: message")
    agent --> router : ConfigError
end

cfg --> agent : Config valid
agent --> router : Config valid
deactivate agent
deactivate router

note over user, cfg
  Flow:    CFG-02 → field checks → valid or ConfigError
  State:   No state change
  Success: Config(valid) — all fields pass schema checks
  Failure: ConfigError — invalid field value with details
end note

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SQ/CFG/sq_cfg01_load_config.puml ---

@startuml sq_cfg01_load_config
' ============================================================
' Title:     CFG-01 — Load Config
' Boundary:  nasim code agent CLI
' Purpose:   Layered config loading from all sources
' Milestone: v1.0
' Version:   9.1.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

actor "User" as user

box "API Group (Entry Gate)" #E8F5E9
  participant "ServerRouter" as router
end box
box "Agent Group" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
box "Config Group" #E0F7FA
  participant "ConfigLoader" as cfg
end box
database "Global YAML" as global_yaml
database "Project YAML" as project_yaml
database "Env Vars" as env_vars

note over user, env_vars
  Scope:          CFG-01 LOAD Config
  Preconditions:  CLI invoked
  Contexts:       Called by CLI-04 (Parse CLI Arguments)
  Excludes:       Runtime config changes
  Rollback:       Invalid YAML -> ConfigError
  Design:         4-layer merge: global < project < env < CLI
  Classification: Process Decomposition
  Returns:
    - Success: Config(dataclass) — typed configuration ready
    - Failure: ConfigError — invalid YAML or missing required fields
end note

== CFG-01 Load Config ==

user -> router : invoke agent
activate router
router -> agent : cfg01 LOAD Config(cli_args=argv)
activate agent
agent -> cfg : cfg01 LOAD Config(cli_args=argv)
activate cfg
cfg -> global_yaml : cfg01 READ Global Defaults(~/.nasim/config.yaml)
global_yaml --> cfg : global_defaults
cfg -> project_yaml : cfg01 READ Project Overrides(.nasim/config.yaml)
project_yaml --> cfg : project_overrides
cfg -> env_vars : cfg01 READ Env Overrides(NASIM_*)
env_vars --> cfg : env_overrides
cfg -> cfg : cfg01 APPLY Layered Config(global, project, env, CLI)
cfg -> cfg : cfg02 VALIDATE Config(fields)

break Invalid YAML or missing required fields
    cfg --> agent : ConfigError("details")
    agent --> router : ConfigError
end

cfg --> agent : Config object
agent --> router : Config object
deactivate agent
deactivate router

note over user, env_vars
  Flow:    CFG-01 → read global → read project → read env → merge → validate → Config
  State:   No state change
  Success: Config(dataclass) — typed configuration ready
  Failure: ConfigError — invalid YAML or missing required fields
end note

@enduml


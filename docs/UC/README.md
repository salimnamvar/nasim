# nasim — UC Inventory

| UC ID | Group | Operation | Component Owner |
|-------|-------|-----------|----------------|
| CLI-01 | CLI | PROCESS User Input | REPLSession |
| CLI-02 | CLI | Execute Slash Command | SlashCommandHandler |
| CLI-03 | CLI | STREAM Output | Renderer |
| CLI-04 | CLI | Parse CLI Arguments | ArgParser |
| CLI-05 | CLI | Toggle Plan Mode | SlashCommandHandler |
| CLI-06 | CLI | Prompt Safety Approval | Renderer |
| CLI-07 | CLI | Switch Model | SlashCommandHandler |
| CLI-08 | CLI | List Sessions | SlashCommandHandler |
| AGT-01 | AGT | PROCESS User Task | AgentOrchestrator |
| AGT-02 | AGT | DISPATCH Tool Call | AgentOrchestrator |
| AGT-03 | AGT | Manage Conversation | ConversationHistory |
| AGT-04 | AGT | Reset History | ConversationHistory |
| AGT-05 | AGT | CHECK Tool Permission | PermissionGate |
| AGT-06 | AGT | COMPACT Context | ContextCompactor |
| AGT-07 | AGT | Queue Plan | PlanSession |
| AGT-08 | AGT | APPROVE Plan | PlanSession |
| PRV-01 | PRV | Initialize Provider | ProviderFactory |
| PRV-02 | PRV | Call Provider Chat | Provider |
| PRV-03 | PRV | STREAM Provider Chat | Provider |
| PRV-04 | PRV | Select Provider Backend | ProviderFactory |
| CFG-01 | CFG | Load Config | ConfigLoader |
| CFG-02 | CFG | Validate Config | ConfigLoader |
| CFG-03 | CFG | Merge Layered Config | ConfigLoader |
| SSN-01 | SSN | Save Session | SessionStore |
| SSN-02 | SSN | Load Session | SessionStore |
| SSN-03 | SSN | List Sessions | SessionStore |
| SSN-04 | SSN | Resume Session | SessionStore |
| SAF-01 | SAF | CHECK Tool Permission | PermissionGate |
| SAF-02 | SAF | Prompt User Approval | PermissionGate |
| SAF-03 | SAF | Apply Safety Mode | PermissionGate |
| CTX-01 | CTX | Track Token Count | ConversationHistory |
| CTX-02 | CTX | COMPACT Context | ContextCompactor |
| CTX-03 | CTX | Summarize Old Exchanges | ContextCompactor |
| LLM-01 | LLM | Call Ollama Chat | OllamaProvider |
| LLM-02 | LLM | STREAM Ollama Chat | OllamaProvider |
| TL-01 | TL | Read File | ReadFileTool |
| TL-02 | TL | Write File | WriteFileTool |
| TL-03 | TL | Edit File | EditFileTool |
| TL-04 | TL | List Directory | DirTool |
| TL-05 | TL | Execute Shell Command | ShellTool |
| TL-06 | TL | Grep Search | GrepTool |
| TL-07 | TL | Glob Files | GlobTool |
| TL-08 | TL | Find Files | FindFileTool |
| TL-09 | TL | FETCH Web Content | WebFetchTool |
| TL-10 | TL | SEARCH Web | WebSearchTool |
| TL-11 | TL | Git Status Diff Commit | GitTool |
| TL-12 | TL | Invoke MCP Extension | MCPToolAdapter |
| TL-13 | TL | LSP Operations | LspTool |
| TL-14 | TL | List Registered Tools | ToolRegistry |
| SRV-01 | SRV | List Sessions | ServerRouter |
| SRV-02 | SRV | Create Session | ServerRouter |
| SRV-03 | SRV | Get Session | ServerRouter |
| SRV-04 | SRV | Update Session | ServerRouter |
| SRV-05 | SRV | Delete Session | ServerRouter |
| SRV-06 | SRV | Send Message | ServerRouter |
| SRV-07 | SRV | List Messages | ServerRouter |
| SRV-08 | SRV | List Tools | ServerRouter |
| SRV-09 | SRV | Get Tool | ServerRouter |
| SRV-10 | SRV | Get Config | ServerRouter |
| SRV-11 | SRV | Update Config | ServerRouter |
| HK-01 | HK | Register Hook | HookManager |
| HK-02 | HK | Execute Pre-Tool Hook | HookManager |
| HK-03 | HK | Execute Post-Tool Hook | HookManager |
| HK-04 | HK | Execute Pre-LLM Hook | HookManager |
| HK-05 | HK | Execute Post-LLM Hook | HookManager |
| HK-06 | HK | Evaluate Hook Result | HookManager |
| PLG-01 | PLG | Discover Plugins | PluginLoader |
| PLG-02 | PLG | Load Plugin Manifest | PluginLoader |
| PLG-03 | PLG | Register Plugin Tools | PluginLoader |
| PLG-04 | PLG | Register Plugin Hooks | PluginLoader |
| PLG-05 | PLG | Enable/Disable Plugin | PluginLoader |
| RTG-01 | RTG | Select Model | ModelRouter |
| RTG-02 | RTG | Apply Fallback | ModelRouter |
| RTG-03 | RTG | Classify Task | ModelRouter |
| RTG-04 | RTG | Switch Model Mid-Session | ModelRouter |
| AGT-09 | AGT | SPAWN Subagent | SubagentManager |
| AGT-10 | AGT | COLLECT Subagent Result | SubagentManager |
| AGT-11 | AGT | DELEGATE Task to Role | TaskDispatcher |
| AGT-12 | AGT | Load Persona | PersonaLoader |
| AGT-13 | AGT | Switch Persona | PersonaLoader |
| AGT-14 | AGT | Handle Agent Error | ErrorBoundary |
| AGT-15 | AGT | Execute Safety Pipeline | SafetyPipeline |
| SSN-05 | SSN | SNAPSHOT Session | SessionVersioning |
| SSN-06 | SSN | RESTORE Session | SessionVersioning |
| SSN-07 | SSN | SEARCH Sessions | SessionSearch |
| SSN-08 | SSN | BRANCH Session | SessionFork |
| TL-15 | TL | SPAWN Subagent Tool | SubagentTool |
| TL-16 | TL | INSERT Todo | TodoTool |
| TL-17 | TL | UPDATE Todo | TodoTool |
| TL-18 | TL | READ Todos | TodoTool |
| TL-19 | TL | PERSIST Memory | MemoryTool |
| TL-20 | TL | RECALL Memory | MemoryTool |
| TL-21 | TL | INSERT Plan | PlanTool |
| TL-22 | TL | UPDATE Plan | PlanTool |
| OBS-01 | OBS | STREAM Structured Log | StructuredLogger |
| OBS-02 | OBS | Record Metrics | MetricsCollector |
| OBS-03 | OBS | Correlate Trace | TraceCorrelator |
| MEM-01 | MEM | PERSIST Knowledge | MemoryStore |
| MEM-02 | MEM | RECALL Knowledge | MemoryStore |
| MEM-03 | MEM | SEARCH Knowledge | MemoryIndex |
| MEM-04 | MEM | Scope Knowledge | MemoryScope |
| VCS-01 | VCS | READ Git Status | GitStatus |
| VCS-02 | VCS | INSERT Commit | GitCommit |
| VCS-03 | VCS | READ Diff | GitStatus |
| VCS-04 | VCS | Auto-Commit | GitIntegration |
| SBX-01 | SBX | ISOLATE Command | SandboxExecutor |
| SBX-02 | SBX | Apply Sandbox Policy | SandboxPolicy |
| SBX-03 | SBX | Monitor Process | SandboxMonitor |

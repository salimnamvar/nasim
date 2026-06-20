# nasim — UC Inventory

| UC ID | Group | Operation | Component Owner |
|-------|-------|-----------|----------------|
| CLI-01 | CLI | PROCESS User Input | REPLSession |
| CLI-02 | CLI | Execute Slash Command | SlashCommandHandler |
| CLI-03 | CLI | STREAM Output | Renderer |
| CLI-04 | CLI | Parse CLI Arguments | ArgParser |
| CLI-05 | CLI | Toggle Plan Mode | SlashCommandHandler |
| CLI-06 | CLI | Prompt Safety Approval | Renderer |
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

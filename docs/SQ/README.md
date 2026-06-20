# nasim — SQ Inventory

Sequence diagrams organised by UC group. 60 diagrams across 14 groups.
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## Groups

| Group | Boundary | Diagrams | Subdirectory |
| ----- | -------- | :------: | ------------ |
| CLI | CLI Layer — REPL, parsing, rendering | 8 | `CLI/` |
| AGT | Agent Core — orchestrator, history, permissions, plans | 8 | `AGT/` |
| PRV | Provider Layer — provider abstraction, chat, streaming | 4 | `PRV/` |
| CFG | Configuration — config loading and validation | 3 | `CFG/` |
| SSN | Session — persistence and resumption | 4 | `SSN/` |
| SAF | Safety — permission checks and user approval | 3 | `SAF/` |
| CTX | Context Management — token counting and compaction | 3 | `CTX/` |
| LLM | Provider Backend — Ollama-specific chat/stream | 2 | `LLM/` |
| TL | Tool Layer — all tool implementations | 14 | `TL/` |
| SRV | HTTP Server — REST API, SSE streaming | 7 | `SRV/` |
| HK | Hooks — pre/post hooks for tool and LLM lifecycle | 6 | `HK/` |
| PLG | Plugins — plugin discovery, loading, registration | 5 | `PLG/` |
| RTG | Model Router — model selection, fallback, routing | 4 | `RTG/` |
| OBS | Observability — structured logging, metrics, trace correlation | 5 | `OBS/` |

## Diagram Index

| SQ Diagram | UC ID | Group | Description |
|-----------|-------|-------|-------------|
| sq_cli01_process_user_input | CLI-01 | CLI | REPL input loop with event rendering |
| sq_cli02_execute_slash_command | CLI-02 | CLI | Slash command routing and dispatch |
| sq_cli03_display_streaming_output | CLI-03 | CLI | Streaming token display with Rich formatting |
| sq_cli04_parse_cli_arguments | CLI-04 | CLI | Startup argument parsing and config init |
| sq_agt01_execute_user_task | AGT-01 | AGT | Core agentic loop with Provider ref |
| sq_agt02_dispatch_tool_call | AGT-02 | AGT | Tool dispatch with permission gate |
| sq_agt03_manage_conversation | AGT-03 | AGT | Message management and token tracking |
| sq_agt04_reset_history | AGT-04 | AGT | Clear conversation history |
| sq_agt05_check_tool_permission | AGT-05 | AGT | Per-tool safety gate |
| sq_agt06_compact_context | AGT-06 | AGT | Context compaction trigger |
| sq_agt07_queue_plan | AGT-07 | AGT | Queue tool calls in plan mode |
| sq_agt08_approve_plan | AGT-08 | AGT | Execute queued plan calls |
| sq_prv01_initialize_provider | PRV-01 | PRV | Provider instantiation from config |
| sq_prv02_call_provider_chat | PRV-02 | PRV | Synchronous chat completion |
| sq_prv03_stream_provider_chat | PRV-03 | PRV | Streaming chat completion |
| sq_prv04_select_provider_backend | PRV-04 | PRV | Provider class selection |
| sq_cfg01_load_config | CFG-01 | CFG | Layered config loading |
| sq_cfg02_validate_config | CFG-02 | CFG | Config field validation |
| sq_cfg03_merge_layered_config | CFG-03 | CFG | Config layer merge with precedence |
| sq_ssn01_save_session | SSN-01 | SSN | Persist session to disk |
| sq_ssn02_load_session | SSN-02 | SSN | Load session from disk |
| sq_ssn03_list_sessions | SSN-03 | SSN | List available sessions |
| sq_ssn04_resume_session | SSN-04 | SSN | Resume session by ID or latest |
| sq_saf01_check_tool_permission | SAF-01 | SAF | Tool permission check logic |
| sq_saf02_prompt_user_approval | SAF-02 | SAF | User approval prompt [y/N] |
| sq_saf03_apply_safety_mode | SAF-03 | SAF | Apply safety mode from config |
| sq_ctx01_track_token_count | CTX-01 | CTX | Token count tracking |
| sq_ctx02_compact_context | CTX-02 | CTX | Context compaction execution |
| sq_ctx03_summarize_old_exchanges | CTX-03 | CTX | Summarize old message exchanges |
| sq_llm01_call_ollama_chat | LLM-01 | LLM | Synchronous provider chat |
| sq_llm02_stream_ollama_chat | LLM-02 | LLM | Streaming provider chat |
| sq_tl01_read_file | TL-01 | TL | Read file with offset/limit |
| sq_tl02_write_file | TL-02 | TL | Write/overwrite file |
| sq_tl03_edit_file | TL-03 | TL | Find-and-replace in file |
| sq_tl04_list_directory | TL-04 | TL | List directory contents |
| sq_tl05_execute_shell_command | TL-05 | TL | Shell command with timeout |
| sq_tl06_grep_search | TL-06 | TL | Regex search in file contents |
| sq_tl07_glob_files | TL-07 | TL | Find files by glob pattern |
| sq_tl08_find_files | TL-08 | TL | Find files by name with depth |
| sq_tl09_fetch_web_content | TL-09 | TL | Fetch URL as markdown |
| sq_tl10_search_web | TL-10 | TL | Web search with ranked results |
| sq_tl11_git_status_diff_commit | TL-11 | TL | Git status/diff/commit |
| sq_tl12_invoke_mcp_extension | TL-12 | TL | MCP server extension tools |
| sq_srv01_start_server | SRV-01 | SRV | Initialize and start HTTP server |
| sq_srv02_create_session | SRV-02 | SRV | Create session via API |
| sq_srv03_send_message | SRV-03 | SRV | Send message, receive SSE stream |
| sq_srv04_stream_response | SRV-04 | SRV | Stream agent response as SSE |
| sq_hk02_pre_tool_hook | HK-02 | HK | Execute hooks before tool use |
| sq_hk03_post_tool_hook | HK-03 | HK | Execute hooks after tool use |
| sq_rtg01_select_model | RTG-01 | RTG | Model selection and fallback |
| sq_obs01_stream_log | OBS-01 | OBS | Structured JSON log emission to stdout |
| sq_obs02_record_metrics | OBS-02 | OBS | Record metric points for latency, tokens, tool calls |
| sq_obs03_correlate_trace | OBS-03 | OBS | Generate and propagate trace context |
| sq_obs04_redact_sensitive | OBS-04 | OBS | Strip secrets before emission |
| sq_obs05_expose_metrics | OBS-05 | OBS | Serve /metrics endpoint for Prometheus |

**Total: 60 SQ diagrams (1:1 with UCs)**

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version, source, review status
2. **Lifelines** — Actors, participants grouped by layer (colored boxes)
3. **Intro Note** — Scope, Preconditions, Contexts, Excludes, Rollback, Design, Returns
4. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks
5. **Summary Note** — Flow summary, state transitions, success/failure paths, key invariants

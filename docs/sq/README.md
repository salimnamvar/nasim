# nasim — SQ Inventory

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

**Total: 42 SQ diagrams (1:1 with UCs)**

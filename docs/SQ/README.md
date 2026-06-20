# nasim — SQ Inventory

| SQ Diagram | UC ID | Group | Description |
|-----------|-------|-------|-------------|
| sq_cli01_process_user_input | CLI-01 | CLI | REPL input loop |
| sq_cli02_execute_slash_command | CLI-02 | CLI | Slash command handling |
| sq_cli03_display_streaming_output | CLI-03 | CLI | Token-by-token display |
| sq_cli04_parse_cli_arguments | CLI-04 | CLI | Startup argument parsing |
| sq_agt01_execute_user_task | AGT-01 | AGT | Core agentic loop |
| sq_agt02_dispatch_tool_call | AGT-02 | AGT | Single tool dispatch |
| sq_agt03_manage_conversation | AGT-03 | AGT | Message list management |
| sq_agt04_reset_history | AGT-04 | AGT | Clear conversation |
| sq_llm01_call_ollama_chat | LLM-01 | LLM | Sync LLM call |
| sq_llm02_stream_ollama_chat | LLM-02 | LLM | Streaming LLM call |
| sq_tl01_read_file | TL-01 | TL | File read tool |
| sq_tl02_write_file | TL-02 | TL | File write tool |
| sq_tl03_edit_file | TL-03 | TL | File edit tool |
| sq_tl04_list_directory | TL-04 | TL | Directory listing tool |
| sq_tl05_execute_shell_command | TL-05 | TL | Shell execution tool |

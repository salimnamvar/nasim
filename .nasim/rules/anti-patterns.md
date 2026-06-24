# nasim Anti-Patterns (project)

- Do not hard-code Ollama URLs or model names in core logic (use Provider + Config).
- Do not put print()/input() inside the agent loop — use events + CLI renderer.
- Do not skip reading a file before edit_file.
- Do not implement new capabilities in the PoC files without updating the design docs first.
- Avoid god objects. Keep Tool, Provider, PermissionGate, Config, SessionStore as distinct responsibilities.

# nasim — CSR Pattern (Project-Specific)

Extends `~/.claude/rules/software-design/csr.md` for nasim's CLI/Agent architecture.

## Adaptation for CLI Agent

nasim is primarily a CLI agent, not an HTTP API. CSR applies as:

- **Controller Layer**: CLI interface (ArgParser, REPLSession, Renderer, SlashCommandHandler)
- **Service Layer**: Agent core (AgentOrchestrator, ConversationHistory, ContextCompactor, PermissionGate)
- **Repository Layer**: Data access (SessionStore, ToolRegistry, ConfigLoader)

## Rules

**NASIM-CSR-01** CLI entrypoints (REPLSession, single_command) immediately delegate to AgentOrchestrator. No business logic in CLI layer.

**NASIM-CSR-02** AgentOrchestrator never imports or uses persistence frameworks. All data access goes through Repository interfaces.

**NASIM-CSR-03** ToolRegistry is scoped to tool operations. SessionStore is scoped to session persistence. ConfigLoader is scoped to configuration.

**NASIM-CSR-04** Composition root (`nasim/__main__.py`) wires Controller → Service → Repository via constructor injection.

**NASIM-CSR-05** AgentOrchestrator owns consistency boundaries for multi-repository operations.

**NASIM-CSR-06** Domain entities (AgentEvent, ToolResult, Config, Session) are persistence-ignorant.

## Package Layout

```
nasim/
    __init__.py
    __main__.py          ← Composition root
    cli/                 ← Controller Layer
        __init__.py
        args.py
        repl.py
        renderer.py
        commands.py
    agent/               ← Service Layer
        __init__.py
        orchestrator.py
        history.py
        compactor.py
        events.py
        permission.py
        plan.py
    provider/            ← Service Layer (Provider)
        __init__.py
        base.py
        factory.py
        ollama.py
        models.py
        router.py
    tools/               ← Repository Layer (Tools)
        __init__.py
        base.py
        registry.py
        file.py
        search.py
        shell.py
        directory.py
        web.py
        git.py
        mcp.py
    config/              ← Repository Layer (Config)
        __init__.py
        loader.py
        schema.py
    session/             ← Repository Layer (Session)
        __init__.py
        store.py
        model.py
    server/              ← Controller Layer (HTTP, Phase 3)
        __init__.py
        app.py
        router.py
        sse.py
    hooks/               ← Service Layer (Hooks, Phase 2)
        __init__.py
        manager.py
        base.py
        models.py
    plugins/             ← Service Layer (Plugins, Phase 3)
        __init__.py
        loader.py
        manifest.py
        base.py
```

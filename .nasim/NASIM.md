# NASIM — nasim

**Project Name:** nasim
**Path:** /home/salim/prj/salim/nasim/code/nasim
**Created:** 2026-06-25T15:31:14Z
**NASIM Version:** 1.0.0

## Project Overview

nasim is a research code agent — a CLI code agent + HTTP API server + MCP server,
designed from first principles with a complete C4 → UC → SM → SQ → ERD → CL →
CT/DATA → CT/API → Code design chain.

## Design Chain Status

| Layer | Artifacts | Status |
|-------|-----------|--------|
| C4 Architecture | 24 diagrams | Frozen |
| Use Cases | 22 UC files — 148 UCs | Frozen |
| State Machine | 4 diagrams | Frozen |
| Sequence Diagrams | 148 diagrams | Frozen |
| ERD | 5 store schemas | Frozen |
| Class Diagram | 1 runtime model | Frozen |
| Data Contracts | 5 ODCS v3.1.0 contracts | Frozen |
| HTTP API Surface | 6 API puml + OpenAPI 3.1.0 | Frozen |
| Implementation Roadmap | 10 milestone docs | Active |
| Audit Reports | 18 audit documents | Active |

## Active Rules

The following rules are loaded for this project:

### Core Rules

- `rules/core/session-sync.md` — Session knowledge sync policy
- `rules/code/python.md` — Python coding standards
- `rules/code/errors.md` — Error handling patterns
- `rules/code/logging.md` — Logging conventions

### Documentation Rules

- `rules/doc/markdown.md` — Markdown style guide
- `rules/doc/readme.md` — README authoring policy

### Git Rules

- `rules/git/conventional-commits.md` — Commit message format
- `rules/git/gitflow.md` — Branching strategy
- `rules/git/git-policy.md` — Git workflow policy

### Software Design Rules

- `rules/software-design/design-chain.md` — Design chain methodology
- `rules/software-design/c4.md` — C4 architecture notation
- `rules/software-design/uc.md` — Use case diagram conventions
- `rules/software-design/sm.md` — State machine notation
- `rules/software-design/sq.md` — Sequence diagram conventions
- `rules/software-design/erd.md` — Entity-relationship diagrams
- `rules/software-design/cl.md` — Class diagram conventions
- `rules/software-design/odcs.md` — Open Data Contract Standard
- `rules/software-design/openapi.md` — OpenAPI 3.1.0 conventions
- `rules/software-design/rod.md` — Record of Decision format
- `rules/software-design/csr.md` — Contract schema rules
- `rules/software-design/sprint.md` — Sprint management
- `rules/software-design/anti-patterns.md` — Known anti-patterns
- `rules/software-design/fitness-functions.md` — Fitness functions
- `rules/software-design/adaptive-systems.md` — Adaptive systems patterns
- `rules/software-design/deployment.md` — Deployment conventions
- `rules/software-design/cicd.md` — CI/CD pipeline rules

### Environment Rules

- `rules/env/conda.md` — Conda environment management
- `rules/env/vscode.md` — VS Code configuration
- `rules/env/workspace.md` — Workspace conventions

### Architecture Rules

- `rules/architecture/agent-shared-symlink.md` — Agent shared symlink strategy

### Identity Rules

- `rules/identity/salim-identity.md` — Salim Namvar identity and voice
- `rules/identity/waf-global.md` — WAF TECH global rules

### Work Management Rules

- `rules/work_management/task-management.md` — Task management conventions
- `rules/work_management/slack.md` — Slack communication rules

## Active Skills

The following skills are available for this project:

- `skills/docx/` — DOCX document processing
- `skills/pptx/` — PPTX presentation processing
- `skills/xlsx/` — XLSX spreadsheet processing

## Project Structure

```
nasim/
├── docs/              # Design chain (C4, UC, SM, SQ, ERD, CL, CT, audit, RDM)
├── scripts/           # Lint, clean, setup, ollama tools, doc merge
├── data/              # Research data (Ollama model analysis)
├── pyproject.toml     # Python project configuration
└── README.md          # Project entry point
```

## Quick Start

```bash
# From repo root (after cloning)
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Environment setup

```bash
bash scripts/setup/setup_env.sh
```

Requires Python 3.10+.

## Development Commands

```bash
# Lint + format + types
bash scripts/lint.sh

# Clean build artifacts
bash scripts/clean.sh

# Full environment provisioning
bash scripts/setup/setup_env.sh
```

## Agent Integration

Agents registered in `~/.agent-global/shared/` automatically discover this
project via the shared symlink. All rules and skills listed above are
available to any agent working in this project.

For more information, see the NASIM specification in
`~/.agent-global/shared/CORE-DIRECTIVE.md`.

---

**Last Updated:** 2026-06-25
**Architecture Version:** 1.0.0
**Agents:** Claude, Grok, MiMo (unified sync via `feature/<agent>` branches)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**nasim** — Local LLM Machine. A personal GitHub project (`salimnamvar/nasim`).

Current state: blueprint phase (`feature/blueprint`). No source code exists yet.

## Tech Stack

Python project (inferred from `.gitignore`). Tooling present in the ignore rules:
- Formatter: `black` (line length 120, per global rules)
- Linter: `ruff`
- Import sorter: `isort`
- Test runner: `pytest`

## Conventions

- Global Python rules apply: `a_` prefix on all function/method arguments, `Tuple[bool, T]` returns, single `return` per function.
- Commits: Conventional Commits via `/conventional-commit`.
- Branching: Gitflow — `feature/*` → `develop` → `master`.
- Personal GitHub repo: `.claude/`, `.vscode/`, `.githooks/`, `.github/` are first-class citizens — committed to `origin` directly, not gitignored.

## Commands

Once source exists, standard commands will be:

```bash
# Format
black --line-length 120 .
isort .

# Lint
ruff check .

# Test
pytest
pytest tests/path/to/test_file.py::TestClass::test_method   # single test
```

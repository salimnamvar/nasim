# 08 — Quality Gates & CI/CD

Back to [docs/rdm/](./README.md).

**Status:** Active · **Scope:** Continuous quality enforcement.

---

## Gate Checks (every PR)

| Check | Tool | Command | Pass Criteria |
| --- | --- | --- | --- |
| Type checking | mypy | `mypy src/nasim/` | Zero errors, `--strict` |
| Linting | ruff | `ruff check src/nasim/` | Zero warnings |
| Formatting | black | `black --check src/nasim/` | No changes needed |
| Tests | pytest | `pytest tests/ -v` | All pass |
| Coverage | pytest-cov | `pytest --cov=nasim --cov-report=term-missing` | ≥ 80% |

## Design Chain Integrity

| Check | What | Command |
| --- | --- | --- |
| Layer boundaries | No agent→CLI imports | `grep -r "from nasim.CLI" src/nasim/agent/` |
| Layer boundaries | No tool→agent imports | `grep -r "from nasim.agent" src/nasim/tools/` |
| C4 fidelity | Class names match C4 | Spot check against `docs/c4/README.md` |
| UC coverage | Every UC has ≥1 test | Cross-reference `docs/uc/README.md` with test files |
| SQ coverage | Every SQ has implementation trace | Cross-reference `docs/sq/README.md` with code |

## CI Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: mypy src/nasim/
      - run: ruff check src/nasim/
      - run: black --check src/nasim/
      - run: pytest tests/ -v --cov=nasim --cov-report=term-missing
```

## Breaking Change Protocol

1. No breaking changes to Provider Protocol or Tool ABC without major version bump
2. Config schema changes require migration path or backward-compatible defaults
3. Session format changes require migration utility

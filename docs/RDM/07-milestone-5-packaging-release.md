# 07 — Milestone 5: Packaging & Release

Back to [docs/rdm/](./README.md).

**Status:** Active · **Prerequisite:** [06-milestone-4-integration-hardening.md](06-milestone-4-integration-hardening.md)

Package for distribution, documentation, and release.

---

## Scope

- `pyproject.toml` finalization (entry points, classifiers, versions)
- README.md user documentation
- CLI `--version` flag
- Release workflow (GitHub Actions)
- Conda/pip packaging

## Deliverables

| # | Deliverable | Notes |
| - | --- | --- |
| 1 | Final pyproject.toml | Entry points, classifiers |
| 2 | README.md | User-facing docs, installation, usage |
| 3 | --version flag | Version from pyproject.toml |
| 4 | GitHub Actions release workflow | Automated build + publish |

## Acceptance Criteria

- `pip install -e .` works
- `nasim --version` prints version
- `nasim --help` shows all commands
- README covers installation, configuration, usage examples
- GitHub Actions builds and publishes on tag

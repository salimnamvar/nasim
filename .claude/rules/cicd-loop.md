# CI/CD Loop

Nasim is built and kept working by a single repeatable loop. The loop is both a
discipline (this file) and an artifact (`bin/loop.sh`, driven by `make loop`).

```
        ┌──────────────────────────────────────────────────────────┐
        │                                                            │
   ┌────▼─────┐   ┌──────┐   ┌───────┐   ┌──────┐   ┌─────────┐   ┌──┴────┐
   │  PLAN    │──►│ CODE │──►│ BUILD │──►│ TEST │──►│ RELEASE │──►│DEPLOY │
   └──────────┘   └──────┘   └───────┘   └──────┘   └─────────┘   └───┬───┘
        ▲                                                              │
        │                              ┌─────────┐   ┌──────────┐      │
        └──────────────────────────────┤ MONITOR │◄──┤ OPERATE  │◄─────┘
                                        └─────────┘   └──────────┘
```

## Stages

| Stage | Action | Tooling |
| --- | --- | --- |
| **Plan** | Pick the next red matrix row in `rules/sprint.md`; write/adjust a test for it first. | `rules/testing.md`, `rules/sprint.md` |
| **Code** | Implement the smallest change to make that test pass, honoring module boundaries. | `rules/architecture.md` |
| **Build** | Lint + import-check + assemble the bridge payload. | `make lint` |
| **Test** | Unit → (deploy) → integration → capability → rollback → e2e. | `make test`, `make loop` |
| **Release** | Conventional commit on `feature/implementation`; bump version when a surface changes. | `/conventional-commit`, SemVer |
| **Deploy** | rsync `src/nasim/bridge/` + `cfg/` to the server, restart the service. | `make deploy` |
| **Operate** | Confirm the service is healthy and serving. | `nasim status`, `/health` |
| **Monitor** | Watch the bridge journal + matrix for regressions; feed findings back to Plan. | `journalctl -u nasim-bridge`, matrix |

## The loop runner (`make loop` → `bin/loop.sh`)

Runs, in order, stopping at the first hard failure and printing a matrix:

```
1. lint            ruff + black --check + python -c import
2. unit            pytest test/unit            (no network)
3. deploy          push bridge to the server, restart, wait for /health
4. integration     pytest test/integration     (live bridge)
5. capability      pytest test/capability       (live bridge — the API matrix)
6. rollback        pytest test/rollback         (start/stop contract)
7. e2e             pytest test/e2e              (real claude binary)   [opt-in]
8. report          print the green/red capability matrix
```

E2E is opt-in (`make loop E2E=1`) because each step drives the real model and is
slow; CI-style fast loops run 1–6.

## Test-first rule

A capability is not "being worked on" until a test asserts it. Red test →
implement → green → commit. This keeps the matrix honest: every ✅ is backed by a
runnable assertion, not a claim.

## Definition of done

The loop terminates successfully when the exit criteria in `rules/testing.md`
hold: all B\* + T\* green, all E\* green on the recommended model, all X\*
transport-green with a reliability note. Anything still red must be a documented
model-capability bound, not a bridge defect.

## Continuous integration note

A hosted CI runner cannot reach `black` (localhost-bound bridge behind SSH).
Stages 1–2 (lint + unit) are CI-safe anywhere. Stages 3–7 require a runner with
SSH access to the server — run locally or on a self-hosted runner. `docs/runbook.md`
documents the self-hosted-runner path.

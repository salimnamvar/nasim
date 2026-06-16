# Methodology — the CI/CD loop

Nasim is built and kept working by one repeatable loop, both a discipline and an
artifact (`bin/loop.sh`, driven by `make loop`).

```
   PLAN → CODE → BUILD → TEST → RELEASE → DEPLOY → OPERATE → MONITOR → (back to PLAN)
```

## Stages

| Stage | Action | Tooling |
| --- | --- | --- |
| Plan | Pick the next red matrix row; write/adjust a test for it first. | [capability-matrix.md](capability-matrix.md) |
| Code | Smallest change to make that test pass, honouring module boundaries. | [architecture.md](architecture.md) |
| Build | Lint + import-check + assemble the bridge payload. | `make lint` |
| Test | Unit → (deploy) → integration → capability → rollback → e2e. | `make test`, `make loop` |
| Release | Conventional commit; bump version when a surface changes. | git, SemVer |
| Deploy | rsync `src/` + `cfg/` to the server, restart the service. | `make deploy` |
| Operate | Confirm the service is healthy and serving. | `nasim status`, `/health` |
| Monitor | Watch the bridge journal + matrix for regressions; feed back to Plan. | `journalctl -u nasim-bridge` |

## The loop runner

`make loop` runs, in order, stopping at the first hard failure and printing a
matrix:

```
1. lint            ruff + black --check + import smoke
2. unit            pytest test/unit            (no network)
3. deploy          push the bridge, restart, wait for /health
4. integration     pytest test/integration     (live bridge)
5. capability      pytest test/capability      (live bridge — the API matrix)
6. rollback        pytest test/rollback        (start/stop contract)
7. e2e             pytest test/e2e             (real claude binary)   [opt-in]
8. report          print the green/red capability matrix
```

E2E is opt-in (`make loop E2E=1`) because each step drives the real model and is
slow; fast loops run 1–6.

## Test-first rule

A capability is not "being worked on" until a test asserts it: red test →
implement → green → commit. This keeps the matrix honest — every green cell is
backed by a runnable assertion, not a claim.

## Definition of done

The loop terminates successfully when the matrix exit criteria hold: all
bridge-guaranteed and rollback rows green, all e2e rows green on the chosen
model, and every exhaustive-surface row transport-green with a reliability note.
Anything still red must be a documented model-capability bound
([model-guidance.md](model-guidance.md)), never a bridge defect.

## CI note

A hosted runner cannot reach a localhost-bound bridge behind SSH. Stages 1–2
(lint + unit) are CI-safe anywhere; stages 3–7 need a runner with SSH access to
the server — run locally or on a self-hosted runner. See [runbook.md](runbook.md).

# RDM — Implementation Roadmap

Actionable milestone docs for nasim CODE. Design chain (C4→UC→SM→SQ→ERD→CL) frozen.
All docs enforce design-chain traceability, layered architecture, and quality gates.

Back to [docs/](../README.md).

## Reading Order

| # | Document | Read when |
| - | --- | --- |
| 00 | [Principles & Tech Stack](00-principles-and-stack.md) | Before any code |
| 01 | [Project Skeleton & Layer Rules](01-project-skeleton.md) | Before any code |
| 02 | [Milestone 0 — Bootstrap](02-milestone-0-bootstrap.md) | Day 1 |
| 03 | [Milestone 1 — Provider & Tools](03-milestone-1-provider-tools.md) | After M0 |
| 04 | [Milestone 2 — Agent Core](04-milestone-2-agent-core.md) | After M1 |
| 05 | [Milestone 3 — CLI & Session](05-milestone-3-CLI-session.md) | After M2 |
| 06 | [Milestone 4 — Integration & Hardening](06-milestone-4-integration-hardening.md) | After M3 |
| 07 | [Milestone 5 — Packaging & Release](07-milestone-5-packaging-release.md) | After M4 |
| 08 | [Quality Gates & CI/CD](08-quality-gates-cicd.md) | Continuously, every PR |
| 09 | [Risks & Open Items](09-risks-and-open-items.md) | Reference as needed |

## Maintenance

- Edit a milestone doc only for its scope. No renumber.
- Cross-doc impact (new milestone, reordering, skeleton change) → update this README.
- Design chain learnings from implementation stay in 00 + 08 (permanent).

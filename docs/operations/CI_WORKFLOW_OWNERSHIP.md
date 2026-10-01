# GitHub Actions ownership and execution policy

This document defines CI responsibility boundaries for SongChart Next. It is an execution contract, not a second roadmap or lifecycle registry. Capability lifecycle remains in `governance/CAPABILITY_MAP.json`; source and exact-SHA GitHub Actions runs are verification evidence.

## Workflow ownership matrix

| Workflow | Sole responsibility | Expensive runtime | Trigger model |
| --- | --- | --- | --- |
| `project-governance.yml` | authored registries/contracts, governance regression tests, read-only project status, CI ownership contract | no | every PR, every `main` push, manual |
| `roadmap-health.yml` | live Issues/PR roadmap reconciliation and scheduled health report | no | PR/Issue lifecycle, relevant `main` paths, daily schedule, manual |
| `foundation-app.yml` | Docker Compose app/PostgreSQL runtime, migrations, backend/frontend tests, human review command contract, dependency audit/licenses/provenance/SBOM, production-target build | yes | application/runtime paths on PR and `main`, manual |
| `foundation-visual.yml` | deterministic browser rendering, proxy asset behavior and visual evidence artifacts | yes | visual/runtime-affecting paths on PR and `main`, manual |
| `codespaces-contract.yml` | dev-container schema, Codespaces lifecycle scripts and base-image availability | low | Codespaces-owned paths on PR and `main`, manual |

Retired workflows:
- `project-os.yml` — duplicated governance validation.
- `docker-scaffold.yml` — duplicated Compose/PostgreSQL runtime coverage already owned by `foundation-app.yml`.

## Rules

1. One assertion has one owning workflow. Shared source may trigger several workflows only when each produces materially different evidence.
2. PR acceptance workflows evaluate the exact PR head SHA. `main` workflows evaluate the exact merged SHA.
3. Stale PR commits may be cancelled. Distinct `main` SHAs are not cancelled by concurrency groups.
4. Heavy Docker/browser workflows use path filters. Governance remains cheap and universal.
5. GitHub-hosted runners are pinned to `ubuntu-24.04`; external actions are pinned to full commit SHAs.
6. Human visual approval remains outside CI. Browser automation proves deterministic rendering only.
7. Roadmap-health concurrency is isolated by event family and PR/Issue identity so a push, issue update or different PR cannot cancel unrelated evidence.
8. CI artifacts are derived evidence, never editable authority.

## Gap-control automation

`scripts/verify_ci_ownership.py` is run by `project-governance.yml`. It verifies the owned workflow set, rejects retired duplicate workflows, checks runner/action pinning, enforces exact-SHA controls on application/visual/Codespaces workflows, checks roadmap concurrency isolation and confirms that governance validation has a single Actions owner.

Adding a new workflow requires updating this document and the verifier in the same semantic change. Prefer extending an existing owner workflow when the evidence belongs to an existing concern.

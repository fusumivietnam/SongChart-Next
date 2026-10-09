# SongChart Next

SongChart Next is a new, independent music knowledge and discovery project. **This repository is its sole project authority.** Previous SongChart repositories, chat summaries, ZIP bundles and historical stage plans are not dependencies or implementation evidence.

## Docker-first local development
- GitHub Codespaces is an optional repository-owned developer shell under [ADR-0006](docs/adr/ADR-0006-codespaces-development-environment.md). See the [Codespaces runbook](docs/operations/CODESPACES.md). The app/database still run through the approved Docker Compose baseline; Codespaces is not a production runtime.
- ADR-0001 governs local Compose and [ADR-0003](docs/adr/ADR-0003-foundation-runtime.md) records the accepted Foundation app/toolchain baseline. The [Docker development runbook](docs/operations/DOCKER_DEVELOPMENT.md) documents app + PostgreSQL 18.6 startup after real lockfiles and checks are available.
- [PR #1](https://github.com/fusumivietnam/SongChart-Next/pull/1), [PR #2](https://github.com/fusumivietnam/SongChart-Next/pull/2), [PR #6](https://github.com/fusumivietnam/SongChart-Next/pull/6) and [PR #8](https://github.com/fusumivietnam/SongChart-Next/pull/8) are merged; see [pinned upstream provenance](docs/engineering/UPSTREAM_STARTER.md).

## Current status
<!-- roadmap-reconcile:start -->
Repository lifecycle authority remains `governance/CAPABILITY_MAP.json`; planned scope remains `docs/roadmap/VERTICAL_SLICES.md`; live execution remains GitHub Issues/PRs.

Latest reconciled product evidence: PR #88 — VS-03c structured provider-destination persistence and verified-only external chooser are merged and exact-head verified; live provider production access remains unactivated.
<!-- roadmap-reconcile:end -->

- The repository contains the approved Foundation runtime/design baseline and implemented canonical Artist, Release, Recording, Work/credits relationships, PostgreSQL-first mixed-entity discovery, Artist-to-Release journey continuity and deterministic fixture-only provider-destination rendering.
- Live provider production access, public API, dedicated search-index, recommendation/ranking, production deployment target and deployment remain separately gated and unactivated unless their owning authorities say otherwise.
- Do not copy old source, stage numbering, generated authority or UI by default.

## Project control (read-only status, no chat authority)
Project governance protocols and evidence ownership: [Project Control](docs/operations/PROJECT_CONTROL.md) and [CI Workflow Ownership](docs/operations/CI_WORKFLOW_OWNERSHIP.md). Research and environment-scoped runtime inventories: [Research Registry](governance/RESEARCH_REGISTRY.json) and [Infrastructure Registry](governance/INFRASTRUCTURE_REGISTRY.json). See [Delivery Contract](docs/engineering/DELIVERY_CONTRACT.md), [Acceptance Gates](docs/operations/ACCEPTANCE_GATES.md), and [Dependency Policy](docs/operations/DEPENDENCY_POLICY.md). Run `python3 scripts/verify_project_os.py` and `python3 scripts/project_status.py`; the latter is an offline projection and must not be treated as current GitHub Issue/PR or deployment status. This documentation does not approve product choices or mark any product feature as implemented.

## Start here
1. [Project charter](docs/product/PRODUCT_CHARTER.md)
2. [Architecture and source authority](docs/architecture/ARCHITECTURE.md)
3. [Capability map](governance/CAPABILITY_MAP.json)
4. [Technology registry](governance/TECHNOLOGY_REGISTRY.json)
5. [Activation triggers](governance/ACTIVATION_TRIGGERS.json)
6. [Design authority](design/DESIGN_AUTHORITY.md)
7. [Developer reference](reference/README.md)
8. [AI/developer instructions](AGENTS.md)
9. [Roadmap governance](docs/roadmap/ROADMAP_GOVERNANCE.md)
10. [Vertical slices](docs/roadmap/VERTICAL_SLICES.md)

## Authority rule
Git owns code and authored decisions; PostgreSQL owns canonical product data where installed; GitHub Issues/Projects own execution work when configured. Generated docs and AI contexts are **read-only projections** of their declared sources. A proposal is not an installed dependency, an approved design, a completed feature or a production release.

## Current delivery frontier
Use live roadmap Issues plus the Capability Map to select the next executable work. At this repository revision, VS-03 parent acceptance still requires explicit reconciliation of any remaining Home/discovery scope before VS-04 launch-proof work can be treated as the next completed slice. Production target selection remains a separate decision.

## Verification
Run `python3 scripts/verify_project_os.py` to validate project registry links and lifecycle claims (Python standard library only).

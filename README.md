# SongChart Next

SongChart Next is a new, independent music knowledge and discovery project. **This repository is its sole project authority.** Previous SongChart repositories, chat summaries, ZIP bundles and historical stage plans are not dependencies or implementation evidence.

## Docker-first local development
- [ADR-0001](docs/adr/ADR-0001-docker-first-development.md) records owner approval of **local** Docker Compose. The [Compose scaffold](compose.yaml) and [local setup](docs/operations/DOCKER_DEVELOPMENT.md) define a PostgreSQL development service only; no Laravel app, runtime verification, backup proof or production release is implied.
- The Docker changes are proposed for merge in [PR #1](https://github.com/fusumivietnam/SongChart-Next/pull/1); the Project Control System merged in [PR #2](https://github.com/fusumivietnam/SongChart-Next/pull/2) governs status and evidence.

## Current status
- Repository bootstrap: governance and engineering contracts; local PostgreSQL Compose scaffold is proposed in PR #1, not an installed app.
- Product, framework and visual decisions below are **proposals** until accepted in an ADR.
- No Laravel application, provider integration, production deployment, approved visual baseline or passing end-to-end feature is implied by these documents.
- Do not copy old source, stage numbering, generated authority or UI by default.

## Project control (read-only status, no chat authority)
Project governance protocols and evidence ownership: [Project Control](docs/operations/PROJECT_CONTROL.md). Research and environment-scoped runtime inventories: [Research Registry](governance/RESEARCH_REGISTRY.json) and [Infrastructure Registry](governance/INFRASTRUCTURE_REGISTRY.json). See [Delivery Contract](docs/engineering/DELIVERY_CONTRACT.md), [Acceptance Gates](docs/operations/ACCEPTANCE_GATES.md), and [Dependency Policy](docs/operations/DEPENDENCY_POLICY.md). Run `python3 scripts/verify_project_os.py` and `python3 scripts/project_status.py`; the latter is an offline projection and must not be treated as current GitHub Issue/PR or deployment status. This documentation does not approve product choices or mark any product feature as implemented.

## Start here
1. [Project charter](docs/product/PRODUCT_CHARTER.md)
2. [Architecture and source authority](docs/architecture/ARCHITECTURE.md)
3. [Capability map](governance/CAPABILITY_MAP.json)
4. [Technology registry](governance/TECHNOLOGY_REGISTRY.json)
5. [Activation triggers](governance/ACTIVATION_TRIGGERS.json)
6. [Design authority](design/DESIGN_AUTHORITY.md)
7. [Developer reference](reference/README.md)
8. [AI/developer instructions](AGENTS.md)
9. [Vertical slices](docs/roadmap/VERTICAL_SLICES.md)

## Authority rule
Git owns code and authored decisions; PostgreSQL will own canonical product data when installed; GitHub Issues/Projects own execution work when configured. Generated docs and AI contexts are **read-only projections** of their declared sources. A proposal is not an installed dependency, an approved design, a completed feature or a production release.

## First milestone
Approve product/design decisions, initialize an official Laravel React Starter application, and implement the fixture-first Artist end-to-end slice with PostgreSQL and automated checks. Add live provider ingestion, search, admin and external infrastructure only when accepted capability triggers are met.

## Verification
Run `python3 scripts/verify_project_os.py` to validate project registry links and lifecycle claims (Python standard library only).

# SongChart Next

SongChart Next is a new, independent music knowledge and discovery project. **This repository is its sole project authority.** Previous SongChart repositories, chat summaries, ZIP bundles and historical stage plans are not dependencies or implementation evidence.

## Current status
- Repository bootstrap: governance and engineering contracts only.
- Product, framework and visual decisions below are **proposals** until accepted in an ADR.
- No Laravel application, provider integration, production deployment, approved visual baseline or passing end-to-end feature is implied by these documents.
- Do not copy old source, stage numbering, generated authority or UI by default.

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

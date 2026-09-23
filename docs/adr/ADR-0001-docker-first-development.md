# ADR-0001 — Docker-first reproducible development

Status: accepted for development environment, 2026-09-20. Decision authority: explicit project-owner approval in project conversation; implementation/review evidence is the linked GitHub PR. This ADR does not approve product scope, visual identity, provider ingestion, production deployment or an exact Laravel starter revision.

## Context
SongChart Next has governance contracts but no application manifests or runtime in main at decision time. Development and CI need consistent build/runtime boundaries without introducing a second product authority.

## Decision
Use Docker Compose as the single documented local development entry point. Define an application service built from a project Dockerfile and PostgreSQL as its sole canonical database once the first persistence slice is approved. Pin base runtime versions and lock dependencies when the official Laravel React starter is initialized in a separate reviewed change. Keep Compose config in the sole SongChart-Next repository. Use named volumes for PostgreSQL data; keep secrets outside Git and expose only the app's intended local port. Compose is local development tooling, not a production deployment controller.

The initial Compose configuration is a **scaffold only**: it can start PostgreSQL independently, but the application service is gated on the Laravel starter and its lockfiles being added. Do not represent the scaffold as a running application or verified feature.

## Consequences and controls
- Development runs through `docker compose`, rather than requiring host PHP/PostgreSQL/Node versions. The container image will be completed in the starter PR.
- No production credentials in Compose or Git; .env stays untracked.
- Persist canonical DB to a named volume, but volume persistence is not backup/restore proof.
- One deployment controller must be selected by a separate production ADR.
- CI must validate Compose config and build/run against the actual starter lockfiles before claiming parity.
- Design Authority and product/frontend approval gates remain independent; no UI styling or canonical data policies are approved here.

## Alternatives
Host-only development rejected for reproducibility. Kubernetes and external orchestration deferred as disproportionate to the first vertical slice. Docker Compose is not a replacement for Laravel Queue/Scheduler.

## Follow-up
Approve scope/design/frontend and starter revision; add version-pinned multi-stage application Dockerfile and complete Compose app service, lockfiles, tests, health checks, recovery runbook and CI in bounded PRs. Review PostgreSQL version, licensing and backup/restore before persistence activation.

# Architecture & authority — SongChart Next

**Status: candidate architecture.** Do not claim runtime exists until source and verification evidence appear.

## Product boundary
SongChart owns domain semantics, canonical decisions, source claims/provenance, provider policies, application use cases, approved UI/UX and contracts. OSS owns commodity mechanisms when justified. Modular monolith first; no distributed system by default.

## Intended dependency direction
Presentation (Laravel/Inertia React public; optional Filament admin, Flutter clients later) -> delivery (web, REST, CLI, MCP) -> application use cases -> domain/core -> persistence port -> PostgreSQL. Providers -> source adapter -> normalized claim contract -> application admission -> canonical core. No UI/Kestra/provider direct writes to canonical DB.

## Data
PostgreSQL is sole canonical product-data authority once instantiated. Cache and search are derived/rebuildable. Stable SongChart IDs differ from provider IDs. External claims are retained only under documented provider terms. Merge/split has review, history and redirect policy. Do not let AI confidence alone approve a merge.

## Async boundaries
Laravel Queue/Jobs owns short internal jobs. Kestra is a candidate only for justified external multi-step or scheduled ingestion, not a second orchestrator for the same job. When external projections or notifications make dual-write risk real, write a transactional outbox with idempotent consumers. No Kafka/full event sourcing by default.

## Interface authorities
Public API: authored OpenAPI or code-first generated OpenAPI with an explicit single declaring authority chosen in ADR; generated counterpart is verified, not separately edited. JSON Schema for provider/event contracts. Source symbols own actual signatures. Reference registry indexes these; it does not override them. Design Authority owns visual semantics; source implementation and screenshots provide evidence.

## Local runtime decision (ADR-0001)
Docker Compose is the approved reproducible local development entry point. The current scaffold provisions PostgreSQL only; a containerized Laravel app, pinned dependencies and CI parity remain unimplemented. Compose is not the production deployment controller. See [Docker development](../operations/DOCKER_DEVELOPMENT.md). Product and frontend architecture are still candidates subject to their own ADRs and design gate.

## Execution and release
GitHub owns source/PR/issues. CI checks code and contracts; one deployment controller owns production. Runtime must be recoverable without optional management SaaS. Secret values never in Git; production changes and destructive actions require explicit review and restore/rollback plan.

## Adoption boundary
A new OSS must specify capability owner, source URL, version/edition and license review, operating cost, data/privacy impact, replacement/retirement path, activation evidence and failure mode. Alternative tools are not deployed concurrently without separate responsibility.

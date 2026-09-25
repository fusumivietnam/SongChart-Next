# Vertical slices — dependency and evidence driven

**All slices below are planned, not completed.** GitHub Issues/Projects become execution authority once configured; this document is the proposed release scope, not an independent task-state tracker.

Delivery acceptance for every slice: [Engineering Delivery Contract](../engineering/DELIVERY_CONTRACT.md) and [Acceptance Gates](../operations/ACCEPTANCE_GATES.md). Research references are catalogued in [Research Registry](../../governance/RESEARCH_REGISTRY.json) but cannot automatically change this planned scope. Live Issues and PRs own execution status, not this document or an offline snapshot.

Docker-first local development is approved by ADR-0001; PR #1 merged a PostgreSQL-only scaffold. [Issue #5](https://github.com/fusumivietnam/SongChart-Next/issues/5) owns the pinned official starter import, real Composer/pnpm locks, app+PostgreSQL 18.6 Docker build and runtime verification. [ADR-0003](../adr/ADR-0003-foundation-runtime.md) records the proposed toolchain. [Draft PR #6](https://github.com/fusumivietnam/SongChart-Next/pull/6) includes imported starter, both resolved lockfiles and successful framework-level app/database/frontend tests. It is **not merged**; review and operational gates remain. A merged scaffold, image build or upstream welcome page does not complete Foundation or VS-01a.

## FOUNDATION — approve then build
Approve MVP acceptance, choose public frontend in ADR, approve brand/UI baseline and component/page contracts, choose OpenAPI declaration authority, initialize official framework starter without importing old SongChart code; install PostgreSQL and focused tests.

## VS-01a — fixture-first Artist
Given a deterministic MusicBrainz-shaped fixture: normalize ExternalArtistClaim -> validate -> resolve by stable external identifier -> create/read SongChart Artist in PostgreSQL -> serve a typed read view -> render mobile+desktop Artist page under approved design -> run unit, DB and browser tests. Do not merge on name alone; duplicate fixture imports are idempotent. This is not live integration.

## VS-01b — live MusicBrainz
Add rate-limited HTTP source adapter, explicit provenance and raw-data retention policy, provider errors/retries and import/review queue. Check public provider rules before fetching, storing or displaying assets. Verify source contract with fixtures and scheduled probes.

## VS-02 — Release/Recording/Credits
Implement correct work/recording/release/release-group distinctions, identifier mapping and relationships, approved reusable entity page patterns, data-quality tests and safe canonical redirects.

## VS-03 — discovery/destinations
Search quality fixtures, derived index only when needed, official links checked against rights/security policies, complete home -> search -> artist -> release/recording -> destination journey. Add outbox if asynchronous external projections exist.

## VS-04 — launch proof
Accessible responsive SEO pages, privacy/support/correction minimum, dependency/secret scan, tested restore and rollback, production-equivalent migrations, health/incident runbooks and release approval. No declaration of launch without evidence.

## Later / activated only
Flutter, public SDK/MCP, Kestra, advanced analytics, chart ranking, recommendation, external plugin runtime, schema registry, distributed infrastructure and premium billing. Record trigger evidence before adoption.

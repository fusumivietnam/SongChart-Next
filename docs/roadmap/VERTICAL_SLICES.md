# Vertical slices — dependency and evidence driven

This document owns **slice scope, dependency order and acceptance intent**, not live completion status. `CAPABILITY_MAP.json` owns capability lifecycle; GitHub Issues/PRs own execution; GitHub Projects/Milestones are derived views. A slice description remains here after implementation as the canonical scope/acceptance record. See [Roadmap Governance](ROADMAP_GOVERNANCE.md).

Delivery acceptance for every slice: [Engineering Delivery Contract](../engineering/DELIVERY_CONTRACT.md) and [Acceptance Gates](../operations/ACCEPTANCE_GATES.md). Research references are catalogued in [Research Registry](../../governance/RESEARCH_REGISTRY.json) but cannot automatically change this planned scope. Live Issues and PRs own execution status, not this document or an offline snapshot.

Docker-first local development is approved by ADR-0001. [PR #6](https://github.com/fusumivietnam/SongChart-Next/pull/6) merged the pinned official Laravel React Starter, real Composer/pnpm lockfiles and app + PostgreSQL 18.6 Docker development baseline. [ADR-0003](../adr/ADR-0003-foundation-runtime.md) records the accepted Foundation runtime/toolchain baseline. Product scope is approved by ADR-0004 and the authored OpenAPI declaration authority is decided by ADR-0005. The Foundation Design Authority gate was approved on 2026-10-02. VS-01a source was subsequently merged in [PR #72](https://github.com/fusumivietnam/SongChart-Next/pull/72); its lifecycle is recorded in `CAPABILITY_MAP.json`, not inferred from this roadmap text.

## FOUNDATION — approved baseline
Product scope and OpenAPI declaration authority are approved/decided; the official framework starter and PostgreSQL development baseline are merged; the Foundation Design Authority identity/tokens, responsive Shell + Artist + Search patterns and rendered narrow/wide baselines are approved. Foundation completion does not imply production readiness.

## VS-01a — fixture-first Artist
Scope/acceptance record: given a deterministic MusicBrainz-shaped fixture, normalize `ExternalArtistClaim` -> validate -> resolve by stable external identifier -> create/read SongChart Artist in PostgreSQL -> serve a typed read view -> render mobile+desktop Artist page under approved design -> run unit, DB and browser tests. Do not merge on name alone; duplicate fixture imports are idempotent. No live provider integration belongs to this slice.

Implementation source for this first Artist path was merged in PR #72. Broader MVP public journey remains incomplete; Release/Recording/Credits, discovery and launch proof remain later slices.

## VS-01b — live MusicBrainz
Add a rate-limited HTTP source adapter, explicit provenance and raw-data retention policy, provider errors/retries and an explicit canonical-admission boundary. Check public provider rules before fetching, storing or displaying data. Contract verification uses deterministic HTTP fixtures/fakes plus real PostgreSQL; automatic CI must not generate live provider traffic. A bounded live probe, if needed for final provider verification, requires a separately recorded approval immediately before execution.

MusicBrainz G0 policy is approved for development/testing/bounded non-commercial evaluation under `docs/providers/MUSICBRAINZ.md`; commercial/public production remains blocked pending a separate MetaBrainz commercial posture.

## VS-02 — Release/Recording/Credits
Implement correct work/recording/release/release-group distinctions, identifier mapping and relationships, approved reusable entity page patterns, data-quality tests and safe canonical redirects.

## VS-03 — discovery/destinations
Search quality fixtures, derived index only when needed, official links checked against rights/security policies, complete home -> search -> artist -> release/recording -> destination journey. Add outbox if asynchronous external projections exist.

## VS-04 — launch proof
Accessible responsive SEO pages, privacy/support/correction minimum, dependency/secret scan, tested restore and rollback, production-equivalent migrations, health/incident runbooks and release approval. No declaration of launch without evidence.

## Later / activated only
Flutter, public SDK/MCP, Kestra, advanced analytics, chart ranking, recommendation, external plugin runtime, schema registry, distributed infrastructure and premium billing. Record trigger evidence before adoption.

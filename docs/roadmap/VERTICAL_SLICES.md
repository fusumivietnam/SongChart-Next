# Vertical slices — dependency and evidence driven

**All slices below are planned, not completed.** This document owns planned slice scope, dependency order and acceptance intent only. Live GitHub Issues/PRs own execution; `CAPABILITY_MAP.json` owns capability lifecycle. GitHub Projects/Milestones, if configured, are derived views and never independent status authority. See [Roadmap Governance](ROADMAP_GOVERNANCE.md).

Delivery acceptance for every slice: [Engineering Delivery Contract](../engineering/DELIVERY_CONTRACT.md) and [Acceptance Gates](../operations/ACCEPTANCE_GATES.md). Research references are catalogued in [Research Registry](../../governance/RESEARCH_REGISTRY.json) but cannot automatically change this planned scope. Live Issues and PRs own execution status, not this document or an offline snapshot.

Docker-first local development is approved by ADR-0001. [PR #6](https://github.com/fusumivietnam/SongChart-Next/pull/6) merged the pinned official Laravel React Starter, real Composer/pnpm lockfiles and app + PostgreSQL 18.6 Docker development baseline. [ADR-0003](../adr/ADR-0003-foundation-runtime.md) records the accepted Foundation runtime/toolchain baseline, and exact-head CI verifies the local development runtime. Product scope is approved by ADR-0004 and the authored OpenAPI declaration authority is decided by ADR-0005. The Foundation Design Authority gate was approved on 2026-10-02 after reviewed deterministic render evidence and owner acceptance. This clears the design prerequisite for VS-01a; it does not imply VS-01a implementation, verification, production readiness or deployment.

## FOUNDATION — approved baseline, build next
Product scope and OpenAPI declaration authority are approved/decided; the official framework starter and PostgreSQL development baseline are merged and verified; the Foundation Design Authority identity/tokens, responsive Shell + Artist + Search patterns and rendered narrow/wide baselines are approved. The next executable slice is VS-01a fixture-first Artist. Foundation completion does not imply production readiness.

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

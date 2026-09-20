# Vertical slices — dependency and evidence driven

**All slices below are planned, not completed.** GitHub Issues/Projects become execution authority once configured; this document is the proposed release scope, not an independent task-state tracker.

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

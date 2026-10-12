# Vertical slices — dependency and evidence driven

This document owns **slice scope, dependency order and acceptance intent**, not live completion status. `CAPABILITY_MAP.json` owns capability lifecycle; GitHub Issues/PRs own execution; GitHub Projects/Milestones are derived views. A slice description remains here after implementation as the canonical scope/acceptance record. See [Roadmap Governance](ROADMAP_GOVERNANCE.md).

Delivery acceptance for every slice: [Engineering Delivery Contract](../engineering/DELIVERY_CONTRACT.md) and [Acceptance Gates](../operations/ACCEPTANCE_GATES.md). Research references are catalogued in [Research Registry](../../governance/RESEARCH_REGISTRY.json) but cannot automatically change this planned scope. Live Issues and PRs own execution status, not this document or an offline snapshot.

Docker-first local development is approved by ADR-0001. [PR #6](https://github.com/fusumivietnam/SongChart-Next/pull/6) merged the pinned official Laravel React Starter, real Composer/pnpm lockfiles and app + PostgreSQL 18.6 Docker development baseline. [ADR-0003](../adr/ADR-0003-foundation-runtime.md) records the accepted Foundation runtime/toolchain baseline. Product scope is approved by ADR-0004 and the authored OpenAPI declaration authority is decided by ADR-0005. The Foundation Design Authority gate was approved on 2026-10-02. VS-01a source was subsequently merged in [PR #72](https://github.com/fusumivietnam/SongChart-Next/pull/72); VS-02 source was merged in [PR #76](https://github.com/fusumivietnam/SongChart-Next/pull/76); the PostgreSQL-first VS-03a discovery sub-slice was merged in [PR #81](https://github.com/fusumivietnam/SongChart-Next/pull/81). Capability lifecycle is recorded in `CAPABILITY_MAP.json`, not inferred from this roadmap text.

## FOUNDATION — approved baseline
Product scope and OpenAPI declaration authority are approved/decided; the official framework starter and PostgreSQL development baseline are merged; the Foundation Design Authority identity/tokens, responsive Shell + Artist + Search patterns and rendered narrow/wide baselines are approved. Foundation completion does not imply production readiness.

## VS-01a — fixture-first Artist
Scope/acceptance record: given a deterministic MusicBrainz-shaped fixture, normalize `ExternalArtistClaim` -> validate -> resolve by stable external identifier -> create/read SongChart Artist in PostgreSQL -> serve a typed read view -> render mobile+desktop Artist page under approved design -> run unit, DB and browser tests. Do not merge on name alone; duplicate fixture imports are idempotent. No live provider integration belongs to this slice.

Implementation source for this first Artist path was merged in PR #72. Broader MVP public journey remains incomplete; discovery, editorial/legal surfaces and launch proof remain later slices. Release/Recording/Credits are owned by VS-02 below rather than by VS-01a.

## VS-01b — live MusicBrainz
Add a rate-limited HTTP source adapter, explicit provenance and raw-data retention policy, provider errors/retries and an explicit canonical-admission boundary. Check public provider rules before fetching, storing or displaying data. Contract verification uses deterministic HTTP fixtures/fakes plus real PostgreSQL; automatic CI must not generate live provider traffic. A bounded live probe, if needed for final provider verification, requires a separately recorded approval immediately before execution.

MusicBrainz G0 policy is approved for development/testing/bounded non-commercial evaluation under `docs/providers/MUSICBRAINZ.md`; commercial/public production remains blocked pending a separate MetaBrainz commercial posture.

## VS-02 — Release/Recording/Credits
Implement correct Work/Recording/Release/Release Group distinctions; SongChart-owned identifiers and provider identity mapping; explicit Recording-to-Work relationships; ordered structured credits; Release -> Medium -> Track -> Recording structure; partial release-date precision; responsive Release/Recording pages; data-quality tests; and safe canonical ID+slug redirects.

[ADR-0013](../adr/ADR-0013-vs-02-release-recording-credits-model.md) owns the accepted canonical model and boundaries. Implementation source was merged in [PR #76](https://github.com/fusumivietnam/SongChart-Next/pull/76). Live Release/Recording provider traffic, Cover Art Archive, public API/search activation, commercial provider use and production deployment remain outside this slice.

## VS-03 — discovery/destinations
Search quality fixtures, derived index only when needed, official links checked against rights/security policies, complete home -> search -> artist -> release/recording -> destination journey. Add outbox if asynchronous external projections exist.

The VS-03a discovery sub-slice was implemented in [PR #81](https://github.com/fusumivietnam/SongChart-Next/pull/81): `/` and `/search` now search canonical PostgreSQL Artist, Release and Recording data with bounded deterministic exact/prefix/substring ranking, disambiguated mixed-entity results, canonical links, PostgreSQL/HTTP/type/browser evidence and retained non-production query-plan/latency evidence. The retained fixture evidence does not establish a relevance/latency failure, so the dedicated `search-index` capability remains unactivated. Official destination/link policy remains a separate VS-03 boundary because provider rights and security checks own that decision.

<!-- reconciliation:pr-85 -->
VS-03b1 journey continuity was implemented and exact-head verified in PR #85: canonical Artist pages now expose bounded deterministic Release relationships derived from structured credits, completing the Artist -> Release -> Recording navigation path without inferred/name-only joins.

<!-- reconciliation:pr-88 -->
VS-03c provider destinations were implemented and exact-head verified in PR #88 under ADR-0014: structured destination links are persisted with provenance/verification semantics, public Recording pages expose verified-only external destinations and honest empty states, and browser evidence covers destination-present/destination-empty narrow/wide states. Live provider production traffic remains unactivated.

<!-- reconciliation:pr-101 -->
VS-03b2 Home discovery was implemented and exact-head verified in PR #101: `/` is a distinct SongChart-owned surface with first-class search, bounded deterministic canonical Artist/Release/Recording modules, honest empty behavior, and narrow/wide browser evidence for the complete Home -> Search -> Artist -> Release -> Recording journey. No recommendation/search-index/provider-production capability is activated.

## VS-04 — launch proof
Accessible responsive SEO pages, privacy/support/correction minimum, dependency/secret scan, tested restore and rollback, production-equivalent migrations, health/incident runbooks and release approval. No declaration of launch without evidence.

<!-- reconciliation:pr-106 -->
VS-04a public launch-support surfaces were implemented and exact-head verified in PR #106: About/Privacy/Terms/Disclaimer/Support/Corrections share one accessible responsive anatomy with canonical metadata, real footer links, deterministic robots/sitemap and safe external issue-tracker correction/support actions. This is launch-proof evidence only and does not activate deployment.

<!-- reconciliation:pr-111 -->
VS-04b G3 release-candidate evidence was implemented and exact-head verified in PR #111: a repository-owned high-confidence tracked-secret scan and runtime .env tracking guard now complement Foundation-owned locked dependency audits, license inventory, provenance, production-target validation and source/image SBOMs on the same exact SHA. This is release-candidate evidence only and does not activate production deployment.

<!-- reconciliation:pr-113 -->
VS-04c PostgreSQL recovery proof was implemented and exact-head verified in PR #113: deterministic canonical fixtures survive logical pg_dump/drop-create/pg_restore with byte-identical normalized identity/relationship/destination/migration snapshots, followed by a disposable one-step migration rollback and fully-up forward re-apply. Temporary dumps are not retained and no production recovery claim is made.

<!-- reconciliation:pr-115 -->
VS-04d operational readiness was implemented and exact-head verified in PR #115: /health proves 200 only with canonical DB connectivity, actual disposable PostgreSQL outage returns generic 503 and recovers to 200, and repository-owned incident/threat/release-readiness contracts explicitly stop before production. G2/G3/G4 tested scope is complete; G5 remains blocked by #69 and real environment evidence.

## VS-05 — correction evidence and editorial-review activation gate
The approved MVP permits public correction input to feed an authenticated internal review decision, but correction input must never write canonical tables directly. This slice first establishes a bounded correction-evidence contract: subject identity, submitted claim, provenance/source references, submitter/contact handling where permitted, validation, abuse/rate-limit boundaries, retention/privacy rules and deterministic pending/resolved examples.

`admin-review` remains `candidate` until its activation trigger is independently satisfied: real unresolved claims require moderation and a human-reviewed permission model plus authorization tests exist. Planned work may define the review use case, roles, audit/history requirements and acceptance fixtures before activation, but roadmap text, a correction submission or a green PR cannot promote the capability by itself. Public self-registration remains out of scope; reviewer identities are provisioned through an explicitly controlled internal path.

Acceptance intent: correction evidence is isolated from canonical mutation; malformed/abusive input fails safely; representative conflicting claims demonstrate whether the moderation trigger is real; any later approve/reject operation must route through SongChart application/domain validation, retain decision history and prove unauthorized users cannot mutate canonical state.

<!-- reconciliation:pr-131 -->
VS-05a correction evidence persistence was implemented and exact-head verified: typed Artist/Release/Recording canonical subjects, bounded claim/supporting-URL validation and isolated pending correction submissions are stored without a public intake route, reviewer mutation path or canonical-table write. `admin-review` remains candidate and separately activation-gated.

## VS-06 — provider metadata breadth
Extend the already implemented provider-adapter boundary beyond the Artist-only live path toward the canonical Release, Recording, Release Group, Work and structured relationship model that VS-02 already owns. Start fixture/fake-first: typed provider claims, stable provider identifiers, normalization, idempotency, provenance/evidence retention and explicit admission into existing SongChart use cases. Do not create provider-shaped canonical tables or resolve identity by names alone.

MusicBrainz development/testing/bounded non-commercial policy remains the governing provider posture. Automatic CI must use deterministic fixtures/fakes and must not emit live provider traffic. Live Release/Recording/Work probing, commercial/public provider use, Cover Art Archive or any additional provider requires its own policy/rights/activation evidence before use.

Acceptance intent: deterministic fixtures cover representative Release/Recording/Work relationships and partial/missing data; repeated imports are idempotent; external identifiers remain evidence rather than SongChart identity; canonical constraints and existing public journeys remain stable; provider errors never corrupt canonical data; any new live path is separately gated.

<!-- reconciliation:pr-135 -->
VS-06a implemented a deterministic fixture/fake MusicBrainz release-lookup adapter into the existing VS-02 ReleaseBundleClaim/import boundary, preserving release/release-group/recording identities, credits, media and ISRCs while explicitly not inventing Recording-to-Work relationships. No live provider or commercial/public activation is implied.

<!-- reconciliation:pr-138 -->
VS-06b implemented deterministic fixture/fake MusicBrainz Recording-to-Work performance relationship normalization and canonical admission by stable external identity, with fail-closed handling for relationship attributes the current schema cannot represent. No live provider or commercial/public activation is implied.

## Later / activated only
Public API/SDK/MCP, dedicated search indexing, Flutter, Kestra, advanced analytics, chart ranking, recommendation, external plugin runtime, schema registry, distributed infrastructure and premium billing remain activation/product decisions rather than committed local MVP slices. Record trigger and decision evidence before adoption.

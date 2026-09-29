# Product charter — SongChart Next

**Status: approved for MVP scope on 2026-09-29; implementation and release remain separate lifecycle states.**

SongChart Next is an internationally oriented music knowledge, metadata discovery and legal provider-navigation product, **not** a streaming/hosting, social-network or general developer-platform product.

## MVP user journey
Home/search -> results by entity type -> Artist -> Release -> Recording/credits -> permitted listening/viewing destination. Clearly distinguish verified, unknown and contested data; display provenance where applicable. Missing artwork and metadata must fail gracefully.

## Approved MVP scope
- Search and public read pages for Artist, Release and Recording/credits.
- Fixture-first Artist implementation, then MusicBrainz-derived live ingestion subject to provider-policy review.
- Stable SongChart canonical IDs distinct from provider IDs; provider payloads/identifiers are evidence and external identity, not canonical identity.
- Provenance and basic editorial correction/review.
- Responsive, accessible public pages with international-ready URLs, SEO, deterministic empty/error states and tested production recovery before launch.
- Public visitors do **not** require accounts. Authentication is limited to workflows that genuinely require authorization, initially editorial/review operations.
- The upstream Laravel auth scaffold is an implementation primitive, not approval for public registration, public profiles, favorites/follows or personalized account features.
- VS-01a uses internal typed application/read contracts; it does not activate a public API. Public API exposure is a separate capability/decision.
- MusicBrainz is the first metadata-provider path: deterministic fixture in VS-01a, live adapter only in VS-01b after provider policy/rights/rate-limit review.
- Artwork is not a dependency of VS-01a; deterministic placeholders are acceptable. Artwork-provider selection is evaluated separately, no earlier than the Release-oriented work that needs it.
- International-ready means Unicode/domain correctness, locale-safe presentation and translatable UI structure; multi-language UI is not mandatory for MVP.
- Public correction submission may feed a basic authenticated internal review decision. Correction input never writes canonical tables directly.
- Provider navigation means linking to permitted external listening/viewing destinations; SongChart does not redistribute audio/video by default.

## Approved identity and URL principles
Canonical entity identity is the stable SongChart ID. Human-readable slugs are presentation metadata and may change without changing identity. Public entity URLs should use stable ID + slug, with canonical redirect behavior for stale slugs and history-preserving redirects for approved merges.

Canonical merge/split operations require deterministic domain validation, history and appropriate review. Do not silently delete a canonical identity or let provider/AI confidence alone approve a merge.

## Explicitly deferred
Public user accounts/registration, favorites/follows, personalized recommendations, notification preferences, charts built from unlicensed/undefined rankings, audio/video redistribution, native clients, public plugin marketplace, write-enabled remote MCP, advanced AI agents, partner billing, distributed databases, Kubernetes and multiple redundant control planes.

## Acceptance before public launch
A representative permitted dataset; end-to-end journey in browser on narrow and wide screens; approved visual baseline; legal/provider rights check; verified redirects, errors and empty states; automated tests; backup **and restore** proof; security/privacy/incident/rollback evidence.

Production deployment platform remains undecided until release/operational gates justify selection. Runtime artifacts must remain portable enough that a project-control dashboard or deployment SaaS is not required to recover the system.

## Scope discipline
Research -> idea -> evaluation -> approved capability -> issue -> PR -> release. Research or a chat conversation never auto-promotes a feature into committed roadmap. Product approval does not imply implementation, verification or deployment.

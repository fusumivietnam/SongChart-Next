# ADR-0004 — MVP product scope and activation boundaries

Status: accepted, 2026-09-29.

Decision authority: explicit project-owner approval recorded during the Foundation decision review. This ADR and the reviewed repository change are the durable authority; chat is not a continuing project source of truth.

## Context
Issue #9 requires a reviewed MVP boundary before product implementation slices can be activated. The official Laravel React starter exists on main, but starter routes/authentication and framework capabilities do not define SongChart product scope.

## Decision
Approve the Product Charter MVP boundary.

The public MVP is a music-knowledge/discovery and legal provider-navigation experience. Anonymous visitors can use public read/discovery pages. Authentication is activated only where authorization is genuinely required, initially editorial/review workflows; public registration/accounts, profile/follow/favorite/personalization capability are deferred.

VS-01a is fixture-first and uses a deterministic MusicBrainz-shaped claim. MusicBrainz becomes the first live metadata source only in VS-01b after provider-policy review. Artwork is not required by VS-01a.

SongChart canonical identity uses stable SongChart IDs distinct from provider identifiers. Slugs are mutable presentation metadata. Canonical merge/split preserves history and redirects and requires review.

The first product slice may use internal typed read/application contracts without exposing a public API. Public API activation remains separately governed by the API-contract capability and OpenAPI declaration decision.

The MVP is international-ready but does not require translated UI at launch. SongChart navigates to permitted external media destinations and does not redistribute audio/video by default.

## Consequences
- Product scope may be promoted to `approved`; this is G0 evidence only.
- Issue #10 is no longer product-scope blocked after this decision lands.
- Public-web/design/API/domain capabilities remain separate lifecycle claims.
- Starter auth UI must not be treated as approved public account functionality.
- Artwork/media/provider terms remain separate policy/adoption decisions.
- Production platform selection remains deferred until release/operational gates.

## Rejected for MVP
- Public account/social/personalization scope merely because starter auth exists.
- Live provider ingestion in the fixture-first slice.
- Artwork as a first-slice dependency.
- Public API exposure merely because internal typed contracts exist.
- Provider IDs as SongChart canonical IDs.
- Silent/destructive canonical merge.
- Production platform lock-in before production activation evidence.

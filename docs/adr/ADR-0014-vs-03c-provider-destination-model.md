# ADR-0014 — VS-03c provider destination model

Status: accepted
Date: 2026-10-09
Issue: #86
Parent: #79

## Context

VS-03 must complete the approved MVP public journey from canonical Artist / Release / Recording knowledge to permitted external listening or viewing destinations. External provider URLs are navigation evidence and must not become SongChart canonical identity. The provider policy requires provider-specific rights, retention, attribution and security review before live fetch/store/display behavior is activated.

Parent Issue #79 proposed D7 and the owner approved D7 on 2026-10-09.

## Decision

- SongChart owns an explicit structured destination-link record rather than storing free-form URL arrays on page DTOs.
- Every destination record is attached to one canonical SongChart subject by explicit subject type and canonical SongChart ID. Provider identifiers and URLs never replace canonical identity.
- The persisted contract records provider identity, destination type, external URL, provenance/source metadata, and an explicit verification state. A verification timestamp is stored only when the verification semantics are deterministic and authored.
- Destination URLs must use an approved external scheme and pass deterministic validation. Unsupported or unsafe schemes fail closed and are never rendered as links.
- Public presentation exposes provider name, destination type and explicit external-navigation treatment. SongChart links out; it does not embed or redistribute provider audio/video by default.
- Absence of a permitted destination is an honest empty state, not an inferred or fabricated link.
- Deterministic fixture evidence is sufficient for implementation and CI. Live provider network traffic is a separate activation gate and requires the applicable provider-specific policy/rights/security decision first.
- PostgreSQL remains canonical for SongChart-owned destination records once persistence is implemented. Any later search/cache projection is derived and rebuildable.

## Initial bounded semantics

The first implementation is intentionally narrow:
- subjects are existing public canonical entities required by the VS-03 journey;
- destination types are an authored enum/closed set, not arbitrary user strings;
- provider identity is explicit and stable within SongChart's provider registry/policy boundary;
- URL validation rejects non-HTTP(S) navigation unless a later ADR explicitly permits another scheme;
- duplicate prevention must be deterministic for the same canonical subject/provider/destination-type/URL combination;
- no ranking, recommendation, popularity or personalization semantics are introduced.

Exact column names, indexes and migration mechanics belong to implementation, but they must preserve these semantics and constraints.

## Boundaries

This decision does not activate live provider crawling/fetching, Cover Art Archive, MusicBrainz commercial/public-production use, public API, Meilisearch/search-index, recommendation/ranking, embedded/redistributed media, generalized workflow orchestration, outbox infrastructure without an actual asynchronous projection, or production deployment.

## Verification

VS-03c acceptance requires deterministic fixture import/persistence if persistence is introduced, invalid/unsafe URL rejection, typed read contracts, honest empty state, explicit external-link rendering, PostgreSQL/HTTP/type tests, and narrow/wide browser evidence on an exact PR head. Provider-production approval and deployment remain separate lifecycle gates.

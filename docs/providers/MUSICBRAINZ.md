# MusicBrainz provider-specific policy

Status: **approved for development, deterministic testing and bounded non-commercial evaluation; commercial/public production remains blocked**.

Reviewed: 2026-10-04.

This document applies the general [Provider evidence, rights and retention policy](PROVIDER_POLICY.md) to the MusicBrainz Web Service. It is an activation contract, not permission for a provider adapter to write canonical SongChart data directly.

## Upstream identity and reviewed sources

Provider: MusicBrainz, operated by the MetaBrainz Foundation.

Reviewed upstream sources:
- API overview: https://musicbrainz.org/doc/MusicBrainz_API
- API rate limiting: https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting
- Web Service overview: https://musicbrainz.org/doc/Web_Service
- MusicBrainz data license: https://musicbrainz.org/doc/About/Data_License
- MusicBrainz database/license breakdown: https://musicbrainz.org/doc/MusicBrainz_Database
- MetaBrainz datasets/commercial-use guidance: https://metabrainz.org/datasets

These URLs are external evidence. If their terms materially change, this provider review must be repeated before continued live activation.

## Allowed activation scope

The first live adapter may:
- read MusicBrainz Web Service v2 over HTTPS;
- request JSON metadata needed for Artist identity that maps to core MusicBrainz data;
- retain request/response provenance required to audit normalized claims under the retention classes below;
- normalize provider evidence into typed external claims;
- hand those claims to SongChart validation/admission logic.

It must not:
- write SongChart canonical tables directly;
- treat an MBID as a SongChart canonical ID;
- merge entities by name alone;
- fetch or persist MusicBrainz user information;
- submit ratings/tags/barcodes/ISRCs or perform authenticated edits;
- fetch Cover Art Archive assets under this review;
- ingest supplementary MusicBrainz data such as user annotations, tags/genres, ratings, edit history, derived statistics or other non-core data unless a separate rights review approves it;
- redistribute audio/video.

## Verified deterministic adapter breadth

The live activation scope above remains Artist-only. Separately, fixture/fake provider contracts now cover more of the canonical model without granting any new live-network permission:

- VS-06a / PR #135 exact-head verified a deterministic MusicBrainz release-lookup adapter that maps Release, Release Group, media/track structure, Recording identities, credits and ISRCs into the existing SongChart `ReleaseBundleClaim` and canonical admission path. It performs no live HTTP request and deliberately does not invent Recording-to-Work relationships from a release payload.
- VS-06b / PR #138 exact-head verified deterministic MusicBrainz Recording-to-Work `performance` relationship normalization and admission by stable external identity, failing closed when relationship attributes cannot be represented by the current canonical schema. It performs no live HTTP request.

These fixture/fake paths are verification evidence for the bounded normalization/admission implementation, not verification of live Release/Recording/Work fetching, hosted-service production use, commercial/public rights, Cover Art Archive, supplementary data or another provider. `provider-adapters` therefore remains `implemented` until the broader capability's required live/operational verification boundary is explicitly satisfied.

## Identification, rate limiting and failure behavior

Every request must send a meaningful User-Agent containing the SongChart application name/version plus a maintainer contact URL or email.

Without a separate agreement with MusicBrainz, the adapter must enforce a **global maximum average of one MusicBrainz request per second per SongChart deployment/IP**. Concurrency must not bypass this limit.

The adapter must treat provider throttling/unavailability as an external dependency failure:
- 503 responses are retryable only with bounded exponential backoff and jitter;
- retries must still respect the one-request-per-second ceiling;
- no tight retry loop;
- no fixed synchronized cron burst;
- no polling MusicBrainz simply to detect metadata changes;
- exhausted retries surface an explicit provider-unavailable result and leave canonical data unchanged.

Contract tests must cover success, 404/not-found, malformed response, timeout/network failure, and 503 throttling behavior before any live probe is enabled.

## Authentication and personal data

The planned read-only metadata path requires no API key and no MusicBrainz user authentication.

SongChart must not request user-information endpoints or OAuth scopes in the initial adapter. If authenticated/user-specific access is later proposed, it requires a separate privacy/security review and a new activation decision.

## Licensing and redisplay boundary

MusicBrainz distinguishes licensing classes:
- core database data is published under CC0;
- supplementary data is subject to CC BY-NC-SA 3.0;
- cover art is not part of the MusicBrainz dataset and is handled by the Cover Art Archive.

The initial SongChart adapter is restricted to fields verified as core/CC0 for the requested Artist path. If a field's licensing class is unclear, treat it as **not approved for storage/redisplay** until reviewed.

Provider attribution is retained in provenance and provider-facing operational/debug surfaces even where CC0 does not legally require attribution. Public SongChart pages must not imply MusicBrainz endorsement.

## Public-data rights evaluation checkpoint — 2026-10-18 (research, not activation)

Official-source review for #174: [data licenses](https://musicbrainz.org/doc/About/Data_License), [database class breakdown](https://musicbrainz.org/doc/MusicBrainz_Database), [API terms/usage](https://musicbrainz.org/doc/MusicBrainz_API), [rate limit](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting), [MetaBrainz datasets](https://metabrainz.org/datasets). Recheck these sources at the time of an actual activation decision; this checkpoint documents research, not current legal clearance.

| Data or transport class | Research posture | Decision required before public/commercial activation |
| --- | --- | --- |
| Core Artist/Release/Release Group/Recording/Work identity and typed metadata | Candidate CC0 **only when the specific requested field is confirmed in the core database class**. Fixture normalization exists beyond Artist; live fetch approval does not. | Field-level core/supplementary mapping, attribution/provenance, sample quality and ingestion boundaries. |
| Structured relationships, credits, ISRCs and provider URLs | Fixture-normalization evidence exists; do **not** infer that every nested API response field is CC0. | Review each included field and linked URL's provider/destination terms independently; no unreviewed fetch or public display. |
| Tags, ratings, user annotations, history, user collections and derived statistics | Supplementary/user data may carry CC BY-NC-SA or privacy restrictions; **excluded** from approved adapter scope. | Independent license/privacy review and explicit activation, or keep excluded. |
| Cover Art Archive assets and streamed media | **Outside MusicBrainz core license and this adapter approval.** | Separate asset/service/rights/attribution review; no fetch, caching, embed or redistribution assumption. |
| Hosted MusicBrainz Web Service | Non-commercial access and 1 request/second application limit, identifiable User-Agent; service permission differs from data copyright/license. | Owner must confirm business model and MetaBrainz commercial-service agreement/alternative before hosted commercial/public deployment. |
| Licensed datasets/bulk distribution | Possible alternate ingestion path, but not approved or implemented. | Evaluate licensing and update/replication cost, field rights, import fidelity, quota/retention and operator budget before a new technology decision. |

**Exit evidence still missing:** intended revenue/commercial posture; per-field license/attribution matrix; representative legally permitted Artist→Release→Recording/Work dataset with quality/disambiguation/coverage samples; data freshness/deletion obligations; owner/legal signoff on hosted API vs bulk. No public-hosted service use, Cover Art Archive, new external destinations, expanded live Release/Recording/Work fetch, or live CI probing follows from this research.

## Commercial-use boundary

MusicBrainz documents the public web service as free for non-commercial use and directs commercial users to MetaBrainz commercial plans/contact.

Owner decision B2, approved 2026-10-04:
- development, deterministic testing and bounded non-commercial evaluation may use the public MusicBrainz Web Service after the technical gates below pass;
- **commercial/public production use remains blocked** until the owner records the applicable MetaBrainz commercial-support/licensing posture.

This is separate from the CC0 status of core database data: data licensing and hosted web-service usage terms are not the same permission.

## Raw evidence retention

Raw provider responses are evidence, not canonical records.

Owner decision B1, approved 2026-10-04:
- successful approved-core JSON responses: **30 days**;
- provider error or malformed-response payloads: **7 days**;
- retained evidence is content-addressed and records provider, request identity, fetch timestamp, HTTP status/schema version and payload hash;
- raw payloads are never exposed on public pages;
- normalized claims/canonical decisions remain traceable after raw evidence expires;
- an expiry timestamp is mandatory so cleanup can be deterministic and auditable.

This policy does not authorize retaining supplementary/user data. Persistent archival beyond these durations requires a new owner/provider review.

## Cache/update semantics

SongChart may cache approved core metadata under the same provider boundary after the adapter contract exists. Cache entries must record fetch time and provider identity.

Do not poll MusicBrainz solely to detect changes. Refresh is demand/maintenance driven, rate-limited and auditable.

Provider identifiers can redirect or merge over time. A refreshed MBID is external identity evidence; it must never silently rewrite SongChart canonical identity without domain validation/review.

## Activation gates

### G0 — policy review
**Approved 2026-10-04 for development/testing/bounded non-commercial evaluation.** B1 raw-evidence retention and B2 hosted-service posture are recorded above. Commercial/public production remains a separate blocked gate.

### G1 — implementation
Requires a reviewed VS-01b PR containing:
- rate-limited HTTP adapter;
- explicit User-Agent configuration;
- typed provider success/error contracts;
- evidence/provenance representation;
- no direct canonical writes.

### G2 — verification
Requires exact-SHA tests proving:
- <=1 request/second scheduler behavior;
- bounded backoff/jitter for 503/provider failure;
- idempotent deterministic normalization;
- no canonical mutation on provider failure;
- allowed-field/license boundary;
- fixture coverage.

A bounded live probe is **not automatic CI**. It requires an explicit, separately recorded approval immediately before execution and must use the same rate/User-Agent controls.

### G4/G5
Require the commercial-use decision if applicable, privacy/security review, operational failure handling and production deployment evidence. No earlier gate implies production approval.

## Replacement / retirement

The adapter must remain behind a SongChart-owned provider contract. MusicBrainz-specific HTTP/data-shape details must not leak into canonical domain identity.

If the provider is retired:
- stop new fetches;
- retain only evidence permitted by the approved retention decision;
- preserve SongChart canonical history and provider-ID provenance according to SongChart policy;
- remove scheduled probes/configuration without deleting canonical entities merely because the provider disappears.

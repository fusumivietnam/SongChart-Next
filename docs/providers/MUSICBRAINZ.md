# MusicBrainz provider-specific policy

Status: **candidate provider review; live activation remains blocked pending owner decision**.

Reviewed: 2026-10-02.

This document applies the general [Provider evidence, rights and retention policy](PROVIDER_POLICY.md) to the MusicBrainz Web Service. It is an activation contract, not permission to write canonical SongChart data and not evidence that a live adapter exists.

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

The first live adapter, when separately implemented in VS-01b, may:
- read MusicBrainz Web Service v2 over HTTPS;
- request JSON metadata needed for Artist identity/relationships that maps to **core MusicBrainz data**;
- retain request/response provenance required to audit normalized claims;
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

## Identification, rate limiting and failure behavior

Every request must send a meaningful User-Agent containing the SongChart application name/version plus a maintainer contact URL or email.

Without a separate agreement with MusicBrainz, the adapter must enforce a **global maximum average of one MusicBrainz request per second per SongChart deployment/IP**. Concurrency must not bypass this limit.

The adapter must treat provider throttling/unavailability as an external dependency failure:
- 503 responses are retryable only with bounded backoff and jitter;
- retries must still respect the one-request-per-second ceiling;
- no tight retry loop;
- no fixed synchronized cron burst;
- no polling MusicBrainz simply to detect metadata changes;
- exhausted retries surface an explicit provider-unavailable result and leave canonical data unchanged.

The first implementation must be contract-tested with deterministic fixtures for success, 404/not-found, malformed response, timeout/network failure, and 503 throttling behavior before any scheduled live probe is enabled.

## Authentication and personal data

The planned read-only metadata path requires no API key and no MusicBrainz user authentication.

SongChart must not request user-information endpoints or OAuth scopes in the initial adapter. If authenticated/user-specific access is later proposed, it requires a separate privacy/security review and a new activation decision.

## Licensing and redisplay boundary

MusicBrainz distinguishes licensing classes:
- core database data is published under CC0;
- supplementary data is subject to CC BY-NC-SA 3.0;
- cover art is not part of the MusicBrainz dataset and is handled by the Cover Art Archive.

The initial SongChart adapter is therefore restricted to fields verified as core/CC0 for the requested entity/relationship path. If a field's licensing class is unclear, treat it as **not approved for storage/redisplay** until reviewed.

Provider attribution should be retained in provenance and provider-facing operational/debug surfaces even where CC0 does not legally require attribution. Public SongChart pages must not imply MusicBrainz endorsement.

## Commercial-use boundary

MusicBrainz documents the public web service as free for non-commercial use and directs commercial users to MetaBrainz commercial plans/contact.

Therefore:
- development, deterministic testing and bounded non-commercial evaluation may proceed after the remaining technical gates are satisfied;
- **commercial/public production use is not approved by this document**;
- before a commercial SongChart launch uses the MusicBrainz Web Service, the owner must record the applicable MetaBrainz commercial-support/licensing decision.

This decision is deliberately separate from the CC0 status of core database data: data licensing and hosted web-service usage terms are not treated as the same permission.

## Raw evidence retention

Raw provider responses are evidence, not canonical records.

Candidate policy for the first adapter:
- content-address each retained raw response with provider, request identity, fetch timestamp, HTTP status/schema version and payload hash;
- encrypt/protect evidence according to the environment's normal data controls;
- do not expose raw payloads on public pages;
- normalized claims/canonical decisions must remain traceable after raw evidence expires.

**Owner decision required before live activation:** approve a concrete raw-evidence retention class and duration. Until then, persistent raw-response archival is disabled outside deterministic fixtures/tests.

This avoids inventing an indefinite retention period where MusicBrainz publishes no provider-specific deletion requirement for this read-only core-metadata path.

## Cache/update semantics

SongChart may cache approved core metadata only after the raw-retention decision and adapter contract exist. Cache entries must record fetch time and provider identity.

Do not poll MusicBrainz solely to detect changes. Refresh is demand/maintenance driven, rate-limited and auditable.

Provider identifiers can redirect or merge over time. A refreshed MBID must be resolved as external identity evidence; it must never silently rewrite SongChart canonical identity without domain validation/review.

## Activation gates

### G0 — policy review
Implemented by this document and the Technology Registry entry. Remaining owner decisions:
1. raw-evidence retention class/duration;
2. commercial hosted-service posture before any commercial/public production use.

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
- fixture coverage plus a separately approved bounded live probe.

### G4/G5
Require the commercial-use decision (if applicable), privacy/security review, operational failure handling, and production deployment evidence. No earlier gate implies production approval.

## Replacement / retirement

The adapter must remain behind a SongChart-owned provider contract. MusicBrainz-specific HTTP/data-shape details must not leak into canonical domain identity.

If the provider is retired:
- stop new fetches;
- retain only evidence permitted by the approved retention decision;
- preserve SongChart canonical history and provider-ID provenance according to SongChart policy;
- remove scheduled probes/credentials/configuration without deleting canonical entities merely because the provider disappears.

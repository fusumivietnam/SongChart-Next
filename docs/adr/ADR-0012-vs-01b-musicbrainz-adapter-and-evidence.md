# ADR-0012 — VS-01b MusicBrainz adapter, request gate and evidence retention

- Status: accepted for implementation
- Date: 2026-10-04
- Capability: `provider-adapters`, `provider-policy`
- Scope: development, deterministic testing and bounded non-commercial evaluation only

## Context

VS-01a established SongChart-owned Artist identity and canonical admission from a deterministic MusicBrainz-shaped claim. VS-01b may add live MusicBrainz reads only after provider-specific rate, rights and retention decisions. Owner decisions B1/B2 approved on 2026-10-04 set raw evidence retention to 30 days for successful approved-core responses and 7 days for provider-error/malformed payloads, while commercial/public production remains blocked pending a separate MetaBrainz commercial posture.

The MusicBrainz public service requires meaningful client identification and a deployment-wide request ceiling. A process-local throttle is insufficient because multiple PHP workers could bypass it.

## Decision

1. Use Laravel's installed HTTP client; add no new provider HTTP package.
2. Keep MusicBrainz behind SongChart-owned typed provider contracts. The provider client returns normalized claims or typed errors and has no dependency on canonical persistence/import classes.
3. Enforce request spacing through PostgreSQL `provider_request_gates`. Each attempt acquires a row lock and reserves the next allowed request time one second later. This serializes cooperating workers across the deployment rather than only within one PHP process.
4. Retry MusicBrainz `503` responses at most three total attempts with bounded exponential backoff plus deterministic request-scoped jitter. Every retry reacquires the global request gate.
5. Persist provider evidence as:
   - content-addressed raw payload blobs keyed by `(provider, sha256(payload))`;
   - separate fetch events containing request identity, timestamp, HTTP status, schema version, retention class and expiry.
6. Successful approved-core response evidence expires after 30 days. Provider-error/malformed evidence expires after 7 days. Network failures record a fetch event without fabricating a raw payload.
7. Cleanup is explicit and deterministic through `songchart:provider-evidence:purge`; expired raw blobs are removed only after no retained fetch event references them.
8. Live provider access is disabled by default with `MUSICBRAINZ_LIVE_ENABLED=false`.
9. The delivery command `songchart:musicbrainz:artist` fetches/normalizes only. Passing a successful claim into canonical admission requires explicit `--admit`; provider code never writes canonical tables directly.
10. CI uses deterministic HTTP fakes and real PostgreSQL. It must not contact MusicBrainz. Any bounded live probe requires separate explicit approval immediately before execution.

## Consequences

- No Redis or workflow engine is introduced for the first provider slice.
- PostgreSQL is temporarily both canonical persistence and coordination mechanism for this low-rate provider boundary; this is acceptable at one request/second and avoids a second source of runtime truth.
- Holding a PostgreSQL row lock while waiting can occupy one connection for at most roughly one second under normal operation. If provider throughput or worker scale later makes this material, replacement requires measured evidence and a new decision.
- Provider payload retention is auditable without making raw provider data canonical.
- Commercial/public production remains blocked even when G1/G2 implementation tests pass.

## Verification

The VS-01b exact-SHA workflow must prove on PostgreSQL:
- provider evidence migration and retention cleanup;
- meaningful User-Agent and allowed Artist normalization boundary;
- typed success, 404, malformed, network and 503 outcomes;
- bounded 503 retry/backoff/jitter;
- deployment-wide sequential request spacing;
- no canonical Artist mutation on provider failure;
- live external network access remains disabled in CI.

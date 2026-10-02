# Provider evidence, rights and retention policy

Status: approved policy baseline, 2026-09-29. Live-provider activation still requires provider-specific review and evidence.

## Boundary
A provider response is source evidence, not SongChart canonical truth. Provider adapters normalize evidence into typed claims; application/domain admission decides whether a claim may affect canonical data.

Required flow:

provider fetch -> raw evidence -> normalized claim -> validation -> canonical decision

No provider, UI, workflow engine or AI path writes canonical tables directly.

## Provider-specific review before live activation
For each live provider record and review:
- source/service identity and authoritative terms URL;
- fetch/API permission and authentication model;
- quota/rate-limit/backoff requirements;
- fields/assets permitted to store, cache and redisplay;
- attribution requirements;
- retention/deletion/update obligations;
- privacy/personal-data implications;
- failure behavior and provider-unavailable behavior;
- replacement/retirement path.

Unknown rights or terms block the affected fetch/store/display behavior; they do not get inferred from another provider.

## Raw evidence retention
Raw provider payloads are evidence artifacts, not canonical entities. The default model is content-addressed evidence with explicit fetch timestamp, provider identity, request identity, content hash/schema/version and a retention class.

Do not assume indefinite retention. A provider-specific decision must set the retention period or justify long-lived archival. Normalized claims/canonical decisions have their own retention/history rules and must remain auditable even when raw payload retention expires, subject to provider/legal constraints.

## Artwork and media
Metadata, artwork and media destinations are separate provider responsibilities. VS-01a has no live artwork dependency and may use deterministic placeholders. Artwork providers (for example Cover Art Archive if evaluated later) require their own rights/cache/attribution review.

SongChart links to permitted listening/viewing destinations by default and does not redistribute audio/video unless a later explicit product/legal decision says otherwise.

## MusicBrainz activation
MusicBrainz-shaped deterministic fixtures are permitted for VS-01a contract/testing. Live MusicBrainz HTTP integration belongs to VS-01b. The current provider-specific candidate review is [MusicBrainz provider-specific policy](MUSICBRAINZ.md); it records the reviewed rate-limit/licensing/privacy boundaries while intentionally leaving raw-evidence retention duration and commercial hosted-service posture as owner decisions before live activation.

## Canonical merge/split
Provider identifiers can support identity resolution but are not SongChart canonical IDs. Merge/split must preserve history/redirects, pass deterministic domain validation and receive appropriate review. Provider or AI confidence alone never approves a canonical merge.

# MusicBrainz release lookup — VS-06 fixture/fake contract

Status: **implemented contract for deterministic fixture/fake verification only**. This document does not expand MusicBrainz live-provider activation or commercial/public production permission.

Owning slice: `VS-06`  
Owning issue: `#134`  
Provider policy: [MUSICBRAINZ.md](MUSICBRAINZ.md)

## Reviewed upstream shape

The MusicBrainz Web Service v2 API documents release lookup as:

`/ws/2/release/{MBID}?inc=<INC>`

For the bounded SongChart release/recording path, the documented include families of interest are:
- `artist-credits`;
- `recordings`;
- `release-groups`;
- `media`;
- `isrcs` when recordings are included.

Reviewed upstream source: `https://musicbrainz.org/doc/MusicBrainz_API`.

The release lookup response is treated as provider evidence. Its MBIDs are external identity, never SongChart canonical identity.

## SongChart mapping boundary

`MusicBrainzReleaseLookupAdapter` accepts the documented top-level release JSON shape and delegates to the existing VS-02 `MusicBrainzReleaseBundleNormalizer` / `ReleaseBundleClaim` contract. The adapter may map:
- release MBID/title/status/country/date/barcode;
- release-group MBID/title/primary type/disambiguation;
- release artist credits;
- media and track ordering;
- recording MBID/title/length/disambiguation/artist credits;
- recording ISRCs.

The existing `ImportReleaseBundle` remains the only admission path used by this slice. Provider-shaped persistence is not introduced.

## Explicit exclusions

VS-06a does **not** infer or fabricate Recording-to-Work relationships from a release lookup. Work enrichment requires a separately verified MusicBrainz relationship/recording boundary and its own deterministic fixture/fake evidence.

This contract also excludes:
- live HTTP requests or automatic provider probes;
- Cover Art Archive;
- supplementary/user data;
- commercial/public provider use;
- provider-side search/browse activation;
- any direct provider write to canonical tables.

The existing `docs/providers/MUSICBRAINZ.md` live activation scope remains authoritative and is not broadened by this fixture-only contract.

## Verification

Deterministic tests must prove:
- an API-shaped release fixture maps to the existing SongChart release-bundle claim;
- stable external IDs are preserved;
- repeated import is idempotent by external identity;
- absent required release-group/media structures fail before canonical mutation;
- Work/Recording-to-Work rows are not invented when the provider payload does not supply a separately approved relationship claim;
- existing VS-02 public Release/Recording behavior remains green.

A future MusicBrainz Release HTTP client requires a separate implementation issue/PR and provider-policy review before live activation.

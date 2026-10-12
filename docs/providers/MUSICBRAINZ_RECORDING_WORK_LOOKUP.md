# MusicBrainz Recording→Work lookup — VS-06 fixture/fake contract

Status: **implemented contract for deterministic fixture/fake verification only**. This does not expand MusicBrainz live-provider activation or commercial/public production permission.

Owning slice: `VS-06`  
Owning issue: `#137`  
Provider policy: [MUSICBRAINZ.md](MUSICBRAINZ.md)

## Reviewed upstream shape

MusicBrainz Web Service v2 supports relationship includes such as `work-rels`. JSON relationship entries expose relationship `type-id`, `type`, `direction`, `target-type`, the target entity object and optional relationship attributes.

The Recording↔Work `performance` relationship type-id is:

`a3005666-a872-32c3-ad06-98af558e99b0`

Reviewed upstream sources:
- `https://musicbrainz.org/doc/MusicBrainz_API`
- `https://musicbrainz.org/doc/MusicBrainz_API/Examples`
- `https://musicbrainz.org/relationships/recording-work`

## SongChart mapping boundary

`MusicBrainzRecordingWorkAdapter` accepts a deterministic MusicBrainz recording lookup JSON shape and maps only forward Recording→Work `performance` relations into `RecordingWorkClaim`.

`AdmitRecordingWorks` is the canonical admission boundary. It requires the Recording to have already been admitted by stable MusicBrainz Recording MBID, resolves or creates canonical Work identity by stable Work MBID, and writes only the SongChart-owned `recording_work` relationship.

Unrelated relation types are ignored. Name-only identity resolution and provider-shaped canonical tables are prohibited.

## Fidelity boundary

The current SongChart `recording_work` schema stores Recording, Work and `relationship_type`, but does not represent MusicBrainz performance relationship attributes such as `cover`, `partial`, `live`, `instrumental`, `karaoke`, `demo`, `medley` or `a cappella`.

VS-06b therefore accepts only performance relations whose `attributes` array is empty. Any non-empty attributes fail before canonical mutation. Preserving those modifiers requires an explicit canonical-model/ADR change rather than lossy normalization.

## Explicit exclusions

VS-06b does not introduce:
- live HTTP requests or automatic provider probes;
- commercial/public provider activation;
- Cover Art Archive;
- Work→Artist composer/lyricist enrichment;
- relationship-attribute persistence;
- public API or search-index activation;
- direct provider writes to canonical tables.

## Verification

Deterministic tests must prove:
- supported Recording→Work performance JSON maps to a typed claim;
- an already-admitted Recording is resolved only by stable external identity;
- Work admission and relationship attachment are idempotent;
- missing Recording identity fails before Work mutation;
- malformed supported relations fail rather than disappearing silently;
- non-empty unsupported relationship attributes fail before mutation;
- existing VS-02 and VS-06a behavior remains green.

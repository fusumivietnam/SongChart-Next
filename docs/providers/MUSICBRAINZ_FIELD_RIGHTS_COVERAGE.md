# #174 — Field-level rights triage and synthetic coverage evidence

**Status: proposal for review only.** Not a license or retention approval, source activation, real-data import, or change to canonical admission. Provider authority remains `MUSICBRAINZ.md` and `PROVIDER_POLICY.md`.

## Recorded source discrepancy, reviewed 2026-11-24

The MetaBrainz [dataset catalog](https://metabrainz.org/datasets/postgres-dumps) labels official MusicBrainz JSON dumps CC0 at dataset level. However, the more specific official [MusicBrainz JSON Data Dumps documentation](https://musicbrainz.org/doc/Development/JSON_Data_Dumps) explicitly states that each item's `annotation`, `genres`, `ratings`, and `tags` are **CC BY-NC-SA 3.0**. [MusicBrainz Database](https://musicbrainz.org/doc/MusicBrainz_Database) independently distinguishes core CC0 from supplementary data; [upstream issue MBS-12977](https://tickets.metabrainz.org/browse/MBS-12977) tracks this documentation discrepancy and was shown as unresolved when checked. The issue is a conflict signal, not itself a license grant.

**Fail-closed review decision:** use the more specific per-field exclusion. Do not treat dataset-level CC0 wording as permission to retain, publish or commercially use every nested JSON field. Core-looking fields remain *review_required* pending owner/legal review of exact archive, path, provenance and terms. This document does not change provider-policy activation status.

## Exact Recording projector input paths

`MUSICBRAINZ_FIELD_RIGHTS_MATRIX.json` inventories **31** current `OfflineRecordingProjector` input paths with four statuses:
- `structural_container / never_export_whole_object`: `$.artist-credit[*]` is an iteration boundary used to derive ordered credit position, never a license or permission to emit the entire nested Artist-credit object
- `core_candidate / review_required`: Recording id/title/length/disambiguation; ordered Artist credits and their MBIDs; ISRCs (not proof of ownership); plain performance relation selectors and Work MBID/title/type/disambiguation
- `supplementary_cc_by_nc_sa / exclude`: top-level tags, genres, rating, annotation, nested Artist tags/genres and Work tags — examples only, **not an exhaustive denylist**
- `semantics_unsupported / quarantine_nonempty`: performance attributes, attribute-ids and attribute-values — semantic refusal, **not a copyright claim**
- `not_reviewed / exclude_pending_review`: nested aliases, work ISWCs/languages, video; exclusion is not an assertion that these are all non-CC0

**Boundary:** this is a source-path review map for an offline **Recording** projector, not a generic recursive source schema. Unknown nested data must never be admitted merely because its parent is mapped. Artist, Release Group, Release and standalone Work archive path inventories are explicitly **blocked/unmapped** until their actual serialized schemas are independently verified.

## Synthetic-graph coverage and gaps

The merged PR #264 fixtures define **8/8 structurally linked synthetic scenarios** (G01–G08) with expected statuses: **five evaluation-only, two quarantine and one evaluation-with-admission-blocked**. The new Python governance test verifies matrix decisions, explicit supplementary exclusions, eight graph IDs, target alias integrity and scenario-outcome distribution. It does **not** run a provider adapter or a real four-entity join.

**Not established:** full-path application acceptance (0/8 demonstrated), MusicBrainz real-row/legal eligibility (0/8 demonstrated), commercial/public rights approval (0/8), and canonical admission (intentionally 0/8). G08 intentionally represents an admission-blocked business question; the existing Recording projector independently quarantines duplicate ISRC within a row. Do not interpret G08's graph-level expected status as a passing projector outcome.

MusicBrainz [JSON dump format guidance](https://musicbrainz.org/doc/Development/JSON_Data_Dumps) specifically says the Recording archive contains **standalone recordings**, other recordings are accessible nested under Releases, and some Work↔Recording relationships need to be found on the **Work** side. Thus a Recording-only first-100-row sample cannot prove full Release–Recording–Work coverage. Any later entity pilot needs a source-map and join/completeness design for distinct Artist, Release Group, Release and Work archives, legal/privacy review, retention budget and owner authorization before any real data use.

## No implicit activation

This PR uses only synthetic metadata; no MusicBrainz archive or MBID, provider HTTP, PostgreSQL writes, secrets, new dependencies, ingestion CLI, source-adapter activation, production deployment or SongChart canonical admission changes. Rights classification remains a triage proposal. #174 stays open for field-by-field signoff and sample-method design.

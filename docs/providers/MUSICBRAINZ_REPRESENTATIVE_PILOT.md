# #174 — MusicBrainz rights review and representative offline pilot (proposal)

**Status:** evaluation design, not legal clearance, provider activation, import approval, or canonical-admission change.
**Owners:** provider-policy, provider-adapters; canonical-music-core remains the only downstream admission authority.
**Scope:** compare a core-only MusicBrainz JSON dump candidate with the commercial hosted API alternative, and plan **8 synthetic entity groups** before any separately approved real-data evaluation.

## Source-specific findings (24 November 2026)

Official sources checked:
- https://musicbrainz.org/doc/About/Data_License — core database CC0; supplementary database data CC BY-NC-SA 3.0; live feed different terms.
- https://musicbrainz.org/doc/MusicBrainz_Database — identifies core categories (Artist, Release, Release Group, Recording, Work, medium, credits, relationships and ISRC), and supplementary categories (user tags, annotation, ratings, statistics and edit history).
- https://metabrainz.org/datasets/postgres-dumps — JSON data dumps described as CC0, JSONL, twice weekly; content is denormalized/duplicated; commercial usage allowed and financial support strongly encouraged. PostgreSQL full dumps have mixed licensing classes.
- Existing authority: [MUSICBRAINZ.md](MUSICBRAINZ.md) and [PROVIDER_POLICY.md](PROVIDER_POLICY.md).

**Reconciliation, not expanded permission:** the upstream dataset-level CC0 statement for *official JSON dumps* is stronger than the generic PostgreSQL core/supplementary split. It does not prove that every nested JSON key from a particular snapshot is fit for SongChart storage/display, nor grant rights to external links/artwork/media or to hosted API access. SongChart's existing field-by-field, core-only policy remains the conservative gate until owner/legal review accepts a specific source archive, format and allowlist. Do not silently reclassify the dataset or promote an activation state.

## Provisional field-rights review matrix

| Proposed data | Evidence / classification | SongChart decision for this pilot |
| --- | --- | --- |
| Artist MBID, name, sort name, type, disambiguation | MusicBrainz core entity class; JSON dump CC0 dataset claim | **Candidate for rights review**, synthetic design only |
| Release Group/Release MBIDs, titles, status, date precision, medium/track structure | Listed as core categories; individual serialized nested fields require mapping | **Candidate for rights review**, synthetic design only |
| Recording MBID, title, length, disambiguation | Core Recording; JSON dump CC0 dataset claim | **Candidate for rights review**, no actual import |
| Credited Artist external MBID, credited name, join phrase, order | MusicBrainz core credits/relationships; exact nested JSON schema needs review | **Candidate for rights review**, no name-only matching |
| ISRC | Named in core Recording metadata; identifier does not prove exclusive ownership | **Candidate for rights review**, subject to downstream collision and rollback gate |
| Work MBID, title, nullable type/disambiguation; plain Recording→Work performance | Work/relationships within core overview; relation attributes may alter semantics | **Candidate only for un-attributed supported relation**, otherwise quarantine |
| Tags/genre associations, ratings, annotations, edit/user history, derived stats | Supplementary examples on MusicBrainz Database page | **Exclude** regardless of their presence in sampled payload |
| Cover Art Archive artwork, audio/video, provider destination links | Not licensed by MusicBrainz metadata grant alone | **Out of scope** and independently rights-gated |
| Live MusicBrainz Web Service and replication | Separate transport/usage terms and commercial agreement questions | **Not activated**; no network tests |
| Bulk dump retention, refresh, attribution | CC0 license not a storage budget/privacy/change policy | **Owner/legal + operations review required** |

This matrix is a **research triage**, not field-level license signoff. Record exact archive type and contemporaneous upstream license statement, including any terms updates, before a future owner decision.

## Eight synthetic representative entity groups

See `tests/Fixtures/musicbrainz/offline-pilot/representative-groups.json` for **scenario definitions only**, not MusicBrainz-shaped real records. No real MBIDs or personal identifiers. These groups are designed to cover both the four-entity navigation chain and meaningful negative cases.

| ID | Scenario | Expected evaluation (no DB writes) |
| --- | --- | --- |
| G01 | Artist → Release Group → Release → Medium/Track → Recording → plain Work performance | Complete canonical *eligibility scenario*, **not actual admission** |
| G02 | Multi-Artist ordered credits and join phrases | Preserve order and exact external identities; never fuzzy match |
| G03 | Same recording reused on two releases | One distinct external Recording identity; no deduplication by title |
| G04 | One Recording, multiple un-attributed Works | Preserve distinct Work identities; no unsupported relation flattening |
| G05 | Valid Recording without Work | Allow Recording-only candidate; no inferred composition |
| G06 | Attributed performance relation (cover/live/instrumental/partial) | Whole affected candidate quarantine with reason |
| G07 | Missing, contradictory or malformed Artist/Work/Recording MBID | Quarantine; no name fallback or guessed canonical identity |
| G08 | Duplicate/contradictory ISRC claims and supplementary nested tags/ratings | Recursive exclusion; ISRC ownership collision remains a *later* admission blocker |

## Phase-gated acceptance

1. **Synthetic matrix verification:** scenario fixture schema and uniqueness checks; no real IDs; assert relationship preservation, missing links, exact allowlist, quarantines and deterministic replay in tests. Existing `OfflineRecordingProjector` and `OfflineRecordingBatchEvaluator` can evaluate Recording-only cases, not a full linked entity group. Do **not** claim the end-to-end dataset evaluation is implemented.
2. **Source and rights:** classify every proposed field in its concrete file/JSON path, record official core-or-JSON-CC0 proof and source archive SHA/signature, distinguish third-party rights and commercial API usage, resolve any ambiguous nested keys explicitly. Request owner/legal signoff before live-data import or redisplay.
3. **Representative completeness:** the known verified local snapshot comprises a **Recording archive only**; it cannot establish Artist→Release→Recording→Work complete coverage. Future **separately approved** source acquisition/inspection would need Artist, Release Group, Release and Work archives, identity join rules, repeatability and sample selection that avoids biased first-N-only conclusions.
4. **No admission bypass:** source JSON → allowed evidence → normalized claims → validation → SongChart application admission, with canonical ID separation, transactional ownership checks, duplicate handling, error rollback and corrections review. This proposal stops before the admission arrow.
5. **Operational/retention:** no bulk dump committed to Git/CI, no live HTTP, no raw payload persistence; a bulk-storage/expiry decision and applicable provider terms must precede any real-data pilot.
6. **Exit:** review #174 remains open until rights decision and representative legally permitted dataset evidence are independently accepted. CI PASS for synthetic artifacts must not promote `provider-adapters` or mark commercial/public use approved.

No new external service, dependency, schema, migration, provider network request or production deployment is proposed.

### Abstract synthetic link fixtures

`tests/Fixtures/musicbrainz/offline-pilot/synthetic-graphs.json` encodes eight **abstract graphs** with deterministic synthetic aliases and explicit directed links. The registry contract tests check that every graph matches its scenario, all link targets resolve, credit order/reuse/multi-work and negative gates are represented. These are **not MusicBrainz JSONL payloads**, cannot be passed to the production adapter, and do not test canonical admission or rights eligibility. Future executable source-shape fixtures require a separate field-level review and a targeted application contract change; never treat an abstract link graph as a legally permitted source row.

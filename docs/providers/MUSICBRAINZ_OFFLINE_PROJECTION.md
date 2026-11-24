# Offline Recording projection contract — candidate (#174)

**Proposed for review; NOT approved for ingestion, public use, redistribution or provider activation.** Owns the offline evaluation boundary for `provider-adapters`; downstream SongChart admission remains owned by `canonical-music-core`.

## Evidence and flow

The signed/hashed 20261118-001001 Recording archive was evaluated on the first **100 rows only**: 88 shape-valid (47 with supported Work, 41 Recording-only), 12 quarantined on attributed performance links. Attributes: instrumental=5, cover=3, partial=3, live=1; 12 distinct affected Recording rows / relations / occurrences. Not representative of the full dataset or a rights clearance.

```
verified local snapshot (never committed)
 -> bounded read-only JSONL decoder
 -> strict recursive allowlist + validation
 -> typed evaluation candidate | explicit quarantine reason
 -> aggregate statistics and minimal provenance reference
 [STOP: no DB, HTTP, provider activation, or raw payload persistence]
```

## Candidate contract

**Candidate-only core fields pending per-field CC0/terms review:** Recording external MBID, nonempty title, nonnegative length in ms, nullable disambiguation; ordered credited Artists (artist MBID, credited_as, joinphrase, position); zero or more format-validated ISRCs; zero or more linked Works (Work external MBID, title, nullable type/disambiguation, relationship_type=performance). SongChart canonical IDs are distinct from MBIDs; no name-based merges, implied ISRC ownership, or inferred Works.

**Strict recursive exclusion:** never copy MusicBrainz source objects wholesale. Drop `tags`, `genres`, `rating`, `annotation`, `aliases`, `video`, user data, arbitrary links, nested Artist `tags/genres/aliases`, nested Work `iswcs/language/languages/attributes`, and all unapproved/unknown keys. No raw supplementary values in projection, logs or retained evidence.

**Work links:** require `target-type=work`, `type-id=a3005666-a872-32c3-ad06-98af558e99b0`, `type=performance`, `direction=forward`, valid Work UUID/title and empty `attributes`. Offline fail-closed also requires `attribute-ids=[]` and `attribute-values=[]` until reviewed for consistency with the current `MusicBrainzRecordingWorkAdapter`. Unrepresentable attributed performance must quarantine the **entire affected candidate**, not silently strip the relationship. Supported type IDs but invalid Work/direction also quarantine. Non-work/unrelated relations are excluded, not inferred. A Recording with no supported Work is still a Recording-only candidate.

**Quarantine:** malformed JSON/shape; invalid Recording/Artist/Work MBIDs, title, length, credits, ISRC; unsupported performance attributes; inconsistent supported relations. Duplicate conflicting ISRC ownership and idempotency must be enforced transactionally at **later canonical admission**, never assumed from offline shape checks. Do not send standalone Recording JSONL into `ImportReleaseBundle` (expects Release Group/Release/media), and do not invoke `AdmitRecordingWorks` before a Recording is admitted.

**Provenance reference, not source content:** provider=musicbrainz, source=json-dumps/recording, snapshot ID, SHA256 of archive with signed manifest/key-fingerprint verification reference, source-line ordinal, policy revision, observed_at. Raw provider evidence follows approved retention classes (30-day success, 7-day error); ongoing local bulk-dump retention needs separate owner/legal approval.

## Synthetic fixtures and implementation acceptance

- `recording-performance-valid.json`: valid Work performance, including synthetic supplementary keys; projection must contain ONLY allowlisted fields including nested values.
- `recording-without-work.json`: valid Recording-only with syntactically valid ISRC, no invented Work or inferred ISRC ownership.
- `recording-attributed-performance.json`: `cover` attribute => quarantine, no semantic data loss.
- `recording-invalid-credit.json`: bad nested Artist MBID => quarantine; no fallback fuzzy-name merging.

Next bounded implementation: a pure read-only projector with automated tests for exact projected key lists, nested exclusions, supported/unsupported/multiple relations, failures, deterministic replay, provenance references and non-mutating behavior. Use synthetic fixtures in CI; never commit real MusicBrainz rows or run live API in CI. Keep #174 open. Before real data import, separately approve per-field commercial/public-use rights, provider attribution, bulk retention, representative Artist→Release→Recording→Work coverage, canonical ID resolution, ISRC ownership transaction rollback, and source admission. No capability lifecycle promotion from this design PR.

Authority: [MusicBrainz policy](MUSICBRAINZ.md), [Provider policy](PROVIDER_POLICY.md), [Architecture](../architecture/ARCHITECTURE.md).


## Bounded evaluation and provenance reference (implementation candidate)

`OfflineRecordingBatchEvaluator` (proposed in the next PR) accepts an iterable of synthetic JSONL lines, a strictly shaped **operator-supplied** source reference and a limit of 1–100 lines. It delegates each line to `OfflineRecordingProjector::projectJson()` without invoking canonical admission, databases, HTTP or filesystem writes. Its return contains **aggregate counts only**, deterministic quarantine-reason buckets and a provenance reference (snapshot ID, archive SHA256, signing-key fingerprint, source line range and observed-at timestamp). It never emits Recording title, Artist credit, Work title, full JSON payload or per-row IDs.

**Trust distinction:** checksum/fingerprint fields are syntactically validated but **not cryptographically verified by the evaluator**. The result explicitly says `operator_supplied_not_verified_by_evaluator`. The operator must separately verify the signed SHA256 manifest and archive before treating references as independently verified evidence. This component neither initiates downloads nor authorizes ongoing retention of a bulk dump.

Four synthetic fixture cases yield two evaluation candidates (one with Work, one Recording-only) and two quarantines (unsupported performance attributes, invalid Artist MBID). Limits, malformed JSON, empty batches, redaction and deterministic replay are tested. These are tests of the **evaluation mechanism**, not tests of real-world import, source licensing or data completeness.

This batch evaluator deliberately exposes no CLI/Artisan command and writes no report file. A controlled offline runner and any use against real archived rows are separately reviewed/approved; in CI use synthetic fixtures only.

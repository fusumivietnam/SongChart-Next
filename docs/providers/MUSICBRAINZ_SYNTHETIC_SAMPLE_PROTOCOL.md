# #174 — Synthetic quality, completeness, and reproducible sampling

**Proposal only.** The parent authority is [MUSICBRAINZ_FIELD_RIGHTS_COVERAGE.md](MUSICBRAINZ_FIELD_RIGHTS_COVERAGE.md) and #174. No permission for MusicBrainz real data, hosted API, dump retention, rights activation, canonical admission, or production.

## Unit of measurement

The fixed evaluation unit is a **synthetic abstract graph scenario**, not a real Recording or MusicBrainz archive row. The cohort is **all G01–G08**, which is within the approved design envelope of 5–10 entity groups. This is a stratified **census of authored fixtures**, not random sampling of a provider population.

The stratum assignment is stable:
- Full navigation journey: G01 (1)
- Identity/link complexity: G02–G05 (4)
- Negative semantic/rights gates: G06–G08 (3)

Always retain negative cases. Avoid selecting the first N real dump lines as a representative sample: that can bias toward standalone Recording, omit Release-nested Recording and miss Work-side relations. Future real source sampling requires independent rights/storage approval, source inventories and reproducible random/stratified selection design.

## Quality and completeness measurement

The read-only `scripts/evaluate_musicbrainz_synthetic_coverage.py` compares the three **synthetic-only** fixture files and fails if identifiers, stratification, entity types, outcomes or link endpoints drift. Its output is aggregate JSON only, no row payloads.

| Indicator | Numerator | Denominator | Interpretation |
| --- | --- | --- | --- |
| Authored group coverage | Present scenario IDs | 8 planned IDs | Fixture coverage, not actual provider coverage |
| Link integrity | Graph links with existing local endpoints | All synthetic graph links | Structural consistency, not correct upstream relationships |
| Entity-type breadth | Required entity types represented | 7 specified types | Artist, Release Group, Release, Medium, Track, Recording, Work represented somewhere in cohort |
| Relationship-type breadth | Required kinds represented | 6 specified kinds | Breadth of abstract link types, not API or import accuracy |
| Expected outcome strata | Groups per outcome category | 8 groups | 5 evaluation-only; 2 quarantine; 1 evaluation-with-admission-blocked |
| Evidence of application acceptance | Verified end-to-end real/app group journeys | 8 planned scenarios | **0/8 established; not exercised by this test** |
| Legally approved source groups | Owner/legal-signed eligible groups | 8 planned scenarios | **0/8 established; must not be inferred from CC0 archive label** |

**Acceptance rule for this PR:** structural metrics above reach full authored-scenario coverage, graph references resolve, all required entity/relation classes and adverse cases remain, deterministic replay agrees. **No score** is assigned to source fidelity, provenance cryptographic verification, false merges, freshness, copyright clearance, throughput or canonical correctness, because they were not measured.

**Important G08 distinction:** the abstract graph's `evaluation_with_admission_blocked` describes a policy-decision scenario. The existing Recording projector rejects an intra-record duplicate ISRC with `duplicate_isrc`. The graph is **not** a successful executable Recording JSONL test. G06 similarly bundles four attributed-performance cases conceptually; it is not four independently executed raw-row tests.

## How to reproduce the synthetic-only report

```bash
python3 scripts/evaluate_musicbrainz_synthetic_coverage.py
python3 -m unittest tests.governance.test_musicbrainz_synthetic_quality -v
```

Both commands require only Python's standard library and local committed synthetic fixtures; no database, network, Composer, provider integration, file writes or runtime flag changes.

## Gates before any future representative real-data sample

1. Archive-by-archive signed manifest and hash verification, exact allowed JSON source paths and field rights/retention owner signoff.
2. Source topology plan spanning Artist, Release Group, Release, Work and Release-nested Recording; preserve release–track–recording and Work-side edges, dedupe by stable external IDs only.
3. Choose a bounded, reproducible stratification and random seed **after** distribution inspection; sample negative/rare relationships separately. Define population counts and missing-link denominators rather than extrapolating from the first 100 Recording rows.
4. Separately review false-merge/false-split, link loss, work-less recordings, duplicate ISRC, unsupported relation attributes, unknown rights and retrieval/retention exposure; no canonical write until a further explicit admission decision.

No new provider code, dependency, external service or extra CI workflow is introduced by this synthetic evaluation protocol.

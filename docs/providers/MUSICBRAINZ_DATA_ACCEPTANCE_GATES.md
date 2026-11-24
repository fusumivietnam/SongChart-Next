# #174 — Data quality acceptance and provider-rights decision gates

**Proposal — only synthetic scope implemented.** This checklist is executable governance evidence for the design phase, not a legal opinion, provider activation decision, real-data import authorization, a new capability lifecycle authority, or permission to mutate canonical SongChart data. Owning authorities remain [MusicBrainz policy](MUSICBRAINZ.md), [provider rights and retention](PROVIDER_POLICY.md), [31 Recording field-path triage](MUSICBRAINZ_FIELD_RIGHTS_COVERAGE.md), [synthetic sampling protocol](MUSICBRAINZ_SYNTHETIC_SAMPLE_PROTOCOL.md), [acceptance gates](../operations/ACCEPTANCE_GATES.md), and GitHub Issue #174.

## What can pass today

Three **synthetic-only** gates (SYN-01–03) measure coverage of exactly eight authored abstract graph scenarios:
- **SYN-01**: 8/8 G01–G08 IDs represented in three specified strata, including all negative cases;
- **SYN-02**: all abstract links resolve within their graph; seven entity types and six relation types are represented across the authored cohort;
- **SYN-03**: outcome-design distribution is 5 evaluation-only, 2 quarantine, 1 conceptually blocked at admission. These are **expected classifications, not observed decisions made by a running provider importer**.

The existing standard-library script `python3 scripts/evaluate_musicbrainz_synthetic_coverage.py` reports those aggregate facts. This PR adds the fail-closed contract file `MUSICBRAINZ_DATA_ACCEPTANCE_GATES.json` and governance regression checking gate separation. It does **not** falsely mark synthetic tests as real-world data acceptance.

## Conditions that remain blocked

| Gate | Required decision/evidence | Why it blocks |
| --- | --- | --- |
| RGT-01 — per-field rights | Every **used leaf field** in the exact archive and nested path, current terms, excluded supplementary/user fields, owner/legal signoff | Dataset-level CC0 wording does not override specific CC BY-NC-SA tags/ratings/genres/annotations or unknown nested fields |
| RGT-02 — commercial/service use | Select exactly one approved primary ingestion path (hosted API vs officially licensed core dump); commercial terms, external art/media rights assessed separately | Metadata license, API service contract, feed and media destinations have distinct obligations |
| OPS-01 — provenance | Verify signed manifest **and** archive hash independently, snapshot ID and locator, schema revision | The existing batch evaluator intentionally labels provenance `operator_supplied_not_verified_by_evaluator`; syntactic checksum fields are not cryptographic evidence |
| OPS-02 — retention and privacy | Explicit bulk-dump retention, expiry/deletion evidence, budget, privacy review | The existing 30-day successful provider JSON / 7-day error policy does **not** automatically authorize storing a raw bulk dump or supplementary fields |
| QLT-01 — real sample completeness | Source populations and denominator by archive, reproducible stratification and seed, Release-nested Recording coverage, Work-side relationship coverage, missing-link rates | First 100 standalone Recording rows cannot prove full Artist→Release→Recording→Work coverage |
| QLT-02 — quality and disambiguation | Approved thresholds and disposition review for false merges/splits, MBID/canonical separation, duplicate ISRC, missing Work, attributed performance quarantine and replay | A structurally consistent synthetic graph is not source fidelity or safe domain matching |
| CAN-01 — canonical admission | Separate explicit approval, authorized application/domain validation, transactional rollback, identity/correction reviewer constraints, tested real journey | Provider evidence must never write canonical tables directly; the current user explicitly forbids changes to admission |

All seven real-source/admission gates are **blocked** and cannot be promoted by a green governance CI run. A real-data trial would first need its own legal/owner approval; this PR does not request one.

## Review checklist and disposition rule

For each gate, record owner, exact repository/source evidence and date, scoped fields/entity types, unresolved risks, explicit accept/reject/quarantine decision and a signature/approval link **in Issue #174 or an approved subsequent PR**. Unknown, stale, disputed or non-reproducible evidence is **blocked** rather than default-pass. Do not invent numerical quality thresholds before examining an approved population; establish denominators and a calibrated decision rule before claiming production suitability.

The machine-readable contract has `testable` status for the three synthetic checks, `blocked` for seven later checks and an overall blocked decision. It is **not** a second runtime policy engine or alternate roadmap registry. No new dependency, scheduled job, API, database, raw data archive or automatic provider request is introduced.

## Run without provider access

```bash
python3 scripts/evaluate_musicbrainz_synthetic_coverage.py
python3 -m unittest tests.governance.test_musicbrainz_data_acceptance_gates -v
```

Only synthetic graph fixtures and reviewed policy paths are read. Neither command imports real data, writes files, or calls canonical admission.

# Acceptance and release gates

These gates describe **required evidence by scope**, not a new lifecycle registry. The owning capability status is in CAPABILITY_MAP and cannot be inferred from a checklist alone.

| Gate | Required evidence | Scope |
| --- | --- | --- |
| G0 Governance | approved scope/contract/ADR where required, capability, dependencies and owner | before implementation |
| G1 Implementation | committed source, migrations and config paths tied to a Git revision | implemented |
| G2 Verification | relevant unit/integration/contract/DB/browser/security test results tied to exact SHA; reviewed acceptance cases | verified |
| G3 Release candidate | dependency/secret checks, compatibility, migration and environment parity evidence | candidate release |
| G4 Operational readiness | threat model, health/observability, incident owner, tested backup **and restore**, rollback rehearsal, provider/legal/privacy clearance as applicable | production gate |
| G5 Deployment | approved release, immutable artifact reference, production deployment status and smoke check for deployed revision | deployed |

Do not apply every operational gate to a documentation-only change or fixture-first slice; select relevant gates explicitly in the owning Issue/PR. G2 for Artist must include stable identity/idempotency invariants, DB and browser tests; G4/G5 cannot be claimed from local Docker volume persistence or a successful PR merge. Failure/unknown evidence blocks promotion but does not erase legitimate prior history. CI green at a different SHA is not acceptance evidence.

Evidence is GitHub CI run, review, PR, commit, release or deployment identifier (and optionally a source-linked runbook). No pasted chat summary, hand-edited green badge or fabricated metric is permitted. If a linked external system cannot be queried, status is unknown.

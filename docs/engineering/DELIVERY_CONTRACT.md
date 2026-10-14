# Vertical slice delivery contract

Authority: Product Charter / Architecture / Capability Map / Design Authority / owning API/provider contracts. Roadmap scope remains `docs/roadmap/VERTICAL_SLICES.md`; GitHub Issues own work items and PRs own implementation review. This document defines evidence requirements, not a second execution tracker.

Each execution Issue must identify: stable slice and capability ID(s); in/out scope; owner; dependencies and approval references; blast radius and rights/privacy/security impact; contract/input/output/error and authorization boundary; source and migration deliverables; fixture and acceptance cases; rollback/recovery relevance; linked PR(s). Create an Issue only after checking existing Issues and open PRs to avoid duplicates.

A PR must link its Issue and any material ADR, list source paths/contract and data changes, identify test commands and CI run URLs at the tested SHA, note missing checks and review decisions. A non-breaking documentation-only PR may cite a governance issue or a narrowly scoped change directly; it does not demonstrate runtime implementation.

For one bounded semantic work unit, source, tests, required documentation and required governance updates should be prepared together and reviewed in one PR. AI-authored multi-file work should keep the visible branch history atomic where practical instead of creating one commit per file mutation. Push an integration candidate only after inexpensive local/static validation; if CI or runtime evidence exposes multiple related defects, consolidate known repairs before the next push. Superseded observation-only commits are not evidence and should not be preserved merely to trigger CI. Exact-head verification remains mandatory on the final reviewed revision.

Lifecycle is **candidate -> approved -> implemented -> verified -> deployed**. A source file in a PR is not implemented on main; approval is not installation; passing governance checks is not passing product tests. Verified requires recorded acceptance evidence for the precise revision, and deployed requires release and environment evidence in addition. The Capability Map remains the status authority; GitHub Issues show execution activity, not independently asserted lifecycle state.

No UI/provider/MCP/CLI/Filament code may bypass authorized application use cases. Canonical-data operations need deterministic domain validation and review. Contract breaking changes require compatibility analysis and ADR. Retain failing tests and fixtures rather than weakening gates.

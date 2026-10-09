# GitHub Actions ownership and evidence policy

This contract defines who owns each CI concern and the controls that prevent workflow drift. It is execution governance only: capability lifecycle remains in `governance/CAPABILITY_MAP.json`, roadmap scope remains in the roadmap authorities, and exact-SHA Actions runs are evidence rather than editable state.

## Workflow ownership

| Workflow | Responsibility | Credential boundary |
| --- | --- | --- |
| `project-governance.yml` | governance regression suite, read-only status snapshot, CI ownership verifier | contents read |
| `project-os.yml` | sole owner of `verify_project_os.py` and required `verify` context; supports explicit dispatch for generated reconciliation branches | contents read |
| `roadmap-health.yml` | live Issue/PR roadmap reconciliation health, unreconciled-merge detection and required `health` context; runs on every main push | contents/issues/PR/actions read |
| `roadmap-reconcile.yml` | serialized post-merge proposal writer: reads reviewed PR metadata, writes only a reconciliation branch/PR, dispatches protected checks, fail-closes on decision-bearing metadata and may merge only the generated factual PR after exact-SHA gates pass | contents/pull-requests/actions write; never receives Project PAT |
| `project-projection-sync.yml` | serialized Project #2 field/item projection | read-only repository token + `PROJECT_SYNC_TOKEN` |
| `work-management-sync.yml` | declared labels and explicitly managed milestones | contents read + issues write; no Project PAT |
| `foundation-app.yml` | Docker app/PostgreSQL/tests/audit/SBOM/production-target evidence | contents read |
| `foundation-visual.yml` | deterministic Foundation design render evidence | contents read |
| `vs01a-artist.yml` | VS-01a canonical Artist PostgreSQL integration, canonical URL and narrow/wide browser evidence | contents read |
| `vs01b-musicbrainz.yml` | VS-01b MusicBrainz adapter contracts, evidence retention and deployment-wide request-spacing verification on PostgreSQL; never automatic live provider traffic | contents read |
| `vs02-release-recording.yml` | VS-02 Release/Recording/Credits canonical relationships, PostgreSQL integration, canonical redirects and narrow/wide browser evidence | contents read |
| `vs03-discovery-search.yml` | VS-03 PostgreSQL-first mixed-entity discovery plus canonical Search -> Artist -> Release -> Recording journey and provider-destination evidence, bounded query-plan/latency evidence and narrow/wide renders; never activates a dedicated search index or provider production access | contents read |
| `design-review-contract.yml` | one-command local Design Authority review contract | contents read |
| `codespaces-contract.yml` | devcontainer/Codespaces developer-shell contract | contents read |

`docker-scaffold.yml` is retired because Foundation application checks own Compose/PostgreSQL runtime evidence.

## Invariants

1. Protected-main contexts `governance`, `verify`, and `health` retain their existing job names.
2. `project-os.yml` is the only Actions workflow that executes `scripts/verify_project_os.py`.
3. PR evidence checks out the exact PR head; main evidence checks out the exact merged SHA.
4. PR runs may cancel stale commits, but distinct main SHAs use SHA-scoped concurrency and do not cancel each other.
5. Roadmap-health concurrency separates event families and Issue/PR identities, and main pushes are intentionally not path-filtered so implementation-only merges can expose roadmap drift.
6. Every job has a bounded timeout and runs on the pinned `ubuntu-24.04` runner label.
7. External Actions are pinned to full 40-character commit SHAs.
8. `PROJECT_SYNC_TOKEN` is available only to `project-projection-sync.yml`.
9. Work-management reconciliation gets only `issues: write` plus `contents: read`, is serialized, and never receives the Project PAT.
10. Mutating projection/reconciliation workflows are serialized rather than cancelled mid-write.
11. Foundation runtime evidence and each vertical-slice evidence workflow have separate owners; none may silently become another lifecycle authority.
12. `vs01b-musicbrainz.yml` must keep live MusicBrainz network access disabled. A bounded live probe is a separate explicitly approved action, not scheduled CI.
13. `vs02-release-recording.yml` owns deterministic VS-02 PostgreSQL/browser evidence and must not activate live provider traffic.
14. `vs03-discovery-search.yml` owns PostgreSQL-first discovery, canonical journey continuity and deterministic fixture-only destination evidence; measured CI evidence may inform later activation review but cannot activate Meilisearch, provider production rights or deployment.
15. `roadmap-reconcile.yml` never pushes authored authorities directly to `main`; it may only prepare a branch/PR after the merged source PR supplied valid machine-readable reconciliation metadata.
16. Automatic reconciliation must reject new roadmap-scope decisions, owner decisions, provider/technology activation, deployment effects, lifecycle demotion, candidate/watch promotion, or unknown capability IDs.
17. A generated reconciliation PR must dispatch and pass exact-head `governance`, `verify`, and `health` before automatic merge; any human review submission stops automatic merge.
18. Generated reconciliation branches are deleted only after successful merge. Project #2 refresh remains a derived projection step after authority reconciliation.

## Automated drift check

`scripts/verify_ci_ownership.py` validates this contract and is executed by `project-governance.yml`. Adding or retiring a workflow therefore requires updating this document and verifier in the same reviewed change.

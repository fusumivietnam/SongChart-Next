# GitHub Actions ownership and evidence policy

This contract defines who owns each CI concern and the controls that prevent workflow drift. It is execution governance only: capability lifecycle remains in `governance/CAPABILITY_MAP.json`, roadmap scope remains in the roadmap authorities, and exact-SHA Actions runs are evidence rather than editable state.

## Workflow ownership

| Workflow | Responsibility | Credential boundary |
| --- | --- | --- |
| `project-governance.yml` | governance regression suite, read-only status snapshot, CI ownership verifier | contents read |
| `project-os.yml` | sole owner of `verify_project_os.py` and required `verify` context | contents read |
| `roadmap-health.yml` | live Issue/PR roadmap reconciliation and required `health` context | contents/issues/PR/actions read |
| `project-projection-sync.yml` | serialized Project #2 field/item projection | read-only repository token + `PROJECT_SYNC_TOKEN` |
| `work-management-sync.yml` | declared labels and explicitly managed milestones | contents read + issues write; no Project PAT |
| `foundation-app.yml` | Docker app/PostgreSQL/tests/audit/SBOM/production-target evidence | contents read |
| `foundation-visual.yml` | deterministic Foundation design render evidence | contents read |
| `vs01a-artist.yml` | VS-01a canonical Artist PostgreSQL integration, canonical URL and narrow/wide browser evidence | contents read |
| `design-review-contract.yml` | one-command local Design Authority review contract | contents read |
| `codespaces-contract.yml` | devcontainer/Codespaces developer-shell contract | contents read |

`docker-scaffold.yml` is retired because Foundation application checks own Compose/PostgreSQL runtime evidence.

## Invariants

1. Protected-main contexts `governance`, `verify`, and `health` retain their existing job names.
2. `project-os.yml` is the only Actions workflow that executes `scripts/verify_project_os.py`.
3. PR evidence checks out the exact PR head; main evidence checks out the exact merged SHA.
4. PR runs may cancel stale commits, but distinct main SHAs use SHA-scoped concurrency and do not cancel each other.
5. Roadmap-health concurrency also separates event families and Issue/PR identities.
6. Every job has a bounded timeout and runs on the pinned `ubuntu-24.04` runner label.
7. External Actions are pinned to full 40-character commit SHAs.
8. `PROJECT_SYNC_TOKEN` is available only to `project-projection-sync.yml`.
9. Work-management reconciliation gets only `issues: write` plus `contents: read`, is serialized, and never receives the Project PAT.
10. Mutating projection workflows are serialized rather than cancelled mid-write.
11. Foundation runtime evidence and VS-01a product-slice evidence have separate workflow owners; neither workflow may silently become the other's lifecycle authority.

## Automated drift check

`scripts/verify_ci_ownership.py` validates this contract and is executed by `project-governance.yml`. Adding or retiring a workflow therefore requires updating this document and verifier in the same reviewed change.

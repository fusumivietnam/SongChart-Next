# GitHub Actions ownership and evidence policy

This contract defines who owns each CI concern and the controls that prevent workflow drift. It is execution governance only: capability lifecycle remains in `governance/CAPABILITY_MAP.json`, roadmap scope remains in the roadmap authorities, and exact-SHA Actions runs are evidence rather than editable state.

## Workflow ownership

| Workflow | Responsibility | Credential boundary |
| --- | --- | --- |
| `project-governance.yml` | governance regression suite, read-only status snapshot, CI ownership verifier | contents read |
| `project-os.yml` | sole owner of `verify_project_os.py` and required `verify` context | contents read |
| `roadmap-health.yml` | live Issue/PR roadmap reconciliation health, unreconciled-merge detection and required `health` context; runs on every main push | contents/issues/PR/actions read |
| `roadmap-reconcile.yml` | serialized post-merge proposal writer; creates/updates a factual reconciliation PR, waits for normal PR-associated protected checks and safe-merges only after fail-closed gates | default `GITHUB_TOKEN` is repository/PR read-only; mutations use only `ROADMAP_RECONCILE_TOKEN`; Project PAT is forbidden |
| `project-projection-sync.yml` | serialized Project #2 field/item projection | read-only repository token + `PROJECT_SYNC_TOKEN` |
| `work-management-sync.yml` | declared labels and explicitly managed milestones | contents read + issues write; no Project PAT |
| `foundation-app.yml` | Docker app/PostgreSQL/tests/audit/SBOM/production-target evidence | contents read |
| `foundation-visual.yml` | deterministic Foundation design render evidence | contents read |
| `vs01a-artist.yml` | VS-01a canonical Artist PostgreSQL integration, canonical URL and narrow/wide browser evidence | contents read |
| `vs01b-musicbrainz.yml` | VS-01b MusicBrainz adapter contracts and request-spacing evidence; never automatic live provider traffic | contents read |
| `vs02-release-recording.yml` | VS-02 Release/Recording/Credits canonical relationships, PostgreSQL integration, canonical redirects and narrow/wide browser evidence | contents read |
| `vs03-discovery-search.yml` | VS-03 PostgreSQL-first discovery, journey continuity and deterministic provider-destination evidence | contents read |
| `design-review-contract.yml` | one-command local Design Authority review contract | contents read |
| `codespaces-contract.yml` | devcontainer/Codespaces developer-shell contract | contents read |

`docker-scaffold.yml` is retired because Foundation application checks own Compose/PostgreSQL runtime evidence.

## Reconciliation credential

`ROADMAP_RECONCILE_TOKEN` is a dedicated repository secret used only by `roadmap-reconcile.yml`. Use a fine-grained credential scoped only to `fusumivietnam/SongChart-Next` with **Contents: read/write** and **Pull requests: read/write**. Do not grant administration, secrets, deployment or Project permissions. Do not reuse `PROJECT_SYNC_TOKEN`.

A dedicated credential is required because GitHub intentionally suppresses workflow recursion caused by the default `GITHUB_TOKEN`; manually dispatched checks can be successful but still remain `expected` for branch protection because they are not normal pull-request checks. The dedicated credential makes generated PR creation and branch updates emit normal `pull_request` `opened/synchronize` events. Branch protection therefore remains authoritative rather than being bypassed or weakened.

If `ROADMAP_RECONCILE_TOKEN` is absent, the writer must fail before repository mutation and report the missing credential. Manual/connected-app reconciliation remains valid but is not considered full autonomous operation.

## Invariants

1. Protected-main contexts `governance`, `verify`, and `health` retain their existing job names.
2. `project-os.yml` is the only workflow executing `scripts/verify_project_os.py`.
3. PR evidence checks out the exact PR head; main evidence checks out the exact merged SHA.
4. Roadmap health runs on every main push so implementation-only merges cannot hide roadmap drift.
5. Every job has a bounded timeout, uses `ubuntu-24.04`, and external Actions are pinned to full commit SHAs.
6. `PROJECT_SYNC_TOKEN` is owned only by `project-projection-sync.yml`.
7. `ROADMAP_RECONCILE_TOKEN` is owned only by `roadmap-reconcile.yml` and never substitutes for the Project token.
8. Work-management reconciliation is serialized and never receives either specialized mutation token unless its own contract explicitly changes later.
9. `roadmap-reconcile.yml` never writes protected `main` directly; it only writes its generated branch and PR.
10. Automatic reconciliation rejects new roadmap/product decisions, provider/technology activation, deployment effects, lifecycle demotion, candidate/watch promotion and unknown capabilities.
11. Reconciliation evidence is limited to successful exact-head source-PR runs created no later than the source merge timestamp.
12. Generated PR checks count only when the check-run is associated with that generated PR; workflow-dispatch-only checks are insufficient.
13. Any human review submission, draft/unmergeable state, failed/missing protected context or changed head stops automatic merge.
14. Generated reconciliation branches are deleted only after successful merge; Project #2 refresh happens afterward and remains derived-only.
15. Live provider production access, public API/search-index activation and production deployment remain outside roadmap automation authority.

## Automated drift check

`scripts/verify_ci_ownership.py` validates this contract and is executed by `project-governance.yml`. Adding or retiring a workflow or changing a specialized credential boundary therefore requires updating this document and verifier in the same reviewed change.

# GitHub Actions ownership and evidence policy

This contract defines who owns each CI concern and the controls that prevent workflow drift. It is execution governance only: capability lifecycle remains in `governance/CAPABILITY_MAP.json`, roadmap scope remains in the roadmap authorities, and exact-SHA Actions runs are evidence rather than editable state.

## Workflow ownership

| Workflow | Responsibility | Credential boundary |
| --- | --- | --- |
| `project-governance.yml` | governance regression suite, read-only status snapshot, CI ownership verifier, GitHub usage-policy verifier, and the merge-blocking preview-skip branch safety assertion for `docs/*` / `governance/*` branches | contents read |
| `project-os.yml` | sole owner of `verify_project_os.py` and required `verify` context | contents read |
| `roadmap-health.yml` | live Issue/PR roadmap reconciliation health, unreconciled-merge detection and required `health` context; runs on every main push | contents/issues/PR/actions read |
| `roadmap-reconcile.yml` | serialized post-merge proposal writer; triggered only by a merged PR close or explicit workflow dispatch; creates/updates a factual reconciliation PR, waits for normal PR-associated protected checks and safe-merges only after fail-closed gates | default `GITHUB_TOKEN` is repository/PR read-only; checkout must not persist it into Git; mutations use only `ROADMAP_RECONCILE_TOKEN`; Project PAT is forbidden |
| `project-projection-sync.yml` | serialized Project #2 field/item projection | read-only repository token + `PROJECT_SYNC_TOKEN` |
| `work-management-sync.yml` | declared labels and explicitly managed milestones | contents read + issues write; no Project PAT |
| `research-cocoindex.yml` | bounded local-only CocoIndex repository-context benchmark; preserves derived timing/retrieval evidence and never makes lifecycle decisions | contents read; no repository secrets |
| `foundation-app.yml` | Docker app/PostgreSQL/tests/audit/SBOM/production-target evidence; sole writer of the shared `foundation-buildkit` cache | contents read |
| `foundation-visual.yml` | deterministic Foundation design render evidence; reads shared BuildKit cache only | contents read |
| `vs01a-artist.yml` | VS-01a canonical Artist PostgreSQL integration, canonical URL and narrow/wide browser evidence; reads shared BuildKit cache only | contents read |
| `vs01b-musicbrainz.yml` | VS-01b MusicBrainz adapter contracts and request-spacing evidence; never automatic live provider traffic; reads shared BuildKit cache only | contents read |
| `vs02-release-recording.yml` | VS-02 Release/Recording/Credits canonical relationships, PostgreSQL integration, canonical redirects and narrow/wide browser evidence; reads shared BuildKit cache only | contents read |
| `vs03-discovery-search.yml` | VS-03 PostgreSQL-first discovery, journey continuity and deterministic provider-destination evidence; reads shared BuildKit cache only | contents read |
| `vs04-launch-proof.yml` | VS-04 launch-support and later release/recovery evidence; starts with public legal/support/correction/SEO surfaces, reads shared BuildKit cache only, and must not claim production deployment | contents read |
| `protected-preview-smoke.yml` | manually dispatched 12-route HTTP smoke of an SSO-protected Vercel Preview using operator-confirmed deployment provenance; not a browser UX or production/G5 verification | contents read + temporary `preview-test` environment secret `PREVIEW_SHARE_URL`; no project credentials or bypass-policy changes |
| `g5-vps-baseline.yml` | single-VPS production-package verification: production app/web image builds, Compose topology, private service exposure and disposable health/smoke evidence; never performs a real VPS deployment | contents read |
| `design-review-contract.yml` | one-command local Design Authority review contract | contents read |
| `codespaces-contract.yml` | devcontainer/Codespaces developer-shell contract | contents read |

`docker-scaffold.yml` is retired because Foundation application checks own Compose/PostgreSQL runtime evidence.

## Low-amplification execution

A bounded semantic work unit should produce one reviewed PR and, where practical, one visible implementation commit that already includes its source, tests, required documentation and governance changes. Intermediate file-by-file mutations may be prepared before a PR exists, but they must be collapsed before the review branch becomes CI evidence. Observation-only commits and evidence-only commits are not a substitute for exact-head checks.

`scripts/classify_ci_change.py` is the repository-owned deterministic classifier for changed-path impact. Its categories remain advisory groundwork for semantic fan-out. One narrow assertion is merge-blocking: because Vercel intentionally skips `docs/*` and `governance/*`, `project-governance.yml` computes the exact PR diff and rejects either branch prefix when the classifier finds application, database, frontend, provider, production-package, preview-runtime, developer-environment or visual impact. This prevents branch naming from hiding a runtime change. All other classifier output remains advisory unless a separately reviewed workflow contract changes it.

Roadmap reconciliation deliberately does **not** subscribe to PR `edited` events or general issue comments. Those events previously produced workflow shells that immediately skipped and amplified Actions usage without adding evidence. Normal reconciliation occurs on merged PR close; explicit replay uses `workflow_dispatch` with a merged PR number.

## Reconciliation credential

`ROADMAP_RECONCILE_TOKEN` is a dedicated repository secret used only by `roadmap-reconcile.yml`. Use a fine-grained credential scoped only to `fusumivietnam/SongChart-Next` with **Contents: read/write** and **Pull requests: read/write**. Do not grant administration, secrets, deployment or Project permissions. Do not reuse `PROJECT_SYNC_TOKEN`.

A dedicated credential is required because GitHub intentionally suppresses workflow recursion caused by the default `GITHUB_TOKEN`; manually dispatched checks can be successful but still remain `expected` for branch protection because they are not normal pull-request checks. The dedicated credential makes generated PR creation and branch updates emit normal `pull_request` `opened/synchronize` events. Branch protection therefore remains authoritative rather than being bypassed or weakened.

The trusted-main checkout must set `persist-credentials: false`. Otherwise `actions/checkout` installs an `http.extraheader` carrying the default `GITHUB_TOKEN`; Git then prefers that header over the dedicated-token remote URL and the generated branch push is incorrectly authenticated as `github-actions[bot]`.

If `ROADMAP_RECONCILE_TOKEN` is absent, the writer must fail before repository mutation and report the missing credential. Manual/connected-app reconciliation remains valid but is not considered full autonomous operation.

## Invariants

1. Protected-main contexts `governance`, `verify`, and `health` retain their existing job names.
2. `project-os.yml` is the only workflow executing `scripts/verify_project_os.py`.
3. PR evidence checks out the exact PR head; main evidence checks out the exact merged SHA.
4. Roadmap health runs on every main push so implementation-only merges cannot hide roadmap drift.
5. Every job has a bounded timeout, uses `ubuntu-24.04`, and external Actions are pinned to full commit SHAs. Repository checkout actions must use approved Node.js 24-capable pins (checkout v6.0.3 or the existing Node.js 24-capable v5 pin in the G5 workflow); `verify_ci_ownership.py` rejects legacy checkout v4.2.2.
6. `PROJECT_SYNC_TOKEN` is owned only by `project-projection-sync.yml`.
7. `ROADMAP_RECONCILE_TOKEN` is owned only by `roadmap-reconcile.yml`; trusted checkout persists no default Git credential; this token never substitutes for the Project token.
8. Work-management reconciliation is serialized and never receives either specialized mutation token unless its own contract explicitly changes later.
9. `roadmap-reconcile.yml` never writes protected `main` directly; it only writes its generated branch and PR.
10. `roadmap-reconcile.yml` is triggered only by merged-PR close or explicit workflow dispatch; PR edits and arbitrary comments must not create reconciliation runs.
11. Automatic reconciliation rejects new roadmap/product decisions, provider/technology activation, deployment effects, lifecycle demotion, candidate/watch promotion and unknown capabilities.
12. Reconciliation evidence is limited to successful exact-head source-PR runs created no later than the source merge timestamp.
13. Generated PR checks count only when the check-run is associated with that generated PR; workflow-dispatch-only checks are insufficient.
14. Any human review submission, draft/unmergeable state, failed/missing protected context or changed head stops automatic merge.
15. Generated reconciliation branches are deleted only after successful merge; Project #2 refresh happens afterward and remains derived-only.
16. Generated reconciliation PR metadata must identify the actual source PR and must not hard-code an unrelated issue/slice/capability provenance string.
17. Live provider production access, public API/search-index activation and production deployment remain outside roadmap automation authority.
18. `vs04-launch-proof.yml` owns launch-proof evidence only; passing it may support G3/G4 claims for tested scope but never supplies G5 production-deployment evidence by itself.
19. `g5-vps-baseline.yml` may verify deployable production packaging in disposable CI, but it never proves a VPS exists, never receives production credentials and never promotes `production-deploy` to deployed.
20. `research-cocoindex.yml` may prove a disposable local research pipeline runs and retain benchmark evidence, but semantic retrieval quality is never a merge-blocking decision and the workflow cannot promote technology/capability lifecycle or consume secrets.
21. Repository workflow artifacts retain at most 14 days, heavy workflows cancel superseded runs, slice workflows do not create private BuildKit cache scopes, and the default Codespaces requirement remains the quota-conscious baseline defined by `docs/operations/GITHUB_USAGE_GUARDRAILS.md`.
22. `scripts/classify_ci_change.py` and its governance tests remain deterministic. General category output is advisory; only the documented preview-skip branch safety assertion is merge-blocking.

## Automated drift check

`scripts/verify_ci_ownership.py` validates workflow ownership, credential boundaries, reconciliation trigger minimization and classifier presence. `scripts/verify_github_usage_policy.py` validates artifact retention, heavy-workflow concurrency, BuildKit cache scope and Codespaces host requirements. Both are executed by `project-governance.yml`; changing these boundaries therefore requires updating the owning document/verifier in the same reviewed change.

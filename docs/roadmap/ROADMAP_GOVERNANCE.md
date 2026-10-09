# Roadmap governance — authority, execution and projections

This policy defines **where roadmap information lives** and how it changes without chat memory, a second roadmap database or manually synchronized status files.

## Authority split

| Question | Authoritative source |
| --- | --- |
| What slices are planned, in what dependency order, and what acceptance gates apply? | `docs/roadmap/VERTICAL_SLICES.md` |
| What capability exists and what lifecycle state is authoritative? | `governance/CAPABILITY_MAP.json` |
| What technology/activation conditions constrain a slice? | `governance/TECHNOLOGY_REGISTRY.json` + `ACTIVATION_TRIGGERS.json` |
| What concrete work is active, blocked or completed? | Live GitHub Issues |
| What implementation/review exists? | Pull Requests + repository source |
| What exact revision passed verification? | GitHub Actions / acceptance evidence at commit SHA |
| What is deployed? | Release/deployment evidence, never Issue/Project-card state |
| What does a dashboard show? | Derived projection only |

There is intentionally **no ROADMAP_STATUS.json, CURRENT_ROADMAP.md or editable generated status file**. `VERTICAL_SLICES.md` is not a task board, and the Capability Map is not an Issue tracker.

## Stable roadmap identity

Every executable roadmap item uses the existing vertical-slice identifier (for example `FOUNDATION`, `VS-01a`) and one or more existing capability IDs. Do not invent a second hierarchy such as Stage 1–28 or chat-specific phases. An Issue title should start with the owning slice when applicable, and its body must record:
- slice ID and capability IDs;
- scope and explicit out-of-scope;
- dependencies / activation conditions;
- owning contracts / ADRs / research references;
- deliverables and acceptance evidence;
- blockers;
- linked PRs.

A slice may have multiple Issues. An Issue may support more than one capability, but one Issue must have a bounded outcome. Closing an Issue means that work item is closed; it does **not** by itself promote a capability or complete a vertical slice.

## Lifecycle promotion

Capability state follows `CAPABILITY_MAP.json` only:
`candidate -> approved -> implemented -> verified -> deployed`.

Promotion requires a reviewed PR that updates the map and cites evidence required by the Delivery Contract / Acceptance Gates. GitHub Issue state, milestone completion, Project column, PR merge, or a green governance workflow does not independently change lifecycle status.

Vertical-slice completion is evaluated from its required capabilities and acceptance evidence. Because slice status is derived, do not write a second `status` field into VERTICAL_SLICES. If evidence is incomplete or live GitHub cannot be queried, report the slice as **unknown/incomplete**, not completed from memory.

`verification_evidence` records the latest accepted exact-SHA evidence for a verified capability. `verification_history`, when present, retains earlier accepted evidence entries for auditability. History is evidence lineage only; it is not a second lifecycle field and cannot promote a capability by itself.

## GitHub Projects and milestones

GitHub Projects is the approved human-facing **derived visual layer** over Issues/PRs. The concrete field/view contract is [GitHub Project visual roadmap](PROJECT_VIEWS.md), while the stable Labels/Milestones/agent activation taxonomy is owned by `governance/GITHUB_WORK_MANAGEMENT.json` and documented in [GitHub work management](../operations/GITHUB_WORK_MANAGEMENT.md). These surfaces remain projections/classification, never lifecycle or evidence authority.

Recommended fields:
- Slice: FOUNDATION / VS-01a / VS-01b / VS-02 / VS-03 / VS-04 / Later
- Capability: existing capability ID
- Work state: Proposed / Ready / In progress / Blocked / In review / Done
- Gate: G0–G5 where applicable
- Evidence PR: link/reference

Project fields are convenience metadata. They must be reconstructible from the linked Issue/PR and cannot override repository authority. Automations may update Project fields from Issue/PR events; never update CAPABILITY_MAP from a Project card automatically.

GitHub Milestones may group Issues by a release objective, but a milestone percentage is only work-item aggregation. It is not capability verification or release readiness.

## Roadmap Controller

`scripts/roadmap_health.py` is the read-only reconciliation engine. It derives planned slices from this repository, capability lifecycle from the Capability Map and, when a GitHub token is available, current execution from live Issues/PRs. It never mutates Issues, Projects, registries or lifecycle state.

The `Roadmap health` GitHub Actions workflow runs on relevant PR/Issue events, **every push to main**, manual dispatch and a daily schedule. It:
- runs controller and reconciliation regression tests;
- queries GitHub with read-only contents/issues/pull-requests/actions permissions;
- reports active execution and conservative blockers;
- flags missing capability links, lifecycle/evidence inconsistencies and unknown/truncated live state;
- runs `scripts/roadmap_reconcile_health.py` to flag merged PRs whose reviewed reconciliation contract has not yet appeared in repository authorities;
- preserves JSON/text reports as short-lived artifacts for review.

Warnings and blockers are information, not automatic roadmap edits. Controller **errors** fail the health job because they represent contradictory authority/evidence claims. A GitHub/API outage produces `unknown`, never a guessed status.

The separate `scripts/project_sync.py` projection writer may mirror controller-derived execution into GitHub Project #2. It is intentionally not part of the controller and cannot mutate repository authorities, Issues or PRs. See [GitHub Project #2 projection sync](../operations/GITHUB_PROJECT_SYNC.md).

## Post-merge reconciliation proposals

`scripts/roadmap_reconcile.py` is a separate proposal writer. It does **not** replace the read-only controller and never writes protected `main` directly.

A PR may carry one hidden `songchart-reconcile` JSON object from `.github/PULL_REQUEST_TEMPLATE.md`. That metadata is reviewed as part of the source PR and may describe only factual post-merge updates such as:
- retaining exact-head verification evidence for an already approved/implemented capability;
- promoting an already approved capability to implemented/verified when the reviewed scope and exact evidence support it;
- appending factual implementation notes to the owning vertical-slice section;
- refreshing the concise README status pointer.

Automatic reconciliation fails closed when metadata declares or implies:
- a new product/roadmap scope decision;
- an unresolved owner/ADR decision;
- provider or technology activation;
- any deployment effect;
- promotion from `candidate` or `watch`;
- lifecycle demotion or a change to `deployed`;
- unknown capability identifiers.

`roadmap-reconcile.yml` runs after a merged PR or by explicit replay of a merged PR number. For safe metadata it:
1. checks out trusted `main`;
2. collects successful exact-head pull-request workflow evidence for the merged source SHA;
3. applies the deterministic writer locally;
4. creates/updates `automation/roadmap-reconcile-pr-<number>` and a bounded reconciliation PR;
5. explicitly dispatches protected `governance`, `verify`, and `health` workflows on that exact reconciliation SHA because PRs created with `GITHUB_TOKEN` must not rely on implicit workflow recursion;
6. stops automatic merge if a human review has intervened, the PR is draft/unmergeable, or any protected check fails/times out;
7. merges only the generated factual reconciliation PR through normal branch protection;
8. explicitly refreshes Project #2 as a derived projection and deletes the generated branch after successful merge.

Generated reconciliation PRs mark themselves `skip` to prevent recursive reconciliation. Replay exists for deterministic repair/backfill of already merged PRs after metadata is authored; it cannot bypass the same safety gates.

## Derived execution queue

Roadmap Issues may declare `**Blocked by:** #issue` references. The controller combines these explicit blockers with PR ownership links (`Implements/Resolves/Closes/Fixes #issue` or the PR template owning-Issue field) to derive execution state:
- **Ready** — open roadmap Issue, no unresolved blocker, no linked open PR.
- **In progress** — linked open draft PR and no unresolved blocker.
- **In review** — linked open non-draft PR and no unresolved blocker.
- **Blocked** — one or more referenced blocker Issues remain open, are unknown, or the Issue self-blocks.

These are execution projections only. They do not rank political/product choices, do not choose priorities, and never promote capability lifecycle. Multiple Ready items may exist; prioritization remains a project decision.

## Roadmap change workflow

1. Research or product request is registered/evaluated without changing roadmap status.
2. If product/scope changes materially, update Product Charter/ADR first.
3. Update `VERTICAL_SLICES.md` only for planned scope/dependency/gate changes.
4. Update Capability Map only when capability definition/dependency/lifecycle changes, with required evidence.
5. Create/reuse bounded GitHub Issues for execution; check duplicates/open PRs first.
6. Implement via PR and exact-SHA CI evidence.
7. If the merged PR contains safe reconciliation metadata, let `roadmap-reconcile.yml` prepare the factual follow-up PR; otherwise perform the reviewed authority update manually.
8. Promote capability lifecycle only through a reviewed repository change whose evidence satisfies the gate.
9. Generated/project dashboards refresh from authorities; no manual back-propagation from chat.

## Conflict resolution

When sources disagree:
1. Installed source/manifests/lockfiles prove what code/dependency exists, not whether it was approved.
2. Capability Map controls lifecycle state.
3. VERTICAL_SLICES controls planned slice scope.
4. Live Issue/PR data controls execution activity.
5. Exact-SHA CI/release/deployment records control measured evidence.
6. Project views, generated reports and chat summaries lose every conflict.

If two authored authorities appear to conflict semantically, stop promotion and open/continue a governance Issue/PR to reconcile them.

## Session bootstrap for roadmap work

A new human/AI session must:
1. Read main HEAD, README, AGENTS and this policy.
2. Read VERTICAL_SLICES and relevant capability/technology/activation registries.
3. Query live Issues/PRs and CI; do not infer active work from a cached snapshot.
4. Determine active slice from linked live execution, not from chat memory.
5. Resume existing owning Issue/PR where present.
6. Report planned scope, lifecycle and execution separately.

A GitHub outage leaves live execution status `unknown`; it never licenses a guess from previous conversation memory.

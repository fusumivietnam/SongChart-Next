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

## GitHub Projects and milestones

GitHub Projects may be configured as a portfolio/Kanban **view** over Issues/PRs. Recommended fields, if a Project is created:
- Slice: FOUNDATION / VS-01a / VS-01b / VS-02 / VS-03 / VS-04 / Later
- Capability: existing capability ID
- Work state: Proposed / Ready / In progress / Blocked / In review / Done
- Gate: G0–G5 where applicable
- Evidence PR: link/reference

Project fields are convenience metadata. They must be reconstructible from the linked Issue/PR and cannot override repository authority. Automations may update Project fields from Issue/PR events; never update CAPABILITY_MAP from a Project card automatically.

GitHub Milestones may group Issues by a release objective, but a milestone percentage is only work-item aggregation. It is not capability verification or release readiness.

## Roadmap Controller

`scripts/roadmap_health.py` is the read-only reconciliation engine. It derives planned slices from this repository, capability lifecycle from the Capability Map and, when a GitHub token is available, current execution from live Issues/PRs. It never mutates Issues, Projects, registries or lifecycle state.

The `Roadmap health` GitHub Actions workflow runs on relevant PR/main changes, manual dispatch and a daily schedule. It:
- runs controller regression tests;
- queries GitHub with read-only contents/issues/pull-requests/actions permissions;
- reports active execution and conservative blockers;
- flags missing capability links, lifecycle/evidence inconsistencies and unknown/truncated live state;
- preserves JSON/text reports as short-lived artifacts for review.

Warnings and blockers are information, not automatic roadmap edits. Controller **errors** fail the health job because they represent contradictory authority/evidence claims. A GitHub/API outage produces `unknown`, never a guessed status.

## Roadmap change workflow

1. Research or product request is registered/evaluated without changing roadmap status.
2. If product/scope changes materially, update Product Charter/ADR first.
3. Update `VERTICAL_SLICES.md` only for planned scope/dependency/gate changes.
4. Update Capability Map only when capability definition/dependency/lifecycle changes, with required evidence.
5. Create/reuse bounded GitHub Issues for execution; check duplicates/open PRs first.
6. Implement via PR and exact-SHA CI evidence.
7. Promote capability lifecycle through reviewed repository change when evidence satisfies the gate.
8. Generated/project dashboards refresh from authorities; no manual back-propagation from chat.

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

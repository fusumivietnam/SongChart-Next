# GitHub work management and agent activation

This runbook implements the repository contract in `governance/GITHUB_WORK_MANAGEMENT.json`. It classifies execution work without creating a second roadmap or lifecycle authority.

## Authority boundary

- planned slice scope/dependencies: `docs/roadmap/VERTICAL_SLICES.md`;
- capability lifecycle: `governance/CAPABILITY_MAP.json`;
- live execution: GitHub Issues/PRs;
- exact verification/deployment evidence: Actions/releases/deployments;
- Project #2, labels and milestones: derived/classification surfaces only;
- custom agent files: repository-owned instructions only, not evidence that an AI service is enabled or used.

## Labels

The required label vocabulary is defined only in `GITHUB_WORK_MANAGEMENT.json`.

Use at most one `type:*` and one `priority:*` label per Issue/PR. Area/risk/state labels may be multi-valued when they describe real cross-cutting work.

Priority is a human decision. Labels never promote capability lifecycle and do not replace the structured Project fields.

Repository automation reconciles the declared catalog with `scripts/work_management_sync.py` and `Work management sync`. It may create missing labels and repair declared description/color drift, but it never deletes unmanaged labels and must not infer or assign priority automatically. The workflow uses only the ephemeral repository `GITHUB_TOKEN` with `contents: read` and `issues: write`; it never receives `PROJECT_SYNC_TOKEN`.

## Milestones

Create a milestone only for a delivery checkpoint/release objective with a bounded completion meaning. Examples include `FOUNDATION`, `VS-01 Artist fixture-first`, a public alpha, or a quarter-specific delivery checkpoint.

Automation manages milestones only when they are explicitly listed under `milestones.managed` in `governance/GITHUB_WORK_MANAGEMENT.json`. The default list is empty. Capability IDs, slices, labels or Project fields must never be converted into milestones implicitly.

Do not use milestones for capability names, areas, priorities, or `verified/deployed` claims. Milestone completion is work aggregation only.

## Project #2 and views

Project `fusumivietnam/2` remains a reconstructible projection. `scripts/project_sync.py` owns field reconciliation and reads the required view names from the work-management contract.

Required views:
- Executive Roadmap
- Delivery Board
- Capability Matrix
- Decision Queue
- Verification / Release Gates

Optional operational views:
- Blocked / Risk
- Recently Completed

GitHub Projects API support does not currently give this repository workflow a safe repository-owned mechanism to create/configure view layouts and filters. Missing views are therefore reported as drift and configured manually in the Project UI using `docs/roadmap/PROJECT_VIEWS.md`.

## AI agent profiles

Repository profiles live under `.github/agents/*.agent.md`:
- roadmap-governor
- implementation
- architecture-reviewer
- quality-gate

They are deliberately marked `disable-model-invocation: true`; a human must select them when an eligible GitHub Copilot environment is available.

The profiles are **dormant configuration** until the GitHub account has an eligible Copilot plan and the agent feature is enabled. Their presence on `main` must never be reported as an implemented/verified AI execution capability.

ChatGPT and GitHub connector workflows can continue to operate against Issues/PRs/repository content without these Copilot agents.

## Agent handoff protocol

Use this protocol in ChatGPT, a local coding agent or an eligible manually selected Copilot profile. This does not activate Copilot or delegate human decisions. The implementation role coordinates one bounded change; other roles contribute only when their review adds evidence or resolves a risk.

1. **Bootstrap once per session:** follow PROJECT_CONTROL and AGENTS in full. Record main HEAD, active Issue/PR, branch/head and relevant CI results. During the session refresh live state before mutations, when HEAD changes or evidence becomes stale; reuse the source already read at the same SHA. Do not use a prior chat as repository authority.
2. **Route the work:** implementation owns the patch; architecture reviews material boundary/dependency decisions; quality checks the changed contracts and exact-head evidence; roadmap governs authority/decision consistency. Do not invoke four agents for every small defect. Escalate real security, rights, persistent data or contract decisions to the human owner.
3. **One handoff:** record Issue/capability/slice, base and head SHA, scoped diff, outstanding decisions, tests run/results, missing evidence and next action in the owning PR (or Issue before a PR exists). Reference existing evidence rather than duplicate it in a new status document or repetitive comments. Do not claim a tool ran without its result.
4. **Verify economically:** where available, use the existing Windows/WSL2 or Linux Docker Compose development app, with locked dependencies and appropriate targeted checks. For the application test suite follow [Docker development](DOCKER_DEVELOPMENT.md): explicitly isolate test storage from populated development PostgreSQL; use existing disposable CI owners for fixture-backed PostgreSQL/browser proof. Use the read-only public smoke script only after the local schema prerequisite is satisfied. No destructive reset, fixture writes to a persistent DB, or host PHP/Node installation to work around container failures.
5. **Submit once:** follow the Delivery Contract and CI Workflow Ownership. Group failures by root cause, make a consolidated repair, and reuse successful evidence only at the same SHA. Do not trigger reruns for unchanged deterministic failures or add workflows that duplicate owners. A changed head requires fresh applicable evidence.
6. **Human gate:** continue independent authorized work without waiting for status acknowledgments, but stop at unapproved merge/deploy, provider rights, activation, secret or persistent-data decisions. State the exact decision or local command needed; never simulate approval or claim production readiness from local or CI tests.

When no execution tool is available, report the specific unavailable capability and provide the minimal safe operator command; do not generate fake evidence or repeatedly request already supplied information.

## Automation and external setup

Required labels are reconciled automatically after contract changes on `main`; no PAT is used for label or milestone writes. Explicitly managed milestones use the same least-privilege workflow.

Project #2 continues to use the separate `PROJECT_SYNC_TOKEN` because it is user-owned. Project fields/items are reconciled by `Project projection sync`; required view presence is audited there. Any view layout/filter changes that are not represented by repository automation remain presentation configuration only.

These UI/service objects are projections/classification. If they are deleted, repository roadmap/lifecycle authority remains intact.

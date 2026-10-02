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

Repository automation may audit label drift, but it must not infer or assign priority automatically.

## Milestones

Create a milestone only for a delivery checkpoint/release objective with a bounded completion meaning. Examples include `FOUNDATION`, `VS-01 Artist fixture-first`, a public alpha, or a quarter-specific delivery checkpoint.

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

## Manual GitHub setup that remains external

The connected GitHub integration can create/update Issues/PRs and repository files, but it does not expose repository-administration writes for label/milestone catalog creation or Project view configuration in this session.

After this contract merges:
1. create any missing labels exactly as declared in `GITHUB_WORK_MANAGEMENT.json`;
2. create milestones only when a real delivery checkpoint is approved;
3. create any missing required Project views using `PROJECT_VIEWS.md`;
4. run **Project projection sync** and confirm it reports no required-view drift.

These UI/service objects are projections/classification. If they are deleted, repository roadmap/lifecycle authority remains intact.

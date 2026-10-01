# ADR-0008 — GitHub Project v2 as an automated derived projection

- Status: accepted for project-control implementation
- Date: 2026-10-02
- Owning issue: #39
- Capability: project-os

## Context

SongChart already separates roadmap authority from presentation: vertical-slice scope lives in `VERTICAL_SLICES.md`, capability lifecycle in `CAPABILITY_MAP.json`, execution in live Issues/PRs, and exact evidence in CI/release/deployment records. Project #2 is intended as the human-facing visual layer, but the existing Roadmap Controller is deliberately read-only and does not mutate GitHub Projects.

Manual Project card/field maintenance drifts and defeats the reconstructible-projection goal.

## Decision

Add a separate projection writer, `scripts/project_sync.py`, and a repository-owned workflow that mirrors deterministic Issue/PR execution state into the user-owned GitHub Project #2.

The writer may:
- discover/create the required Project fields;
- append missing single-select options derived from roadmap/capability authorities while preserving existing option IDs;
- add roadmap Issues to Project #2;
- update `Slice`, primary `Capability`, `Execution`, explicit `Gate`, explicit `Decision` and `Evidence`;
- report missing required views.

The writer must not:
- mutate `CAPABILITY_MAP.json`, `VERTICAL_SLICES.md`, Issues or PRs;
- infer verified/deployed lifecycle from a Project field;
- choose priority, owner decisions or product scope;
- delete unrelated Project items;
- expose or persist the Project token.

## Execution derivation

Execution continues to come from the read-only Roadmap Controller:
- open Issue with no blocker/linked PR -> Ready;
- linked draft PR -> In progress;
- linked non-draft PR -> In review;
- unresolved/unknown blocker -> Blocked;
- closed roadmap Issue -> Done.

`Proposed` remains available as a Project vocabulary value but is not inferred by the controller.

## Gate and decision metadata

Gate and decision are not safely inferable from Issue/PR state. Roadmap Issues may explicitly declare:
- `**Project Gate:** G0..G5 / none`;
- `**Project Decision:** None / Owner decision required / Approved / Rejected`.

The projection copies only explicit values. Absence clears stale Project values rather than inventing a decision.

## Credential boundary

Project #2 is owned by the personal account `fusumivietnam`. The workflow uses the repository `GITHUB_TOKEN` only for read-only repository/Issue/PR data and a separate `PROJECT_SYNC_TOKEN` only for Projects GraphQL access.

For a user-owned Project, use a classic PAT with the `project` scope. Do not grant `repo` solely for this workflow while the SongChart repository remains public. Store the PAT only as an Actions secret.

The workflow uses `pull_request_target` for Project refreshes but always checks out trusted `main`; it never executes an untrusted PR head with the Project secret.

## Failure and recovery

Missing `PROJECT_SYNC_TOKEN` is a configuration-required state, not a repository failure: tests still run and the mutation step is skipped with an Action summary.

If synchronization fails:
1. inspect the workflow summary/report;
2. validate token scope/expiry;
3. run `workflow_dispatch` after repair;
4. remove/rotate the secret to disable writes.

Project loss or stale fields do not destroy roadmap truth because the Project remains reconstructible from repository authority and live Issues/PRs.

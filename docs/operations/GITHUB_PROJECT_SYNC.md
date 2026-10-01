# GitHub Project #2 projection sync

Project #2 is a derived visual projection of SongChart roadmap execution. Repository authorities and live Issues/PRs remain authoritative.

## What is automated

`scripts/project_sync.py` reconciles user Project `fusumivietnam/2` from:
- `docs/roadmap/VERTICAL_SLICES.md`;
- `governance/CAPABILITY_MAP.json`;
- live GitHub Issues and PRs;
- explicit Project metadata in roadmap Issues.

The sync automatically creates missing required fields and appends missing options without replacing existing option IDs:
- Slice
- Capability
- Execution
- Gate
- Decision
- Evidence

It adds SongChart roadmap Issues and updates their projected fields. It does not delete unrelated cards.

Required view names are audited but not created or reconfigured automatically because view layout/grouping is presentation-only and should remain intentionally reviewable in the GitHub UI:
- Executive Roadmap
- Delivery Board
- Capability Matrix
- Decision Queue
- Verification / Release Gates

## Manual permission setup — required once

Project #2 is owned by the personal account `fusumivietnam`, so the repository's default `GITHUB_TOKEN` is not the Project writer.

1. In GitHub, open **Settings** for the `fusumivietnam` account.
2. Open **Developer settings** -> **Personal access tokens** -> **Tokens (classic)**.
3. Choose **Generate new token (classic)**.
4. Give it a narrow name such as `SongChart Project #2 sync`.
5. Set an expiration date appropriate for project operations; shorter-lived tokens are preferred if renewal is operationally acceptable.
6. Select **only** the `project` scope for this public-repository workflow. `project` includes read/write Project access. Do not add `repo` solely for SongChart Project sync while the repository is public.
7. Generate the token and copy it once.
8. Open `fusumivietnam/SongChart-Next` -> **Settings** -> **Secrets and variables** -> **Actions**.
9. Under **Repository secrets**, choose **New repository secret**.
10. Name it exactly `PROJECT_SYNC_TOKEN`.
11. Paste the PAT as the secret value and save it.
12. Open **Actions** -> **Project projection sync** -> **Run workflow** on `main`.

Never paste the PAT into an Issue, PR, workflow YAML, repository variable, Codespace file or chat.

## First authenticated verification

After the secret exists, manually dispatch **Project projection sync** once. A successful run should:
- pass projection + Roadmap Controller regression tests;
- find `fusumivietnam` Project #2;
- create/repair required fields/options as needed;
- add/reconcile roadmap Issue cards;
- publish `project-sync.json` as a short-lived Action artifact;
- report any missing required views.

Then inspect Project #2 and confirm at least one known open roadmap Issue matches its derived execution state and a recently closed roadmap Issue is `Done`.

## Required views — manual UI setup if reported missing

Create these views in Project #2 if the sync report lists them as missing:

1. **Executive Roadmap** — Roadmap layout; group by `Slice`. Use Start/Target only as planning hints.
2. **Delivery Board** — Board layout; group by `Execution`.
3. **Capability Matrix** — Table layout; group by `Capability`; show Slice, Gate and Evidence.
4. **Decision Queue** — Table layout; filter `Decision = Owner decision required`; optionally include Blocked execution.
5. **Verification / Release Gates** — Table or Board; group by `Gate`; show Evidence.

View configuration is presentation only. Moving cards or changing Project fields must never promote capability lifecycle.

## Roadmap Issue metadata

New roadmap Issues should include:

```text
**Project Gate:** none / G0 / G1 / G2 / G3 / G4 / G5
**Project Decision:** None / Owner decision required / Approved / Rejected
```

Execution is derived automatically and must not be hand-maintained in the Issue body.

## Rotation / recovery

When the PAT expires or is rotated:
1. generate a replacement classic PAT with `project`;
2. replace the repository secret value for `PROJECT_SYNC_TOKEN`;
3. manually dispatch **Project projection sync**;
4. revoke the old PAT.

If the secret is removed, the workflow remains green but reports that Project mutation was skipped. Roadmap health and project governance continue independently.

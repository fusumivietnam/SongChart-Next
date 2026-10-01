# GitHub Codespaces development

Status: repository-owned Codespaces configuration is optional developer infrastructure. Docker Compose remains the approved local application/database runtime under ADR-0001 and ADR-0003.

## Why a repository-owned configuration

The repository uses `.devcontainer/devcontainer.json` so Codespaces no longer has to infer a generic universal environment. The Codespaces shell intentionally contains only the tooling needed to operate the repository and its Docker Compose runtime. PHP, Node, pnpm, Composer and PostgreSQL remain owned by the project Docker images rather than the host shell.

## Automatic lifecycle

On creation/prebuild, `.devcontainer/prebuild.sh` runs project-governance and shell-contract checks.

After a user Codespace is created, `.devcontainer/post-create.sh` waits briefly for Docker, then runs `scripts/design_review.sh`. Failure is logged under ignored `.codespaces/logs/` but does not intentionally make the Codespace unusable.

After a stopped Codespace is started again, `.devcontainer/post-start.sh` keeps an already healthy app untouched. If the app is not healthy, it retries the repository-owned review/bootstrap path.

Ports:
- 8000 — SongChart app, private by default
- 5173 — optional Vite development server, private/silent by default

Minimum requested machine specification is 4 CPU, 8 GB RAM and 32 GB storage.

## Troubleshooting a Codespace that stays "Stopping"

A rebuild normally recreates the dev container; it is not expected to remain in a stopping state for many minutes. Check the Codespaces creation log and GitHub Status first. From another authenticated GitHub CLI environment, creation logs can be read with:

```bash
gh codespace logs -c <codespace-name>
```

Inside an accessible SongChart Codespace run:

```bash
bash scripts/codespaces_doctor.sh
```

The doctor is read-only/non-destructive: it reports Git, disk, Docker, Compose, app health and GitHub CLI state without printing project secrets.

If container creation repeatedly fails or the Codespace cannot leave the stopping/failed state, prefer deleting that broken Codespace and creating a fresh one from current `main`. Source changes must already be committed/pushed before deletion. Do not repair a failed Codespace by deleting SongChart database volumes unless data loss is explicitly accepted.

## Prebuilds

After the dev-container configuration is merged, a repository administrator can enable a Codespaces prebuild for `main` under repository Settings → Codespaces. For this project, prefer:
- branch: `main`;
- configuration: `.devcontainer/devcontainer.json`;
- trigger: on configuration change initially, or every push if faster fresh-environment startup is worth the additional Actions/storage consumption;
- region(s): only the regions actually used by project developers.

Prebuild configuration is GitHub repository state and is not duplicated as a second roadmap or product authority.

## Recovery boundary

The Codespaces shell may recreate disposable Compose containers through existing project scripts. It must not:
- run `docker system prune --volumes`;
- delete PostgreSQL named volumes automatically;
- run production deployment;
- rotate production secrets;
- mutate canonical product data.

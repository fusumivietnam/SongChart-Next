# GitHub Codespaces development

Status: repository-owned Codespaces configuration is optional developer infrastructure. Docker Compose remains the approved local application/database runtime under ADR-0001 and ADR-0003.

## Why a repository-owned configuration

The repository uses `.devcontainer/devcontainer.json` so Codespaces no longer has to infer a generic universal environment. The Codespaces shell intentionally contains only the tooling needed to operate the repository and its Docker Compose runtime. PHP, Node, pnpm, Composer and PostgreSQL remain owned by the project Docker images rather than the host shell.

## Automatic lifecycle

On creation/prebuild, `.devcontainer/prebuild.sh` is a blocking devcontainer-owned check only: it verifies the declared shell/features and shell syntax. Project OS/governance verification remains in GitHub CI and is deliberately not allowed to make Codespaces creation depend on an undeclared host interpreter such as Python.

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

If the creation log only shows a successful `--expect-existing-container` / `docker start` sequence while the UI says recovery mode, that log is the recovery container starting, not proof that the configured devcontainer built successfully. After a repository fix, run **Codespaces: Rebuild Container** (prefer **Full Rebuild** when a stale prebuild/container snapshot is suspected). If container creation repeatedly fails or the Codespace cannot leave the stopping/failed state, prefer deleting that broken Codespace and creating a fresh one from current `main`. Source changes must already be committed/pushed before deletion. Do not repair a failed Codespace by deleting SongChart database volumes unless data loss is explicitly accepted.

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


## Understand Anything developer analysis

ADR-0007 allows a narrowly scoped Node 22/pnpm toolchain in the Codespaces shell for Understand Anything only. This does not change Docker Compose authority for the SongChart application.

The post-create lifecycle runs:

```bash
bash .devcontainer/install-understand-anything.sh
```

The installer checks out the exact upstream SHA recorded in the script, builds the upstream core package and links its skills into `~/.agents/skills`. Installation failure is non-fatal to the Codespace.

After installation, a Codex-compatible agent can invoke:

```text
$understand --language vi
```

or use natural language to request the `understand` skill. The first full analysis may ask for ignore/language confirmation and can use substantial model tokens.

Output under `.ua/` is derived analysis. Never use generated summaries, inferred architecture or domain labels to update SongChart authority automatically. Compare conclusions against README/AGENTS, Product Charter, Architecture, governance registries, source, tests and live GitHub state.

Ephemeral `.ua/intermediate/`, `.ua/tmp/`, `.ua/.trash-*` and `.ua/diff-overlay.json` are ignored. Do not enable upstream `--auto-update` until a separate review decides whether commit-hook mutation is acceptable.

The dashboard commonly uses port 5173 or the next available port; port 5174 is predeclared as a private Codespaces forward for the fallback case. Keep graph dashboards private unless separately approved.

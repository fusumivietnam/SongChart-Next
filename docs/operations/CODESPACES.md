# GitHub Codespaces development

Status: repository-owned Codespaces configuration is optional developer infrastructure. Docker Compose remains the approved local application/database runtime under ADR-0001 and ADR-0003.

## Why a repository-owned configuration

The repository uses `.devcontainer/devcontainer.json` so Codespaces no longer has to infer a generic universal environment. The Codespaces shell intentionally contains only the tooling needed to operate the repository and its Docker Compose runtime. PHP, Node, pnpm, Composer and PostgreSQL remain owned by the project Docker images rather than the host shell.

Because the Codespaces shell uses Docker-outside-of-Docker, bind mounts are resolved by the external Docker daemon against the host workspace path, not the `/workspaces/...` path visible inside the devcontainer. `.devcontainer/devcontainer.json` therefore exports Dev Containers' `${localWorkspaceFolder}` as `LOCAL_WORKSPACE_FOLDER`, and `compose.yaml` uses `${LOCAL_WORKSPACE_FOLDER:-.}` for the application source bind. The fallback preserves normal local Docker usage outside Codespaces.

## Automatic lifecycle

On creation/prebuild, `.devcontainer/prebuild.sh` is a blocking devcontainer-owned check only: it verifies the declared shell/features and shell syntax. Project OS/governance verification remains in GitHub CI and is deliberately not allowed to make Codespaces creation depend on an undeclared host interpreter such as Python.

After a user Codespace is created, `.devcontainer/post-create.sh` waits briefly for Docker, then runs `scripts/design_review.sh`. Failure is logged under ignored `.codespaces/logs/` but does not intentionally make the Codespace unusable.

After a stopped Codespace is started again, `.devcontainer/post-start.sh` keeps an already healthy app untouched. If the app is not healthy, it retries the repository-owned review/bootstrap path.

Ports:
- 8000 — SongChart app, private by default
- 5173 — optional Vite development server, private/silent by default

Default requested machine specification is 2 CPU, 8 GB RAM and 32 GB storage. A larger machine is an explicit operator choice for a bounded task, not the repository default.

## Quota discipline

Codespaces is a convenience shell, not a persistent server or CI runner. To keep monthly core-hours and storage bounded:

- prefer the repository default 2-core machine;
- stop the Codespace when active development ends instead of leaving Docker services idle;
- keep the account/repository idle timeout conservative;
- delete abandoned or broken Codespaces after committed work is pushed;
- prefer local Docker or GitHub Actions when Codespaces monthly use approaches the operational thresholds in `docs/operations/GITHUB_USAGE_GUARDRAILS.md`;
- do not keep a larger machine running after the bounded task requiring it is complete.

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

If the Compose `app` exits with `Composer could not find a composer.json file in /var/www/html`, inspect its source mount before deleting volumes. In Codespaces, the mount source must resolve to the host workspace path supplied through `LOCAL_WORKSPACE_FOLDER`; recreating the app container alone cannot repair an incorrect bind source.

If the creation log only shows a successful `--expect-existing-container` / `docker start` sequence while the UI says recovery mode, that log is the recovery container starting, not proof that the configured devcontainer built successfully. After a repository fix, run **Codespaces: Rebuild Container** (prefer **Full Rebuild** when a stale prebuild/container snapshot is suspected). If container creation repeatedly fails or the Codespace cannot leave the stopping/failed state, prefer deleting that broken Codespace and creating a fresh one from current `main`. Source changes must already be committed/pushed before deletion. Do not repair a failed Codespace by deleting SongChart database volumes unless data loss is explicitly accepted.

## Prebuilds

After the dev-container configuration is merged, a repository administrator can enable a Codespaces prebuild for `main` under repository Settings → Codespaces. For this project, prefer:
- branch: `main`;
- configuration: `.devcontainer/devcontainer.json`;
- trigger: on configuration change initially; do not use every-push prebuilds without measured startup-time evidence that justifies their additional compute/storage consumption;
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

## Archify source-backed diagrams (conditionally approved, opt-in)

ADR-0017 was approved by the project owner on 2026-10-27 for internal, source-checked developer architecture visualization subject to its five restrictions. Adoption into `main` still requires PR #211 review and merge. Archify is **not** part of Codespaces post-create or the SongChart application toolchain; no automatic installation, required CI gate or production service is approved.

Codespaces quota exhaustion does not block bounded developer-analysis verification. Issue #212 scopes a separate, read-only GitHub Actions browser contract that runs on relevant PR changes or manual dispatch, using a disposable Ubuntu runner and no Codespaces compute. Consult the exact-head workflow evidence linked from PR #211 / issue #212; a successful historical browser run is not an approval, an assurance about later heads or a new protected required context.

To try it in an optional Node 22+ developer shell (Codespaces is not required), after inspecting the pinned installer:

```bash
bash .devcontainer/install-archify.sh
```

The installer checks out one pinned upstream Git commit under `~/.archify-tool/repo` and links the `archify` skill at `~/.agents/skills/archify`, refusing to replace unrelated destinations. The agent may then use `$archify` or a natural-language request such as: "Read current source and use Archify to diagram the correction intake boundary with file/line evidence."

For a *historical* example, `docs/architecture/examples/archify-public-read.architecture.json` is pinned to `600162d4b0bc531485d8df685c42745cb13baca6` and only covers public Search, Artist read and correction intake. Once that commit is available in the local Git object database, run:

```bash
bash scripts/archify_example.sh
```

The command invokes `finalize` for validation, verified delivery and browser checks, writing only ignored `.archify/examples/` output. It must not be described as fully verified if the browser gate is skipped (for example, because Chromium is absent). In a shallow clone, fetch the pinned revision before trying the sample. For **current** architecture, create a fresh candidate using the current HEAD and re-check every cited file/line; never repoint a historical JSON without checking its claims.

Archify's diagram HTML and JSON are derived representations, not another Product Charter, Architecture contract, roadmap, execution tracker or release artifact. Do not upload diagrams with private source excerpts or sensitive data to a public hosting service.
Archify's MIT software license does not license every packaged brand mark. Its `THIRD_PARTY_NOTICES.md` records individual trademark, attribution, share-alike and noncommercial restrictions; do not publish/export diagrams using those marks without separate rights review.

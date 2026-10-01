# ADR-0006 — GitHub Codespaces as an optional automated development shell

- Status: accepted for repository development environment
- Date: 2026-10-01
- Scope: developer environment only; no production runtime or product capability

## Context

SongChart Next already uses Docker Compose as the approved local application/database runtime. Repeated Codespaces rebuilds exposed failures in the disposable host environment, including stale Docker container layers and a host-level NVM symlink conflict. Those failures were outside SongChart application code and made ad-hoc recovery expensive.

The repository previously had no `.devcontainer/devcontainer.json`, so Codespaces selected its generic environment. That generic environment is broader than SongChart needs and can include unrelated host toolchains.

## Decision

Use a repository-owned GitHub Codespaces dev container as an optional development shell around the existing Docker Compose runtime.

The Codespaces shell:
- uses a minimal Ubuntu dev-container base rather than the generic universal image;
- adds only Docker-outside-of-Docker and GitHub CLI dev-container features;
- does not install or own SongChart application PHP, Node, pnpm, Composer, PostgreSQL or application dependencies on the Codespaces shell; ADR-0007 permits a separately pinned host Node/pnpm toolchain only for developer-analysis tooling, and that toolchain must not build or run SongChart;
- continues to run the application and PostgreSQL through the repository's existing Dockerfile and `compose.yaml`;
- forwards only the local application and optional Vite ports;
- runs non-destructive repository checks during creation/prebuild;
- performs best-effort application bootstrap after creation and runtime restore after start without making Codespace usability depend on application startup;
- provides a non-destructive doctor script for Git/Docker/Compose/disk/GitHub CLI diagnostics.

GitHub Codespaces is not a source of product truth, production controller, canonical database authority, or replacement for Docker Compose. The repository and GitHub CI remain authoritative.

## Prebuild boundary

The configuration is intentionally prebuild-ready. Repository administrators may enable GitHub Codespaces prebuilds for `main` after this configuration is merged. Prebuilds may cache dev-container setup and repository checks, but they do not approve application changes and must not require user-level secrets.

## Failure and recovery

A post-create or post-start application bootstrap failure does not intentionally terminate the Codespace. The shell remains available for diagnosis. If Codespace container creation itself fails, use Codespaces creation logs; a repeatedly failed Codespace should be recreated rather than patched indefinitely.

No automated recovery may run `docker system prune --volumes`, delete named PostgreSQL volumes, rewrite Git history, or modify production infrastructure.

## Consequences

Benefits:
- repeatable Codespaces environment from Git;
- avoids dependence on the generic Codespaces NVM/Node host toolchain;
- one bootstrap path for application review;
- compatible with GitHub Codespaces prebuilds;
- easier creation-log and runtime diagnostics.

Costs:
- GitHub Codespaces remains a hosted service with billing/service terms;
- dev-container feature availability is an external development dependency;
- prebuild enablement is a repository setting outside Git and must be configured by an administrator.

## Evidence

Implementation authority:
- `.devcontainer/devcontainer.json`
- `.devcontainer/*.sh`
- `scripts/codespaces_doctor.sh`
- `.github/workflows/codespaces-contract.yml`

The existing Docker Compose and Foundation visual/application checks remain the application/runtime evidence.

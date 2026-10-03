# ADR-0010 — Codespaces Docker-outside workspace bind contract

Status: accepted
Date: 2026-10-04

## Context

SongChart Codespaces uses the Dev Containers `docker-outside-of-docker` feature while Docker Compose remains the application/database runtime authority. In this topology the Docker daemon resolves bind-mount source paths on the Docker host, not against paths visible only inside the devcontainer.

A Codespace reproduced a concrete failure: `compose.yaml` used `./:/var/www/html`; the app container started with an empty/non-project bind at `/var/www/html` and Composer failed because `composer.json` was absent. Recreating the app container did not help. A direct probe showed the Docker daemon could read the repository through the Codespaces host workspace path `/var/lib/docker/codespacemount/workspace/SongChart-Next`.

## Decision

`.devcontainer/devcontainer.json` exports Dev Containers' `${localWorkspaceFolder}` as `LOCAL_WORKSPACE_FOLDER` through `remoteEnv`. `compose.yaml` uses `${LOCAL_WORKSPACE_FOLDER:-.}` as the application source bind mount.

The fallback `.` preserves ordinary local Docker Compose usage outside Codespaces. The host path is supplied by the Dev Containers runtime rather than hard-coded to a Codespaces implementation path.

## Consequences

- Codespaces Docker-outside bind mounts use a host-visible workspace path.
- Local Docker Compose behavior remains unchanged when `LOCAL_WORKSPACE_FOLDER` is unset.
- No second application runtime, Docker-in-Docker daemon, or copied source tree is introduced.
- PostgreSQL and dependency named volumes remain independent of the source bind and are not deleted by this decision.
- CI must verify both the devcontainer `remoteEnv` contract and Compose interpolation.

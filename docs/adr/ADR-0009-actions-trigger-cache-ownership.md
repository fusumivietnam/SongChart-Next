# ADR-0009 — GitHub Actions trigger ownership and BuildKit cache

- Status: accepted for CI implementation
- Date: 2026-10-02
- Owning issue: #49
- Capabilities: project-os, local-docker-development

## Context

Foundation CI had three avoidable costs and one evidence gap:
- application verification ran on pull requests but not on the merged `main` revision;
- governance-only test changes could trigger heavyweight Docker/application and visual workflows through broad `tests/**` paths;
- Project governance duplicated the Project OS validator already owned by the required `verify` check;
- Docker image layers were rebuilt on ephemeral runners without a cross-run BuildKit cache.

Read-only workflows may safely cancel superseded runs. Mutating Project projection runs must remain serialized.

## Decision

### Exact-main evidence

Foundation application checks run for relevant pull-request changes and again for the relevant merged `main` revision. The latter is authoritative exact-main runtime evidence and also warms the default-branch build cache.

### Trigger ownership

Heavy workflows own only paths that can change the behavior they verify:
- Foundation application: application/runtime manifests, app source and application/provenance tests;
- Foundation visual render: visual/runtime source and visual capture tooling;
- local Design review contract: Docker/Compose/dependency manifests and the review script itself;
- governance: governance regression suite;
- Project OS: the deterministic registry/contract validator.

The old Docker-scaffold workflow is retired because its Compose/database assertions are a strict subset of Foundation application verification for the same relevant paths.

### Cache policy

CI uses one Docker Buildx GitHub Actions cache scope: `foundation-buildkit`.

Pull requests and secondary heavy workflows import this cache only. The Foundation application production build is the **sole writer**, exporting `mode=max` on relevant `main` runs. A single complete production graph contains the shared PHP/Node/dependency/frontend layers needed by the development, CI-development and visual targets. This avoids per-PR cache proliferation, duplicate cache graphs and same-scope writer races while keeping default-branch cache reusable by pull requests.

Dependency-resolving Docker stages copy lockfiles before application source where safe so source-only changes can reuse the locked Composer/pnpm payload layer for build-oriented targets. The Foundation application Compose path deliberately retains the same dependency-volume initialization semantics as local development; a CI dependency-volume preseed experiment was rejected when it changed license-inventory behavior. Cache changes performance only; lockfiles and Dockerfile remain version authority.

Cache misses are always valid and must fall back to a full deterministic build. Cache content is never acceptance evidence.

The visual workflow also restores a narrowly scoped cache containing only the downloaded `fonts-noto-cjk` Debian package. Pull requests restore it; `main` saves it after a miss. Apt indexes and installed-system state are deliberately not cached.

## Action provenance

Pinned CI actions introduced here:
- `docker/setup-buildx-action` v4.3.0 at `37fe631027851001ddb9b187196cc803df7f5f0e`;
- `docker/build-push-action` v7.4.0 at `c3c9e263c25d99ce0380d002d59b67737d91b0dc`;
- `actions/cache` v5.1.0 at `caa296126883cff596d87d8935842f9db880ef25` for the deterministic CJK font package cache.

The two Docker action revisions are Apache-2.0; the reviewed `actions/cache` revision is MIT.

## Failure/recovery

If cache restore/export fails, diagnose GitHub cache quota/backend health but do not bypass tests. Removing `cache-from/cache-to` must leave the workflows semantically valid, only slower.

Required branch checks remain `governance`, `verify` and `health`; optimization must not rename or remove them without a separate branch-protection change.

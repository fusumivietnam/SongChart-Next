# ADR-0002 — GitHub-native project control and evidence authority

Status: proposed for review in the project-control PR. User requested implementation of missing controls; this record does not presume that product/technology decisions or production release were approved.

## Context
SongChart Next has authored governance registries and roadmap scope, but research provenance, environment-scoped inventory, reproducible status reporting, issue/PR acceptance templates and automated consistency validation are incomplete. Chat and generated snapshots drift and cannot serve as project authority.

## Decision proposed
Retain the sole SongChart-Next Git repository as authority for authored product, architecture, design, contracts, registries and source. GitHub Issues/PRs own execution; exact manifests/lockfiles own installed versions; CI and deployment records own verification/deployment evidence. Add two **non-overlapping** registries: research identity/disposition (not approval) and environment-scoped infrastructure instances (not duplicate technology versions or capability statuses). Keep vertical-slice scope in VERTICAL_SLICES.md and live execution state in Issues/PRs. Extend the existing standard-library governance validator and add an offline read-only project status command that declares API-derived fields unknown. GitHub Actions runs governance checks on PR/main. Do not generate an editable CURRENT_STATUS or add a database, workflow engine or second roadmap.

## Controls
ID uniqueness, capability/technology reference consistency, local path safety, dependency and research supersession cycle checks, evidence presence before verified/deployed status. Evidence presence alone does **not** validate that a CI run succeeded at the relevant SHA or that an external research URL is trustworthy: this requires live GitHub review and independent source evaluation. PRs reference acceptance gates, impact, exact tested commit and outstanding checks. Production releases require separate approval/recovery evidence.

## Alternatives
Chat/project memory and manually maintained snapshots rejected because they drift; standalone roadmap SaaS/database and new orchestration rejected as unnecessary additional authorities. A read-only GitHub Projects view is permissible if derived from existing issue records.

## Consequences
The new registries start empty rather than inventing past research or installed production instances. PR #1 Docker scaffold remains independent and unmerged; adopting it requires reconciling its capability/technology ownership and updating the infrastructure inventory only after its runtime configuration is approved and merged. CI cannot itself approve an ADR, rights decision or feature release.

## Acceptance
Review exact file ownership; run standard-library validator and regression tests on PR SHA; review CI permissions/action provenance; verify a new chat can independently query main and live Issues/PRs. Approval/merge is a separate human decision.

# VS-04 release-candidate evidence contract

Status: G3 release-candidate evidence contract. This document does not select a production platform and does not provide G5 deployment evidence.

## Evidence owners

| Concern | Authoritative workflow | Required evidence |
| --- | --- | --- |
| Locked PHP/JS vulnerability audit | `foundation-app.yml` | `composer audit --locked` and production `pnpm audit --audit-level=high` pass on the exact candidate SHA |
| Dependency licenses | `foundation-app.yml` | retained Composer and pnpm license inventories for the exact candidate SHA |
| Source/image SBOM | `foundation-app.yml` | retained SPDX JSON SBOMs for source and the non-deployable production image on the exact candidate SHA |
| Reproducible runtime/build | `foundation-app.yml` | lockfiles, Docker build, PostgreSQL migrations, frontend build/type checks, framework tests, provenance and production-target validation pass |
| Tracked secret-leak guard | `vs04-launch-proof.yml` | repository-owned high-confidence scanner and fixture tests pass without printing matched secret values |
| Public launch-support contracts | `vs04-launch-proof.yml` | VS-04 public HTTP/browser/SEO evidence passes where those files are in scope |

A VS-04 launch-proof PR must trigger both `VS-04 launch proof verification` and `Foundation application checks` on the same exact PR head. VS-04 must not copy Foundation audit/SBOM logic into a second workflow.

## Secret scan policy

The scanner examines Git-tracked text files and fails on high-confidence credential formats, including private-key headers, GitHub tokens, AWS access keys and common live SaaS/API secret formats. Evidence contains only `path:line:rule-id`; matched values are never written to stdout/stderr artifacts or summaries.

Tracked runtime `.env` files are forbidden. `.env.example` is the only allowed tracked `.env*` basename. Generated dependencies and untracked runtime files are outside the Git-tracked scan set.

There is no silent or inline allowlist in the initial contract. A false positive must be removed by using a non-secret placeholder or by a reviewed change to the scanner contract with explicit rationale. Real credentials found in history require separate incident/rotation handling; this scanner does not rotate secrets.

## Production-parity boundary before platform selection

The following are knowable and testable before choosing a hosting provider:

- PHP/extension and locked package compatibility;
- PostgreSQL migration compatibility on disposable PostgreSQL matching the repository runtime major line;
- production-style frontend build;
- non-deployable production PHP-FPM image composition and image-size sanity;
- source and image dependency inventories/SBOMs;
- application configuration can be supplied through runtime environment without committing runtime `.env` files.

The following remain unknown until #69 is resolved and G5 evidence exists:

- platform networking, TLS/DNS, persistent volume/database service behavior and backup integration;
- production secret delivery/rotation mechanism;
- immutable deploy artifact identity on the selected platform;
- production migration execution, smoke tests, rollback and incident behavior;
- production observability/alert delivery.

Therefore passing this contract means **release-candidate G3 evidence is verified for tested scope**, not that SongChart Next is launched or deployed.

## Stop conditions

Do not advance a candidate if any exact-head Foundation or VS-04 check is missing/failed, a high-confidence secret finding exists, a runtime `.env` file is tracked, or evidence is from a different SHA. Production deployment remains candidate/unactivated until #69 and G5 are explicitly completed.

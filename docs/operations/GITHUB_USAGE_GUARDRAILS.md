# GitHub usage guardrails

Status: approved repository-operating policy for issue #142. This document controls cost/quota hygiene only; it does not change product lifecycle, verification ownership, or production architecture.

## Principles

- SongChart Next is a public repository, so standard GitHub-hosted runners are preferred for repository CI. Do not weaken required checks merely to reduce runner minutes.
- Do not adopt larger runners without a bounded benchmark and explicit cost approval.
- GitHub artifacts and caches are disposable evidence transport/acceleration, not project authority. Durable authority remains Git, Issues/PRs, governance registries and exact-SHA workflow evidence.
- Codespaces is an optional developer shell. Docker Compose remains the application/database runtime authority.
- Automation should be event-driven. Avoid tight API polling loops; back off on rate-limit or abuse/secondary-limit responses.

## Repository-enforced limits

`scripts/verify_github_usage_policy.py` is run by Project governance and enforces:

- workflow artifact retention must not exceed 14 days;
- heavy verification workflows must cancel superseded in-progress runs;
- BuildKit GitHub Actions cache uses the single shared `foundation-buildkit` scope rather than branch/SHA-specific scopes;
- the default Codespaces host requirement remains 2 CPU, 8 GB RAM and 32 GB storage.

Project governance additionally enforces the Vercel preview-skip safety contract through `scripts/classify_ci_change.py`: a PR whose branch starts with `docs/` or `governance/` must not contain application, database, frontend, provider, production-package, preview-runtime, developer-environment or visual-impact changes. This protects the Vercel Ignored Build Step from silently skipping a runtime change merely because the branch name is classified as non-runtime.

The classifier remains advisory for general CI fan-out. Only this narrow branch-safety assertion is merge-blocking.

Diagnostics that are useful only for short failure investigation should prefer 7-day retention. SBOM, provenance, browser captures and bounded CI evidence may retain up to 14 days. If durable evidence is required beyond that window, record exact SHA/run/digest references in authored governance or operational evidence rather than increasing artifact retention.

## Operational thresholds

These are warning/action thresholds, not lifecycle authority:

| Resource | Target | Warning | Action boundary |
| --- | --- | --- | --- |
| GitHub Actions artifact storage | keep well below account allowance | 60% | investigate at 75%; remove avoidable retention before 90% |
| Actions cache for this repository | <= 6 GB preferred | >= 7.5 GB | clean/reshape cache before 9 GB; default repository cache ceiling is treated as a hard operational limit |
| Codespaces monthly quota | <= 50% preferred | >= 70% | stop discretionary use at 85% and use local Docker/Actions instead |
| GitHub API remaining primary quota | normal event-driven use | <= 20% remaining | stop optional polling and use backoff/event triggers |

Account-level consumed quota is not stored in the repository because it is live provider state. Check GitHub Billing/Usage and repository Actions Caches when current consumption is needed.

## Workflow policy

- Keep `paths`/`paths-ignore` ownership narrow enough that heavy workflows do not run for unrelated files.
- Keep `concurrency.cancel-in-progress: true` on heavy PR/SHA verification workflows.
- Re-run failed jobs instead of re-running successful jobs where GitHub permits it.
- Cache keys/scopes must represent reusable dependency/build state, never evidence identity. Exact SHA belongs in evidence names and workflow metadata, not cache scope names.
- Main may be the sole writer for expensive shared caches when the owning workflow requires that policy; PRs should read where practical.
- `docs/*` and `governance/*` branch names are reserved for non-runtime work units because Vercel intentionally skips them; use a runtime-eligible branch for any change that needs preview evidence.

## Codespaces policy

The repository requests a 2-core/8-GB machine by default. Select a larger machine manually only when a bounded task cannot complete on the baseline and stop it immediately afterward. Do not use Codespaces as a persistent server or CI replacement.

Repository administrators should keep Codespaces idle timeout conservative and enable prebuilds only when startup savings justify their additional compute/storage consumption. Prefer configuration-change prebuild triggers over every-push prebuilds unless measured developer wait time justifies the cost.

## Change control

Any proposal to increase artifact retention above 14 days, add a new BuildKit cache scope, require a larger default Codespaces machine, weaken preview-skip branch safety, or adopt paid/larger runners must be justified in a bounded issue and update this policy plus its verifier/contract in the same PR.

# Optional local agent-browser UX reconnaissance pilot

**Status: candidate for review; not a required check, protected Preview acceptance, or deployment proof.** Owning acceptance issue: #175; protected Preview browser auth/preflight is independently owned by #215 and draft PR #216. Capability owners: `public-web` and `design-authority` (observations only).

## Scope and safety boundary

This pilot drives **only an already-running local fixture-backed SongChart app** over plain HTTP loopback. It captures interactive accessibility snapshots at 390×844 and 1440×1024 for one approved public route; it does not click, submit, record browser screenshots, write application data, reuse user profiles, access Vercel, or collect secrets. `AGENT_BROWSER_BIN` optionally selects a preinstalled executable. Reject URLs with credentials, query strings, fragments, non-loopback hosts, HTTPS, missing explicit port, or unapproved paths. The CLI's `AGENT_BROWSER_ALLOWED_DOMAINS` is forced to `localhost,127.0.0.1` for **all** browser commands, blocking off-origin redirects and subresources at its network-policy layer. This is not an OS-level egress firewall, so use trusted local fixtures and keep runner egress restricted too.

The local CLI is the open-source `vercel-labs/agent-browser` version **0.41.1** (npm metadata: Apache-2.0, Node >=24). Operator installs it manually in a disposable developer environment; this pilot does not alter the application package manifests, production images, CI workflows, Codespaces bootstrap, or browser session profiles. The optional tool may have its own npm transitive dependencies; it is not an approved committed application dependency. Do not point it at real accounts, personal data, third-party services, or an SSO-protected Preview. The CLI network allowlist is defense in depth, not a guarantee against all process-level egress.

## Run (opt-in)

1. Launch the existing approved Docker Compose app and deterministic test fixtures following `DOCKER_DEVELOPMENT.md`. Confirm the page is accessible on `127.0.0.1:8000`.
2. In an isolated developer shell with Node 24, manually install `npm install --global agent-browser@0.41.1` and run `agent-browser install` (Chromium may require additional OS dependencies). Confirm `agent-browser --version`.
3. Run `bash scripts/agent_browser_pilot.sh http://127.0.0.1:8000/search` and repeat for `/`, `/corrections` or an approved legal/support route. Never use a Preview/share URL in this command.
4. Inspect the terminal snapshots without exporting sensitive page data. Classify every observation as **manual candidate finding**, not a pass/fail assertion. Record reproduction details in #175 only after reproducing a defect with the repository-owned deterministic tests or an approved exact-deployment browser verifier.

## Decision and retirement

Playwright E2E and the existing `foundation-visual`/VS workflows remain sole owners of deterministic browser assertions. The protected Preview smoke remains HTTP-only. No additional required Actions context, credential, artifacts, remote AI provider, or paid browser SaaS is introduced. This is a no-credential local experiment; it **cannot** close #175 or #215. If the pilot gives no reproducible evidence beyond Playwright, delete its helper and runbook in a reviewed PR; no application migration is required. Promote only after explicit review of license, transitive lockfile/provenance, CI ownership, privacy and measured value.

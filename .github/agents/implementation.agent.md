---
name: implementation
description: Implements bounded SongChart Next issues through small contract-tested pull requests while preserving repository authority and Docker-first boundaries
target: github-copilot
disable-model-invocation: true
metadata:
  songchart-status: dormant-until-eligible-copilot-plan
---

Before changing source, read `AGENTS.md`, the owning Issue, relevant architecture/contracts, capability entries and actual manifests/tests.

Implement only the bounded outcome owned by the Issue. Resume existing work instead of creating duplicates. Prefer framework-native or already-approved dependencies. Do not introduce a new service, framework, workflow engine, design system or canonical-data authority without the required ADR/registry approval.

Use the approved Docker-first development/runtime contract. Preserve security, provider-rights, canonical-data and Design Authority boundaries. Add or update tests with the implementation; never weaken tests to make a change pass.

Do not merge, deploy, rotate secrets, delete data or promote capability lifecycle without explicit human authorization and required evidence. Report exactly what is proposed, implemented and verified, including checks that did not run.

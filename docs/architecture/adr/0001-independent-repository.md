# ADR-0001 — Independent project authority

Status: accepted
Date: 2026-09-20

## Context
Historical SongChart source and chat contain implementation details, stage plans and UI contracts that are not necessarily valid for the new project. Uncontrolled reuse would create competing current-state authorities.

## Decision
SongChart-Next GitHub repository is the only current project source authority. Historical repositories, ZIP bundles and conversations are non-authoritative references. No automatic migration or import. New design/framework/runtime decisions remain candidates until separately approved. Generated context is derived from this repository alone.

## Consequences
Future assistants start at README and AGENTS.md and inspect live source/PRs. Reuse requires an explicit issue, audited source/license/data boundary and acceptance tests. This ADR does not claim that any product runtime has been implemented.

# RES-0004 — UX/UI agent skills evaluation reference

Status: evaluated as third-party design QA reference only; no adoption or change to Design Authority.

## Retrievable sources (reviewed 2026-10-18)
- Upstream repository and instructions: https://github.com/plugin87/ux-ui-agent-skills
- Guide: https://github.com/plugin87/ux-ui-agent-skills/blob/main/docs/GUIDE.md
- Package configuration / scripts: https://github.com/plugin87/ux-ui-agent-skills/blob/main/package.json
- Releases / upstream version history: https://github.com/plugin87/ux-ui-agent-skills/releases

## Findings and boundaries
This upstream project offers agent-oriented UX/design guidance plus example accessibility and UI quality checks. Its repository describes checks such as keyboard/focus, responsive overflow, axe-based audits, states and reduced motion. These are potential **ideas for evaluating gaps** in SongChart's existing design and browser verification, not imported rules or established passing results. No benchmark of this package against SongChart has been performed here, and the upstream branch/version can change.

SongChart's `design/DESIGN_AUTHORITY.md`, approved tokens, components and page patterns remain sole visual authority. The existing browser and CI workflow own acceptance; do not install this package, copy its design system, add competing QA pipelines or elevate upstream instruction files to SongChart authority. A future adoption proposal requires pinned version/license review, deterministic evidence of a missed defect, CI cost evaluation, and an explicit owning decision.

Disposition: **research only**, follow existing VS-04/preview UX audit and reuse existing tests first. No capability activation, product scope change, or implementation claim.

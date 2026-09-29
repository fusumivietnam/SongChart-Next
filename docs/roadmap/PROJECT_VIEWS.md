# GitHub Project visual roadmap — derived view contract

Status: approved projection model, 2026-09-29. This document defines human-facing views only. It does not create a second roadmap authority.

## Purpose
Give maintainers a visual, low-friction way to answer:
- what needs an owner decision;
- what work is ready, blocked, active or under review;
- which slice/capability owns the work;
- which acceptance gate is next;
- what exact PR/CI evidence supports a claim.

The Project must be reconstructible from repository authority plus live Issues/PRs. Dragging a card or editing a Project field never promotes a capability lifecycle state.

## Required fields
- `Slice`: FOUNDATION / VS-01a / VS-01b / VS-02 / VS-03 / VS-04 / Later
- `Capability`: existing capability ID only
- `Execution`: Proposed / Ready / In progress / Blocked / In review / Done
- `Gate`: G0 / G1 / G2 / G3 / G4 / G5
- `Decision`: None / Owner decision required / Approved / Rejected
- `Evidence`: PR/CI/release reference
- `Start`, `Target`: optional planning dates; never verification evidence

Do not manually maintain a Project field that claims capability lifecycle truth (`candidate/approved/implemented/verified/deployed`). If lifecycle is displayed, it must be a derived projection of `governance/CAPABILITY_MAP.json`.

## Required views

### 1. Executive Roadmap
Roadmap/timeline grouped by `Slice`. Purpose: human-readable dependency and horizon view. Dates are planning hints, not release commitments.

### 2. Delivery Board
Board columns by `Execution`: Ready / In progress / Blocked / In review / Done. The Roadmap Controller's derived execution rules remain authoritative for the projection.

### 3. Capability Matrix
Table grouped by `Capability`, showing owning Slice, next Gate and Evidence. Lifecycle, if shown, is read-only/derived from the Capability Map.

### 4. Decision Queue
Filtered table where `Decision = Owner decision required`, plus blocked work that depends on those decisions. This is the primary owner-facing review queue.

### 5. Verification / Release Gates
Table or board grouped by `Gate`, showing exact evidence links. G2 means exact-SHA verification; G4/G5 cannot be inferred from merge or local Docker.

## Automation boundary
Project automation may mirror Issue/PR lifecycle into execution/project fields. It must never:
- write to `CAPABILITY_MAP.json`;
- mark verified/deployed from a card move;
- invent evidence;
- choose priority or product decisions;
- close governance gates when source evidence is unknown.

The read-only roadmap controller remains the reconciliation mechanism. A Project outage or stale card is a UI problem, not authority loss.

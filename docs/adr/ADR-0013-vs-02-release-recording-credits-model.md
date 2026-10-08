# ADR-0013 — VS-02 Release / Recording / Credits canonical model

Status: accepted
Date: 2026-10-06
Issue: #74

## Context

VS-02 extends the verified Artist path into the next MVP knowledge slice. The owner approved C1-C8 on 2026-10-06. SongChart must preserve the semantic distinction between Work, Recording, Release and Release Group rather than flattening provider shapes into one title record.

## Decision

- Work, Recording, Release and Release Group each receive independent SongChart ULID identities.
- Release Group is the conceptual grouping; Release is a concrete edition/issue.
- Provider IDs remain external identity evidence with uniqueness on `(provider, entity_type, external_id)` and never become canonical primary keys.
- Recording ISRCs belong to Recording. Release barcode belongs to Release.
- Credits are ordered structured rows with artist, role, credited-as, join phrase and position.
- Release structure is `Release -> Medium -> Track -> Recording`; Track is not a Recording and may carry release-specific title/number metadata.
- Recording-to-Work relationships are explicit many-to-many and are never inferred from titles.
- Release dates support year/month/day precision; country may be unknown/null.
- VS-02 activates public Release and Recording ID+slug pages with canonical redirect behavior. Release Group and Work remain canonical/readable domain entities without mandatory public detail pages in this slice.

## Persistence

VS-02 uses explicit PostgreSQL tables and foreign keys for canonical relationships. A dedicated `music_external_identities` table indexes VS-02 entities and enforces the provider tuple. The existing VS-01a Artist external identity table remains intact to avoid destabilizing verified Artist behavior; a future unification requires its own compatibility ADR if justified.

## Boundaries

This decision does not activate live Release/Recording MusicBrainz traffic, Cover Art Archive, public API, search infrastructure, commercial provider use, or production deployment.

## Verification

Acceptance requires deterministic fixture import, idempotency, identity isolation, relationship/credit integrity, partial-date semantics, typed Release/Recording pages, canonical redirects, PostgreSQL integration tests and narrow/wide browser evidence on an exact PR SHA.
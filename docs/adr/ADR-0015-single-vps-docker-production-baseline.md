# ADR-0015 — Single-VPS Docker production baseline

Status: accepted for G5 preparation
Date: 2026-10-11
Issue: #118
Parent: #69
Capability: `production-deploy`

## Context

SongChart Next has exact-SHA G2/G3/G4 launch-proof evidence, but no production target has been selected or deployed. The initial production objective is to minimize recurring infrastructure cost while preserving a clean migration path to managed/cloud infrastructure if demand grows.

The application already has a Docker-first development/runtime baseline, a PHP-FPM production image target, PostgreSQL canonical authority, tested backup/restore and rollback evidence, and a DB-aware `/health` endpoint. Coolify is not required for the initial deployment and must not become a control-plane dependency.

## Decision

The first production target baseline is:

- one Ubuntu Server 24.04 LTS x86_64 VPS;
- Docker Engine + Docker Compose as the production container mechanism;
- one immutable SongChart `web` image containing Nginx and public assets;
- one immutable SongChart `app` image containing PHP-FPM application runtime;
- PostgreSQL 18.6 in a private Docker service with persistent storage on the VPS for the initial low-cost phase;
- only Nginx publishes HTTP(S) ports; PHP-FPM and PostgreSQL are private-network only;
- production secrets are injected from an untracked environment file or future secret manager and are never committed;
- PostgreSQL backups must leave the VPS. A local dump alone is not a valid backup completion signal;
- releases are identified by immutable image references/digests. Rollback changes the application/web image references; it does not perform destructive database rollback by default;
- DNS/TLS termination, VPS vendor and off-host backup provider are replaceable operating choices, not application architecture authority.

## Portability boundary

The Compose topology must permit later migration to managed PostgreSQL or a cloud/container platform by changing deployment configuration and secret delivery, not domain/application code. PostgreSQL remains the canonical product-data authority regardless of hosting provider.

## Explicit non-decisions

This ADR does not:

- select a VPS vendor;
- create or mutate a real VPS;
- select a DNS provider;
- provision TLS certificates;
- create production credentials;
- approve production MusicBrainz/provider traffic;
- activate public API, search-index, recommendation, Coolify or Kubernetes;
- claim the application is deployed.

## G5 promotion rule

`production-deploy` may move beyond candidate/approved only after a separate G5 execution records:

1. immutable app/web image identities;
2. production environment identity;
3. production database migration and backup result;
4. `/health` and representative public journey smoke evidence;
5. TLS/DNS result where public exposure is intended;
6. rollback/recovery evidence applicable to that deployed revision;
7. release-owner approval.

Repository CI may verify this deployment package, but CI verification alone is not deployment evidence.

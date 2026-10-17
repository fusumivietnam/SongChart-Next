# Single-VPS Docker production runbook

Authority: ADR-0015 and issues #69/#121. This runbook prepares G5 execution; it is not evidence that production exists.

## Baseline

- Ubuntu Server 24.04 LTS x86_64 VPS.
- Docker Engine with the Compose plugin.
- `compose.production.yaml` only; development `compose.yaml` is not a production deployment manifest.
- immutable `APP_IMAGE` and `WEB_IMAGE` references from the same reviewed release revision.
- PostgreSQL 18.6 on the private `backend` network with a persistent named volume.
- Nginx is the only container with a host-published HTTP port.
- secrets live in an owner-readable untracked production env file or a future secret manager.

VPS vendor, DNS provider, TLS mechanism, off-host backup provider and external health-check provider are replaceable. They do not become SongChart application authority.

## Host prerequisites

1. Apply OS security updates and configure SSH key-only access.
2. Install Docker Engine from an approved source and the Docker Compose plugin.
3. Configure host firewall so only SSH and the intended HTTP/TLS entry points are reachable.
4. Create a deployment directory owned by the release operator.
5. Copy `compose.production.yaml` and repository-owned production helpers to that directory, or deploy from a verified release bundle.
6. Create the untracked environment file from `deploy/production.env.example`; mode `0600` is recommended.
7. Keep `HTTP_BIND_ADDRESS=127.0.0.1` until the intended public TLS/network path is ready.

## Release inputs

A production attempt requires all of:

- reviewed exact Git SHA;
- immutable `APP_IMAGE` and `WEB_IMAGE` references/digests built from that SHA;
- production `APP_KEY` and database credentials outside Git;
- `APP_URL` for the intended public hostname;
- a release-specific migration impact and rollback/forward-fix review;
- off-host backup destination and retention rule;
- an external `/health` monitoring path, alert destination and named incident/release owner;
- release owner approval.

Do not begin public cutover if the health monitor cannot reach the intended endpoint or if an alert has no accountable human/operator destination.

## Pre-deploy backup

Run:

```bash
bash scripts/production/backup.sh /secure/path/production.env
```

The helper deliberately exits non-zero after creating and hashing the local logical dump. This is fail-closed: **a dump that remains on the same VPS is not a completed backup**. Copy the dump and checksum to independent storage, verify the remote checksum, then record the remote object/version in the release evidence before continuing.

## Deploy

Once backup and release approval are recorded:

```bash
bash scripts/production/deploy.sh /secure/path/production.env
```

The helper validates Compose, pulls immutable images, waits for PostgreSQL health, applies forward migrations with `--force`, starts app/web, and runs the repository smoke contract.

Do not run this command against an unknown database state. A migration failure stops the release and requires the release-specific recovery/forward-fix decision.

## Smoke, health and alerting

```bash
bash scripts/production/smoke.sh https://example.com
```

Minimum G5 smoke covers `/health`, `/`, and `/search`. `/health` must return the generic healthy JSON state and HTTP 200. Add release-specific canonical journey checks where the release changed those paths.

Before production is accepted as deployed, record evidence that an **external** monitor checks the public `/health` path and can reach the configured alert destination. The first release does not require a dedicated observability stack: a commodity uptime/HTTP checker is sufficient if it is independent of the VPS, has a bounded check interval, identifies the monitored hostname, and routes failure to the named incident/release owner. Prometheus/Grafana/Loki or a second monitoring platform must not be introduced without an independent activation need.

G5 evidence must record the monitor/provider identity (not credentials), monitored URL/hostname, check interval, alert destination/owner and a successful alert-path test or equivalent provider verification. Passing CI or local Compose health is not production monitoring evidence.

## Application rollback

Use only previously recorded immutable image references:

```bash
bash scripts/production/rollback.sh /secure/path/production.env \
  ghcr.io/example/songchart-next-app@sha256:... \
  ghcr.io/example/songchart-next-web@sha256:...
```

This changes application/web images only. It intentionally does **not** run database `migrate:rollback`. Schema rollback is a separate destructive decision; prefer backward-compatible migrations and forward fixes. If schema compatibility is broken, stop and execute the release-specific recovery plan.

## Database recovery

The repository's VS-04 recovery drill proves logical restore mechanics on disposable infrastructure. Production recovery additionally requires the production backup object/version, target environment identity, restore timestamps and post-restore health/smoke evidence. Never claim production recovery solely from CI evidence.

## Later migration to managed/cloud infrastructure

The application contract uses standard PostgreSQL connection variables and separate app/web images. Moving PostgreSQL off the VPS or moving containers to a cloud platform must not require domain/application-code changes. Re-evaluate network, secret delivery, backup/PITR, observability and deployment controller ownership at that activation boundary.

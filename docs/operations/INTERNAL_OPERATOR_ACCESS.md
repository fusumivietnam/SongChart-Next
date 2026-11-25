# Internal operator identity (proposed; not deployed)

This foundation stores an explicit `is_super_admin` flag, default false, outside User mass assignment. It does **not** implement correction review, a privileged dashboard, canonical mutation, bypass policies, or production deployment. Its purpose is to reserve a revocable internal owner identity before a separately reviewed authorization surface exists. Issue #173 and the `admin-review` activation trigger remain unchanged.

## Provisioning (after code review, merge and migration approval)

First complete Fortify email verification and confirm 2FA through the existing security settings. On the operator-controlled application CLI, inspect the intended user ID without exposing credentials. Run only after the additive migration is reviewed/applied:

```bash
docker compose exec app php artisan songchart:operator:access 1
```

The command asks for confirmation; it refuses an unverified email, missing confirmed 2FA or nonexistent user. For revocation:

```bash
docker compose exec app php artisan songchart:operator:access 1 --revoke
```

No predefined email, password, secret or admin user is committed. Existing users default to non-admin. `--force` is reserved for controlled non-interactive execution and tests.

`hasOperatorAccess()` is an identity predicate only, **not** proof that the current session passed MFA. No privileged web route may authorize writes solely from this flag or `two_factor_confirmed_at`. Any future route must establish fresh session assurance, CSRF, explicit policies and denial tests, per `docs/engineering/VS05E_REVIEWER_CONTRACT.md`. Do not enable reviewer routes or roles without separate issue #173 activation approval.

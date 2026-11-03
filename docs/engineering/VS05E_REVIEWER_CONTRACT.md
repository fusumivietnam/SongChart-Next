# VS-05e reviewer implementation contract (pre-activation)

Status: **proposal for human review**, issue [#173](https://github.com/fusumivietnam/SongChart-Next/issues/173). This is not approval to activate `admin-review`, register reviewers or deploy new routes. Lifecycle authority stays `governance/CAPABILITY_MAP.json` (`candidate`); trigger is `governance/ACTIVATION_TRIGGERS.json`.

## Existing source, verified by inspection

- `routes/web.php`: public GET/POST `/corrections`; `dashboard` is merely `auth,verified` and **not** a reviewer authorization boundary.
- `app/Http/Controllers/CorrectionController.php`: bounded anonymous intake with rate limits, request validation and generic failure handling; does not decide evidence.
- `app/Music/Corrections/SubmitCorrectionEvidence.php`: validates canonical subject existence and stores/deduplicates pending evidence using DB transactions. Source submission must remain unchanged by reviewer activation.
- `app/Models/User.php`: `MustVerifyEmail` and Fortify `TwoFactorAuthenticatable`; `two_factor_confirmed_at` cast exists.
- `config/fortify.php`: email verification and `twoFactorAuthentication(confirm=true,confirmPassword=true)` are configured. **These do not establish role authorization, forced reviewer enrolment, or that the current session passed MFA.**

## Contract before any implementation

1. **Activation decision**: document actual unresolved moderation need, human approval of reviewer-role provisioning/revocation and negative authorization tests. No change from `candidate` merely because this file or a fixture exists.
2. **Reviewer identity**: one internal provisioned identity, verified email, 2FA enrolled **and confirmed**, explicit server-side reviewer allow rule; revoked or inactive reviewers denied immediately. Do not infer reviewer authorization from general `auth`, `verified`, `dashboard` or possession of a passkey.
3. **Session assurance**: define an auditable MFA-authenticated-session check, including Fortify recovery/passkey flows, session expiry and step-up before writing a decision. A populated `two_factor_confirmed_at` alone is insufficient proof of MFA on the active session. Existing CSRF protections remain mandatory.
4. **Evidence-only decision**: pending -> approved or rejected exactly once; lock the row or use equivalent compare-and-set, reject concurrent conflicting decisions. Record reviewer ID, bounded rationale, `resolved_at`, and immutable decision event atomically. Never mutate canonical Artist/Release/Recording or fetch submitted evidence URLs.
5. **Privacy and retention**: pending expires at 180 days under existing job; resolved evidence **and decision history** expire by 365 days after authoritative `resolved_at`. No mass deletion before a reviewed migration/backfill and recovery plan.
6. **Presentation**: after activation, use the approved Design Authority; keep reviewer views separate from anonymous public route. Do not install Filament, create a generic admin platform or enable public account features as a prerequisite.

## Required code evidence on an eventual implementation PR

- Database/feature tests deny guest, ordinary verified user, unconfirmed 2FA, missing session MFA, revoked reviewer and CSRF-invalid requests; no canonical writes in any case.
- PostgreSQL concurrency and transaction-rollback tests show one decision/audit record and unchanged canonical rows.
- Boundary tests for 180-day pending vs 365-day resolved retention, with safe behavior for null `resolved_at`.
- Browser narrow/wide, keyboard and error/empty states; exact-head checks before release.
- Human sign-off on activation, reviewer provisioning and authorization contract recorded in #173 before any reviewer route or credential is enabled.

## Resource limit

Implement this as **one bounded vertical-slice PR**, reusing existing app DB/auth/tests and owned CI. No new workflow, secondary queue, SaaS or Preview build for this design-only contract. Do not overlap #215/#216, #174 or G5 owners.

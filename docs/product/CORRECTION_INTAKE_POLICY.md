# Public correction intake policy

**Status:** approved for VS-05 public-intake implementation on 2026-10-16. Implementation, verification, `admin-review` activation and production deployment remain separate lifecycle states.

Authority: Product Charter, VS-05 roadmap scope and owner decision #133.

## Purpose and boundary

SongChart may accept public metadata-correction evidence for an existing canonical Artist, Release or Recording. A submission is evidence for later review; it is never a canonical write, never an approval signal and never sufficient by itself to activate `admin-review`.

The initial public intake is anonymous. It does not require registration and does not collect submitter name, email address, account identity or free-form contact information.

## Accepted data

The public form may accept only:

- canonical subject type: Artist, Release or Recording;
- stable SongChart subject ID;
- correction claim, using the existing bounded `CorrectionEvidence` contract of 1–4000 characters;
- one optional supporting URL, using the existing bounded contract of at most 2048 characters and `http` or `https` scheme only.

The form and public copy must explicitly prohibit passwords, access tokens, private credentials, private account data, health/financial/government identifiers and other sensitive personal information.

No additional contact/identity field may be added without a new privacy decision.

## Request metadata and rate limiting

Infrastructure may transiently process normal request metadata needed for transport, security and abuse prevention. Public correction evidence must not persist the submitter IP address, user agent or a reversible rate-limit identifier in the correction-submission row.

VS-05c should use an ephemeral, one-way rate-limit key derived from the request IP and application secret/salt through the framework rate limiter or equivalent cache-backed primitive. The key expires with the abuse-control window and is not review evidence.

Initial anonymous limits:

- maximum 5 correction submissions per 10 minutes per derived client key;
- maximum 20 correction submissions per 24 hours per derived client key;
- maximum request body size 8 KiB at the application boundary, independent of broader web-server limits.

Exceeding a limit returns a deterministic throttled state and creates no correction row.

CAPTCHA is not approved for the initial implementation. It may be reconsidered only if measured abuse shows that bounded throttling and duplicate suppression are insufficient.

## Duplicate and spam handling

Before persistence, VS-05c should normalize only the fields needed for deterministic duplicate comparison without changing claim meaning: trim surrounding whitespace, use the canonical subject identity, and normalize an absent evidence URL to null.

An identical subject + normalized claim + normalized evidence URL submitted within 24 hours must not create another correction row. The public response remains the same generic accepted state as a new valid submission; callers are not told whether an equivalent row already existed.

Do not use fuzzy-text similarity, AI classification or provider fetching as an admission gate for the initial public form.

## Supporting URL security

The supporting URL is stored as user-supplied evidence only.

At intake SongChart must not:

- fetch the URL;
- resolve its hostname for validation;
- follow redirects;
- execute HTML, scripts or embeds;
- download media or attachments;
- treat the URL as trusted provider identity.

Validation is syntactic and bounded only. Any later reviewer-facing navigation must preserve browser safety controls and continue to treat the destination as untrusted external content.

This non-fetching rule is an explicit SSRF boundary.

## Retention

Correction evidence uses bounded retention rather than indefinite storage:

- a submission that remains pending may be retained for at most 180 days from submission;
- after a submission is resolved, its claim, supporting URL and associated decision history may be retained for at most 365 days from resolution to support audit/reconsideration;
- after the applicable period expires, free-text claims and supporting URLs must be deleted rather than anonymized into another long-lived evidence store;
- aggregate operational counters that cannot reconstruct a submission may be retained separately under the applicable observability policy.

A future legal, fraud or abuse requirement for longer retention requires a separate recorded decision before changing these limits.

Retention enforcement may be implemented with the review workflow or an earlier bounded cleanup job, but public intake must not be described as production-ready until an enforceable cleanup path exists for the deployed environment.

## Public UX contract

The correction experience must expose deterministic states:

- **accepted:** the evidence was accepted for possible review; copy must say this does not mean the correction is approved or canonical data changed;
- **validation error:** identify invalid public fields without reflecting unsafe HTML or internal exception detail;
- **throttled:** state that too many submissions were received and the caller should retry later;
- **unavailable:** fail closed if the evidence store is unavailable; do not claim acceptance.

A valid POST should use the normal Laravel/Inertia post-redirect-get pattern so browser refresh does not accidentally repeat a submission. Validation, throttle and unavailable behavior must remain testable as distinct outcomes.

## Public privacy/corrections copy before activation

Before the repository exposes the public POST route, `/privacy` and `/corrections` must clearly state all of the following:

- no name/email/account identity is requested by the initial correction form;
- SongChart stores the canonical subject, submitted claim and optional supporting URL for review;
- pending evidence may be retained up to 180 days and resolved evidence up to 365 days after resolution;
- normal request metadata may be processed transiently for security/rate limiting but is not stored as correction evidence;
- users must not submit secrets or sensitive personal information;
- supporting URLs are not fetched at intake;
- submitting evidence never means SongChart accepted the correction or changed canonical data.

The existing external GitHub issue-tracker correction path remains the public path until VS-05c is implemented and exact-head verified.

## Review and canonical mutation boundary

`admin-review` remains `candidate`. Public intake alone does not activate it.

If unresolved real claims demonstrate a moderation need, a later separately approved review slice must define reviewer identity, authorization, approve/reject semantics and decision history. Any approved canonical mutation must enter through SongChart application/domain validation and must never update canonical tables directly from public-submission code.

Public self-registration remains out of scope.

## VS-05c implementation acceptance

A bounded VS-05c implementation may proceed only within this policy and should prove at minimum:

1. no name/email/account/contact field exists;
2. existing correction-evidence validation bounds are reused rather than duplicated as a second source of truth;
3. public subject identity is resolved by stable SongChart identity, never display-name matching;
4. the body-size and anonymous rate limits are enforced;
5. duplicate submissions in the 24-hour window do not create duplicate rows and do not disclose prior existence;
6. supporting URLs are never fetched;
7. accepted, validation, throttled and unavailable states are deterministic;
8. `/privacy` and `/corrections` contain the required public copy before POST activation;
9. public intake has no canonical write path;
10. `admin-review` remains candidate until separately activated.

## Change control

Changes to collected PII, retention periods, public identity/account requirements, CAPTCHA adoption, external evidence fetching or direct canonical mutation are outside this approval and require a new owner decision before implementation.

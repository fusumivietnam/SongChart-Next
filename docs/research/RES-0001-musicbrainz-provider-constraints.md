# RES-0001 — MusicBrainz provider activation constraints

- **Status:** accepted research evidence for the bounded VS-01b provider-policy decision
- **Reviewed:** 2026-10-02
- **Publisher/operator:** MusicBrainz / MetaBrainz Foundation
- **Applicable capabilities:** provider-policy, provider-adapters
- **Decision reference:** `docs/providers/MUSICBRAINZ.md`
- **Implementation authority:** none; this note is research evidence only

## Research question

What externally documented constraints must SongChart respect before implementing and activating a live MusicBrainz metadata adapter for VS-01b?

## Retrievable sources

Reviewed official sources:

1. MusicBrainz API overview  
   https://musicbrainz.org/doc/MusicBrainz_API
2. MusicBrainz API rate limiting  
   https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting
3. MusicBrainz Web Service overview  
   https://musicbrainz.org/doc/Web_Service
4. MusicBrainz data license  
   https://musicbrainz.org/doc/About/Data_License
5. MusicBrainz database/license breakdown  
   https://musicbrainz.org/doc/MusicBrainz_Database
6. MetaBrainz datasets/commercial-use guidance  
   https://metabrainz.org/datasets

These sources were retrievable on 2026-10-02 and are provider-operated documentation rather than third-party summaries.

## Findings used by the decision

### API identification and throughput

MusicBrainz requires a meaningful User-Agent for API clients. The documented public-service rule is no more than one request per second unless separately agreed with MusicBrainz. Requests may be throttled with HTTP 503 based on application, source IP or global service load.

Operational implication adopted by SongChart: a future adapter must identify itself, globally rate-limit MusicBrainz traffic, and use bounded retry/backoff without allowing concurrency to bypass the provider ceiling.

### Authentication/privacy boundary

Read-only public metadata can be requested without an API key. Authenticated data submission and requests involving user information require authentication.

Operational implication: initial SongChart scope excludes user-information endpoints, OAuth and authenticated edits.

### Data licensing

MusicBrainz documents core database data as CC0 and supplementary data under CC BY-NC-SA 3.0. Cover art is explicitly outside the MusicBrainz dataset and provided through the Cover Art Archive.

Operational implication: the first SongChart adapter is restricted to reviewed core/CC0 fields. Supplementary data and artwork require separate rights review.

### Hosted-service/commercial-use boundary

MusicBrainz documents non-commercial use of its web service as free and directs commercial users to commercial plans/contact. MetaBrainz separately publishes downloadable datasets with their own license/commercial-support framing.

Operational implication: SongChart does not equate CC0 database licensing with unrestricted commercial use of the hosted MusicBrainz API. Commercial/public production activation remains an owner decision.

## Rights / security / privacy assessment

- No SongChart right to redistribute supplementary MusicBrainz data is inferred from the CC0 status of core data.
- No Cover Art Archive rights are inferred from MusicBrainz metadata rights.
- No user information or authenticated editing is required by the planned initial adapter.
- Provider availability is external and must not be allowed to corrupt or directly mutate SongChart canonical data.
- Provider documentation can change; material changes require re-evaluation before continued live activation.

## Alternatives considered

- **Deterministic fixture only:** retained for VS-01a and contract tests; insufficient for VS-01b live provider goals.
- **MusicBrainz downloadable dumps:** potentially useful for a future bulk-ingestion architecture, but not selected by the current VS-01b web-service decision and would require separate operational/storage/update analysis.
- **Other metadata providers:** not evaluated by this research record; adding one requires its own provider-specific evidence.

## Limitations / unresolved decisions

This research does not establish:
- a SongChart raw-evidence retention duration;
- approval for persistent raw-response archival;
- approval for commercial hosted-service use;
- the exact field allow-list for every future MusicBrainz endpoint;
- live-adapter implementation or verification evidence;
- provider availability/SLA guarantees.

Those unresolved items remain gates in `docs/providers/MUSICBRAINZ.md` and Issue #19.

## Disposition

**Accepted** as evidence supporting the bounded MusicBrainz provider-policy candidate merged through PR #57.

Acceptance here means the research is useful and traceable. It does **not** approve the provider adapter, promote `provider-policy` or `provider-adapters`, activate live HTTP, or change roadmap scope.

# RES-0003 — YouTube embedded player and navigation research

Status: evaluated as a source-backed policy/design reference only. No embed or persistent-player product approval.

## Retrievable primary sources (reviewed 2026-10-18)
- YouTube IFrame Player API: https://developers.google.com/youtube/iframe_api_reference
- YouTube API Services required minimum functionality: https://developers.google.com/youtube/terms/required-minimum-functionality
- YouTube developer policies: https://developers.google.com/youtube/terms/developer-policies
- YouTube Help, embedding and privacy-enhanced mode: https://support.google.com/youtube/answer/171780

## Findings and boundaries
YouTube publishes an official iframe player interface and requires compliance with its developer policies for embedded playback. The minimum-functionality policies address player identification/referrer, player visibility/autoplay and controls; an embedded player is not equivalent to a simple permitted outbound destination link. A privacy-enhanced embedding option exists but does not waive platform rules.

SongChart Product Charter currently authorizes permitted **external provider navigation**, not video redistribution or automatically an embedded/persistent player. Any proposed YouTube-first or persistent-player experience therefore needs its own product decision, provider-rights review, privacy/security/consent and accessibility evaluation, Design Authority contract, and browser acceptance. This research does not authorize YouTube Data API integration, storage, scraping, embedding, autoplay, playback persistence, or production usage.

Disposition: **research only**, revisit if an explicitly scoped product issue requests an embedded/persistent player. Current external-link contracts and provider-policy gates remain unchanged.

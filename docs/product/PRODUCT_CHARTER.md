# Product charter — SongChart Next

**Status: proposed; approval is tracked in an ADR/issue.**

SongChart Next is an internationally oriented music knowledge, metadata discovery and legal provider-navigation product, **not** a streaming/hosting or general developer-platform product.

## MVP user journey
Home/search -> results by entity type -> Artist -> Release -> Recording/credits -> permitted listening/viewing destination. Clearly distinguish verified, unknown and contested data; display provenance where applicable. Missing artwork and metadata must fail gracefully.

## MVP scope candidate
Search, Artist/Release/Recording read pages, MusicBrainz-derived ingestion with provider compliance, canonical entity identity, provenance, basic editorial correction/review, responsive accessible pages, international-ready URLs, SEO and tested production recovery. Authentication only for workflows that genuinely need it.

## Explicitly deferred
Charts built from unlicensed/undefined rankings, audio/video redistribution, native clients, public plugin marketplace, write-enabled remote MCP, advanced AI agents, partner billing, distributed databases, Kubernetes and multiple redundant control planes.

## Acceptance before public launch
A representative permitted dataset; end-to-end journey in browser on narrow and wide screens; approved visual baseline; legal/provider rights check; verified redirects, errors and empty states; automated tests; backup **and restore** proof; security/privacy/incident/rollback evidence.

## Scope discipline
Research -> idea -> evaluation -> approved capability -> issue -> PR -> release. Research or a chat conversation never auto-promotes a feature into committed roadmap.

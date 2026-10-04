# SongChart Next — shared component contracts

Status: shared component anatomy contract derived from the approved Foundation concept. Existing Foundation behavior is approved where already rendered; extensions remain candidate until their owning surface is reviewed.

## Shell primitives

### SiteHeader
- brand/home affordance;
- global search when appropriate;
- navigation only for activated public destinations;
- no fake/placeholder product links in production;
- compact mobile arrangement must preserve search and keyboard reachability.

### SiteFooter
- restrained secondary navigation;
- legal/support links only when real routes exist;
- no fabricated copyright/license claims.

### SkipLink
- first keyboard-accessible page control;
- becomes visible on focus;
- targets the unique main landmark.

## Navigation/content primitives

### Breadcrumbs
Use for deeper editorial/legal/entity hierarchy when it adds orientation. Do not duplicate a shallow global navigation path mechanically.

### PageTypeLabel
Small semantic context label above the page title. Uppercase/tracking treatment may be used consistently; it is not a decorative category chip.

### PageTitleBlock
Contains title, optional disambiguation/purpose text and essential status context. Long Unicode/mixed-script titles wrap; detail-page identity is not ellipsized by default.

## Data primitives

### Artwork
- square/near-square;
- deterministic placeholder when missing;
- meaningful alt text or intentionally decorative semantics depending context;
- image absence never collapses identity layout.

### MetadataList
Label/value pairs with visible grouping and semantic `dl` where appropriate. Avoid converting every scalar into a badge.

### EntityResultRow
Required fields: entity type, primary label/name, disambiguation/context. Optional artwork/secondary metadata. Same-name results must remain distinguishable without artwork.

### RelationshipSection
Section heading + grouped relationships/list/empty state. Unknown relationships are not silently omitted if their absence matters to understanding.

### ProvenanceBlock
Displays source/provenance/correction context in factual language. It must distinguish provider evidence from SongChart canonical identity.

## Action primitives

### PrimaryButton
One dominant action within a local task. Accent-filled, visible focus, minimum pointer target 44px where layout permits.

### SecondaryButton
Border/text treatment for retry/cancel/secondary navigation.

### TextLink
Clearly identifiable link; external/provider destination may include explicit destination context. Never style non-navigation actions as ambiguous links without semantics.

### SearchField
Visible or programmatic label, search icon optional, keyboard submit, predictable clear behavior. Placeholder never substitutes for an accessible label.

## State primitives

### EmptyState
States what is absent, avoids invented fallback data, and gives a useful next action when available.

### ErrorState
Uses semantic alert behavior when immediate. Contains error meaning, recovery expectation and retry/support action when possible. Color is not the only signal.

### LoadingState
Preserves approximate final hierarchy without fabricated names/metrics. Motion must respect reduced-motion.

### Notice
Informational, warning, success and danger semantics use text + semantic markup; icon/color only reinforce meaning.

## Long-form primitives

### DocumentHeader
Title, optional last-updated/effective metadata, optional concise summary/notice. Legal dates must come from authored legal content, not UI defaults.

### DocumentSection
Readable `48rem` maximum measure by default, stable heading hierarchy, link treatment consistent with the global concept.

### ArticleMeta
Optional author/source/date/category metadata only when real and contractually owned. Do not fabricate authorship or engagement metrics.

## Forms and correction

### FormField
Persistent label, help text/error text relationships, accessible validation, no color-only errors.

### CorrectionEntry
Clearly explains that submission enters review and does not mutate canonical data immediately.

### SubmissionStatus
Pending/accepted/rejected/needs-more-information language must reflect real workflow state; never use success styling before acceptance.

## Anti-patterns

- card-per-section dashboard look for ordinary document pages;
- pill/badge proliferation;
- hidden essential metadata behind hover only;
- icon-only critical actions without accessible names;
- fake verification/trust badges;
- social counters or ranking widgets without approved product/data contracts;
- local one-off colors/radii/spacing where a semantic token exists.

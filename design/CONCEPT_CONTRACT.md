# SongChart Next — cross-page concept contract

Status: **approved interpretation of the 2026-10-02 Foundation baseline**. This file consolidates how the approved identity/tokens are reused across future pages. It does not approve unrendered page families.

## 1. Concept sentence

SongChart Next is a **calm knowledge interface / editorial database for music metadata**: trustworthy, quiet, information-first, internationally robust and explicit about provenance, uncertainty and external destinations.

## 2. Visual DNA

- Light neutral canvas; white is the default page background.
- Slate-like text hierarchy; strong dark headings and muted explanatory text.
- One blue accent family for links, focus and primary action.
- Restrained rounded corners; medium radius is normal, pill shapes are exceptional.
- Borders/dividers organize information before shadows. Decorative elevation is discouraged.
- System sans typography, clear hierarchy, comfortable long-form reading.
- Artwork is contextual evidence, never required for layout integrity.
- Icons are simple line/support icons and never replace text for critical meaning.
- Motion is optional, short and nonessential; reduced-motion remains fully usable.

## 3. Layout DNA

- Global shell max width: `72rem`.
- Long-form/document reading width: `48rem`; compact explanatory copy may use `40rem`.
- Narrow/wide reference evidence: `390x844` and `1440x1024` CSS px.
- Mobile starts as a single readable column; secondary information stacks below primary identity.
- Desktop may use 2-column entity anatomy where artwork/context is secondary to metadata.
- Horizontal scrolling is not a normal page-layout strategy; dense tables require a specific pattern decision.
- Page whitespace communicates hierarchy; do not solve density by wrapping every section in a card.

## 4. Information hierarchy

Preferred order for public pages:
1. context/navigation;
2. entity/page type label;
3. primary title/identity;
4. disambiguation or purpose text;
5. primary data/content;
6. relationships/actions;
7. provenance/correction/support information.

Legal/editorial pages replace entity metadata with readable document content but retain the same shell, typography, action and footer semantics.

## 5. Interaction language

- Primary action: filled accent button, one clear dominant action per local task.
- Secondary action: border/text treatment.
- Links remain recognizable links; destructive or external-provider actions are explicitly labeled.
- Every interactive element has visible keyboard focus.
- Loading never fabricates data; unknown remains unknown.
- Error states explain whether retry/recovery is possible.
- Empty states state what is absent and the next useful action, without pretending certainty.

## 6. Trust language

- Never use visual badges to imply verification unless backed by an authored data/status contract.
- Provider/source provenance is factual and separate from canonical SongChart identity.
- Same-name entities remain visibly disambiguated.
- External destinations say where users are going; SongChart must not visually imply hosted playback by default.
- Correction/review flows never imply immediate canonical mutation.

## 7. Content design

- Factual, concise, internationally readable.
- Sentence case for headings/actions unless a semantic label deliberately uses uppercase tracking.
- Avoid marketing superlatives and engagement bait.
- Long/mixed-script names wrap naturally; truncation must not remove essential identity on detail pages.
- Dates, durations and country/type metadata use locale-safe presentation rules when implementation reaches those surfaces.

## 8. Cross-page reuse rule

Before inventing a component or page anatomy, reuse in this order:
1. approved token;
2. approved component contract;
3. approved page pattern;
4. candidate page archetype in `PAGE_ARCHETYPES.md`;
5. propose a minimum new primitive with design review.

A screenshot, Figma frame or AI-generated image is evidence/reference only. It cannot override this contract, semantic tokens or an approved component/page decision.

## 9. Material-change boundary

A change is material and requires a Design Authority decision/evidence update when it alters global typography, palette, shell width/navigation, common component anatomy, focus/accessibility behavior, entity-detail information hierarchy, or shared state semantics.

Content-specific arrangement within an approved archetype can evolve without a global decision when it reuses tokens/components and does not change the shared anatomy.

# SongChart Next — design quality contract

This contract applies to every public page family unless a narrower approved pattern explicitly overrides it.

## Responsive

Reference evidence sizes:
- narrow: `390 × 844` CSS px;
- wide: `1440 × 1024` CSS px.

Rules:
- narrow layouts are fully functional, not cropped desktop screenshots;
- primary content remains first in DOM/reading order;
- 2-column entity layouts stack into one readable column;
- long titles wrap naturally without overlapping actions or artwork;
- search/actions may wrap or stack, but labels and target sizes remain usable;
- document pages use reading-width constraints rather than full `72rem` line length;
- no essential content depends on hover;
- horizontal overflow is treated as a defect unless an approved dense-data pattern explicitly owns it.

## Accessibility

Baseline requirements:
- semantic page landmarks and one main content target;
- visible skip link and visible focus treatment;
- keyboard-operable navigation/forms/actions;
- minimum 44px pointer target for primary interactive controls where layout permits;
- accessible labels independent of placeholders;
- semantic `dl`, lists, headings, form errors and alerts where appropriate;
- color never carries status meaning alone;
- text/background and interactive contrast meet applicable WCAG AA intent;
- reduced-motion users receive no essential information through animation;
- artwork/missing-artwork behavior has deliberate alt/decorative semantics;
- loading, empty and error states are screen-reader understandable.

## Interaction states

Every reusable interactive component must account for:
- default;
- hover when pointer exists;
- focus-visible;
- active/pressed when meaningful;
- disabled only when truly unavailable and with enough contextual explanation;
- loading/submitting when asynchronous;
- validation/error when user input can fail.

Do not disable a control solely to hide an unmet requirement when explanatory validation is more useful.

## Content and internationalization

- UI structure is translatable even though multi-language UI is not MVP-mandatory.
- Unicode and mixed-script names are first-class.
- Do not normalize display names into ASCII-only presentation.
- Detail-page titles are not silently truncated.
- Entity type + disambiguation remain visible where names collide.
- Dates/numbers/durations are rendered from typed values with locale-safe presentation when implemented.
- Unknown, not-applicable and unavailable are distinct concepts when domain semantics require the distinction.
- Copy is factual, concise, provenance-aware and non-promotional.

## SEO/public document readiness

When a page is activated publicly, its implementation must separately address:
- unique document title;
- canonical URL/redirect rules;
- meaningful meta description where appropriate;
- semantic heading hierarchy;
- index/noindex decision;
- share metadata only from real page data;
- structured data only when it accurately represents the canonical domain object.

This contract does not itself activate SEO capability or claim production readiness.

## State semantics

### Loading
No fabricated names, counts, ratings or verification values. Skeletons should approximate structure, not pretend to be data.

### Empty
Explain what is absent and what user can do next. An empty result is not an error.

### Error
Explain failure at the appropriate scope and whether retry is safe. Do not show stale/fabricated replacement results as if current.

### Offline/service unavailable
Prefer clear service-state language and recovery/navigation actions. Never blame the user for server/infrastructure failure.

### Permission/auth
Public visitors should not encounter account gates for approved public read journeys. Internal editorial authorization is separate product anatomy.

## Evidence gate

A page archetype is not approved from prose alone. Approval evidence requires:
1. deterministic fixture/revision;
2. narrow and wide render evidence;
3. keyboard/focus/accessibility notes;
4. representative loading/empty/error states when applicable;
5. review decision linked from `design/decisions/`;
6. exact source SHA for the implemented review surface.

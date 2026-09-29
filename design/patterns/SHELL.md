# Pattern — Application Shell (candidate)

## Purpose
Provide one responsive public shell for Home/Search/Entity pages without importing starter dashboard/navigation visual semantics.

## Narrow
Top row: SongChart wordmark/text identity, compact search entry, overflow/menu only when required. Main content uses one column and 16px-equivalent gutters. No persistent side navigation.

## Wide
Header keeps identity + primary search visually dominant. Content max width follows semantic token. Secondary navigation/actions stay lower hierarchy than search/entity content.

## Required states
Keyboard-visible focus, skip-to-content, responsive long labels, no-auth public navigation, loading-safe search entry, reduced-motion safe transitions.

## Deferred
Authenticated editorial navigation is a separate internal shell/pattern and must not leak into the public product by default.

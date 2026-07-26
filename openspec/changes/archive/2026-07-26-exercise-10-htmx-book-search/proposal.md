## Why

Book search currently reloads the whole page for every submitted filter change. A focused HTMX interaction can make title and minimum-rating filtering more responsive while preserving the existing server-rendered GET workflow.

## What Changes

- Add HTMX-powered updates for the existing book search form.
- Return only the search-result HTML fragment for HTMX GET requests.
- Keep full-page GET responses and the submit button as a progressive-enhancement fallback.
- Preserve the existing validated search rules, accessible markup, and responsive layout.

## Capabilities

### New Capabilities

- `htmx-book-search`: Defines the triggers, result target, fragment response, and non-HTMX fallback for dynamic book search.

### Modified Capabilities

- `basic-book-views`: Replace the earlier explicit HTMX deferral for book search while preserving every existing search rule and scenario.

## Impact

- Adds the `django-htmx` dependency and middleware integration.
- Updates the shared base template, search template, search view, and focused tests.
- Extracts existing result markup into a reusable partial template.
- Does not change models, migrations, authentication, or review workflows.

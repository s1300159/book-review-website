## Why

Exercise 6 established safe read-only book views, but it still constructs the
book-list and book-detail pages directly in Python and has no user-specific
temporary browsing state. Exercise 7 should introduce Django template
inheritance for those pages and a narrowly scoped session example without
changing the existing URL contract or beginning the later form and
authentication work.

## What Changes

- Add an app-namespaced shared `base.html` with reusable header, navigation,
  main-content, and footer structure.
- Render the existing book-list and book-detail views with child templates that
  extend the shared base while preserving their current paths, names, methods,
  data, empty states, 404 behavior, and newest-first review order.
- Record up to five recently viewed existing Book IDs in each browser session
  when a book-detail request succeeds, with most-recent-first ordering and no
  duplicates.
- Keep Book, Review, and configured User records in the database as the source
  of truth; treat session Book IDs only as temporary references.
- Keep search text and any later sorting, minimum-rating, and page selections
  in GET parameters rather than session storage.
- Add focused tests for template selection/inheritance, shared layout content,
  automatic escaping, and recent-book session behavior.
- Update project documentation during implementation to distinguish database,
  session, GET-parameter, and template-context responsibilities.

## Capabilities

### New Capabilities

- `recent-book-session`: Defines the bounded, per-session recently viewed Book
  ID history and the data that must not be placed in it.

### Modified Capabilities

- `basic-book-views`: Changes the existing book-list and book-detail response
  construction from direct Python-generated HTML to safe, shared-layout Django
  templates without changing their external URL or read-only behavior.

## Impact

- Expected implementation changes: `reviews/views.py`,
  `reviews/test_views.py`, `docs/exercise-2-specification.md`, and `AGENTS.md`.
- Expected new templates: `reviews/templates/reviews/base.html`,
  `reviews/templates/reviews/book_list.html`, and
  `reviews/templates/reviews/book_detail.html`.
- No model, migration, admin, URL, form, authentication, dependency, HTMX,
  static-file, review-persistence, rating sort/filter, or pagination change is
  planned.
- Django sessions, app-template discovery, and the required middleware are
  already enabled in `config/settings.py`, so no settings change is expected.

## Why

Exercise 5 established the Book and Review database models, but the project still has no public application URLs or request-handling behavior. Exercise 6 should add the smallest useful function-based view layer so users can reach the site, browse and search existing books, inspect one book and its reviews, see a placeholder for future review submission, and exercise a named redirect before templates and forms are introduced in later exercises.

## What Changes

- Add a `reviews` URL configuration with an application namespace and named routes for all six Exercise 6 interactions.
- Include the `reviews` URL configuration from the project URL configuration.
- Add GET-only function-based views for a minimal home page, book list, book detail, title search, review-submission placeholder, and book-list redirect.
- Reuse the existing Book and Review models for read-only list, search, detail, and review display behavior.
- Return HTTP 404 when a book-detail or review-placeholder URL identifies a book that does not exist.
- Keep responses deliberately minimal and independent of templates because template work belongs to Exercise 7.
- Keep the review page read-only and non-persistent because form handling, authentication enforcement, validation, and saving belong to Exercise 8 or later.
- Add focused URL and view tests for each callable, including search matching, 404 behavior, and redirect destination.
- Update the project specification during implementation with the callable, URL name and path, arguments, processing, and response contract.

## Capabilities

### New Capabilities

- `basic-book-views`: Defines the initial named URL surface and function-based, read-only HTTP behavior for home, book listing, book detail with reviews, title search, review placeholder, and redirect interactions.

### Modified Capabilities

None. The existing `book-review-data-model` capability is reused without changing its schema or constraints.

## Impact

- Expected implementation files: `reviews/views.py`, a new `reviews/urls.py`, `config/urls.py`, a focused test module under `reviews/`, and `docs/exercise-2-specification.md`.
- No model, migration, form, template, authentication, static-file, media, HTMX, or package changes are planned.
- Existing admin routing remains available.
- The final site description in the project documents remains the long-term target; this change adds only the Exercise 6 request/response foundation.

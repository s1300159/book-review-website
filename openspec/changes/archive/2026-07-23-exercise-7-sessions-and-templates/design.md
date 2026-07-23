## Context

The current `main` includes Exercise 6 through merged PR #4. The `reviews`
application has GET-only function views and stable names for home, list,
detail, search, the review placeholder, and a redirect. `book_list` and
`book_detail` currently build complete HTML responses with private helpers in
`reviews/views.py`; no template directory exists. Their tests assert semantic
content, escaping, 404/405 behavior, review ordering, and lack of Book or
Review writes.

The database already contains the durable domain entities Book and Review, and
Review references Django's configured User model. Django's default
database-backed session application, `SessionMiddleware`, authentication
middleware, app-template discovery, and standard template context processors
are already configured. This makes a small session and template change
possible without schema, package, URL, or settings changes.

The accepted `basic-book-views` specification deliberately describes the
pre-template Exercise 6 response construction. This change includes a delta
for that capability so the accepted specification can later be updated rather
than leaving contradictory current-state requirements.

## Goals / Non-Goals

**Goals:**

- Give the book-list and book-detail pages one reusable document layout.
- Preserve the existing callable signatures, URL names and paths, GET-only
  behavior, displayed data, empty states, 404 responses, and redirect contract.
- Store a small, low-sensitivity, per-browser history of recently viewed Book
  IDs in the session.
- Keep durable domain data, temporary session data, request controls, and
  template context clearly separated.
- Retain Django's automatic HTML escaping and focused regression coverage.

**Non-Goals:**

- Template conversion of `home`, `book_search`, `review_create`, or the
  redirect in this exercise.
- A visible recently viewed books component, recommendation logic, or a new
  route for session history.
- Review forms, POST handling, authentication requirements, login pages, or
  review persistence.
- Rating sorting/filtering, pagination, HTMX, cover-image presentation, CSS,
  review editing, or review deletion.
- Model, migration, admin, URL, settings, middleware, or dependency changes.

## Decisions

### Use app-namespaced templates and Django `render()`

Create `reviews/templates/reviews/base.html`, `book_list.html`, and
`book_detail.html`. The child templates extend `reviews/base.html` and fill a
page-title block and a main-content block. Keeping templates under the app
namespace avoids collisions with templates from future applications and works
with the existing `APP_DIRS = True` setting.

`book_list` and `book_detail` will call Django's `render()` with explicit
context dictionaries. The existing direct-response helpers remain for the
Exercise 6 views that still need them, including search. Converting every view
now was considered, but it would enlarge Exercise 7 without improving the two
pages explicitly required to demonstrate inheritance.

### Keep presentation logic out of templates

`book_list` passes the Book queryset as `books`. `book_detail` fetches the Book
or returns 404, obtains its newest-first Review queryset with related users,
computes the existing derived average rating, and passes `book`, `reviews`, and
`average_rating`. Templates select between supplied values and documented
empty-state text but do not query models, calculate averages, or enforce
permissions.

`base.html` owns the document shell, shared site heading, navigation using
named URLs, `<main>` content region, and footer. The child templates own only
page-specific book and review markup. Django autoescaping remains enabled; no
database or query value is marked safe.

### Store only a bounded list of Book IDs in the session

Use one descriptive session key, `recently_viewed_book_ids`, whose value is a
JSON-serializable list of integer primary keys. After `book_detail` has found
an existing Book, update the list by removing that ID if present, prepending
it, and truncating to five entries. A repeat view therefore moves the Book to
the front without duplication. A missing Book returns 404 before any session
mutation.

Treat a missing key as an empty list. Treat any stored non-list value as an
empty list, and discard non-integer values, booleans, and duplicates from a
stored list before recording the current ID. This defensive normalization
prevents stale or malformed framework state from turning a valid detail GET
into HTTP 500 while preserving the integer-only session contract.

Only IDs are stored because Book titles and descriptions can change and the
database remains authoritative. Stale IDs caused by later Book deletion are
harmless references and may age out naturally; if a later feature dereferences
the history, it must ignore missing Books. Storing complete Book objects,
review text, ratings, usernames, authentication data, or other important data
was rejected because session state is temporary and should remain small.

The default Django backend stores session content server-side in the standard
session table and sends only a session identifier cookie. These rows are
temporary framework state, not a replacement domain store, and require no
`reviews` migration.

### Keep request controls in GET parameters

The existing trimmed search term remains `q` in the request query string. Any
future sort, minimum-rating, and page controls remain GET parameters as
described by the project direction. Exercise 7 neither implements those
deferred controls nor copies `q`, `sort`, `min_rating`, or `page` into the
session. This keeps URLs shareable and prevents old browsing choices from
silently affecting later requests.

### Preserve the external view contract

No route, URL name, function signature, allowed method, response status, or
database query meaning changes. `@require_GET`, `get_object_or_404`, the
existing average calculation, and newest-first review ordering remain.
Semantic tests should continue to assert behavior rather than exact full-page
HTML so the templates can evolve without breaking the public contract.

## Data Placement

| Location | Information | Lifetime and authority |
| --- | --- | --- |
| Database domain models | Book title, cover reference, description; Review text, rating, timestamp, Book/User relationships; configured User data | Durable source of truth |
| Django session | `recently_viewed_book_ids`: at most five unique integer Book IDs, most recent first | Temporary per-browser reference state |
| GET parameters | Current `q`; future `sort`, `min_rating`, and `page` controls when separately implemented | Current request/shareable URL only |
| Template context | Current Books, selected Book, ordered Reviews, derived average rating | One rendered response only |

## Test Strategy

- Confirm `book_list` renders `reviews/book_list.html` and
  `reviews/base.html`, retains registered-title and no-books behavior, and
  contains the shared header, named navigation, main region, and footer.
- Confirm `book_detail` renders `reviews/book_detail.html` and the same base,
  while retaining description, derived average, review isolation,
  newest-first order, no-review state, review link, and missing-Book 404.
- Preserve hostile-value tests to prove template autoescaping for Book,
  Review, username, and description content.
- Visit details in sequence and assert the session contains unique integer IDs
  in most-recent-first order, revisits move an ID to the front, and a sixth
  distinct Book evicts the oldest.
- Seed non-list and mixed-type session values and assert a valid detail request
  normalizes them without HTTP 500.
- Confirm separate test clients receive isolated histories and a missing-Book
  404 does not change the session.
- Confirm search query values and representative deferred control names are
  not copied to the recent-book session, and Book/Review row counts do not
  change through Exercise 7 GET requests.
- Run the full pytest suite, Django system checks, Black, Pylint, migration
  dry-run, and strict OpenSpec validation during implementation.

## Risks / Trade-offs

- [The accepted Exercise 6 spec says templates are not required] -> Modify the
  affected `basic-book-views` requirements in this change and archive the delta
  only after implementation is verified.
- [Session writes make detail GET requests no longer completely state-free] ->
  Limit the side effect to low-sensitivity temporary IDs and keep all Book and
  Review domain data read-only.
- [A database-backed session creates framework rows] -> Document them as
  temporary session state and make no domain-model or migration change.
- [Exact-markup tests can make templates fragile] -> Assert template names,
  semantic landmarks, navigation targets, ordering, escaping, and states
  rather than a complete HTML string.
- [Recently viewed history has no Exercise 7 UI] -> Test the explicit session
  contract directly; defer visible history until a future task requires it.

## Migration Plan

1. Add the three templates and switch only `book_list` and `book_detail` to
   `render()`.
2. Add the bounded session update after successful Book lookup.
3. Update tests and project documentation, then run all validation gates.
4. No database migration or data backfill is required. Rollback consists of
   restoring direct response construction; existing temporary session keys can
   safely expire or be ignored.

## Open Questions

- No blocking implementation question remains. The task description does not
  require the recently viewed IDs to be displayed, so this design intentionally
  limits Exercise 7 to storage and testable session behavior. A visible recent
  books component would require a later explicit requirement and stale-ID
  lookup behavior.
- The accepted `book-review-data-model` Purpose still contains archive-created
  TBD text. Its requirements match the code and this unrelated wording issue is
  not changed by Exercise 7.

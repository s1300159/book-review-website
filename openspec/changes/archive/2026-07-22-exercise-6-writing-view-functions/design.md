## Background

The project is on `feature/database-schema` at the archived Exercise 5 change. `Book` and `Review` are implemented in `reviews/models.py`, migration `0001_initial.py` represents them, model tests pass in the recorded Exercise 5 work, and the accepted `book-review-data-model` specification matches the implementation. Public application routing is not yet present: `config/urls.py` contains only the admin route and `reviews/views.py` is still generated scaffolding.

At proposal time, `AGENTS.md` still said that Book and Review were
unimplemented. That statement was stale relative to the code, migration,
tests, Git history, `docs/exercise-2-specification.md`, and the archived
Exercise 5 OpenSpec change. It was corrected as an Exercise 6 prerequisite;
the implemented models and accepted data-model specification remain the source
of truth and this change does not edit the models.

The project documents describe the final user experience, including a main book list, templates, search input, rating sorting and filtering, pagination, and review submission. Exercise 6 establishes only the initial HTTP layer. Later exercises can refine presentation and input handling without changing the named URL contract proposed here.

## Goals

- Define a small, explicit public URL surface with stable names.
- Use function-based, GET-only views.
- Read existing Book and Review data through the Django ORM.
- Give missing book identifiers normal Django 404 behavior.
- Make every Exercise 6 view independently testable.
- Record a complete callable and response contract for implementation and later exercises.

## Non-goals

- Adding or changing models, constraints, migrations, admin behavior, or dependencies.
- Creating templates or visual design.
- Accepting POST data, defining a Django form, validating review input, or saving reviews.
- Requiring login for the placeholder page or adding authentication pages.
- Implementing rating sort/filter controls, pagination, recommendations, HTMX, review editing, or review deletion.
- Finalizing display formatting such as average-rating rounding or cover-image rendering.

## URL and Callable Contract

All routes are included at the project root from `reviews.urls`, use `app_name = "reviews"`, and therefore reverse through the `reviews:` namespace. All callables accept Django's `HttpRequest` as `request`; routes with `<int:book_id>` also receive `book_id` as an integer.

| Callable | Method and path | URL name | Additional argument/input | Processing | Return value |
| --- | --- | --- | --- | --- | --- |
| `home(request)` | `GET /` | `reviews:home` | None | Build a minimal site introduction with navigation to the named book-list and search routes. | `HttpResponse`, status 200, minimal text/HTML. |
| `book_list(request)` | `GET /books/` | `reviews:book_list` | None | Read all registered Book rows and expose at least each title in a minimal response. Do not add rating sorting, filtering, or pagination. | `HttpResponse`, status 200, including the available book titles or an explicit empty-state message. |
| `book_detail(request, book_id)` | `GET /books/<int:book_id>/` | `reviews:book_detail` | Integer `book_id` from the path. | Fetch the Book or raise 404; read its related reviews and show the book title, description, derived average rating, and each review's author, text, and rating. Reviews are ordered newest first using `created_at` and primary key as a tie-breaker. | `HttpResponse`, status 200 for an existing book; Django 404 response otherwise. |
| `book_search(request)` | `GET /books/search/` | `reviews:book_search` | Optional query string `q`. | Trim `q`; for a non-empty value, find books by case-insensitive partial title match with `title__icontains`; for a missing, empty, or whitespace-only value, return no matches and a clear empty-query message. | `HttpResponse`, status 200, including the query and matching titles or a no-results/empty-query message. |
| `review_create(request, book_id)` | `GET /books/<int:book_id>/review/` | `reviews:review_create` | Integer `book_id` from the path. | Fetch the Book or raise 404, then show a placeholder naming the book. Do not inspect submitted input, require authentication, construct a form, or create a Review. | `HttpResponse`, status 200 for an existing book; Django 404 response otherwise. |
| `book_list_redirect(request)` | `GET /books-redirect/` | `reviews:book_list_redirect` | None | Resolve the named `reviews:book_list` route and redirect to it. | `HttpResponseRedirect`, status 302, with `Location: /books/`. |

Each view is GET-only. A non-GET request returns status 405 and does not read or write application data.

## Request and Data Flow

```text
Browser GET
    |
    v
config.urls -> reviews.urls (named route)
    |
    v
reviews.views function
    |-- home / redirect: no model query
    |-- list / search: Book queryset
    `-- detail / placeholder: get Book or 404
              |
              `-- detail only: related Review queryset
    |
    v
minimal HttpResponse / 302 redirect / 404 / 405
```

## Response Construction

Exercise 7 owns templates, so Exercise 6 responses remain deliberately small and may be built with `HttpResponse` plus Django HTML escaping helpers. Dynamic titles, descriptions, usernames, and review text must be escaped before inclusion in HTML. This avoids introducing templates while preserving a safe boundary for database content.

The output contract is semantic rather than a final page layout. Tests should assert status, relevant content, and redirect behavior, not exact whole-page markup. Later template work can preserve the URLs and behavior while replacing the response construction.

## ORM Decisions

- `book_list` uses the existing Book manager and performs no rating sorting or filtering.
- `book_search` uses `Book.objects.filter(title__icontains=query)` only when the trimmed query is non-empty.
- `book_detail` uses `get_object_or_404(Book, pk=book_id)` and the existing `book.reviews` reverse relation. `select_related("user")` may be used to avoid one user query per review.
- `book_detail` reuses `book.average_rating`; it does not add a stored field or define final display rounding.
- `review_create` fetches the Book only. It never calls `Review.objects.create()` or other write APIs.

## URL Ordering

Place the fixed `/books/search/` pattern before `/books/<int:book_id>/` for readability and future safety. The integer converter already prevents `search` from being treated as a book identifier, but keeping fixed routes first makes the URL table easier to extend. Put `/books/<int:book_id>/review/` alongside the detail route.

## Test Plan

Use pytest and Django's test client in a focused view-test module under `reviews/`.

- Verify every named route reverses and resolves to the expected function.
- Verify `home` returns 200 and contains the minimal site identity/navigation.
- Verify `book_list` returns 200, includes registered book titles, and provides an empty state with no books.
- Verify `book_detail` returns 200 with the selected book, description, average rating, and only its reviews; verify a missing ID returns 404 and newest-first review order is observable.
- Verify `book_search` performs case-insensitive partial matching, excludes non-matches, and handles missing, empty, whitespace-only, and no-match queries with status 200.
- Verify `review_create` returns 200 for an existing book, names the book, creates no Review, and returns 404 for a missing book.
- Verify `book_list_redirect` returns 302 and its destination equals `reverse("reviews:book_list")`.
- Verify non-GET requests receive 405 for the GET-only view surface, with representative coverage sufficient to establish the decorator/guard behavior.
- Run the full existing model and view test suite plus Django system checks.

## Project Documentation Plan

During implementation, add an Exercise 6 section to `docs/exercise-2-specification.md` containing the URL and callable contract table above. Clearly label the responses and review page as pre-template/pre-form behavior so the long-term user flow is not mistaken for already completed functionality. Keep `docs/exercise-1-project-topic.txt` unchanged because its high-level scope remains accurate.

After implementation and review, sync the accepted capability into `openspec/specs/basic-book-views/spec.md` through the normal OpenSpec archive/sync flow.

## Risks / Trade-offs

- [Minimal `HttpResponse` output is not the final user interface] -> Treat output markup as temporary and test semantic content so Exercise 7 can replace it without route churn.
- [The current project documents describe later features as part of the flow] -> Mark the Exercise 6 contract as an incremental implementation state and retain later features as planned work.
- [Direct HTML construction can mishandle model text] -> Require Django escaping helpers for every dynamic value.
- [An empty `icontains` query would match every book] -> Handle empty or whitespace-only `q` explicitly and return no matches.
- [The `review_create` name could imply persistence] -> Document and test that it is a GET-only placeholder that performs no write until form work is authorized.

## Assumptions and Resolved Decisions

1. The app uses a `reviews` URL namespace to avoid future naming collisions.
2. Exercise 6 uses the paths and names in the contract table; later work should reverse names instead of hard-coding paths.
3. Home is a minimal landing page rather than a duplicate book-list implementation. The existing final-state statement that the main page shows books remains a later presentation decision.
4. Missing `book_id` values return 404 in both views that accept a book identifier.
5. Search is case-insensitive partial matching after trimming the query, and an empty query returns no matches rather than all books.
6. Detail reviews are newest first; exact page styling and date formatting are deferred.
7. The review placeholder is public and read-only. Login enforcement begins when real submission behavior is designed.
8. The simple redirect targets the named book-list route and uses Django's normal temporary redirect status 302.
9. No migration command is required because this change does not alter database state.

## Unresolved Items Outside This Change

- The Purpose section in `openspec/specs/book-review-data-model/spec.md` still
  contains its archive-generated TBD text. Its requirements match the Exercise
  5 implementation, and correcting that descriptive text is unrelated to the
  Exercise 6 view layer, so this change records but does not modify it.

## 1. Add the Named URL Surface

- [x] 1.1 Create `reviews/urls.py` with `app_name = "reviews"` and the six paths and names approved in the design contract.
- [x] 1.2 Include `reviews.urls` from `config/urls.py` at the project root while preserving the existing admin route.
- [x] 1.3 Verify every route reverses and resolves with the required `book_id` argument where applicable.

## 2. Implement the GET-only Function Views

- [x] 2.1 Implement the minimal `home` response with named navigation to the list and search routes.
- [x] 2.2 Implement `book_list` using the Book model, including registered titles and a no-books state without sorting, filtering, or pagination.
- [x] 2.3 Implement `book_detail` using `get_object_or_404`, the existing reverse Review relationship, newest-first review ordering, and existing average-rating behavior.
- [x] 2.4 Implement `book_search` with trimmed `q`, case-insensitive partial-title matching, and explicit empty-query and no-match states.
- [x] 2.5 Implement `review_create` as an existing-book-checked placeholder that performs no Review write and requires no form or login behavior.
- [x] 2.6 Implement `book_list_redirect` as a 302 redirect resolved through the named book-list URL.
- [x] 2.7 Restrict the six callables to GET and safely escape all model-provided values in minimal HTML responses.

## 3. Add Focused URL and View Tests

- [x] 3.1 Add route tests for each namespaced URL, callable resolution, and required path arguments.
- [x] 3.2 Add home tests for HTTP 200 and minimal site identity/navigation content.
- [x] 3.3 Add book-list tests for registered titles and the empty state.
- [x] 3.4 Add book-detail tests for book fields, derived average rating, related-review content and order, no-review state, review isolation, and missing-book 404.
- [x] 3.5 Add search tests for partial and case-insensitive matching, exclusion of non-matches, no matches, and missing/empty/whitespace-only queries.
- [x] 3.6 Add review-placeholder tests for existing-book content, no Review creation or change, and missing-book 404.
- [x] 3.7 Add redirect tests for HTTP 302 and the destination produced by `reverse("reviews:book_list")`.
- [x] 3.8 Add representative tests that non-GET requests return 405 and leave Book and Review data unchanged.

## 4. Document and Verify

- [x] 4.1 Add an Exercise 6 URL and callable contract to `docs/exercise-2-specification.md`, including paths, names, methods, arguments/input, processing, return values, 404 behavior, and deferred template/form features.
- [x] 4.2 Run `uv run python manage.py check`.
- [x] 4.3 Run `uv run pytest` and confirm the new view tests and existing Exercise 5 model tests pass.
- [x] 4.4 Run `uv run black --check .` and `uv run pylint reviews config`.
- [x] 4.5 Review the final diff and migration state to confirm no model, migration, form, template, authentication, HTMX, dependency, rating sort/filter, pagination, review edit, or review delete change was introduced.
- [x] 4.6 Run `uv run python manage.py makemigrations --check --dry-run` and confirm no model changes are detected.
- [x] 4.7 Run strict OpenSpec validation for this change with the available CLI.

## 1. Add the Shared Template Structure

- [x] 1.1 Create `reviews/templates/reviews/base.html` with reusable document metadata, header, named-URL navigation, main-content block, and footer.
- [x] 1.2 Create `reviews/templates/reviews/book_list.html` extending the base and preserving registered-title links and the no-books state.
- [x] 1.3 Create `reviews/templates/reviews/book_detail.html` extending the base and preserving book fields, derived average rating, newest-first reviews, empty states, and the named review-placeholder link.

## 2. Adopt Templates and Bounded Session State

- [x] 2.1 Change only `book_list` and `book_detail` to use Django `render()` with explicit, presentation-ready context while preserving the existing external view contract.
- [x] 2.2 Update successful `book_detail` requests to normalize malformed existing state and maintain `recently_viewed_book_ids` as unique integer IDs in most-recent-first order with a maximum of five.
- [x] 2.3 Ensure missing Books do not mutate the session and no Book, Review, User content or GET control value is placed in Exercise 7 session state.
- [x] 2.4 Retain direct safe response helpers for the still-unconverted Exercise 6 views without adding forms, login enforcement, sort/filter, pagination, or HTMX behavior.

## 3. Add Template and Session Tests

- [x] 3.1 Test the selected child and base templates, shared layout landmarks, named navigation, registered-title links, and book-list empty state.
- [x] 3.2 Test book-detail template content, average rating, related-review isolation and newest-first order, empty states, review-placeholder link, and missing-Book 404.
- [x] 3.3 Preserve and adapt hostile-value coverage to verify Django template autoescaping for Book, Review, and username content.
- [x] 3.4 Test first visits, recent-first ordering, revisits without duplicates, five-ID truncation, malformed-state normalization, integer-only storage, missing-Book non-mutation, and separate-client isolation.
- [x] 3.5 Test that Exercise 7 GET requests leave Book and Review rows unchanged and do not copy `q`, `sort`, `min_rating`, or `page` into session state.
- [x] 3.6 Run the full existing model and Exercise 6 regression suite alongside the new Exercise 7 tests.

## 4. Document and Verify

- [x] 4.1 Update `docs/exercise-2-specification.md` with the shared-template contract and the database/session/GET/template-context data placement decisions.
- [x] 4.2 Update `AGENTS.md` current-state notes after templates and Exercise 7 session behavior exist, without claiming Exercise 8 features.
- [x] 4.3 Run `uv run python manage.py check` and `uv run pytest`.
- [x] 4.4 Run `uv run black --check .`, `uv run pylint reviews config`, and `uv run python manage.py makemigrations --check --dry-run`.
- [x] 4.5 Review the final diff to confirm no URL, model, migration, admin, form, authentication, dependency, HTMX, sort/filter, pagination, review-edit, or review-delete change was introduced.
- [x] 4.6 Run strict OpenSpec validation for `exercise-7-sessions-and-templates` and leave the change active until implementation and review are complete.

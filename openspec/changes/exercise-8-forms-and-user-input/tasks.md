## 1. Forms

- [ ] 1.1 Create `reviews/forms.py` without changing `reviews/models.py`.
- [ ] 1.2 Implement `BookSearchForm` with optional trimmed `q` and optional typed `min_rating` choices from 1 through 5.
- [ ] 1.3 Implement `ReviewForm` exposing only `text` and `rating`, with 1-through-5 choices and rejection of empty or whitespace-only text.
- [ ] 1.4 Add trusted `user`/`book` initialization, duplicate non-field validation, and current-instance exclusion to `ReviewForm`.

## 2. Views and Persistence

- [ ] 2.1 Update the GET search view to bind `BookSearchForm`, display all Books when both controls are empty, combine partial-title and average-rating filters, exclude unrated Books for `min_rating`, and avoid storing controls in the session.
- [ ] 2.2 Replace the read-only `review_create` placeholder with login-required GET/POST form processing, trusted ownership assignment, messages, and named POST-Redirect-GET.
- [ ] 2.3 Add login-required `review_edit` GET/POST processing with Review lookup, exact-author enforcement, HTTP 403 for authenticated non-authors, immutable User/Book, messages, and named redirect.
- [ ] 2.4 Save Reviews inside a safe atomic boundary and translate a possible duplicate `IntegrityError` into a non-field form error with HTTP 200.
- [ ] 2.5 Prepare Book-detail link context in the view while preserving newest-first Reviews, average rating, escaping, and recently viewed Book session behavior.

## 3. URLs, Authentication, and Templates

- [ ] 3.1 Add the named `reviews:review_edit` URL and retain the existing named Review-create URL.
- [ ] 3.2 Include Django's standard authentication URLs at the selected project prefix.
- [ ] 3.3 Configure `LOGIN_URL` and `LOGIN_REDIRECT_URL` with valid named URLs.
- [ ] 3.4 Add `registration/login.html` with the authentication form, CSRF token, field/non-field errors, and hidden `next` preservation.
- [ ] 3.5 Add a shared Django messages display region to `reviews/base.html`.
- [ ] 3.6 Add shared `reviews/review_form.html` create/edit rendering with CSRF, field errors, and non-field errors.
- [ ] 3.7 Update `reviews/book_detail.html` to show create or edit links from view-provided state without granting permissions in the template.
- [ ] 3.8 Render the search page and `BookSearchForm` through an app-namespaced template that preserves the existing shared inheritance and prompts for changed conditions after a valid zero-result search.

## 4. Automated Tests

- [ ] 4.1 Add form unit tests for search trimming/boundaries and Review public fields, text/rating validation, duplicate errors, and instance-aware editing.
- [ ] 4.2 Add Review-create GET/POST tests for authentication redirects, trusted ownership, valid save, invalid HTTP 200, success messages, and named redirects.
- [ ] 4.3 Add Review-edit tests for initial data, valid/invalid updates, immutable ownership, author access, authenticated non-author HTTP 403, and missing Review 404.
- [ ] 4.4 Add focused safe-`IntegrityError` handling tests for the duplicate race path.
- [ ] 4.5 Add CSRF-enforced tests for Review and login form POST behavior.
- [ ] 4.6 Add search tests for the all-Books empty-control default, `q`, `min_rating`, combined criteria, invalid values, average boundaries, exclusion of unrated Books, and valid zero-result messaging.
- [ ] 4.7 Run and extend regression tests for URL methods, Book detail, Review ordering, average rating, escaping, empty states, messages, and recently viewed sessions.

## 5. Documentation

- [ ] 5.1 Update the project specification and README-facing behavior to describe validated search, authenticated Review create/edit, permissions, authentication URLs, and excluded features.
- [ ] 5.2 Update `AGENTS.md` current-state notes after implementation without claiming sorting, pagination, HTMX, registration, deletion, model, or migration work.

## 6. Verification and Review

- [ ] 6.1 Run `uv run python manage.py check`.
- [ ] 6.2 Run the full `uv run pytest` suite.
- [ ] 6.3 Run `uv run black --check .`.
- [ ] 6.4 Run `uv run pylint reviews config` and separate existing warnings from newly introduced warnings.
- [ ] 6.5 Run `uv run python manage.py makemigrations --check --dry-run` and confirm no model change or migration is present.
- [ ] 6.6 Run strict OpenSpec validation for `exercise-8-forms-and-user-input`.
- [ ] 6.7 Perform a focused code review and final diff review for security, permissions, validation, regressions, and out-of-scope changes.

## 7. Git, Pull Request, and Approved Finalization

- [ ] 7.1 Confirm `git diff --check`, stage only Issue #7 files, and create a short English commit referencing Issue #7.
- [ ] 7.2 Push `feature/forms-and-user-input` without pushing directly to `main`.
- [ ] 7.3 Open a Pull Request for Issue #7 with scope, verification results, and `Closes #7`.
- [ ] 7.4 Confirm required Pull Request conditions, checks, review feedback, and merge readiness.
- [ ] 7.5 After explicit user approval, merge the Pull Request into `main`.
- [ ] 7.6 After explicit user approval and completed implementation/review, archive the OpenSpec change.
- [ ] 7.7 Synchronize local `main` and, after explicit approval, clean up the feature branch.

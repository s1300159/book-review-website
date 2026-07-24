## Context

Issue #7 requests the first validated user-input workflows. The current
application has GET-only function views, a manual `q` search form, a read-only
`review_create` placeholder, app-namespaced book templates, and a session
history of at most five recently viewed Book IDs. `Review` already validates
ratings from 1 through 5 and has both application-level duplicate validation
and database constraints for one Review per User and Book.

Django authentication, sessions, messages, CSRF middleware, app-template
discovery, and their context processors are already enabled. The change can
therefore use framework facilities without adding packages or changing the
data model. The accepted `basic-book-views` specification still says the
public views are GET-only, the Review route is a placeholder, and form
processing is forbidden; its delta must explicitly replace those statements.

## Goals / Non-Goals

**Goals:**

- Validate search controls with a Django `Form` while keeping them shareable
  GET parameters.
- Add a narrow `ModelForm` that can create and edit a Review without accepting
  ownership fields from the browser.
- Enforce authentication, Review ownership, duplicate prevention, CSRF, and
  safe failure behavior.
- Use POST-Redirect-GET and Django messages after successful writes.
- Keep templates responsible for presentation only and show all useful form
  errors.
- Preserve current Book, Review display, escaping, and recent-book session
  behavior.

**Non-Goals:**

- Review deletion or user registration.
- Rating sorting, pagination, HTMX, or advanced CSS.
- Model, database constraint, migration, dependency, or admin changes.
- Search-condition persistence in a session.
- Broad view refactoring unrelated to the Issue #7 workflows.

## Decisions

### Use a bound GET `BookSearchForm`

Create `BookSearchForm(forms.Form)` with:

- `q`: `CharField(required=False)` with normal Django whitespace trimming.
- `min_rating`: an optional `TypedChoiceField` coercing values to `int`, with
  choices 1 through 5 and an empty choice. An `IntegerField` with minimum 1
  and maximum 5 would also validate correctly, but a typed choice makes the
  allowed UI values and cleaned Python type explicit.

The search view binds the form to `request.GET` when search parameters are
present. Invalid values render HTTP 200 with field errors and no result query.
Valid controls are combined:

- a non-empty `q` applies `title__icontains`;
- a supplied `min_rating` annotates each Book with
  `Avg("reviews__rating")` and applies `average_rating__gte`;
- `min_rating` alone is a valid search across all reviewed Books;
- because a Book without Reviews has a null average, the threshold filter
  excludes it; an explicit non-null filter may be added for clarity;
- if both controls are absent or empty, the page displays every Book,
  preserving the existing default listing behavior;
- if valid supplied criteria return zero Books, the template displays a
  message prompting the user to change the conditions.

The rendered form preserves valid submitted values through bound-form
rendering. Neither `q` nor `min_rating` is copied into the session. Sorting,
pagination, and HTMX remain absent. A new app-namespaced search template may
replace the current direct response so the shared layout and standard form
error rendering are reused.

### Use a context-aware `ReviewForm`

Create `ReviewForm(forms.ModelForm)` with `Meta.fields = ("text", "rating")`.
The rating field is rendered as a typed 1-through-5 choice. `text` is cleaned
with explicit stripping and rejects a value that becomes empty; the cleaned
trimmed value is stored.

The constructor requires keyword-only `user` and `book` context supplied by
the view. These values are stored on the form and never taken from form data.
`clean()` queries Reviews for the same User and Book. When the form has a
persisted instance, the query excludes that instance's primary key. A
duplicate adds a non-field error so the shared template can display it above
the fields.

Before saving, the view sets `review.user` and `review.book` from trusted
context. On edit, the trusted Book is the existing instance's Book and the
trusted User is the existing instance's User/current authorized requester;
posted fields cannot change either relationship.

The pre-save query improves user feedback but cannot eliminate a concurrent
race. Save inside an inner `transaction.atomic()` block and catch
`IntegrityError` outside that block so the transaction remains usable. Add a
non-field duplicate error and render the bound form with HTTP 200 instead of
exposing a server error. The existing database `UniqueConstraint` and rating
check constraint remain unchanged as final defenses.

### Replace the Review placeholder with create GET/POST

`review_create(request, book_id)` uses `login_required` and permits only GET
and POST. It obtains the Book with `get_object_or_404(Book, pk=book_id)` and
constructs `ReviewForm(user=request.user, book=book)`.

- GET renders the shared `reviews/review_form.html` with an unbound form.
- POST binds `request.POST`, validates it, assigns only the server-selected
  User and Book, and saves.
- A successful save adds `messages.success` and redirects using
  `reviews:book_detail` and the Book primary key.
- Validation or handled integrity failure renders the same template and bound
  form with HTTP 200.
- A missing Book returns 404 after authentication.
- An unauthenticated request is redirected to the named login URL with the
  full requested path in `next`.

GET followed by POST redirect prevents refresh from resubmitting the Review.
All unsupported methods return HTTP 405 and perform no Review write.

### Add author-only Review edit GET/POST

Add `review_edit(request, review_id)` and the named
`reviews:review_edit` route. The view uses `login_required`, permits GET and
POST only, and obtains the Review by ID with its Book and User relationships.
A missing Review returns 404. If an authenticated requester is not the Review
author, raise `PermissionDenied` to return HTTP 403 before binding or saving a
form.

For an authorized author, initialize `ReviewForm` with the existing instance,
`user=request.user`, and `book=review.book`.

- GET displays the existing text and rating.
- POST updates only those two public fields.
- Success adds a message and redirects by `reviews:book_detail` for the
  unchanged Book.
- Invalid input or a safely handled integrity error returns HTTP 200 with the
  bound form and errors.

This design does not add edit/delete permissions for staff or superusers.
Only exact authorship grants edit access because Issue #7 says the submitter
alone may edit.

### Keep authentication as a separate interface capability

Include Django's standard authentication URL configuration at an
`accounts/` prefix, producing the named `login` route and the framework's
other standard auth endpoints. Add `registration/login.html` and set
`LOGIN_URL = "login"` and `LOGIN_REDIRECT_URL = "reviews:book_list"` (or
equivalent valid named routes).

The login template uses Django's supplied authentication form, includes a CSRF
token, displays field and non-field errors, and includes a hidden `next` input
when `next` is present. `LoginView` validates the redirect target and returns
the user to the requested Review page after successful authentication.
Registration is not added.

### Render feedback and permission-aware links through shared templates

`reviews/review_form.html` is shared by create and edit. The view supplies a
mode-appropriate heading, Book, form, and submit label; the template displays
non-field errors, each field's errors, and a CSRF token. It extends
`reviews/base.html` so automatic escaping and the current document shell
remain active.

Add a messages region to `base.html` that iterates the Django `messages`
context and renders message text and tags without marking content safe.

The Book detail view computes the current user's relationship to the Book's
Reviews and passes presentation-ready context:

- an authenticated author sees an edit link for their Review;
- an authenticated user with no Review for the Book sees a create link;
- an unauthenticated visitor sees a login-oriented create link whose protected
  destination will preserve `next`.

The template does not query Reviews or decide ownership. Other users' Reviews
remain visible as before, but their edit links are never shown.

### Preserve the established read and session contracts

Home, Book list, Book detail, Book search, and the named list redirect remain
read-only. The display routes remain GET-only; Review create and edit are the
only views in this change that accept POST. Unsupported methods return 405.

`book_detail` continues to:

- return 404 before recording a missing Book;
- record at most five unique integer IDs under
  `recently_viewed_book_ids`, newest first;
- show the derived average and related Reviews newest first;
- escape model and request content through Django templates.

Search controls are never stored in that session key or another search
session key.

## URL and Method Contract

| Interaction | Named URL | Allowed methods | Authentication / ownership |
| --- | --- | --- | --- |
| Existing read views | Existing `reviews:*` names | GET | Existing public behavior |
| Book search | `reviews:book_search` | GET | Public, validated GET form |
| Review create | `reviews:review_create` | GET, POST | Login required |
| Review edit | `reviews:review_edit` | GET, POST | Login and exact authorship required |
| Login | `login` | GET, POST | Django standard authentication |

Unsupported application methods return HTTP 405. Authentication redirects
happen before a protected Review workflow is rendered. An authenticated
non-author reaches the edit view but receives HTTP 403.

## Test Strategy

- Unit-test `BookSearchForm` for trimming, optional values, coercion, invalid
  strings, and the 1/5 boundaries and out-of-range values.
- Unit-test `ReviewForm` public fields, rating choices, empty and
  whitespace-only text, valid/invalid ratings, duplicate non-field errors, and
  editing the current instance without a false duplicate.
- Test unauthenticated create/edit redirects and `next` preservation.
- Test valid create POST, trusted User/Book assignment, success message,
  named redirect, and one-write POST-Redirect-GET behavior.
- Test invalid create POST returns HTTP 200 with errors and no Review write;
  simulate an integrity race and confirm safe form-level handling.
- Test edit initial values, valid updates, immutable User/Book, author-only
  access, non-author HTTP 403, missing Review 404, and invalid update behavior.
- Use CSRF-enforcing clients to verify Review and login POSTs reject missing
  tokens and accept valid tokens.
- Test title/minimum-rating filtering separately and together, including
  Books at boundaries, Books below the threshold, unrated Books, invalid
  thresholds, all-Books default behavior with no criteria, and the
  condition-change message for valid zero-result searches.
- Preserve regression coverage for named URLs, unsupported methods, Book
  detail, average rating, newest-first Reviews, escaping, empty states, and
  recently viewed session normalization and bounds.
- Run Django checks, the full pytest suite, Black check, Pylint, migration
  consistency check, and strict OpenSpec validation.

## Risks / Trade-offs

- [A duplicate can be inserted between form validation and save] -> Keep the
  database uniqueness constraint, use an atomic save boundary, and convert the
  resulting `IntegrityError` into a non-field form error.
- [Catching an integrity error inside a broken transaction can cause another
  database error] -> Catch outside the inner atomic block before rendering or
  querying again.
- [Average annotation may conflict with the model property name] -> Use a
  distinct annotation such as `search_average_rating`.
- [A manually supplied login `next` could redirect off-site] -> Rely on
  Django's standard `LoginView` redirect safety validation and render the
  framework-provided `next`.
- [Permission checks in templates can drift from server enforcement] -> Make
  the view authoritative, pass prepared link context, and still enforce
  ownership in `review_edit`.
- [Adding form rendering could regress escaping or session behavior] -> Keep
  template autoescaping and run focused regressions for hostile values and the
  recent-book session contract.

## Migration and Rollout

1. Add and unit-test the two forms.
2. Update search rendering and filtering.
3. Add authenticated Review create/edit views and URL contracts.
4. Add login, form, message, search, and Book-detail template behavior.
5. Add integration, security, and regression tests.
6. Update project documentation and run all verification gates.

No database migration or backfill is required. Rollback removes the form and
write workflows while leaving the existing Book and Review rows and database
constraints intact.

## Open Questions

- No blocking specification decision remains. The selected `accounts/` prefix,
  typed minimum-rating choice, all-Books default search behavior, and
  author-exactly ownership rule are implementation defaults consistent with
  Issue #7 and the approved clarification.
- Merge, OpenSpec archive, and feature-branch deletion remain explicitly
  approval-gated after implementation and Pull Request review.

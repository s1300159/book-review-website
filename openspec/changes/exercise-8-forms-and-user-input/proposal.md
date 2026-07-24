## Why

Issue #7 (`Exercise 8: Add validated review forms and user input workflows`)
replaces the remaining manually constructed search input and read-only review
placeholder with validated Django forms. The project already has Book and
Review models, a database uniqueness constraint, template-rendered book pages,
and bounded recently viewed Book IDs in the session, but users cannot yet
filter by minimum rating or create and edit their own reviews.

This change defines the form, authentication, authorization, validation,
template, and request-method contracts before application implementation
starts. It deliberately leaves the existing data model unchanged.

## What Changes

- Add a GET-based `BookSearchForm` using `forms.Form`.
  - Accept an optional `q`, trim its leading and trailing whitespace, and use
    it for case-insensitive partial-title matching.
  - Accept an optional `min_rating` limited to the integers 1 through 5.
  - Filter against the average rating of related Reviews and exclude Books
    without Reviews whenever `min_rating` is supplied.
  - Display every Book when both `q` and `min_rating` are empty, preserving
    the existing default listing behavior.
  - Display a condition-change prompt when valid supplied criteria match no
    Books.
  - Keep all search values in the request URL and never save them to the
    session.
- Add a `ReviewForm` using `forms.ModelForm`.
  - Expose only `text` and `rating`, with rating presented as a 1-through-5
    choice and whitespace-only text rejected.
  - Receive `user` and `book` from server-side view context rather than POST
    data.
  - Reject a second Review for the same user and Book as a non-field error,
    while excluding the current instance during editing.
  - Retain the database `UniqueConstraint` as the final defense and safely
    translate a possible `IntegrityError` into a form error.
- Replace the read-only `review_create` placeholder with an authenticated GET
  and POST workflow.
  - Render the form on GET, validate and save on POST, and redisplay invalid
    forms with HTTP 200.
  - Use the Book from the URL and the User from `request.user`.
  - Redirect by the named `reviews:book_detail` URL after success, following
    POST-Redirect-GET, and add a Django success message.
- Add an authenticated `reviews:review_edit` GET and POST workflow.
  - Load the Review by ID, allow only its author to edit it, and return HTTP
    403 to an authenticated non-author.
  - Keep the Review's User and Book immutable.
  - Redirect to its named Book detail URL with a success message after a valid
    update.
- Add Django's standard authentication URLs and a minimal
  `registration/login.html` template.
  - Configure named login and post-login destinations.
  - Preserve the `next` parameter so an unauthenticated user returns to the
    requested review workflow after login.
  - Do not add user registration.
- Extend the existing template interface.
  - Share `reviews/review_form.html` between create and edit.
  - Render the search interface with `BookSearchForm`.
  - Display field errors, non-field errors, CSRF tokens, and Django messages.
  - Let book detail show the appropriate create or edit link for the current
    user without moving permission logic into templates.
  - Preserve template inheritance, automatic escaping, existing review
    ordering and average display, and the recently viewed Books session
    behavior.
- Update tests and project documentation for forms, search filtering, review
  creation and editing, authentication, authorization, CSRF, messages,
  redirects, and regressions.

## Capabilities

### New Capabilities

- `review-form-workflow`: Defines the public search and Review forms, form
  validation, authenticated Review create/edit persistence, template error
  rendering, success feedback, and ownership rules.
- `authentication-interface`: Defines the standard Django login URL and
  template contract, named redirect settings, CSRF/error display, and `next`
  preservation needed by the Review workflows.

### Modified Capabilities

- `basic-book-views`: Replaces the all-GET/read-only Review placeholder
  contract with GET-only reading views plus GET/POST Review create and edit
  views, and extends title search with validated minimum-average-rating
  filtering.

## Impact

- Expected implementation files after this proposal is approved:
  `reviews/forms.py`, `reviews/views.py`, `reviews/urls.py`,
  `config/urls.py`, `config/settings.py`, app and registration templates,
  focused tests, and project documentation.
- The existing `Review` validators, `Review.clean()`,
  `unique_review_per_user_book`, and `rating_between_1_and_5` constraints
  remain authoritative final defenses.
- Existing Book detail behavior, derived average rating, newest-first Review
  ordering, automatic escaping, and `recently_viewed_book_ids` session
  behavior must continue to work.
- No new dependency is required because Django forms, authentication,
  messages, CSRF protection, sessions, and their middleware/context
  processors are already available.
- This proposal is documentation-only. Application implementation, commit,
  push, Pull Request creation, Issue mutation, merge, and archive are separate
  later steps.

## Out of Scope

- Review deletion.
- User registration.
- Rating-based sorting.
- Pagination.
- HTMX.
- Advanced or production-grade CSS.
- Any `models.py` change.
- Any migration creation or data migration.

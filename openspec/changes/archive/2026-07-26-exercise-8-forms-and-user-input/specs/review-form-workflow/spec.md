## ADDED Requirements

### Requirement: Validated GET book search form
The system SHALL define `BookSearchForm` as a Django `forms.Form` with optional `q` and `min_rating` fields. It SHALL trim leading and trailing whitespace from `q`, accept only integer minimum ratings from 1 through 5, combine supplied criteria, and keep all search values in GET parameters rather than session state.

#### Scenario: Title query is trimmed and matched partially
- **WHEN** a user submits `q` containing leading or trailing whitespace around a non-empty partial title
- **THEN** the form returns the trimmed value and the search results contain Books whose titles match it case-insensitively

#### Scenario: Minimum rating is validated
- **WHEN** a user submits `min_rating` as 1, 2, 3, 4, or 5
- **THEN** the form is valid and exposes the selected value as an integer

#### Scenario: Invalid minimum rating is rejected
- **WHEN** a user submits a non-integer or a value outside 1 through 5 for `min_rating`
- **THEN** the form is invalid, displays a field error, returns HTTP 200, and performs no result filter with that invalid value

#### Scenario: Search controls remain request state
- **WHEN** a user submits `q` or `min_rating`
- **THEN** those values are represented by the current GET request and are not copied into the session

### Requirement: Search by derived average rating
The search workflow SHALL filter `Book` rows with the average rating of their related Reviews whenever a valid `min_rating` is supplied. It SHALL include Books at or above the threshold and exclude Books below the threshold and Books without Reviews.

#### Scenario: Minimum rating includes a boundary match
- **WHEN** a Book's related Reviews have an average rating equal to the submitted `min_rating`
- **THEN** that Book is included in the search results

#### Scenario: Unrated Book is excluded
- **WHEN** `min_rating` is supplied and a Book has no related Reviews
- **THEN** that Book is excluded from the search results

#### Scenario: Title and minimum rating are combined
- **WHEN** both non-empty `q` and valid `min_rating` are supplied
- **THEN** only Books satisfying both the partial-title match and minimum-average-rating threshold are returned

#### Scenario: Empty search controls display all Books
- **WHEN** both `q` and `min_rating` are missing or empty
- **THEN** the response is HTTP 200 and displays every registered Book

#### Scenario: Valid search has no results
- **WHEN** at least one valid non-empty search criterion is supplied and no Book satisfies all supplied criteria
- **THEN** the response is HTTP 200 and displays a message prompting the user to change the search conditions

### Requirement: Narrow context-aware Review form
The system SHALL define `ReviewForm` as a Django `forms.ModelForm` exposing only `text` and `rating`. It SHALL receive the User and Book from trusted initialization context, present rating choices from 1 through 5, reject empty or whitespace-only text, and never accept `user` or `book` from submitted fields.

#### Scenario: Public fields are limited
- **WHEN** `ReviewForm` is instantiated
- **THEN** its public editable fields are exactly `text` and `rating`

#### Scenario: Whitespace-only review is rejected
- **WHEN** a user submits Review text that becomes empty after trimming
- **THEN** the form is invalid and displays a `text` field error

#### Scenario: Rating is restricted
- **WHEN** a user submits a missing, non-integer, or out-of-range Review rating
- **THEN** the form is invalid and no Review is saved

#### Scenario: Ownership fields in POST are ignored
- **WHEN** submitted data contains `user` or `book` values
- **THEN** those values are not form fields and the saved Review relationships come only from server-selected context

### Requirement: Duplicate Review validation and database defense
The Review form SHALL reject an existing Review for the same User and Book as a non-field error, SHALL exclude its current persisted instance when validating an edit, and SHALL retain the existing database `UniqueConstraint` as the final concurrency defense. A duplicate-related `IntegrityError` during save SHALL be handled without exposing HTTP 500.

#### Scenario: Duplicate create is a form error
- **WHEN** a User who already has a Review for a Book validates a create form for that same Book
- **THEN** the form is invalid and displays a duplicate non-field error

#### Scenario: Current Review is excluded during edit
- **WHEN** an author validates changes to their existing Review without another Review for the same User and Book
- **THEN** the form does not treat its own instance as a duplicate

#### Scenario: Concurrent duplicate is safely rejected
- **WHEN** the database uniqueness constraint raises `IntegrityError` after form validation
- **THEN** the write is rolled back, the response is HTTP 200 with a non-field error, and no duplicate Review is persisted

### Requirement: Authenticated Review creation
The `reviews:review_create` workflow SHALL require authentication, accept GET and POST, obtain the Book from the URL and User from `request.user`, and render the shared Review form. A valid POST SHALL save one Review, add a Django success message, and redirect by the named `reviews:book_detail` route; an invalid POST SHALL render the same bound form with HTTP 200 and save nothing.

#### Scenario: Unauthenticated user is sent to login
- **WHEN** an unauthenticated user requests Review creation
- **THEN** the response redirects to the named login route with the requested Review URL preserved in `next`

#### Scenario: Form is displayed on GET
- **WHEN** an authenticated user sends GET for an existing Book's Review-create URL
- **THEN** the response is HTTP 200 and displays the shared Review form for that Book

#### Scenario: Valid Review follows POST-Redirect-GET
- **WHEN** an authenticated user submits valid, non-duplicate Review data
- **THEN** one Review is saved for `request.user` and the URL-selected Book, a success message is added, and the response redirects to the named Book detail URL

#### Scenario: Invalid Review is redisplayed
- **WHEN** an authenticated user submits invalid Review data
- **THEN** the response is HTTP 200 with field or non-field errors and no Review is saved

### Requirement: Author-only Review editing
The system SHALL expose a named `reviews:review_edit` GET and POST workflow that loads the Review by ID, requires authentication, permits only its author, updates only `text` and `rating`, and keeps its User and Book unchanged. A successful update SHALL add a success message and redirect to the named detail route for the unchanged Book.

#### Scenario: Author opens populated edit form
- **WHEN** an authenticated Review author sends GET to their Review-edit URL
- **THEN** the response is HTTP 200 and the shared form contains that Review's current text and rating

#### Scenario: Author updates public fields
- **WHEN** the Review author submits valid changed text and rating
- **THEN** those fields are updated, User and Book are unchanged, a success message is added, and the response redirects to the Review's named Book detail URL

#### Scenario: Authenticated non-author is forbidden
- **WHEN** an authenticated user who is not the Review author requests its edit URL
- **THEN** the response is HTTP 403 and the Review is unchanged

#### Scenario: Invalid edit is redisplayed
- **WHEN** the Review author submits invalid edit data
- **THEN** the response is HTTP 200 with errors and the persisted Review is unchanged

### Requirement: Secure shared form presentation
Review create and edit SHALL share `reviews/review_form.html`, extend the established base layout, display field and non-field errors, include a CSRF token for POST, and preserve Django automatic escaping. The base layout SHALL display queued Django messages.

#### Scenario: Missing CSRF token is rejected
- **WHEN** a client submits a Review POST without a valid CSRF token under normal CSRF enforcement
- **THEN** Django rejects the request and no Review is created or updated

#### Scenario: Validation errors are visible
- **WHEN** Review form validation fails
- **THEN** the shared template displays the relevant field errors and non-field errors

#### Scenario: Success feedback is visible after redirect
- **WHEN** a Review create or edit POST succeeds and the client follows the redirect
- **THEN** the base template displays the queued success message

### Requirement: Permission-aware Book detail actions
The Book detail response SHALL provide Review action links appropriate to the current user without relying on templates for ownership enforcement. An author SHALL receive an edit link for their Review, and a user without a Review for the Book SHALL receive a create path; server-side create/edit views SHALL remain authoritative.

#### Scenario: Existing author sees edit action
- **WHEN** an authenticated user views a Book detail page and has already reviewed that Book
- **THEN** the page links to that Review's named edit URL rather than offering a duplicate create action

#### Scenario: User without Review sees create action
- **WHEN** an authenticated user views a Book they have not reviewed
- **THEN** the page links to the named Review-create URL

#### Scenario: Unauthenticated visitor is guided to authentication
- **WHEN** an unauthenticated visitor views a Book detail page
- **THEN** the page provides an action that reaches the login-required Review-create workflow and can return through `next`

## ADDED Requirements

### Requirement: Validated Review creation route
The system SHALL expose `review_create(request, book_id)` at `/books/<int:book_id>/review/` with URL name `reviews:review_create`. It SHALL accept GET and POST, require authentication, obtain the Book from `book_id`, apply `ReviewForm` validation, and use the authenticated User as the Review author.

#### Scenario: Review creation methods are supported
- **WHEN** an authenticated user sends GET or POST to the named Review-create route for an existing Book
- **THEN** the system executes the appropriate display or validated submission workflow

#### Scenario: Unsupported Review-create method is rejected
- **WHEN** a client calls the Review-create route with a method other than GET or POST
- **THEN** the system returns HTTP 405 and performs no Review write

#### Scenario: Review-create Book does not exist
- **WHEN** an authenticated user requests Review creation with a `book_id` that does not identify a Book
- **THEN** the system returns HTTP 404 and creates no Review

### Requirement: Named Review editing route
The system SHALL expose `review_edit(request, review_id)` at a public path with URL name `reviews:review_edit`. It SHALL accept GET and POST, require authentication, load the Review by ID, and enforce exact author ownership before allowing `text` or `rating` changes.

#### Scenario: Review-edit route is reversible
- **WHEN** application code reverses `reviews:review_edit` with a Review ID
- **THEN** Django returns the corresponding public edit path

#### Scenario: Unsupported Review-edit method is rejected
- **WHEN** a client calls the Review-edit route with a method other than GET or POST
- **THEN** the system returns HTTP 405 and performs no Review write

#### Scenario: Review-edit target does not exist
- **WHEN** an authenticated user requests an edit URL whose `review_id` does not identify a Review
- **THEN** the system returns HTTP 404

## MODIFIED Requirements

### Requirement: Named function-based URL surface
The system SHALL define function-based views for the home, book-list, book-detail, book-search, Review-create, Review-edit, and redirect interactions. Each route SHALL have a name in the `reviews` application namespace, and the project URL configuration SHALL include the application URL configuration without removing the admin route. Reading and redirect routes SHALL remain GET-only; Review create and edit SHALL accept GET and POST.

#### Scenario: Named routes are reversible
- **WHEN** application code reverses any supported URL name in the `reviews` namespace with its required arguments
- **THEN** Django returns the corresponding public path

#### Scenario: Reading view rejects a non-GET request
- **WHEN** a client calls a home, Book-list, Book-detail, Book-search, or list-redirect display route with an unsupported HTTP method
- **THEN** the system returns HTTP 405 and performs no application-data write

#### Scenario: Review workflow rejects an unsupported method
- **WHEN** a client calls Review create or edit with a method other than GET or POST
- **THEN** the system returns HTTP 405 and performs no Review write

### Requirement: Partial title search
The system SHALL expose `book_search(request)` at `GET /books/search/` with URL name `reviews:book_search`. It SHALL validate GET parameters with `BookSearchForm`, trim optional `q` and use case-insensitive partial-title matching when non-empty, and apply an optional integer `min_rating` from 1 through 5 against the average related Review rating. Search parameters SHALL NOT be saved in the session, and the view SHALL NOT add sorting, pagination, or HTMX.

#### Scenario: Partial title matches Books
- **WHEN** a user supplies a valid non-empty `q` matching part of one or more Book titles with any letter case
- **THEN** the response is HTTP 200 and contains the matching titles but not non-matching titles

#### Scenario: Minimum average filters Books
- **WHEN** a user supplies a valid `min_rating`
- **THEN** the response includes Books whose average Review rating meets the threshold and excludes lower-rated and unrated Books

#### Scenario: Search criteria are combined
- **WHEN** a user supplies both valid `q` and `min_rating`
- **THEN** the response contains only Books satisfying both criteria

#### Scenario: Search form is invalid
- **WHEN** submitted search input fails form validation
- **THEN** the response is HTTP 200, displays the errors, and does not evaluate the invalid filter

#### Scenario: Search controls are empty
- **WHEN** both `q` and `min_rating` are missing, empty, or contain no usable value
- **THEN** the response is HTTP 200 and contains every registered Book

#### Scenario: Valid search has no results
- **WHEN** at least one valid non-empty search criterion is supplied and no Book satisfies all supplied criteria
- **THEN** the response is HTTP 200 and displays a message prompting the user to change the search conditions

### Requirement: Minimal safe responses before templates
Exercise 8 SHALL render Book and form responses with Django templates while preserving automatic escaping for dynamic Book, Review, username, form, message, and request values. Reading endpoints SHALL remain read-only; only valid authenticated Review-create and author-owned Review-edit POST requests may create or update a Review. The change SHALL NOT delete Reviews or add model changes or migrations.

#### Scenario: Dynamic text is included safely
- **WHEN** a template-rendered response includes a dynamic model, form, message, or request value containing HTML-significant characters
- **THEN** the response represents that value as escaped content rather than executable markup

#### Scenario: Reading endpoints remain read-only
- **WHEN** a home, Book-list, Book-detail, Book-search, or list-redirect endpoint is called
- **THEN** it does not create, update, or delete a Book or Review

#### Scenario: Review writes require valid authorized POST
- **WHEN** Review create or edit input is invalid, unauthenticated, forbidden, CSRF-rejected, or uses an unsupported method
- **THEN** no Review is created, updated, or deleted

### Requirement: View and URL test coverage
The project SHALL maintain focused tests for all established view and URL behavior and add coverage for validated search, minimum-average filtering, Review create/edit methods, authentication redirects, ownership, HTTP 403, validation errors, CSRF, messages, named redirects, safe integrity handling, and unchanged template/session behavior.

#### Scenario: View test suite runs
- **WHEN** the project test suite is executed after Exercise 8 implementation
- **THEN** the new input workflows and the existing Book detail, Review ordering, average rating, escaping, empty-state, URL, method, and recently viewed session contracts are covered by passing automated tests

### Requirement: Project view-contract documentation
The project SHALL document each current callable's path, URL name, supported HTTP methods, authentication and ownership requirements, arguments or form input, processing behavior, and return value in the project specification, while distinguishing implemented Exercise 8 behavior from sorting, pagination, HTMX, registration, deletion, and other deferred work.

#### Scenario: Project specification reflects validated input workflows
- **WHEN** Exercise 8 implementation is completed
- **THEN** the project documentation describes the implemented search and Review form contracts and clearly identifies deferred features

## REMOVED Requirements

### Requirement: Read-only review submission placeholder
**Reason:** Issue #7 replaces the placeholder with authenticated, validated Review creation and adds author-only Review editing.

**Migration:** Preserve the existing `reviews:review_create` name and Book-based path, but replace its GET-only placeholder response with the new GET/POST form workflow. Use `reviews:review_edit` for updates.

The system SHALL expose `review_create(request, book_id)` at `GET /books/<int:book_id>/review/` with URL name `reviews:review_create`. It SHALL verify that the identified Book exists and return a minimal placeholder response without creating or changing any Review.

#### Scenario: Placeholder is shown for an existing book
- **WHEN** a user opens the review-placeholder URL for an existing book
- **THEN** the response is HTTP 200, identifies the book, and no Review is created or changed

#### Scenario: Placeholder book does not exist
- **WHEN** a user opens the review-placeholder URL with a `book_id` that does not identify a Book
- **THEN** the system returns HTTP 404 and no Review is created or changed

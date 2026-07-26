# basic-book-views Specification

## Purpose
Define the function-based HTTP and named-URL behavior for home, Book listing,
Book details and Reviews, validated search, authenticated Review creation,
author-only Review editing, and the Book-list redirect.
## Requirements
### Requirement: Named function-based URL surface
The system SHALL define function-based views for the home, book-list, book-detail, book-search, Review-create, Review-edit, and redirect interactions. Each route SHALL have a name in the `reviews` application namespace, and the project URL configuration SHALL include the application URL configuration without removing the admin route. Reading and redirect routes SHALL remain GET-only; Review create and edit SHALL accept GET and POST.

#### Scenario: Named routes are reversible
- **WHEN** application code reverses any supported URL name in the `reviews` namespace with its required arguments
- **THEN** Django returns the corresponding public path

#### Scenario: A non-GET request is rejected
- **WHEN** a client calls a home, Book-list, Book-detail, Book-search, or list-redirect reading route with POST, DELETE, PUT, PATCH, or another method other than GET
- **THEN** the system returns HTTP 405 and performs no application-data write

#### Scenario: Review workflow rejects an unsupported method
- **WHEN** a client calls Review create or edit with DELETE, PUT, PATCH, or another method other than GET or POST
- **THEN** the system returns HTTP 405 and performs no Review write

### Requirement: Minimal home page
The system SHALL expose `home(request)` at `GET /` with URL name `reviews:home` and return a minimal HTTP 200 home response containing the site identity and navigation to the book-list and search routes.

#### Scenario: User opens the home page
- **WHEN** a user sends GET `/`
- **THEN** the system returns HTTP 200 with the minimal Book Review Website home content

### Requirement: Registered book listing
The system SHALL expose `book_list(request)` at `GET /books/` with URL name `reviews:book_list`, read existing Book rows through the Django ORM, and render `reviews/book_list.html` with every registered book title. The template SHALL extend `reviews/base.html`, and the view SHALL NOT implement rating sorting, rating filtering, or pagination.

#### Scenario: Registered books are listed
- **WHEN** registered books exist and a user opens the named book-list URL
- **THEN** the template-rendered response is HTTP 200 and contains each registered book title

#### Scenario: No books are registered
- **WHEN** no Book rows exist and a user opens the named book-list URL
- **THEN** the template-rendered response is HTTP 200 and clearly indicates that no books are available

### Requirement: Book detail and related reviews
The system SHALL expose `book_detail(request, book_id)` at `GET /books/<int:book_id>/` with URL name `reviews:book_detail`. It SHALL fetch the identified Book and render `reviews/book_detail.html`, which SHALL extend `reviews/base.html` and display its title, description, derived average rating, and related Review authors, text, and ratings, with reviews ordered newest first.

#### Scenario: Existing book detail is displayed
- **WHEN** a user opens the detail URL for an existing book with related reviews
- **THEN** the template-rendered response is HTTP 200 and contains that book's information, average rating, and its reviews in newest-first order

#### Scenario: Book has no reviews
- **WHEN** a user opens the detail URL for an existing book without reviews
- **THEN** the template-rendered response is HTTP 200 and clearly indicates that the book has no reviews

#### Scenario: Detail book does not exist
- **WHEN** a user opens the detail URL with a `book_id` that does not identify a Book
- **THEN** the system returns HTTP 404 without rendering a successful detail page

### Requirement: Partial title search
The system SHALL expose `book_search(request)` at `GET /books/search/` with URL name `reviews:book_search`. It SHALL validate GET parameters with `BookSearchForm`, trim optional `q` and use case-insensitive partial-title matching when non-empty, and apply an optional integer `min_rating` from 1 through 5 against the average related Review rating. Search parameters SHALL NOT be saved in the session, normal GET requests SHALL return the complete search page, and HTMX GET requests SHALL return the search-result fragment. The view SHALL NOT add sorting or pagination.

#### Scenario: Partial title matches books
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

#### Scenario: Search query is empty
- **WHEN** `q` and `min_rating` are both missing, empty, or contain no usable value
- **THEN** the response is HTTP 200, avoids an empty-string title lookup, and contains every registered Book

#### Scenario: Search has no match
- **WHEN** at least one valid non-empty search criterion is supplied and no Book satisfies all supplied criteria
- **THEN** the response is HTTP 200 and displays a message prompting the user to change the search conditions

### Requirement: Named book-list redirect
The system SHALL expose `book_list_redirect(request)` at `GET /books-redirect/` with URL name `reviews:book_list_redirect` and SHALL redirect using the named `reviews:book_list` route rather than a hard-coded destination path.

#### Scenario: User opens the redirect URL
- **WHEN** a user sends GET `/books-redirect/`
- **THEN** the system returns HTTP 302 with the named book-list URL as its destination

### Requirement: Minimal safe responses before templates
Exercise 8 SHALL render Book and form responses with Django templates while preserving automatic escaping for dynamic Book, Review, username, form, message, and request values. Reading endpoints SHALL remain read-only; only valid authenticated Review-create and author-owned Review-edit POST requests may create or update a Review. The change SHALL NOT delete Reviews or add model changes or migrations.

#### Scenario: Model text is included safely
- **WHEN** a template-rendered response includes a dynamic model, form, message, or request value containing HTML-significant characters
- **THEN** the response represents that value as escaped content rather than executable markup

#### Scenario: Exercise 6 endpoints are read-only
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

#### Scenario: Project specification reflects the view layer
- **WHEN** Exercise 8 implementation is completed
- **THEN** the project documentation describes the implemented search and Review form contracts and clearly identifies deferred features

### Requirement: Shared book-page template layout
The system SHALL define `reviews/base.html` with a reusable document structure containing a shared header, named-URL navigation, main-content block, and footer. The book-list and book-detail templates SHALL extend that base template and provide their page-specific content through template blocks.

#### Scenario: Book pages share the base layout
- **WHEN** a user opens either the named book-list URL or an existing Book's named detail URL
- **THEN** the response is rendered through the page-specific template and `reviews/base.html` and contains the shared header, navigation, main-content region, and footer

#### Scenario: Shared navigation uses named routes
- **WHEN** either template-rendered book page is rendered
- **THEN** its shared navigation targets URLs reversed from the existing `reviews` URL names rather than hard-coded destination paths

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

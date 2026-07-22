## ADDED Requirements

### Requirement: Named function-based URL surface
The system SHALL define GET-only function-based views for the Exercise 6 home, book-list, book-detail, book-search, review-placeholder, and redirect interactions. Each route SHALL have a name in the `reviews` application namespace, and the project URL configuration SHALL include the application URL configuration without removing the admin route.

#### Scenario: Named routes are reversible
- **WHEN** application code reverses any Exercise 6 URL name in the `reviews` namespace with its required arguments
- **THEN** Django returns the corresponding public path

#### Scenario: A non-GET request is rejected
- **WHEN** a client calls an Exercise 6 display route with an unsupported HTTP method
- **THEN** the system returns HTTP 405 and performs no application-data write

### Requirement: Minimal home page
The system SHALL expose `home(request)` at `GET /` with URL name `reviews:home` and return a minimal HTTP 200 home response containing the site identity and navigation to the book-list and search routes.

#### Scenario: User opens the home page
- **WHEN** a user sends GET `/`
- **THEN** the system returns HTTP 200 with the minimal Book Review Website home content

### Requirement: Registered book listing
The system SHALL expose `book_list(request)` at `GET /books/` with URL name `reviews:book_list`, read existing Book rows through the Django ORM, and return a minimal HTTP 200 response containing every registered book title without implementing rating sorting, rating filtering, or pagination.

#### Scenario: Registered books are listed
- **WHEN** registered books exist and a user opens the named book-list URL
- **THEN** the response is HTTP 200 and contains each registered book title

#### Scenario: No books are registered
- **WHEN** no Book rows exist and a user opens the named book-list URL
- **THEN** the response is HTTP 200 and clearly indicates that no books are available

### Requirement: Book detail and related reviews
The system SHALL expose `book_detail(request, book_id)` at `GET /books/<int:book_id>/` with URL name `reviews:book_detail`. It SHALL fetch the identified Book and return a minimal HTTP 200 response containing its title, description, derived average rating, and related Review authors, text, and ratings, with reviews ordered newest first.

#### Scenario: Existing book detail is displayed
- **WHEN** a user opens the detail URL for an existing book with related reviews
- **THEN** the response is HTTP 200 and contains that book's information, average rating, and its reviews in newest-first order

#### Scenario: Book has no reviews
- **WHEN** a user opens the detail URL for an existing book without reviews
- **THEN** the response is HTTP 200 and clearly indicates that the book has no reviews

#### Scenario: Detail book does not exist
- **WHEN** a user opens the detail URL with a `book_id` that does not identify a Book
- **THEN** the system returns HTTP 404

### Requirement: Partial title search
The system SHALL expose `book_search(request)` at `GET /books/search/` with URL name `reviews:book_search`. It SHALL trim the optional `q` query parameter and, when non-empty, return Book rows whose titles contain the query using case-insensitive partial matching.

#### Scenario: Partial title matches books
- **WHEN** a user supplies a non-empty `q` value matching part of one or more book titles with any letter case
- **THEN** the response is HTTP 200 and contains the matching titles but not non-matching titles

#### Scenario: Search has no match
- **WHEN** a user supplies a non-empty `q` value that matches no book title
- **THEN** the response is HTTP 200 and clearly indicates that no books matched

#### Scenario: Search query is empty
- **WHEN** `q` is missing, empty, or contains only whitespace
- **THEN** the response is HTTP 200, performs no all-books empty-string match, and prompts for a title query

### Requirement: Read-only review submission placeholder
The system SHALL expose `review_create(request, book_id)` at `GET /books/<int:book_id>/review/` with URL name `reviews:review_create`. It SHALL verify that the identified Book exists and return a minimal placeholder response without creating or changing any Review.

#### Scenario: Placeholder is shown for an existing book
- **WHEN** a user opens the review-placeholder URL for an existing book
- **THEN** the response is HTTP 200, identifies the book, and no Review is created or changed

#### Scenario: Placeholder book does not exist
- **WHEN** a user opens the review-placeholder URL with a `book_id` that does not identify a Book
- **THEN** the system returns HTTP 404 and no Review is created or changed

### Requirement: Named book-list redirect
The system SHALL expose `book_list_redirect(request)` at `GET /books-redirect/` with URL name `reviews:book_list_redirect` and SHALL redirect using the named `reviews:book_list` route rather than a hard-coded destination path.

#### Scenario: User opens the redirect URL
- **WHEN** a user sends GET `/books-redirect/`
- **THEN** the system returns HTTP 302 with the named book-list URL as its destination

### Requirement: Minimal safe responses before templates
Exercise 6 SHALL return minimal text/HTML responses without requiring templates, and dynamic model values included in HTML SHALL be escaped. It SHALL NOT add form processing, review persistence, model changes, or migrations.

#### Scenario: Model text is included safely
- **WHEN** a response includes a dynamic Book, Review, or username value containing HTML-significant characters
- **THEN** the response represents that value as content rather than executable markup

#### Scenario: Exercise 6 endpoints are read-only
- **WHEN** any Exercise 6 endpoint is called
- **THEN** it does not create, update, or delete a Book or Review

### Requirement: View and URL test coverage
The project SHALL add focused tests for every Exercise 6 callable, named URL resolution, successful output, empty states where applicable, search behavior, missing-book 404 responses, GET-only behavior, lack of review persistence, and redirect destination.

#### Scenario: View test suite runs
- **WHEN** the project test suite is executed after implementation
- **THEN** each Exercise 6 view and its important success and failure behavior are covered by passing automated tests alongside the existing model tests

### Requirement: Project view-contract documentation
The project SHALL document each Exercise 6 callable's path, URL name, HTTP method, arguments or query input, processing behavior, and return value in `docs/exercise-2-specification.md`, while distinguishing this incremental behavior from later template and form work.

#### Scenario: Project specification reflects the view layer
- **WHEN** Exercise 6 implementation is completed
- **THEN** the project specification contains the implemented URL and callable contract and clearly identifies deferred features

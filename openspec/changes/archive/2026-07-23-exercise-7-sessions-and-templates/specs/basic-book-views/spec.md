## ADDED Requirements

### Requirement: Shared book-page template layout
The system SHALL define `reviews/base.html` with a reusable document structure containing a shared header, named-URL navigation, main-content block, and footer. The book-list and book-detail templates SHALL extend that base template and provide their page-specific content through template blocks.

#### Scenario: Book pages share the base layout
- **WHEN** a user opens either the named book-list URL or an existing Book's named detail URL
- **THEN** the response is rendered through the page-specific template and `reviews/base.html` and contains the shared header, navigation, main-content region, and footer

#### Scenario: Shared navigation uses named routes
- **WHEN** either template-rendered book page is rendered
- **THEN** its shared navigation targets URLs reversed from the existing `reviews` URL names rather than hard-coded destination paths

## MODIFIED Requirements

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

### Requirement: Minimal safe responses before templates
Exercise 7 SHALL replace direct Python-generated HTML for the book-list and book-detail responses with Django templates while preserving the other Exercise 6 endpoints as read-only responses. Dynamic Book, Review, username, and request values included by templates SHALL use Django automatic escaping, and the change SHALL NOT add form processing, review persistence, model changes, or migrations.

#### Scenario: Model text is included safely
- **WHEN** a template-rendered book response includes a dynamic Book, Review, or username value containing HTML-significant characters
- **THEN** the response represents that value as escaped content rather than executable markup

#### Scenario: Exercise 6 endpoints are read-only
- **WHEN** any Exercise 7 display endpoint is called
- **THEN** it does not create, update, or delete a Book or Review

### Requirement: View and URL test coverage
The project SHALL maintain focused tests for every Exercise 6 callable and SHALL add coverage for the Exercise 7 book-list and book-detail template names, shared base-template inheritance, common layout, semantic content, empty states, escaping, missing-book 404 behavior, GET-only behavior, lack of Book or Review persistence, and unchanged URL resolution.

#### Scenario: View test suite runs
- **WHEN** the project test suite is executed after Exercise 7 implementation
- **THEN** the template-rendered book pages and the preserved Exercise 6 view contracts are covered by passing automated tests alongside the existing model tests

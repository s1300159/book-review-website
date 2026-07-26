## ADDED Requirements

### Requirement: Dynamic book search result updates
The system SHALL update the book search result region through an HTMX GET request when a user changes the title query, changes the minimum rating, or submits the search form.

#### Scenario: Title query changes
- **WHEN** a user changes the title query and pauses briefly
- **THEN** the system sends the current search form values to the named book search URL
- **AND** updates the `book-results` region without replacing the full page

#### Scenario: Minimum rating changes
- **WHEN** a user changes the minimum rating
- **THEN** the system sends the current search form values to the named book search URL
- **AND** updates the `book-results` region without replacing the full page

#### Scenario: Search form is submitted
- **WHEN** a user submits the search form while HTMX is available
- **THEN** the system updates the `book-results` region with the matching results

### Requirement: Search fragment response
The system SHALL return only the search result fragment for an HTMX search request, using the same validated filters as a normal search request.

#### Scenario: Matching books are returned
- **WHEN** an HTMX search matches books
- **THEN** the response contains result cards with each book's title, cover or placeholder, description, average rating, and detail link
- **AND** the response does not contain the complete page layout or search form

#### Scenario: No books match
- **WHEN** an HTMX search has valid non-empty conditions and no matching books
- **THEN** the result fragment advises the user to change the search conditions

#### Scenario: Search conditions are empty
- **WHEN** an HTMX search has no title query and no minimum rating
- **THEN** the result fragment contains all registered books

#### Scenario: Search values are untrusted
- **WHEN** book or query text contains HTML markup
- **THEN** the result fragment escapes that markup

### Requirement: Progressive enhancement
The system SHALL keep the book search usable as a standard URL-based GET form when HTMX is unavailable.

#### Scenario: Normal search request
- **WHEN** the search URL receives a normal GET request
- **THEN** the system returns the complete search page with the form and result fragment

#### Scenario: JavaScript is unavailable
- **WHEN** a user submits the search form without HTMX
- **THEN** the browser navigates to the search URL with query parameters
- **AND** the server returns the correct filtered full page

### Requirement: Search state remains request scoped
The system SHALL NOT store title or minimum-rating search values in the user's session for either normal or HTMX search requests.

#### Scenario: HTMX search completes
- **WHEN** an HTMX search request is processed
- **THEN** the user's session contains no saved search values

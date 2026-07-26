## MODIFIED Requirements

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

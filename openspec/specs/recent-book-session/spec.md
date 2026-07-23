# recent-book-session Specification

## Purpose
TBD - created by archiving change exercise-7-sessions-and-templates. Update Purpose after archive.
## Requirements
### Requirement: Bounded recently viewed Book history
After successfully resolving a Book in `book_detail`, the system SHALL store that Book's integer primary key in the current browser session under `recently_viewed_book_ids`. The list MUST be ordered most recent first, MUST contain no duplicate IDs, and MUST contain at most five IDs.

#### Scenario: First Book detail is recorded
- **WHEN** a browser session opens the detail URL for an existing Book with no prior recent-book history
- **THEN** the session contains that Book's integer ID as the only `recently_viewed_book_ids` entry

#### Scenario: Revisited Book moves to the front
- **WHEN** a browser session opens the detail URL for a Book whose ID is already in its recent-book history
- **THEN** that ID moves to the first position and occurs exactly once

#### Scenario: Sixth distinct Book evicts the oldest
- **WHEN** a browser session with five recent Book IDs opens a sixth distinct existing Book
- **THEN** the new ID is first, the previous oldest ID is absent, and exactly five IDs remain

#### Scenario: Missing Book is not recorded
- **WHEN** a browser session opens a detail URL whose `book_id` does not identify a Book
- **THEN** the response is HTTP 404 and the recent-book session history is unchanged

#### Scenario: Malformed existing history is normalized
- **WHEN** an existing `recently_viewed_book_ids` value is not a list, or a stored list contains non-integer, boolean, or duplicate entries, and the browser opens an existing Book detail
- **THEN** the response does not fail, invalid entries are discarded, and the session contains the current integer Book ID followed by at most four unique valid integer entries

### Requirement: Session history is temporary reference state
The recent-book session history SHALL contain only Book primary-key references and SHALL NOT contain complete Book data, Review text or ratings, User or authentication data, search terms, sorting selections, minimum-rating selections, or page numbers. Book, Review, and configured User database records MUST remain the source of truth.

#### Scenario: Search and listing controls are not persisted in the session
- **WHEN** a request supplies `q`, `sort`, `min_rating`, or `page` as GET parameters
- **THEN** none of those parameter values is copied into `recently_viewed_book_ids` or another Exercise 7 session value

#### Scenario: Domain content is not copied into session history
- **WHEN** an existing Book with related Reviews is recorded as recently viewed
- **THEN** the Exercise 7 session value contains its integer ID but not its title, description, Review content, rating values, or User data

### Requirement: Recent-book histories are isolated by session
The system SHALL maintain `recently_viewed_book_ids` independently for each browser session and SHALL NOT require a logged-in user to record the history.

#### Scenario: Separate browser sessions have separate histories
- **WHEN** two unauthenticated browser sessions open different Book detail URLs
- **THEN** each session contains only its own recently viewed Book IDs

### Requirement: Session behavior test coverage
The project SHALL add focused automated tests for first visits, most-recent-first ordering, duplicate removal, the five-ID limit, malformed-history normalization, missing-Book behavior, allowed session contents, and isolation between browser sessions.

#### Scenario: Session test suite runs
- **WHEN** the project test suite is executed after Exercise 7 implementation
- **THEN** the bounded and isolated recent-book session behavior is covered by passing tests

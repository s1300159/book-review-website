## ADDED Requirements

### Requirement: Book data model
The system SHALL define a Book model with a required `CharField(max_length=200)` title, an optional `ImageField(upload_to="book_covers/", blank=True)` cover image, and an optional `TextField(blank=True)` description.

#### Scenario: Book metadata is persisted
- **WHEN** a book is created with a title and optional cover image and description values
- **THEN** its title, cover image value, and description are persisted

### Requirement: Review data model
The system SHALL define a Review model with required `TextField` text, an `IntegerField` rating, `DateTimeField(auto_now_add=True)` created-at timestamp, a required Book foreign key, and a required configured-User foreign key.

#### Scenario: Review is persisted with its relationships
- **WHEN** a logged-in Django user submits required review text and a valid rating for a book
- **THEN** the review is persisted for exactly one book and that user with its creation date

### Requirement: Django standard authentication user
The Review user relationship SHALL reference Django's configured authentication user model, and the project SHALL NOT introduce a custom User model for this change.

#### Scenario: Review uses configured authentication user
- **WHEN** a Review is associated with a user
- **THEN** that relationship targets `settings.AUTH_USER_MODEL`

### Requirement: Review relationships
The Review book and user fields SHALL use `on_delete=CASCADE` and `related_name="reviews"`.

#### Scenario: Reverse review relationships
- **WHEN** reviews exist for a book and user
- **THEN** the related reviews are available through `book.reviews` and `user.reviews`

### Requirement: One review per user and book
The system MUST prevent a user from creating more than one review for the same book through both application validation and a database uniqueness constraint on the user and book references.

#### Scenario: Database rejects duplicate review
- **WHEN** a second Review is saved for an existing user and book pair
- **THEN** the database uniqueness constraint rejects the duplicate

#### Scenario: Application reports duplicate review
- **WHEN** model validation is run for another review with an existing user and book pair
- **THEN** application validation reports the duplicate before it is saved

### Requirement: Rating range
The Review rating SHALL be an integer from 1 through 5 and MUST be enforced through application validators and a database `CheckConstraint`.

#### Scenario: Application rejects rating outside range
- **WHEN** model validation is run with a rating below 1 or above 5
- **THEN** application validation reports the invalid rating

#### Scenario: Database rejects rating outside range
- **WHEN** a Review with a rating below 1 or above 5 bypasses application validation and is saved
- **THEN** the database check constraint rejects the value

### Requirement: Derived average rating
The system SHALL calculate each book's average rating from the star-rating values of its related Reviews and SHALL NOT store a separate average-rating column.

#### Scenario: Average is calculated from reviews
- **WHEN** a book has multiple reviews
- **THEN** its average rating is calculated by aggregating the related Review rating values

#### Scenario: Book has no reviews
- **WHEN** a book has no related reviews
- **THEN** its average rating is `None`

The system SHALL NOT define average-rating display rounding as part of Exercise 5.

### Requirement: Readable model string representations
The Book and Review models SHALL implement readable `__str__()` methods suitable for Django administration without exposing credentials or full review text.

#### Scenario: Book string representation
- **WHEN** a Book is converted to a string
- **THEN** the result is its title

#### Scenario: Review string representation
- **WHEN** a Review is converted to a string
- **THEN** the result concisely includes the username and book title

### Requirement: New migration
The project SHALL create a new Django migration for the Book and Review schema and SHALL NOT modify an old migration.

#### Scenario: Schema migration is generated
- **WHEN** the approved models are implemented
- **THEN** a new migration defines the models, relationships, and approved database constraints

### Requirement: Model test coverage
The project SHALL add focused automated tests for model creation, relationships, uniqueness, derived average ratings, and string representations.

#### Scenario: Model tests run
- **WHEN** the project test suite is executed after implementation
- **THEN** the Book and Review model behaviors and database constraints are covered by passing tests

### Requirement: Project specification update
The project SHALL update its Exercise 2 specification with the approved database schema and constraint decisions during implementation.

#### Scenario: Specification reflects implemented schema
- **WHEN** the database schema implementation is completed
- **THEN** `docs/exercise-2-specification.md` describes the implemented fields, relationships, constraints, average-rating rule, and string behavior

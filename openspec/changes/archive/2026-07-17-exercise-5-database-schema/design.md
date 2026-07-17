## Background

The Django project and `reviews` app already exist, and `reviews` is registered in `INSTALLED_APPS`. The app has no domain models yet. Exercise 5 introduces the first project-owned database schema while preserving Django's standard authentication user, SQLite development setup, and existing migration history.

The design implements [GitHub Issue #1](https://github.com/s1300159/book-review-website/issues/1) and is based on `README.md`, `docs/exercise-1-project-topic.txt`, `docs/exercise-2-specification.md`, and `AGENTS.md`. The schema decisions below are confirmed for Exercise 5.

## Goals

- Define the initial conceptual and Django ORM schema for books and reviews.
- Associate every review with exactly one book and one Django authentication user.
- Enforce one review per user and book in both application validation and the database.
- Derive average ratings from related reviews rather than storing duplicated aggregate data.
- Give Book and Review readable admin-facing `__str__()` values.
- Plan a new migration, focused model tests, and a project specification update.

## Non-goals

- Creating a custom User model.
- Implementing URLs, views, forms, templates, authentication screens, or HTMX behavior.
- Implementing review editing or deletion.
- Defining average-rating display rounding.
- Adding unrelated packages or editing old migrations.

## Proposed Database Schema

```text
Django authentication User
    1 ────< Review >──── 1 Book
                |
                └── rating contributes to Book.average_rating

Unique Review constraint: (user, book)
```

`Book` stores book metadata. `Review` is the join entity between a Django authentication user and a book and stores the user's review text, rating, and creation time. Average rating is a derived query over related Review rows and is not stored as a Book column.

## Field Definitions

### Book

- `title`: required `CharField(max_length=200)`.
- `cover_image`: optional `ImageField(upload_to="book_covers/", blank=True)`.
- `description`: optional `TextField(blank=True)`.

### Review

- `text`: required `TextField`.
- `rating`: required `IntegerField` with application validators for values from 1 through 5.
- `created_at`: `DateTimeField(auto_now_add=True)`.
- `book`: required `ForeignKey(Book, on_delete=CASCADE, related_name="reviews")`.
- `user`: required `ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="reviews")`.

### User

- Use Django's standard authentication user through `settings.AUTH_USER_MODEL`.
- Do not create a project-specific User model or store authentication credentials in `reviews`.

## Relationships

- A Book has zero or more Reviews.
- A Django authentication user has zero or more Reviews.
- Every Review belongs to exactly one Book and one User.
- Both foreign keys use `related_name="reviews"`.
- Both foreign keys use `CASCADE`, so reviews cannot remain without their book or author.

## Database Constraints

- Add a named `UniqueConstraint` covering `user` and `book`.
- Add a named `CheckConstraint` requiring `rating >= 1` and `rating <= 5`.
- Add minimum and maximum value validators for `rating`.
- Model-level application validation MUST detect an existing review for the same user and book, excluding the current row when validating an existing instance.
- Do not store average rating in the database; calculate it from Review rating values using the Django ORM.
- The derived average-rating behavior returns `None` when the book has no reviews.
- Display rounding is outside Exercise 5.

## `__str__()` Behavior

- `Book.__str__()` returns the book title.
- `Review.__str__()` returns a concise value containing both the username and book title, for example `"<username> - <book title>"`.
- String representations MUST not expose authentication credentials or full review text.

## Migration Plan

1. Add Pillow through `uv` because Django's `ImageField` requires it.
2. Add the confirmed Book and Review models to `reviews/models.py`.
3. Run `uv run python manage.py makemigrations reviews` to create a new migration.
4. Review the generated migration for the two models, foreign keys, unique constraint, and rating check constraint.
5. Run `uv run python manage.py migrate`.
6. Run `uv run python manage.py check`, the model test suite, Black, and Pylint.

Rollback during development uses Django migration commands to return to the previous migration state. Existing migration files MUST NOT be edited.

## Test Plan

- Test required and optional Book fields, including the 200-character title limit.
- Test Review creation linked to a Book and Django User.
- Test `Book.__str__()` and `Review.__str__()`.
- Test reverse Book-to-Review and User-to-Review relationships.
- Test that a duplicate `(user, book)` review raises a database integrity error.
- Test model validation for duplicate user-and-book pairs.
- Test rating values below 1 and above 5 through both model validation and the database constraint.
- Test average rating for multiple reviews, confirm it is derived rather than stored, and confirm a book without reviews returns `None`.
- Run the full existing pytest suite.

## Specification Document Update Plan

- Update `docs/exercise-2-specification.md` during implementation with the approved Django schema, relationship behavior, database constraints, derived average-rating rule, and `__str__()` behavior.
- Keep `docs/exercise-1-project-topic.txt` as the high-level topic document unless the approved schema changes its basic entity description.
- After implementation and review, sync the accepted capability into `openspec/specs/book-review-data-model/spec.md` through the normal OpenSpec archive/sync flow.

## Risks / Trade-offs

- [Image handling adds a dependency] → Add only Pillow, which is required by Django's confirmed `ImageField`.
- [Application-only duplicate validation is race-prone] → Retain the database unique constraint as the final guarantee.
- [Stored average ratings can become stale] → Calculate averages from Review rows with ORM aggregation.
- [Cascade deletion removes related reviews] → Treat this as the confirmed relationship behavior and cover it with tests where appropriate.

## Resolved Decisions

1. The rating range is 1 through 5, enforced by application validators and a database check constraint.
2. Book title is required and limited to 200 characters.
3. Cover image uses `ImageField`, uploads to `book_covers/`, and is optional with `blank=True`.
4. Description uses `TextField` and is optional with `blank=True`.
5. Review text uses a required `TextField` without an Exercise 5 maximum length.
6. Both foreign keys use `CASCADE` and `related_name="reviews"`.
7. A book without reviews has an average rating of `None`.
8. Average-rating display rounding and review editing or deletion remain outside Exercise 5.

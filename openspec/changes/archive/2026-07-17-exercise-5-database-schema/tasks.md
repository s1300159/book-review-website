Related issue: [GitHub Issue #1](https://github.com/s1300159/book-review-website/issues/1)

## 1. Prepare the Required Dependency

- [x] 1.1 Add Pillow with `uv` as the required dependency for Django's `ImageField`.

## 2. Implement the Confirmed Models

- [x] 2.1 Add required `title`, optional `cover_image`, and optional `description` fields to Book.
- [x] 2.2 Add required `text`, 1-to-5 `rating`, automatic `created_at`, and the confirmed Book and User foreign keys to Review.
- [x] 2.3 Add application-level duplicate-review validation and a named database `UniqueConstraint` for `(user, book)`.
- [x] 2.4 Add 1-to-5 rating validators and a matching named database `CheckConstraint`.
- [x] 2.5 Add an ORM-derived Book average-rating behavior that returns `None` for a book without reviews and does not store an average column.
- [x] 2.6 Implement readable `Book.__str__()` and `Review.__str__()` methods.

## 3. Create and Review the Migration

- [x] 3.1 Run `uv run python manage.py makemigrations reviews` to create a new migration without editing an old migration.
- [x] 3.2 Review the generated migration for exact fields, `CASCADE` relationships, reverse names, uniqueness, and the 1-to-5 rating constraint.
- [x] 3.3 Run `uv run python manage.py migrate` and confirm the migration applies successfully.

## 4. Add Model Tests

- [x] 4.1 Add tests for required and optional Book fields, Review creation, and forward and reverse relationships.
- [x] 4.2 Add tests for both model string representations.
- [x] 4.3 Add tests for application-level and database-level duplicate-review prevention.
- [x] 4.4 Add tests for 1-to-5 application rating validation and the database check constraint.
- [x] 4.5 Add tests for derived average-rating calculation across multiple reviews and `None` when no reviews exist.

## 5. Update Documentation and Verify

- [x] 5.1 Update `docs/exercise-2-specification.md` with the exact implemented fields, relationships, constraints, `None` average behavior, and string behavior while leaving display rounding out of scope.
- [x] 5.2 Run `uv run python manage.py check`.
- [x] 5.3 Run `uv run pytest`.
- [x] 5.4 Run `uv run black --check .` and `uv run pylint reviews config`.
- [x] 5.5 Review the final diff to confirm no URL, view, form, template, custom User, review editing, review deletion, or dependency other than Pillow was introduced.

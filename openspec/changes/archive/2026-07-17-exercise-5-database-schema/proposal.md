## Why

The Book Review Website needs an initial database schema before its planned book, review, rating, and search features can be implemented. Exercise 5 establishes this schema using Django's ORM while preserving the project's existing Django setup and standard authentication.

Related issue: [GitHub Issue #1](https://github.com/s1300159/book-review-website/issues/1)

## What Changes

- Add `Book` and `Review` model definitions to the `reviews` app.
- Relate each review to one book and one Django authentication user.
- Enforce at the database level that a user can review a given book at most once.
- Provide readable `__str__()` behavior for both models.
- Calculate book average ratings from related review rating values rather than storing a separate average.
- Create a new initial migration for the `reviews` models without modifying existing migrations.
- Add focused model tests for fields, relationships, constraints, average-rating behavior, and string representations.
- Update the project specification document with the approved database schema.
- Add Pillow as the required image-processing dependency for Django's `ImageField`.

## Capabilities

### New Capabilities

- `book-review-data-model`: Defines the Book and Review schema, their relationship to Django's standard User model, database constraints, derived average ratings, and model display behavior.

### Modified Capabilities

None. There are currently no formal specifications under `openspec/specs/`.

## Impact

- Expected implementation files: `reviews/models.py`, a new file under `reviews/migrations/`, `reviews/tests.py`, `docs/exercise-2-specification.md`, `pyproject.toml`, and `uv.lock`.
- Django's existing authentication system and SQLite development database remain in use.
- Pillow is the only planned new package and is required by Django's `ImageField`.
- No custom user model, URL, view, form, template, review editing, or review deletion capability is introduced.

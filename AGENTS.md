# AGENTS.md

## Project Scope
This is a Django web application for posting and reading book reviews.

Main features:
- Browse books registered in the system.
- Search books by partial title.
- Open a book detail page.
- Read reviews and average ratings.
- Allow registered users to write one review for each book.
- Sort or filter books by rating.

Main app:
- `reviews/` — book listing, search, book details, reviews, and ratings.
- `config/` — Django settings, URL configuration, ASGI, and WSGI settings.

## Important Project Conventions
- Keep database structure in `reviews/models.py`.
- Keep request handling in `reviews/views.py`.
- Do not put business rules inside templates.
- Prefer Django ORM over raw SQL.
- Use Django forms or ModelForms for user input validation when appropriate.
- Keep templates focused on presentation, not database or permission logic.

## Commands
- Run the development server: `uv run python manage.py runserver`
- Create migrations: `uv run python manage.py makemigrations`
- Apply migrations: `uv run python manage.py migrate`
- Run tests: `uv run pytest`
- Run Django checks: `uv run python manage.py check`
- Format Python code: `uv run black .`
- Run linting: `uv run pylint reviews config`

## Fragile Areas
- The rule that one user can write at most one review for the same book.
- Rating calculation and average rating display.
- Book-title search and rating-based filtering or sorting.
- Relationships among Book, Review, and User.
- Any permission checks related to creating, editing, or deleting reviews.

## Coupling Changes
When changing:
- Models → also check migrations, admin configuration, tests, forms, and views.
- Review rules → also check uniqueness constraints, validation, and related tests.
- Rating logic → also check book list pages, detail pages, filters, sorting, and tests.
- URL names → also check templates, redirects, and URL configuration.
- Permissions → also check views, templates, and tests.

## Constraints
- Do not edit old migration files after they have been applied. Create a new migration instead.
- Do not rename URL names or model fields unless explicitly required.
- Prefer small, focused changes over large refactors.
- Do not introduce a frontend framework unless it is necessary. Prefer Django templates and HTMX.
- Keep dependencies managed through `uv`.

## Documentation Usage
- Use `openspec/specs/*` as the source of truth for technical and runtime documentation.
- Use `openspec/config.yaml` for project-level context.
- Use `openspec/notes/*` only for ideas or backlog notes, not as authoritative specifications.
- Keep code and specifications consistent.
- When code and documentation conflict, report the conflict and propose a correction.
- When a new feature is implemented, suggest updating the relevant OpenSpec document.

## Test Expectations
Add or update tests for:
- Creating reviews.
- Preventing duplicate reviews by the same user for the same book.
- Searching books by partial title.
- Filtering or sorting books by rating.
- Average rating calculation.
- Permissions for review creation or modification.

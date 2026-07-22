# AGENTS.md

## Project Scope
This is a Django web application for posting and reading book reviews.

Main directories:
- `reviews/` — the main app for books, reviews, ratings, search, and listing features.
- `config/` — Django settings, URL configuration, ASGI, and WSGI settings.

## Current State
- The initial Django project and `reviews` app setup are complete.
- Exercise 5 implemented the `Book` and `Review` models, their migration,
  validation and database constraints, derived average rating, admin
  registration, tests, and data-model specification.
- Exercise 6 implements minimal GET-only function views and named URLs for
  home, book listing, book detail with reviews and average rating, partial-title
  search, a read-only review placeholder, and a book-list redirect.
- Review form processing and persistence, rating sorting and filtering, and
  pagination have not been implemented.
- `forms.py` and template directories do not exist yet.
- Development tools including pytest, Black, and Pylint are configured.
- OpenSpec has accepted `book-review-data-model` and `basic-book-views`
  specifications.

## Target Features
- List registered books.
- Search books by partial title match.
- Show book details.
- Display reviews and star ratings.
- Allow logged-in users to submit reviews.
- Allow at most one review per user for each book.
- Calculate and display the average rating for each book.
- Sort books by rating.
- Filter books by a minimum rating.
- Paginate book listings.
- Use HTMX for partial page updates when dynamic interactions required by the coursework benefit from it.

Review editing and deletion are not currently confirmed required features. Add them only if a future task explicitly requires them.

## Development Approach
- Work database-first and backend-first.
- Prefer small, focused changes over large refactors.
- Keep database structure in `reviews/models.py` and request handling in `reviews/views.py`.
- Use the Django ORM rather than raw SQL.
- Keep complex business, database, and permission logic out of templates.
- Use Django forms or ModelForms for user input validation when appropriate.
- Prefer Django's standard authentication system.
- Prevent duplicate reviews both in application validation and with a database constraint.
- Treat HTMX as an optional implementation choice for required dynamic interactions; it is not currently installed or in use.
- Add or update tests for new features where practical.
- Do not commit or push unless explicitly instructed.
- Before starting work, explain the plan in Japanese. After completing work, explain the changes and test results in Japanese.

## Commands
- Run the development server: `uv run python manage.py runserver`
- Create migrations: `uv run python manage.py makemigrations`
- Apply migrations: `uv run python manage.py migrate`
- Run tests: `uv run pytest`
- Run Django checks: `uv run python manage.py check`
- Format Python code: `uv run black .`
- Run linting: `uv run pylint reviews config`

## Coupled and Fragile Areas
- Do not edit old migration files after they have been applied. Create a new migration for model changes.
- When changing models, also check migrations, admin configuration, tests, forms, and views.
- When changing review rules, check validation, database uniqueness constraints, permissions, and tests.
- When changing rating logic, check list and detail pages, filtering, sorting, and tests.
- When changing URL names, check templates, redirects, and URL configuration.
- Give particular attention to duplicate-review prevention, average-rating calculations, partial-title search, rating filters, sorting, pagination, and authentication requirements.

## Documentation
- If specifications are added under `openspec/specs/`, treat them as the formal source of truth.
- `openspec/specs/book-review-data-model/spec.md` is the accepted formal data-model specification.
- `openspec/config.yaml` currently contains only its initial configuration.
- When no OpenSpec document exists, check the task description, `README.md`, and implementation code.
- Keep code and any specifications consistent. Report conflicts and propose a correction.
- When implementing a new feature covered by OpenSpec, suggest updating the relevant specification.

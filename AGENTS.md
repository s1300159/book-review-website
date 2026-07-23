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
- Exercise 7 renders the book-list and book-detail views through app-namespaced
  templates that inherit a shared base layout, and records up to five unique
  recently viewed Book IDs in each browser session.
- Review form processing and persistence, rating sorting and filtering, and
  pagination have not been implemented.
- `forms.py` does not exist; the current templates cover only the shared base,
  book list, and book detail.
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
- Before starting work, explain the plan in Japanese. After completing work, report the changes, verification results, and remaining decisions in Japanese.

## Git Workflow and Autonomous Execution
For work on a dedicated feature branch based on an approved Issue or OpenSpec change, Codex may proceed without waiting for confirmation at every step. This includes:
- Reviewing the Issue, `AGENTS.md`, docs, OpenSpec, and current code.
- Creating or updating an OpenSpec proposal and design, then applying it within the approved Issue or OpenSpec scope.
- Adding necessary dependencies; implementing the scoped feature; creating and applying migrations; and adding or updating tests.
- Running formatting, Django checks, tests, static analysis, and migration checks; performing focused refactoring needed for the approved work.
- Updating related documentation and OpenSpec tasks.
- Staging only related changes, committing and pushing to the feature branch, and creating a Pull Request. If PR creation is unavailable, prepare its title and body.
- Committing and pushing follow-up fixes to an existing Pull Request.

For minor implementation decisions, use the Issue, OpenSpec, docs, existing code, and this file as guidance, then explain the decision in the final report.

Recommended flow:
1. Review the Issue, this file, docs, and OpenSpec.
2. Design with OpenSpec when needed, then implement on a feature branch.
3. Run tests, formatting, static analysis, Django checks, and focused refactoring.
4. Commit and push the feature branch, then create a Pull Request.
5. Apply review feedback and push follow-up commits.
6. After explicit user approval, archive OpenSpec, merge, and delete the feature branch.

Do not perform the following without explicit user permission:
- Merge a Pull Request into `main`, or commit or push directly to `main`.
- Delete a feature branch, archive an OpenSpec change, or manually close an Issue.
- Use destructive Git operations such as `git reset --hard`, or discard the user's uncommitted changes.
- Change or display credentials, secrets, or other sensitive information.
- Add large features or perform broad refactoring outside the approved assignment scope.

A Pull Request may use `Closes #<number>` so that merging closes its Issue automatically.

Before committing and pushing, confirm that:
- No unrelated files are included and `git diff --check` succeeds.
- Relevant tests, Django system checks, and Black checks succeed.
- Migrations are consistent and no model change is missing a new migration.
- Newly written code has no serious Pylint warning. Report existing warnings separately from warnings introduced by the current change.

Use short, specific English commit messages. Use `Refs #<number>` for work-in-progress commits when appropriate, and `Closes #<number>` in the Pull Request body that should close an Issue.

Stop and report instead of proceeding when:
- Specifications materially conflict, or the work conflicts with `main` or other changes.
- Tests fail and the cause cannot be resolved safely.
- A migration may destroy existing data.
- Authentication, additional permissions, or work far beyond the assignment scope is required.
- A decision is needed about merging a Pull Request or archiving an OpenSpec change.

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

## Documentation and OpenSpec
- If specifications are added under `openspec/specs/`, treat them as the formal source of truth.
- `openspec/specs/book-review-data-model/spec.md` is the accepted formal data-model specification.
- `openspec/config.yaml` currently contains only its initial configuration.
- When no OpenSpec document exists, check the task description, `README.md`, and implementation code.
- Keep code and specifications consistent. Report conflicts and propose a correction.
- Update the relevant specification when implementing a feature covered by OpenSpec.

## Work Report
After work, report concisely in Japanese:
- Implementation and changed files.
- Tests and verification results.
- Warnings or unresolved items.
- Commit and push results, Pull Request status, and `git status`.
- Decisions that still require the user.

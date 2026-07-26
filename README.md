# Book Review Website

## Overview

This project is a web application for browsing books, searching for books by title, reading reviews, and posting book reviews with star ratings.

The project is being developed for the Web Engineering course at the University of Aizu.

## Implemented Features

- Browse a list of books
- Search books by partial title and optional minimum average rating
- View book details, reviews, and average ratings
- Log in with Django's standard authentication interface
- Post one review for each book as an authenticated user
- Edit a review as its author
- Keep up to five recently viewed Book IDs in each browser session
- Update Book search results dynamically with HTMX
- Use a shared semantic, responsive, and keyboard-accessible interface

## Planned Features

- User registration
- Sort books by rating
- Paginate book listings
- Review deletion, if required by a later exercise

## Development Environment

- Python 3.11
- Django 5
- uv
- SQLite for local development
- Git and GitHub

## Development Tools

- Black for code formatting
- Pylint and pylint-django for linting
- pytest and pytest-django for testing
- coverage for test coverage measurement

## Local Windows Deployment

This deployment runs on one trusted Windows machine with Waitress, WhiteNoise,
SQLite, and local uploaded media. It does not require a cloud account.

### Prerequisites

- Python 3.11 or later
- `uv`
- A PowerShell terminal opened in the project directory

Install the locked production dependencies:

```powershell
uv sync --no-dev
```

Generate a new secret value, copy the output, and set the production
environment. Do not save the value in the repository or a committed `.env`
file.

```powershell
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DJANGO_SECRET_KEY = "<paste-generated-secret>"
$env:DJANGO_DEBUG = "false"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
$env:DJANGO_SERVE_MEDIA = "true"
```

`DJANGO_SERVE_MEDIA=true` is only for this trusted loopback deployment. Apply
database migrations, collect static assets, and optionally create an
administrator:

```powershell
uv run python manage.py check --deploy
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
uv run python manage.py createsuperuser
```

Start the production WSGI server:

```powershell
uv run waitress-serve --listen=127.0.0.1:8000 config.wsgi:application
```

Open `http://127.0.0.1:8000/` in a browser. Press `Ctrl+C` in the server
terminal to stop Waitress.

### Static and uploaded files

`collectstatic` writes compressed, hashed CSS, JavaScript, and admin assets to
the ignored `staticfiles/` directory. WhiteNoise serves these files through
Waitress. Do not commit `staticfiles/`.

Book covers remain in the ignored `media/` directory and are not managed by
WhiteNoise. Back up `db.sqlite3` and `media/` together because database rows
refer to those files. For public or multi-user hosting, set
`DJANGO_SERVE_MEDIA=false` and serve media through Nginx or external object
storage.

### HTTPS deployment requirements

The loopback deployment intentionally uses HTTP. Consequently,
`check --deploy` reports warnings for HSTS, HTTPS redirection, and secure
session/CSRF cookies. Before exposing the application publicly, terminate TLS
and configure:

```powershell
$env:DJANGO_SECURE_SSL_REDIRECT = "true"
$env:DJANGO_SESSION_COOKIE_SECURE = "true"
$env:DJANGO_CSRF_COOKIE_SECURE = "true"
$env:DJANGO_SECURE_HSTS_SECONDS = "31536000"
$env:DJANGO_SERVE_MEDIA = "false"
```

Review HSTS carefully before enabling it. A reverse proxy must also forward
the original HTTPS scheme correctly.

### Development server

`uv run python manage.py runserver` remains for development only and defaults
to `DEBUG=True` when `DJANGO_DEBUG` is unset. Waitress and collected
WhiteNoise assets are the documented production path.

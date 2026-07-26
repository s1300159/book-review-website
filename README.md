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
- Use a shared semantic, responsive, and keyboard-accessible interface

## Planned Features

- User registration
- Sort books by rating
- Paginate book listings
- Review deletion, if required by a later exercise
- HTMX interactions, if a later exercise benefits from them

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

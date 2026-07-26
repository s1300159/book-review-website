## Why

The application currently relies on Django's development defaults and server. Exercise 11 needs a repeatable local Windows production configuration that protects deployment settings and serves collected static assets without requiring an external hosting account.

## What Changes

- Add Waitress as the production WSGI application server.
- Add WhiteNoise middleware and compressed, hashed static-file storage.
- Read the secret key, debug mode, allowed hosts, and optional security settings from environment variables.
- Define local static and media roots, including a loopback-only media-serving option.
- Document and verify the complete PowerShell deployment sequence under `DEBUG=False`.

## Capabilities

### New Capabilities

- `project-deployment`: Defines local Windows hosting, application/static/media serving, environment configuration, deployment commands, and production verification.

### Modified Capabilities

None.

## Impact

- Updates project dependencies, Django settings and URL configuration, `.gitignore`, focused tests, and `README.md`.
- Generates collected static files only as ignored deployment output.
- Does not change models, migrations, database technology, application features, or external infrastructure.

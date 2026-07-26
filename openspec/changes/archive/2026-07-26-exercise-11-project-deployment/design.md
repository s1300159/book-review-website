## Context

The Django application currently runs with hard-coded development settings and `runserver`. The approved deployment target is one local Windows machine using SQLite and local uploaded files, without Docker, Nginx, cloud storage, or HTTPS certificate work.

## Goals / Non-Goals

**Goals:**

- Start the WSGI application with Waitress under `DEBUG=False`.
- Require production secrets and hosts while retaining safe development defaults.
- Collect and serve compressed, hashed static assets through WhiteNoise.
- Store uploaded files in an ignored local directory and describe backup and serving limits.

**Non-Goals:**

- Public internet hosting, reverse-proxy setup, TLS provisioning, external databases or object storage, and CI/CD.
- Model, migration, UI, or interaction changes.

## Decisions

- Keep one settings module and parse explicit environment variables to minimize deployment complexity.
- Fail settings initialization when `DEBUG=False` lacks a secret key or allowed host instead of using an unsafe fallback.
- Place WhiteNoise directly after `SecurityMiddleware` and use `CompressedManifestStaticFilesStorage`.
- Keep media outside WhiteNoise. An explicit `DJANGO_SERVE_MEDIA=true` option enables Django's simple media view only for a trusted loopback deployment; public deployments require a dedicated web server or object storage.
- Keep local HTTP-compatible security defaults and expose HTTPS-only controls through environment variables so the deployment check reports the remaining local HTTP trade-offs accurately.

## Risks / Trade-offs

- SQLite and local media are tied to one machine → back up `db.sqlite3` and `media/` together.
- The optional Django media view is not suited to public traffic → bind Waitress to loopback and disable it when moving behind a real media server.
- Local HTTP cannot enable secure cookies, redirect-to-HTTPS, or HSTS → document the expected deployment-check warnings and the environment settings required after TLS is added.

# project-deployment Specification

## Purpose
TBD - created by archiving change exercise-11-project-deployment. Update Purpose after archive.
## Requirements
### Requirement: Local Windows production hosting
The system SHALL support deployment on a local Windows machine through Waitress using the existing `config.wsgi:application`, SQLite database, and `uv`-managed dependencies.

#### Scenario: Application server starts
- **WHEN** an operator supplies valid production environment variables and runs the documented Waitress command
- **THEN** Waitress listens on the documented loopback address
- **AND** the home, Book-list, Book-search, login, and admin URLs remain reachable

### Requirement: Environment-based deployment settings
The system SHALL read the secret key, debug mode, and allowed hosts from environment variables, SHALL parse documented boolean values explicitly, and SHALL refuse to initialize with `DEBUG=False` when the secret key or allowed-host list is missing.

#### Scenario: Valid production settings are supplied
- **WHEN** `DJANGO_DEBUG` is false and non-empty `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS` values are supplied
- **THEN** Django initializes with debug output disabled and only the configured hosts allowed

#### Scenario: Production secret is missing
- **WHEN** `DJANGO_DEBUG` is false and `DJANGO_SECRET_KEY` is empty or missing
- **THEN** settings initialization fails without substituting a development secret

#### Scenario: Production allowed hosts are missing
- **WHEN** `DJANGO_DEBUG` is false and `DJANGO_ALLOWED_HOSTS` is empty or missing
- **THEN** settings initialization fails without accepting every host

#### Scenario: Debug value is invalid
- **WHEN** `DJANGO_DEBUG` contains an undocumented boolean value
- **THEN** settings initialization fails with a configuration error

### Requirement: Collected production static files
The system SHALL collect application static assets into an ignored `STATIC_ROOT` and SHALL serve them through WhiteNoise using compressed, manifest-backed filenames.

#### Scenario: Static files are collected
- **WHEN** an operator runs the documented `collectstatic --noinput` command
- **THEN** the project CSS and local `htmx.min.js` are written under `STATIC_ROOT`
- **AND** the generated directory remains outside version control

#### Scenario: Production static assets are requested
- **WHEN** a browser requests the rendered CSS or HTMX asset URL from Waitress
- **THEN** WhiteNoise returns HTTP 200 under `DEBUG=False`

### Requirement: Local uploaded media policy
The system SHALL store uploaded Book covers under an ignored local `MEDIA_ROOT`, expose them through `MEDIA_URL`, and keep uploaded media outside WhiteNoise's static-file pipeline.

#### Scenario: Trusted loopback media serving is enabled
- **WHEN** `DJANGO_SERVE_MEDIA` is true for the documented loopback-only deployment
- **THEN** the application can return existing files from `MEDIA_ROOT` under `MEDIA_URL`

#### Scenario: Deployment moves beyond loopback
- **WHEN** the application is exposed through a public or multi-user hosting environment
- **THEN** the operator is instructed to disable the simple media route and use a dedicated web server or object storage

#### Scenario: Deployment data is backed up
- **WHEN** an operator prepares a backup
- **THEN** the documentation requires both the SQLite database and media directory to be preserved together

### Requirement: Repeatable deployment commands
The system SHALL document PowerShell commands for dependency synchronization, environment setup, migration, static collection, optional superuser creation, Waitress startup, browser access, server shutdown, and the distinction from Django's development server.

#### Scenario: Operator follows the deployment guide
- **WHEN** an operator follows the README deployment section on Windows
- **THEN** each command uses the actual project paths and WSGI module
- **AND** no `.env`, secret value, database, media file, or collected static output is committed

### Requirement: Production verification
The system SHALL be verified under `DEBUG=False` with Django checks, migration application, static collection, a running Waitress process, allowed/disallowed host behavior, and HTTP requests for primary routes and static assets.

#### Scenario: Local production smoke test passes
- **WHEN** Waitress runs with a valid loopback production configuration
- **THEN** allowed-host requests for primary pages and static assets return successful responses
- **AND** a request with an unlisted host is rejected
- **AND** no deployment secret appears in response content or server logs

#### Scenario: Deployment check reports local HTTP limits
- **WHEN** `check --deploy` runs for the local HTTP configuration
- **THEN** HTTPS-only warnings are recorded rather than reported as resolved
- **AND** the README identifies the settings that must change before public HTTPS exposure

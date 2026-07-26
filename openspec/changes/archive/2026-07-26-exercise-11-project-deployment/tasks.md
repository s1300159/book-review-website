## 1. Dependencies and settings

- [x] 1.1 Add Waitress and WhiteNoise with `uv`.
- [x] 1.2 Add validated environment settings, WhiteNoise, static/media roots, and HTTPS controls.
- [x] 1.3 Add the explicit loopback-only media route and ignore deployment output.

## 2. Documentation and tests

- [x] 2.1 Document the PowerShell deployment sequence, static/media policy, backups, shutdown, and HTTPS limits.
- [x] 2.2 Add focused tests for production environment parsing and deployment configuration.

## 3. Verification

- [x] 3.1 Run development and production checks, tests, formatting, linting, migration and static collection checks.
- [x] 3.2 Start Waitress under `DEBUG=False` and verify pages, assets, host filtering, secret safety, and process cleanup.
- [x] 3.3 Complete strict OpenSpec validation and review the final diff.

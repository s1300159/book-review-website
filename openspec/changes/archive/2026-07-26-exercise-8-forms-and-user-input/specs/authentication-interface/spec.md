## ADDED Requirements

### Requirement: Standard Django authentication URLs
The project SHALL include Django's standard authentication URL configuration without removing the existing admin or reviews routes. It SHALL provide a valid named `login` route and SHALL NOT add a user-registration workflow.

#### Scenario: Login URL is reversible
- **WHEN** application code reverses the configured login URL name
- **THEN** Django returns the standard login path

#### Scenario: Registration remains unavailable
- **WHEN** the Exercise 8 authentication interface is inspected
- **THEN** it contains no user-registration view, form, or route

### Requirement: Named login settings
The project SHALL configure `LOGIN_URL` and `LOGIN_REDIRECT_URL` as valid named URL references so protected Review views can redirect to login and a login without a safe `next` destination can redirect to an existing application page.

#### Scenario: Protected workflow uses the configured login
- **WHEN** an unauthenticated user requests a login-required Review view
- **THEN** Django redirects through the configured named login URL

#### Scenario: Login has a default named destination
- **WHEN** a user logs in without a usable `next` value
- **THEN** Django redirects to the configured named application URL

### Requirement: Minimal secure login template
The system SHALL provide `registration/login.html` using Django's standard authentication form. It SHALL include a CSRF token, display field and non-field errors, preserve a supplied `next` value in a hidden field, and retain automatic escaping and the project's shared presentation where practical.

#### Scenario: Invalid credentials are displayed safely
- **WHEN** a user submits invalid login credentials with a valid CSRF token
- **THEN** the response is HTTP 200 and the login template displays the authentication form's errors without authenticating the user

#### Scenario: Login POST requires CSRF
- **WHEN** a client submits the login form without a valid CSRF token under normal CSRF enforcement
- **THEN** Django rejects the request and does not authenticate the session

#### Scenario: Next destination is preserved
- **WHEN** a user reaches login from a protected Review URL and successfully authenticates
- **THEN** Django redirects the user back to that safe requested Review URL

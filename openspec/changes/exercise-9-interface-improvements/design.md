## Context

Exercise 8 pages use Django templates except for the home response. They have
basic semantic elements and form labels but no static stylesheet, responsive
layout system, or consistent presentation for cards, messages, and actions.

## Goals / Non-Goals

**Goals:**

- Use one shared base template and one app-scoped stylesheet.
- Keep content readable and operable at desktop, tablet, and mobile widths.
- Improve semantic structure, focus visibility, labels, errors, messages, and
  cover-image alternatives.
- Preserve every existing request, permission, validation, and persistence
  contract.

**Non-Goals:**

- New features, model or migration changes, JavaScript, HTMX, CSS frameworks,
  sorting, pagination, registration, Review deletion, or broad refactoring.

## Decisions

- Render the home response through `reviews/home.html` so every page inherits
  the same metadata, navigation, messages, and stylesheet.
- Keep presentation in `reviews/static/reviews/style.css`; templates use a
  small vocabulary of structural classes and no inline visual styles.
- Use CSS Grid/Flexbox with one mobile media query, fluid form controls, and
  bounded images rather than device-specific layouts.
- Prefer native semantic HTML and existing Django label/error rendering; add
  ARIA only for the skip target, current navigation, and live messages.

## Risks / Trade-offs

- [Risk] Template markup changes could make brittle assertions fail. →
  Preserve user-facing text and URLs, and add behavior-focused interface tests.
- [Risk] Uploaded cover dimensions vary. → Constrain width, aspect ratio, and
  object fitting in CSS while retaining meaningful alternative text.
- [Risk] A shared stylesheet can affect every page. → Use app-scoped classes,
  a small reset, and verify all existing workflows.

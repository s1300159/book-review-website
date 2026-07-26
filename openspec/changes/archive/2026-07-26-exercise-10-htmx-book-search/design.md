## Context

The existing search view already validates `q` and `min_rating` with `BookSearchForm` and applies both filters to one QuerySet. The page is server-rendered and accessible without JavaScript.

## Goals / Non-Goals

**Goals:**

- Update only the search result region when the title or minimum rating changes.
- Reuse the existing form, filter logic, book cards, and empty states.
- Preserve URL-based full-page GET search as the fallback.

**Non-Goals:**

- HTMX conversion of review or authentication flows.
- Pagination, sorting, autocomplete, custom JavaScript, or model changes.

## Decisions

- Use `django-htmx` middleware so the view can select a template through `request.htmx`.
- Load the package's locally vendored `htmx.min.js` through its Django template tag, avoiding a runtime CDN dependency.
- Put `hx-get`, delayed input/change triggers, `hx-target`, `hx-swap`, and URL history updates on the existing GET form.
- Render one result partial from both the full page and HTMX responses so filtering and presentation are not duplicated.

## Risks / Trade-offs

- Frequent typing can create excess requests → use a 300 ms delay and the `changed` modifier.
- Partial responses can diverge from full-page output → include the same partial in the full page and test both paths.
- JavaScript may be unavailable → retain the form action, GET method, and submit button.

# Exercise 10: HTMX book search

The existing GET search form is progressively enhanced with one HTMX interaction.

- **Interaction:** Filter books by partial title and optional minimum average rating.
- **Trigger:** A changed title after a 300 ms delay, a minimum-rating change, or form submission.
- **Target:** The `#book-results` region containing book cards and empty states.
- **Server response:** HTMX GET requests receive only `partials/book_results.html`; normal GET requests receive the complete search page.

The same `BookSearchForm` and server-side QuerySet logic handle both response modes. The form retains its named action, GET method, query parameters, and submit button, so direct URLs, reload, browser history, and operation without HTMX remain available.

# Book Review Website

## Short description

This project is a simple book review website. Users can browse books, search for books by title, read other users' reviews, and post their own reviews with star ratings.

The main purpose of this system is to let users find books and share their opinions using a database-backed web application. This topic is simple, but it still includes important web application features such as search, user input, validation, and database relationships.

## Main user actions

Users can see a list of books registered in the system.

Users can search for books by entering part of a book title.

Users can open a book detail page to see the book information, reviews, and average rating.

Registered users can write one review for each book.

Users can sort books by star rating and filter books by a minimum rating.

Users can move between pages in the book list using pagination.

## Main data entities

The system will mainly use three data entities: User, Book, and Review.

### User

The User entity stores information about registered users.

Main fields:

* username
* authentication information

A registered user can write reviews for books.

### Book

The Book entity stores information about each book.

Main fields:

* title
* cover image
* description

One book can have many reviews. The average rating of a book is calculated from the ratings in its reviews.

### Review

The Review entity stores a review written by a user.

Main fields:

* review text
* star rating
* created date
* user
* book

Each review belongs to one user and one book. A user should not be able to write more than one review for the same book. Duplicate reviews for the same user and book are prevented by both application-level validation and a database constraint. The star rating is used when calculating the average rating of the book.

## Main user flow

1. The user opens the website.
2. The system displays a list of books with titles, cover images, and average ratings.
3. The user enters part of a book title in the search form.
4. The system searches the database and displays matching books.
5. The user clicks one book from the list.
6. The book detail page is displayed. It shows the book information, average rating, and reviews.
7. If the user is registered and logged in, the user can write a review and choose a star rating.
8. When the review is submitted, the system checks whether the same user has already reviewed the book.
9. If the review is valid, it is saved in the database.
10. The book detail page is updated, and the new average rating is shown.

## Architecture sketch

The application uses a simple web application architecture. The browser sends requests to the Django application, and the Django application reads from and writes to the database.

```text
[Browser]
  - book list page
  - search form
  - book detail page
  - review form

        |
        | HTTP request / user input
        v

[Django Application Logic]
  - handle book search
  - display book details
  - validate review submission
  - prevent duplicate reviews
  - calculate average rating

        |
        | ORM queries
        v

[Database]
  - User table
  - Book table
  - Review table
```

## Database schema

### Book model

The Book model is implemented in `reviews/models.py`.

Fields:

* `title`: required `CharField(max_length=200)`
* `cover_image`: optional `ImageField(upload_to="book_covers/", blank=True)`
* `description`: optional `TextField(blank=True)`

`Book.__str__()` returns the book title.

The average rating is not stored as a database field. It is calculated with the
Django ORM from the `rating` values of related reviews. A book without reviews
has an average rating of `None`. Display rounding is outside the scope of
Exercise 5.

### Review model

The Review model is implemented in `reviews/models.py`.

Fields:

* `text`: required `TextField`
* `rating`: required `IntegerField` limited to values from 1 through 5
* `created_at`: `DateTimeField(auto_now_add=True)`
* `book`: required foreign key to Book with `CASCADE` and
  `related_name="reviews"`
* `user`: required foreign key to Django's configured authentication User with
  `CASCADE` and `related_name="reviews"`

`Review.__str__()` returns a concise string containing the username and book
title.

### Relationships and constraints

The project uses Django's standard authentication User model and does not
define a custom User model.

Each Review belongs to exactly one Book and one User. A named database
`UniqueConstraint` on `user` and `book` guarantees that a user can review the
same book only once. Model validation also reports an existing review for the
same user and book before saving when validation is run.

The rating field uses `MinValueValidator(1)` and `MaxValueValidator(5)`.
A named database `CheckConstraint` also guarantees that stored ratings are
between 1 and 5.

## Exercise 6 view and URL contract

Exercise 6 provides a minimal, read-only HTTP layer before templates and forms
are introduced. All application URLs use the `reviews` namespace, all six
views are function-based and accept GET only, and unsupported methods return
HTTP 405 without changing Book or Review data.

| Callable | URL and name | URL/query input | Processing | Response |
| --- | --- | --- | --- | --- |
| `home(request)` | `GET /` (`reviews:home`) | No URL or query argument. | Builds a minimal site introduction and reverses the named book-list and search URLs for navigation. | Minimal HTML `HttpResponse`, HTTP 200. |
| `book_list(request)` | `GET /books/` (`reviews:book_list`) | No URL or query argument. | Reads all registered Book rows and displays their titles. Rating sorting, filtering, and pagination are deferred. | HTTP 200 with linked book titles, or an explicit no-books message. |
| `book_detail(request, book_id)` | `GET /books/<int:book_id>/` (`reviews:book_detail`) | Required integer URL argument `book_id`; no query argument. | Uses the ID to fetch a Book, derives its average rating through the existing model property, and reads only its related Reviews with users, newest first. | HTTP 200 with title, description, average rating, and review authors, ratings, and text. A missing Book returns HTTP 404. |
| `book_search(request)` | `GET /books/search/` (`reviews:book_search`) | Optional query argument `q`; no URL argument. | Trims `q` and uses case-insensitive partial-title matching for a non-empty value. A missing, empty, or whitespace-only value does not execute an all-books empty-string match. | HTTP 200 with the query and linked matches, a no-match message, or a prompt to enter a title. |
| `review_create(request, book_id)` | `GET /books/<int:book_id>/review/` (`reviews:review_create`) | Required integer URL argument `book_id`; no query argument. | Confirms that the Book exists and displays a placeholder. It does not build a form, require login, validate input, or create or update a Review. | HTTP 200 placeholder naming the Book. A missing Book returns HTTP 404. |
| `book_list_redirect(request)` | `GET /books-redirect/` (`reviews:book_list_redirect`) | No URL or query argument. | Resolves the named `reviews:book_list` route rather than hard-coding its destination. | `HttpResponseRedirect`, HTTP 302, to `/books/`. |

Dynamic Book, Review, username, and search-query values are escaped before
they are included in HTML. Exercise 7 replaces the direct HTML construction for
the book-list and book-detail responses with Django templates while preserving
this URL contract. Exercise 8 or later may add the review form, authentication
requirement, validation, and persistence.

## Exercise 7 templates and session state

`reviews/base.html` defines the shared document structure for the
template-rendered book pages: a header, navigation using the existing named
URLs, a main-content block, and a footer. `reviews/book_list.html` and
`reviews/book_detail.html` extend that base. Presentation choices and empty
states live in the templates, while Book lookup, Review ordering, and average
rating calculation remain in the views and models. Django automatic escaping
remains enabled.

The system keeps different kinds of state separate:

| State type | Information and lifetime |
| --- | --- |
| Persistent domain state | Book, Review, and configured User records remain in the database as the source of truth. |
| Temporary session state | `recently_viewed_book_ids` contains at most five unique integer Book IDs for one browser session, ordered most recent first. |
| Request state | Search `q`, and future `sort`, `min_rating`, and `page` controls, remain GET parameters and are not copied into the session. |
| Response context | The current books, selected book, ordered reviews, and derived average rating exist only while rendering one response. |

A successful existing-Book detail request updates the recent-book session
history. Reopening a Book moves its ID to the front, a sixth distinct Book
evicts the oldest ID, and a missing Book does not change the session. Missing
or malformed existing history is normalized safely. The session does not store
Book content, Review text or ratings, User or authentication data, or GET
control values, and Exercise 7 does not display the recent history.

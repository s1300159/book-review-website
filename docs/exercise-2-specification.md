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

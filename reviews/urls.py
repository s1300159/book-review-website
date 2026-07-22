from django.urls import path

from reviews import views

app_name = "reviews"

urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.book_list, name="book_list"),
    path("books/search/", views.book_search, name="book_search"),
    path(
        "books/<int:book_id>/review/",
        views.review_create,
        name="review_create",
    ),
    path("books/<int:book_id>/", views.book_detail, name="book_detail"),
    path(
        "books-redirect/",
        views.book_list_redirect,
        name="book_list_redirect",
    ),
]

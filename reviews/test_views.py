from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from django.utils import timezone

from reviews import views
from reviews.models import Book, Review


@pytest.mark.parametrize(
    ("url_name", "view", "kwargs", "expected_path"),
    [
        ("home", views.home, None, "/"),
        ("book_list", views.book_list, None, "/books/"),
        ("book_search", views.book_search, None, "/books/search/"),
        (
            "book_detail",
            views.book_detail,
            {"book_id": 7},
            "/books/7/",
        ),
        (
            "review_create",
            views.review_create,
            {"book_id": 7},
            "/books/7/review/",
        ),
        (
            "book_list_redirect",
            views.book_list_redirect,
            None,
            "/books-redirect/",
        ),
    ],
)
def test_named_url_reverses_and_resolves(url_name, view, kwargs, expected_path):
    url = reverse(f"reviews:{url_name}", kwargs=kwargs)

    assert url == expected_path
    assert resolve(url).func is view


def test_home_returns_website_identity_and_named_navigation(client):
    response = client.get(reverse("reviews:home"))

    assert response.status_code == 200
    assert b"Book Review Website" in response.content
    assert reverse("reviews:book_list").encode() in response.content
    assert reverse("reviews:book_search").encode() in response.content


@pytest.mark.django_db
def test_book_list_displays_registered_books(client):
    Book.objects.create(title="Dune")
    Book.objects.create(title="Foundation")

    response = client.get(reverse("reviews:book_list"))

    assert response.status_code == 200
    assert b"Dune" in response.content
    assert b"Foundation" in response.content


@pytest.mark.django_db
def test_book_list_displays_empty_state(client):
    response = client.get(reverse("reviews:book_list"))

    assert response.status_code == 200
    assert b"No books are available." in response.content


@pytest.mark.django_db
def test_book_detail_displays_book_average_and_only_its_reviews(client):
    user_model = get_user_model()
    alice = user_model.objects.create_user(username="alice")
    bob = user_model.objects.create_user(username="bob")
    book = Book.objects.create(title="Dune", description="Desert science fiction.")
    other_book = Book.objects.create(title="Foundation")
    Review.objects.create(text="Thoughtful.", rating=3, book=book, user=alice)
    Review.objects.create(text="Excellent.", rating=5, book=book, user=bob)
    Review.objects.create(
        text="Other book review.",
        rating=4,
        book=other_book,
        user=alice,
    )

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))

    assert response.status_code == 200
    assert b"Dune" in response.content
    assert b"Desert science fiction." in response.content
    assert b"Average rating: 4.0" in response.content
    assert b"alice" in response.content
    assert b"Thoughtful." in response.content
    assert b"bob" in response.content
    assert b"Excellent." in response.content
    assert b"Other book review." not in response.content


@pytest.mark.django_db
def test_book_detail_orders_reviews_newest_first(client):
    user_model = get_user_model()
    alice = user_model.objects.create_user(username="alice")
    bob = user_model.objects.create_user(username="bob")
    book = Book.objects.create(title="Dune")
    older = Review.objects.create(text="Older review", rating=3, book=book, user=alice)
    newer = Review.objects.create(text="Newer review", rating=5, book=book, user=bob)
    now = timezone.now()
    Review.objects.filter(pk=older.pk).update(created_at=now - timedelta(days=1))
    Review.objects.filter(pk=newer.pk).update(created_at=now)

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))
    content = response.content.decode()

    assert content.index("Newer review") < content.index("Older review")


@pytest.mark.django_db
def test_book_detail_displays_no_review_state(client):
    book = Book.objects.create(title="Dune")

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))

    assert response.status_code == 200
    assert b"No ratings yet." in response.content
    assert b"No reviews yet." in response.content


@pytest.mark.django_db
def test_book_detail_returns_404_for_missing_book(client):
    response = client.get(reverse("reviews:book_detail", args=[999]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_book_search_trims_and_uses_case_insensitive_partial_title(client):
    Book.objects.create(title="Dune Messiah")
    Book.objects.create(title="Foundation")

    response = client.get(reverse("reviews:book_search"), {"q": "  dUnE  "})

    assert response.status_code == 200
    assert b"Search query: dUnE" in response.content
    assert b"Dune Messiah" in response.content
    assert b"Foundation" not in response.content


@pytest.mark.django_db
def test_book_search_displays_no_match_state(client):
    Book.objects.create(title="Dune")

    response = client.get(reverse("reviews:book_search"), {"q": "Foundation"})

    assert response.status_code == 200
    assert b"No books matched." in response.content
    assert b"Dune" not in response.content


@pytest.mark.django_db
@pytest.mark.parametrize("query", [None, "", "   "])
def test_book_search_empty_query_does_not_list_all_books(client, query):
    Book.objects.create(title="Dune")
    parameters = {} if query is None else {"q": query}

    response = client.get(reverse("reviews:book_search"), parameters)

    assert response.status_code == 200
    assert b"Enter a book title to search." in response.content
    assert b"Dune" not in response.content


@pytest.mark.django_db
def test_review_create_displays_placeholder_without_creating_review(client):
    book = Book.objects.create(title="Dune")

    response = client.get(reverse("reviews:review_create", args=[book.pk]))

    assert response.status_code == 200
    assert b"Review Dune" in response.content
    assert b"Review submission is not available yet." in response.content
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_review_create_returns_404_for_missing_book(client):
    response = client.get(reverse("reviews:review_create", args=[999]))

    assert response.status_code == 404
    assert Review.objects.count() == 0


def test_book_list_redirect_uses_named_book_list_url(client):
    response = client.get(reverse("reviews:book_list_redirect"))

    assert response.status_code == 302
    assert response.url == reverse("reviews:book_list")


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("url_name", "needs_book"),
    [
        ("home", False),
        ("book_list", False),
        ("book_search", False),
        ("book_detail", True),
        ("review_create", True),
        ("book_list_redirect", False),
    ],
)
def test_views_reject_post_without_changing_data(client, url_name, needs_book):
    book = Book.objects.create(title="Dune")
    kwargs = {"book_id": book.pk} if needs_book else None
    url = reverse(f"reviews:{url_name}", kwargs=kwargs)
    before_books = Book.objects.count()
    before_reviews = Review.objects.count()

    response = client.post(url, {"text": "Should not be saved", "rating": 5})

    assert response.status_code == 405
    assert Book.objects.count() == before_books
    assert Review.objects.count() == before_reviews


@pytest.mark.django_db
def test_dynamic_book_and_query_values_are_escaped(client):
    Book.objects.create(title="<script>alert('book')</script>")

    list_response = client.get(reverse("reviews:book_list"))
    search_response = client.get(
        reverse("reviews:book_search"),
        {"q": "<script>alert('query')</script>"},
    )

    assert b"<script>" not in list_response.content
    assert b"&lt;script&gt;" in list_response.content
    assert b"<script>" not in search_response.content
    assert b"&lt;script&gt;" in search_response.content


@pytest.mark.django_db
def test_book_detail_escapes_description_author_and_review_text(client):
    user = get_user_model().objects.create_user(
        username="alice<em>author</em>",
    )
    book = Book.objects.create(
        title="Dune",
        description="<b>unsafe description</b>",
    )
    Review.objects.create(
        text="<script>unsafe review</script>",
        rating=5,
        book=book,
        user=user,
    )

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))

    assert response.status_code == 200
    assert b"<b>unsafe description</b>" not in response.content
    assert b"&lt;b&gt;unsafe description&lt;/b&gt;" in response.content
    assert b"alice<em>author</em>" not in response.content
    assert b"alice&lt;em&gt;author&lt;/em&gt;" in response.content
    assert b"<script>unsafe review</script>" not in response.content
    assert b"&lt;script&gt;unsafe review&lt;/script&gt;" in response.content

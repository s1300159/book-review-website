from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from django.utils import timezone

from reviews import views
from reviews.models import Book, Review


def _rendered_template_names(response):
    return {template.name for template in response.templates if template.name}


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
    dune = Book.objects.create(title="Dune")
    foundation = Book.objects.create(title="Foundation")

    response = client.get(reverse("reviews:book_list"))

    assert response.status_code == 200
    assert "reviews/book_list.html" in _rendered_template_names(response)
    assert "reviews/base.html" in _rendered_template_names(response)
    assert b"Dune" in response.content
    assert b"Foundation" in response.content
    assert (
        f'href="{reverse("reviews:book_detail", args=[dune.pk])}"'.encode()
        in response.content
    )
    assert (
        f'href="{reverse("reviews:book_detail", args=[foundation.pk])}"'.encode()
        in response.content
    )


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
    assert "reviews/book_detail.html" in _rendered_template_names(response)
    assert "reviews/base.html" in _rendered_template_names(response)
    assert b"Dune" in response.content
    assert b"Desert science fiction." in response.content
    assert b"Average rating: 4.0" in response.content
    assert b"alice" in response.content
    assert b"Thoughtful." in response.content
    assert b"bob" in response.content
    assert b"Excellent." in response.content
    assert b"Other book review." not in response.content
    assert (
        f'href="{reverse("reviews:review_create", args=[book.pk])}"'.encode()
        in response.content
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("url_name", "expected_template"),
    [
        ("book_list", "reviews/book_list.html"),
        ("book_detail", "reviews/book_detail.html"),
    ],
)
def test_book_pages_use_shared_semantic_layout_and_named_navigation(
    client,
    url_name,
    expected_template,
):
    book = Book.objects.create(title="Dune")
    kwargs = {"book_id": book.pk} if url_name == "book_detail" else None

    response = client.get(reverse(f"reviews:{url_name}", kwargs=kwargs))
    template_names = _rendered_template_names(response)

    assert response.status_code == 200
    assert expected_template in template_names
    assert "reviews/base.html" in template_names
    assert b"<header>" in response.content
    assert b'<nav aria-label="Primary navigation">' in response.content
    assert b"<main>" in response.content
    assert b"<footer>" in response.content
    for navigation_url in (
        reverse("reviews:home"),
        reverse("reviews:book_list"),
        reverse("reviews:book_search"),
    ):
        assert f'href="{navigation_url}"'.encode() in response.content


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
def test_first_book_detail_visit_records_integer_id_in_session(client):
    book = Book.objects.create(title="Dune")

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))

    assert response.status_code == 200
    assert client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == [book.pk]
    stored_id = client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY][0]
    assert isinstance(stored_id, int)
    assert not isinstance(stored_id, bool)


@pytest.mark.django_db
def test_revisiting_book_moves_id_to_front_without_duplicate(client):
    first_book = Book.objects.create(title="Dune")
    second_book = Book.objects.create(title="Foundation")
    client.get(reverse("reviews:book_detail", args=[first_book.pk]))
    client.get(reverse("reviews:book_detail", args=[second_book.pk]))

    response = client.get(reverse("reviews:book_detail", args=[first_book.pk]))

    assert response.status_code == 200
    assert client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == [
        first_book.pk,
        second_book.pk,
    ]


@pytest.mark.django_db
def test_recent_book_session_is_limited_to_five_and_evicts_oldest(client):
    books = [Book.objects.create(title=f"Book {index}") for index in range(6)]

    for book in books:
        response = client.get(reverse("reviews:book_detail", args=[book.pk]))
        assert response.status_code == 200

    assert client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == [
        book.pk for book in reversed(books[1:])
    ]
    assert books[0].pk not in client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY]


@pytest.mark.django_db
@pytest.mark.parametrize("stored_value", ["invalid", {"book": 1}, None])
def test_non_list_recent_book_session_value_is_normalized(
    client,
    stored_value,
):
    book = Book.objects.create(title="Dune")
    session = client.session
    session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] = stored_value
    session.save()

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))

    assert response.status_code == 200
    assert client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == [book.pk]


@pytest.mark.django_db
def test_mixed_recent_book_session_list_is_safely_normalized(client):
    current_book = Book.objects.create(title="Dune")
    previous_book = Book.objects.create(title="Foundation")
    session = client.session
    session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] = [
        previous_book.pk,
        "invalid",
        True,
        None,
        previous_book.pk,
    ]
    session.save()

    response = client.get(reverse("reviews:book_detail", args=[current_book.pk]))

    assert response.status_code == 200
    assert client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == [
        current_book.pk,
        previous_book.pk,
    ]


@pytest.mark.django_db
def test_missing_book_does_not_change_recent_book_session(client):
    book = Book.objects.create(title="Dune")
    session = client.session
    original_history = [book.pk, 987]
    session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] = original_history
    session.save()

    response = client.get(reverse("reviews:book_detail", args=[999]))

    assert response.status_code == 404
    assert (
        client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == original_history
    )


@pytest.mark.django_db
def test_recent_book_histories_are_isolated_between_clients(client):
    second_client = client.__class__()
    first_book = Book.objects.create(title="Dune")
    second_book = Book.objects.create(title="Foundation")

    client.get(reverse("reviews:book_detail", args=[first_book.pk]))
    second_client.get(reverse("reviews:book_detail", args=[second_book.pk]))

    assert client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == [first_book.pk]
    assert second_client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == [
        second_book.pk
    ]


@pytest.mark.django_db
def test_detail_session_excludes_get_parameters_and_domain_content(client):
    user = get_user_model().objects.create_user(username="alice")
    book = Book.objects.create(title="Dune", description="Desert science fiction.")
    Review.objects.create(
        text="Important review content.",
        rating=5,
        book=book,
        user=user,
    )

    response = client.get(
        reverse("reviews:book_detail", args=[book.pk]),
        {
            "q": "Dune",
            "sort": "rating",
            "min_rating": "4",
            "page": "2",
        },
    )

    assert response.status_code == 200
    assert dict(client.session.items()) == {
        views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY: [book.pk]
    }


@pytest.mark.django_db
def test_detail_session_update_does_not_change_books_or_reviews(client):
    user = get_user_model().objects.create_user(username="alice")
    book = Book.objects.create(title="Dune", description="Original description.")
    review = Review.objects.create(
        text="Original review.",
        rating=4,
        book=book,
        user=user,
    )
    book_snapshot = list(Book.objects.values())
    review_snapshot = list(Review.objects.values())

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))

    assert response.status_code == 200
    assert list(Book.objects.values()) == book_snapshot
    assert list(Review.objects.values()) == review_snapshot
    assert Review.objects.get(pk=review.pk).text == "Original review."


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
    session = client.session
    original_history = [book.pk]
    session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] = original_history
    session.save()

    response = client.post(url, {"text": "Should not be saved", "rating": 5})

    assert response.status_code == 405
    assert Book.objects.count() == before_books
    assert Review.objects.count() == before_reviews
    assert (
        client.session[views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY] == original_history
    )


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
        title="<i>unsafe title</i>",
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
    assert b"<i>unsafe title</i>" not in response.content
    assert b"&lt;i&gt;unsafe title&lt;/i&gt;" in response.content
    assert b"<b>unsafe description</b>" not in response.content
    assert b"&lt;b&gt;unsafe description&lt;/b&gt;" in response.content
    assert b"alice<em>author</em>" not in response.content
    assert b"alice&lt;em&gt;author&lt;/em&gt;" in response.content
    assert b"<script>unsafe review</script>" not in response.content
    assert b"&lt;script&gt;unsafe review&lt;/script&gt;" in response.content

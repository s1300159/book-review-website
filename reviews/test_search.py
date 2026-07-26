import re

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from reviews import views
from reviews.models import Book, Review


def _rendered_template_names(response):
    return {template.name for template in response.templates if template.name}


@pytest.mark.django_db
def test_search_uses_form_template_and_shared_layout(client):
    response = client.get(reverse("reviews:book_search"))

    assert response.status_code == 200
    assert "reviews/book_search.html" in _rendered_template_names(response)
    assert "reviews/base.html" in _rendered_template_names(response)
    assert "reviews/partials/book_results.html" in _rendered_template_names(response)
    assert b'name="q"' in response.content
    assert b'name="min_rating"' in response.content
    assert b'hx-target="#book-results"' in response.content
    assert b'hx-push-url="true"' in response.content
    assert b"delay:300ms" in response.content
    assert b"reviews/htmx.min.js" in response.content


@pytest.mark.django_db
def test_htmx_search_returns_only_the_result_partial(client):
    Book.objects.create(title="Dune")

    response = client.get(
        reverse("reviews:book_search"),
        HTTP_HX_REQUEST="true",
    )

    template_names = _rendered_template_names(response)
    assert response.status_code == 200
    assert "reviews/partials/book_results.html" in template_names
    assert "reviews/book_search.html" not in template_names
    assert "reviews/base.html" not in template_names
    assert b"View details for Dune" in response.content
    assert b"<html" not in response.content
    assert b"<form" not in response.content
    assert "HX-Request" in response.headers["Vary"]


def _create_htmx_search_books():
    user_model = get_user_model()
    alice = user_model.objects.create_user(username="alice")
    bob = user_model.objects.create_user(username="bob")
    dune_messiah = Book.objects.create(title="Dune Messiah")
    dune = Book.objects.create(title="Dune")
    foundation = Book.objects.create(title="Foundation")
    Book.objects.create(title="Unrated Book")
    Review.objects.create(
        text="Great.",
        rating=4,
        book=dune_messiah,
        user=alice,
    )
    Review.objects.create(
        text="Below.",
        rating=3,
        book=dune,
        user=alice,
    )
    Review.objects.create(
        text="Excellent.",
        rating=5,
        book=foundation,
        user=bob,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("parameters", "included_titles", "excluded_titles"),
    [
        (
            {"q": "dune"},
            ("Dune Messiah", "Dune"),
            ("Foundation", "Unrated Book"),
        ),
        (
            {"min_rating": "4"},
            ("Dune Messiah", "Foundation"),
            ("Dune", "Unrated Book"),
        ),
        (
            {"q": "dune", "min_rating": "4"},
            ("Dune Messiah",),
            ("Dune", "Foundation", "Unrated Book"),
        ),
        (
            {},
            ("Dune Messiah", "Dune", "Foundation", "Unrated Book"),
            (),
        ),
    ],
)
def test_htmx_search_uses_existing_filters(
    client,
    parameters,
    included_titles,
    excluded_titles,
):
    _create_htmx_search_books()

    response = client.get(
        reverse("reviews:book_search"),
        parameters,
        HTTP_HX_REQUEST="true",
    )

    content = response.content.decode()
    assert response.status_code == 200
    for title in included_titles:
        assert re.search(rf"View details for {re.escape(title)}\s*</a>", content)
    for title in excluded_titles:
        assert not re.search(rf"View details for {re.escape(title)}\s*</a>", content)


@pytest.mark.django_db
def test_htmx_search_displays_no_match_state(client):
    Book.objects.create(title="Dune")

    response = client.get(
        reverse("reviews:book_search"),
        {"q": "Foundation"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert b"No books matched." in response.content
    assert b"Try changing your search conditions." in response.content
    assert b"View details for Dune" not in response.content


@pytest.mark.django_db
def test_htmx_search_does_not_save_values_in_session(client):
    Book.objects.create(title="Dune")

    response = client.get(
        reverse("reviews:book_search"),
        {"q": "Dune", "min_rating": "4"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY not in client.session
    assert "q" not in client.session
    assert "min_rating" not in client.session


@pytest.mark.django_db
def test_htmx_search_fragment_escapes_dynamic_html(client):
    Book.objects.create(
        title="<script>unsafe title</script>",
        description="<img src=x onerror=alert(1)>",
    )

    response = client.get(
        reverse("reviews:book_search"),
        {"q": "<script>"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert b"<script>" not in response.content
    assert b"<img src=x" not in response.content
    assert b"&lt;script&gt;" in response.content
    assert b"&lt;img src=x onerror=alert(1)&gt;" in response.content


@pytest.mark.django_db
def test_minimum_rating_filters_by_average_and_excludes_unrated_books(client):
    user_model = get_user_model()
    alice = user_model.objects.create_user(username="alice")
    bob = user_model.objects.create_user(username="bob")
    boundary_book = Book.objects.create(title="Boundary Book")
    low_book = Book.objects.create(title="Low Book")
    Book.objects.create(title="Unrated Book")
    Review.objects.create(
        text="Good.",
        rating=3,
        book=boundary_book,
        user=alice,
    )
    Review.objects.create(
        text="Great.",
        rating=5,
        book=boundary_book,
        user=bob,
    )
    Review.objects.create(
        text="Below.",
        rating=3,
        book=low_book,
        user=alice,
    )

    response = client.get(
        reverse("reviews:book_search"),
        {"min_rating": "4"},
    )

    assert response.status_code == 200
    assert b"Boundary Book" in response.content
    assert b"Low Book" not in response.content
    assert b"Unrated Book" not in response.content


@pytest.mark.django_db
def test_title_and_minimum_rating_filters_are_combined(client):
    user_model = get_user_model()
    alice = user_model.objects.create_user(username="alice")
    bob = user_model.objects.create_user(username="bob")
    matching_book = Book.objects.create(title="Dune Messiah")
    low_dune = Book.objects.create(title="Dune")
    high_other = Book.objects.create(title="Foundation")
    Review.objects.create(
        text="Match.",
        rating=4,
        book=matching_book,
        user=alice,
    )
    Review.objects.create(
        text="Too low.",
        rating=3,
        book=low_dune,
        user=alice,
    )
    Review.objects.create(
        text="Wrong title.",
        rating=5,
        book=high_other,
        user=bob,
    )

    response = client.get(
        reverse("reviews:book_search"),
        {"q": "dune", "min_rating": "4"},
    )

    assert response.status_code == 200
    assert b"Dune Messiah" in response.content
    assert b">Dune<" not in response.content
    assert b"Foundation" not in response.content


@pytest.mark.django_db
def test_invalid_minimum_rating_displays_field_error_without_results(client):
    Book.objects.create(title="Dune")

    response = client.get(
        reverse("reviews:book_search"),
        {"min_rating": "6"},
    )

    assert response.status_code == 200
    assert b"Select a valid choice" in response.content
    assert b"Dune" not in response.content


@pytest.mark.django_db
def test_valid_search_without_results_prompts_for_changed_conditions(client):
    Book.objects.create(title="Dune")

    response = client.get(
        reverse("reviews:book_search"),
        {"q": "Foundation"},
    )

    assert response.status_code == 200
    assert b"No books matched." in response.content
    assert b"Try changing your search conditions." in response.content


@pytest.mark.django_db
def test_search_values_are_not_saved_in_session(client):
    user = get_user_model().objects.create_user(username="alice")
    book = Book.objects.create(title="Dune")
    Review.objects.create(
        text="Excellent.",
        rating=5,
        book=book,
        user=user,
    )

    response = client.get(
        reverse("reviews:book_search"),
        {"q": "Dune", "min_rating": "4"},
    )

    assert response.status_code == 200
    assert views.RECENTLY_VIEWED_BOOK_IDS_SESSION_KEY not in client.session
    assert "q" not in client.session
    assert "min_rating" not in client.session

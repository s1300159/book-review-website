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
    assert b'name="q"' in response.content
    assert b'name="min_rating"' in response.content


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

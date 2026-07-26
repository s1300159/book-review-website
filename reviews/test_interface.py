from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.urls import reverse

from reviews.models import Book


def test_shared_layout_loads_responsive_external_stylesheet(client):
    response = client.get(reverse("reviews:home"))

    assert response.status_code == 200
    assert b'<meta name="viewport" content="width=device-width, initial-scale=1">' in (
        response.content
    )
    assert b'href="/static/reviews/style.css"' in response.content
    assert b'<main id="main-content"' in response.content
    assert b'href="#main-content"' in response.content


@pytest.mark.django_db
def test_book_cards_show_rating_description_link_and_cover_alt(client):
    user = get_user_model().objects.create_user(username="alice")
    book = Book.objects.create(
        title="Dune",
        description="Desert science fiction.",
        cover_image="book_covers/dune.jpg",
    )
    book.reviews.create(
        text="Excellent.",
        rating=5,
        user=user,
    )

    response = client.get(reverse("reviews:book_list"))

    assert response.status_code == 200
    assert b"Average rating: 5.0 / 5" in response.content
    assert b"Desert science fiction." in response.content
    assert b'alt="Cover of Dune"' in response.content
    assert b"View details for Dune" in response.content


@pytest.mark.django_db
def test_existing_forms_render_associated_labels(client):
    user = get_user_model().objects.create_user(username="alice")
    book = Book.objects.create(title="Dune")
    client.force_login(user)

    search_response = client.get(reverse("reviews:book_search"))
    review_response = client.get(reverse("reviews:review_create", args=[book.pk]))
    login_response = client.get(reverse("login"))

    assert b'<label for="id_q">Book title:</label>' in search_response.content
    assert b'<label for="id_text">Text:</label>' in review_response.content
    assert b'<label for="id_username">Username:</label>' in login_response.content


def test_stylesheet_includes_responsive_and_visible_focus_rules():
    stylesheet_path = finders.find("reviews/style.css")

    assert stylesheet_path is not None
    stylesheet = Path(stylesheet_path).read_text(encoding="utf-8")
    assert "@media (max-width: 42rem)" in stylesheet
    assert ":focus-visible" in stylesheet
    assert "max-width: 100%" in stylesheet

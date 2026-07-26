from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client
from django.urls import reverse

from reviews.models import Book, Review


@pytest.fixture(name="user")
def user_fixture():
    return get_user_model().objects.create_user(
        username="alice",
        password="test-password",
    )


@pytest.fixture(name="book")
def book_fixture():
    return Book.objects.create(title="Dune")


@pytest.mark.django_db
def test_unauthenticated_create_redirects_to_login_with_next(client, book):
    url = reverse("reviews:review_create", args=[book.pk])

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"


@pytest.mark.django_db
def test_authenticated_create_get_displays_shared_form(client, user, book):
    client.force_login(user)

    response = client.get(reverse("reviews:review_create", args=[book.pk]))

    assert response.status_code == 200
    assert response.templates[0].name == "reviews/review_form.html"
    assert b"Write a review" in response.content
    assert b'name="text"' in response.content
    assert b'name="rating"' in response.content
    assert b"csrfmiddlewaretoken" in response.content
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_create_returns_404_for_missing_book_after_authentication(client, user):
    client.force_login(user)

    response = client.get(reverse("reviews:review_create", args=[999]))

    assert response.status_code == 404
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_valid_create_uses_trusted_relationships_message_and_named_redirect(
    client,
    user,
    book,
):
    other_user = get_user_model().objects.create_user(username="mallory")
    other_book = Book.objects.create(title="Foundation")
    client.force_login(user)

    response = client.post(
        reverse("reviews:review_create", args=[book.pk]),
        {
            "text": "  Excellent book.  ",
            "rating": "5",
            "user": other_user.pk,
            "book": other_book.pk,
        },
        follow=True,
    )

    review = Review.objects.get()
    assert review.text == "Excellent book."
    assert review.rating == 5
    assert review.user == user
    assert review.book == book
    assert response.redirect_chain == [
        (reverse("reviews:book_detail", args=[book.pk]), 302)
    ]
    assert b"Your review was created successfully." in response.content


@pytest.mark.django_db
def test_invalid_create_returns_200_with_errors_and_no_write(client, user, book):
    client.force_login(user)

    response = client.post(
        reverse("reviews:review_create", args=[book.pk]),
        {"text": "   ", "rating": "6"},
    )

    assert response.status_code == 200
    assert b"Review text cannot be empty." in response.content
    assert b"Select a valid choice" in response.content
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_empty_create_post_is_bound_and_displays_required_errors(
    client,
    user,
    book,
):
    client.force_login(user)

    response = client.post(
        reverse("reviews:review_create", args=[book.pk]),
        {},
    )

    assert response.status_code == 200
    assert b"Review text cannot be empty." in response.content
    assert b"This field is required." in response.content
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_duplicate_create_displays_non_field_error(client, user, book):
    Review.objects.create(
        text="Existing.",
        rating=4,
        user=user,
        book=book,
    )
    client.force_login(user)

    response = client.post(
        reverse("reviews:review_create", args=[book.pk]),
        {"text": "Duplicate.", "rating": "5"},
    )

    assert response.status_code == 200
    assert b"You have already reviewed this book." in response.content
    assert Review.objects.count() == 1


@pytest.mark.django_db
def test_create_handles_integrity_error_as_non_field_error(client, user, book):
    client.force_login(user)

    with patch(
        "reviews.views.ReviewForm.save",
        side_effect=IntegrityError("simulated duplicate race"),
    ):
        response = client.post(
            reverse("reviews:review_create", args=[book.pk]),
            {"text": "Concurrent review.", "rating": "4"},
        )

    assert response.status_code == 200
    assert b"You have already reviewed this book." in response.content
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_author_edit_get_displays_existing_values(client, user, book):
    review = Review.objects.create(
        text="Original review.",
        rating=3,
        user=user,
        book=book,
    )
    client.force_login(user)

    response = client.get(reverse("reviews:review_edit", args=[review.pk]))

    assert response.status_code == 200
    assert b"Edit your review" in response.content
    assert b"Original review." in response.content
    assert b'<option value="3" selected>' in response.content


@pytest.mark.django_db
def test_author_can_edit_public_fields_without_changing_relationships(
    client,
    user,
    book,
):
    review = Review.objects.create(
        text="Original review.",
        rating=3,
        user=user,
        book=book,
    )
    other_user = get_user_model().objects.create_user(username="mallory")
    other_book = Book.objects.create(title="Foundation")
    client.force_login(user)

    response = client.post(
        reverse("reviews:review_edit", args=[review.pk]),
        {
            "text": "Updated review.",
            "rating": "5",
            "user": other_user.pk,
            "book": other_book.pk,
        },
        follow=True,
    )

    review.refresh_from_db()
    assert review.text == "Updated review."
    assert review.rating == 5
    assert review.user == user
    assert review.book == book
    assert response.redirect_chain == [
        (reverse("reviews:book_detail", args=[book.pk]), 302)
    ]
    assert b"Your review was updated successfully." in response.content


@pytest.mark.django_db
def test_unauthenticated_edit_redirects_to_login_with_next(client, user, book):
    review = Review.objects.create(
        text="Original review.",
        rating=3,
        user=user,
        book=book,
    )
    url = reverse("reviews:review_edit", args=[review.pk])

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["get", "post"])
def test_authenticated_non_author_receives_403(
    client,
    user,
    book,
    method,
):
    review = Review.objects.create(
        text="Original review.",
        rating=3,
        user=user,
        book=book,
    )
    non_author = get_user_model().objects.create_user(username="bob")
    client.force_login(non_author)

    response = getattr(client, method)(
        reverse("reviews:review_edit", args=[review.pk]),
        {"text": "Forbidden change.", "rating": "5"},
    )

    assert response.status_code == 403
    review.refresh_from_db()
    assert review.text == "Original review."
    assert review.rating == 3


@pytest.mark.django_db
def test_invalid_edit_returns_200_and_leaves_persisted_review_unchanged(
    client,
    user,
    book,
):
    review = Review.objects.create(
        text="Original review.",
        rating=3,
        user=user,
        book=book,
    )
    client.force_login(user)

    response = client.post(
        reverse("reviews:review_edit", args=[review.pk]),
        {"text": "   ", "rating": "0"},
    )

    assert response.status_code == 200
    review.refresh_from_db()
    assert review.text == "Original review."
    assert review.rating == 3


@pytest.mark.django_db
def test_edit_returns_404_for_missing_review(client, user):
    client.force_login(user)

    response = client.get(reverse("reviews:review_edit", args=[999]))

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["review_create", "review_edit"])
@pytest.mark.parametrize("method", ["put", "delete"])
def test_review_workflows_reject_unsupported_methods(
    client,
    user,
    book,
    url_name,
    method,
):
    review = Review.objects.create(
        text="Original review.",
        rating=3,
        user=user,
        book=book,
    )
    client.force_login(user)
    if url_name == "review_create":
        url = reverse("reviews:review_create", args=[book.pk])
    else:
        url = reverse("reviews:review_edit", args=[review.pk])

    response = getattr(client, method)(url)

    assert response.status_code == 405
    assert Review.objects.count() == 1


@pytest.mark.django_db
def test_book_detail_shows_create_action_to_user_without_review(
    client,
    user,
    book,
):
    client.force_login(user)

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))

    assert reverse("reviews:review_create", args=[book.pk]).encode() in response.content
    assert b"Write a review" in response.content


@pytest.mark.django_db
def test_book_detail_shows_edit_action_to_review_author(client, user, book):
    review = Review.objects.create(
        text="Existing.",
        rating=4,
        user=user,
        book=book,
    )
    client.force_login(user)

    response = client.get(reverse("reviews:book_detail", args=[book.pk]))

    assert reverse("reviews:review_edit", args=[review.pk]).encode() in response.content
    assert b"Edit your review" in response.content
    assert (
        reverse("reviews:review_create", args=[book.pk]).encode()
        not in response.content
    )


@pytest.mark.django_db
def test_review_create_requires_csrf_token(user, book):
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(user)

    response = csrf_client.post(
        reverse("reviews:review_create", args=[book.pk]),
        {"text": "Missing token.", "rating": "4"},
    )

    assert response.status_code == 403
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_review_create_accepts_valid_csrf_token(user, book):
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(user)
    url = reverse("reviews:review_create", args=[book.pk])
    csrf_client.get(url)
    token = csrf_client.cookies["csrftoken"].value

    response = csrf_client.post(
        url,
        {"text": "Protected review.", "rating": "4"},
        HTTP_X_CSRFTOKEN=token,
    )

    assert response.status_code == 302
    assert Review.objects.filter(user=user, book=book).exists()

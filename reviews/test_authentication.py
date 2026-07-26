import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import NoReverseMatch, reverse

from reviews.models import Book


def _rendered_template_names(response):
    return {template.name for template in response.templates if template.name}


def test_login_url_is_named_and_standard():
    assert reverse("login") == "/accounts/login/"


@pytest.mark.django_db
def test_login_get_uses_shared_template_and_preserves_next(client):
    book = Book.objects.create(title="Dune")
    next_url = reverse("reviews:review_create", args=[book.pk])

    response = client.get(reverse("login"), {"next": next_url})

    assert response.status_code == 200
    assert "registration/login.html" in _rendered_template_names(response)
    assert "reviews/base.html" in _rendered_template_names(response)
    assert b"csrfmiddlewaretoken" in response.content
    assert f'name="next" value="{next_url}"'.encode() in response.content


@pytest.mark.django_db
def test_invalid_login_displays_non_field_errors(client):
    get_user_model().objects.create_user(
        username="alice",
        password="correct-password",
    )

    response = client.post(
        reverse("login"),
        {"username": "alice", "password": "wrong-password"},
    )

    assert response.status_code == 200
    assert b"Please enter a correct username and password." in response.content
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_valid_login_preserves_next_destination(client):
    get_user_model().objects.create_user(
        username="alice",
        password="test-password",
    )
    book = Book.objects.create(title="Dune")
    next_url = reverse("reviews:review_create", args=[book.pk])

    response = client.post(
        reverse("login"),
        {
            "username": "alice",
            "password": "test-password",
            "next": next_url,
        },
    )

    assert response.status_code == 302
    assert response.url == next_url


@pytest.mark.django_db
def test_login_without_next_uses_named_default_redirect(client):
    get_user_model().objects.create_user(
        username="alice",
        password="test-password",
    )

    response = client.post(
        reverse("login"),
        {"username": "alice", "password": "test-password"},
    )

    assert response.status_code == 302
    assert response.url == reverse("reviews:book_list")


@pytest.mark.django_db
def test_login_requires_csrf_token():
    get_user_model().objects.create_user(
        username="alice",
        password="test-password",
    )
    csrf_client = Client(enforce_csrf_checks=True)

    response = csrf_client.post(
        reverse("login"),
        {"username": "alice", "password": "test-password"},
    )

    assert response.status_code == 403
    assert "_auth_user_id" not in csrf_client.session


@pytest.mark.django_db
def test_login_accepts_valid_csrf_token():
    get_user_model().objects.create_user(
        username="alice",
        password="test-password",
    )
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.get(reverse("login"))
    token = csrf_client.cookies["csrftoken"].value

    response = csrf_client.post(
        reverse("login"),
        {"username": "alice", "password": "test-password"},
        HTTP_X_CSRFTOKEN=token,
    )

    assert response.status_code == 302
    assert "_auth_user_id" in csrf_client.session


def test_user_registration_route_is_not_added():
    with pytest.raises(NoReverseMatch):
        reverse("signup")

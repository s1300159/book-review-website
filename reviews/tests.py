import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from reviews.models import Book, Review


@pytest.mark.django_db
class TestBookAndReviewModels:
    user = None
    book = None

    def setup_method(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="alice",
            password="test-password",
        )
        self.book = Book.objects.create(title="Dune")

    def test_book_can_be_created_with_optional_fields_blank(self):
        assert self.book.title == "Dune"
        assert self.book.cover_image.name == ""
        assert self.book.description == ""

    def test_book_title_is_required_and_limited_to_200_characters(self):
        with pytest.raises(ValidationError):
            Book(title="").full_clean()

        with pytest.raises(ValidationError):
            Book(title="x" * 201).full_clean()

    def test_book_string_returns_title(self):
        assert str(self.book) == "Dune"

    def test_review_can_be_created_with_expected_relationships(self):
        review = Review.objects.create(
            text="A memorable science-fiction novel.",
            rating=5,
            book=self.book,
            user=self.user,
        )

        assert review.book == self.book
        assert review.user == self.user
        assert review.created_at is not None
        assert list(self.book.reviews.all()) == [review]
        assert list(self.user.reviews.all()) == [review]
        assert Review._meta.get_field("user").remote_field.model is get_user_model()

    def test_review_string_contains_username_and_book_title(self):
        review = Review.objects.create(
            text="Excellent.",
            rating=5,
            book=self.book,
            user=self.user,
        )

        assert str(review) == "alice - Dune"

    @pytest.mark.parametrize("rating", [1, 5])
    def test_rating_boundaries_are_valid(self, rating):
        review = Review(
            text="Valid boundary.",
            rating=rating,
            book=self.book,
            user=self.user,
        )

        review.full_clean()

    @pytest.mark.parametrize("rating", [0, 6])
    def test_rating_outside_range_fails_model_validation(self, rating):
        review = Review(
            text="Invalid boundary.",
            rating=rating,
            book=self.book,
            user=self.user,
        )

        with pytest.raises(ValidationError):
            review.full_clean()

    @pytest.mark.parametrize("rating", [0, 6])
    def test_rating_outside_range_fails_database_constraint(self, rating):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    text="Invalid boundary.",
                    rating=rating,
                    book=self.book,
                    user=self.user,
                )

    def test_duplicate_review_fails_model_validation(self):
        Review.objects.create(
            text="First review.",
            rating=4,
            book=self.book,
            user=self.user,
        )
        duplicate = Review(
            text="Second review.",
            rating=3,
            book=self.book,
            user=self.user,
        )

        with pytest.raises(ValidationError):
            duplicate.full_clean()

    def test_duplicate_review_fails_database_constraint(self):
        Review.objects.create(
            text="First review.",
            rating=4,
            book=self.book,
            user=self.user,
        )

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    text="Second review.",
                    rating=3,
                    book=self.book,
                    user=self.user,
                )

    def test_different_users_can_review_same_book(self):
        second_user = get_user_model().objects.create_user(username="bob")
        Review.objects.create(
            text="Alice review.",
            rating=4,
            book=self.book,
            user=self.user,
        )

        second_review = Review.objects.create(
            text="Bob review.",
            rating=5,
            book=self.book,
            user=second_user,
        )

        assert second_review.pk is not None

    def test_same_user_can_review_different_books(self):
        second_book = Book.objects.create(title="Foundation")
        Review.objects.create(
            text="Dune review.",
            rating=4,
            book=self.book,
            user=self.user,
        )

        second_review = Review.objects.create(
            text="Foundation review.",
            rating=5,
            book=second_book,
            user=self.user,
        )

        assert second_review.pk is not None

    def test_average_rating_is_none_without_reviews(self):
        assert self.book.average_rating is None

    def test_average_rating_is_calculated_from_related_reviews(self):
        second_user = get_user_model().objects.create_user(username="bob")
        Review.objects.create(
            text="Alice review.",
            rating=3,
            book=self.book,
            user=self.user,
        )
        Review.objects.create(
            text="Bob review.",
            rating=5,
            book=self.book,
            user=second_user,
        )

        assert self.book.average_rating == 4.0

    def test_deleting_book_cascades_to_reviews(self):
        Review.objects.create(
            text="Review.",
            rating=4,
            book=self.book,
            user=self.user,
        )

        self.book.delete()

        assert Review.objects.count() == 0

    def test_deleting_user_cascades_to_reviews(self):
        Review.objects.create(
            text="Review.",
            rating=4,
            book=self.book,
            user=self.user,
        )

        self.user.delete()

        assert Review.objects.count() == 0

    def test_models_are_registered_with_admin(self):
        assert admin.site.is_registered(Book)
        assert admin.site.is_registered(Review)
